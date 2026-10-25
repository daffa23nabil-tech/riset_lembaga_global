"""Event study lintas saham BEI untuk E1 dan E2 (RQ C: siapa yang membayar?).

Input : data/olah/{harga.csv.gz, bench.csv, static.csv, msci.csv}, opsional data/olah/ppk_event.csv (01f)
        atau data/mentah/idx_ppk.csv
Output: hasil/sampel_<event>.csv, hasil/regresi.csv, hasil/kerugian_kelompok.csv,
        hasil/jalur_car.csv (+ .png), hasil/ringkasan.md
"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

import konfigurasi as k

DEPENDEN = ["car_0", "car_0_1", "car_0_5", "car_2_20", "car_2_60", "abn_car_0_1"]
MIN_HARI_TRADING_ESTIMASI = 100


def muat():
    harga = pd.read_csv(k.DATA_OLAH / "harga.csv.gz", parse_dates=["date"])
    bench = pd.read_csv(k.DATA_OLAH / "bench.csv", parse_dates=["date"]).dropna(subset=["JCI"])
    bench = bench.sort_values("date").set_index("date")
    static = pd.read_csv(k.DATA_OLAH / "static.csv").set_index("ticker")
    msci = pd.read_csv(k.DATA_OLAH / "msci.csv")
    # PPK: status per hari bursa sebelum tiap event (dari kolom Remarks BEI, 01f) bila ada;
    # kalau tidak, status terkini dari daftar saham BEI untuk semua event.
    ppk_event = k.DATA_OLAH / "ppk_event.csv"
    ppk_path = k.DATA_MENTAH / "idx_ppk.csv"
    ppk = None
    if ppk_event.exists():
        p = pd.read_csv(ppk_event)
        ppk = {ev: set(g.loc[g["ppk"] == 1, "ticker"]) for ev, g in p.groupby("event")}
    elif ppk_path.exists():
        p = pd.read_csv(ppk_path, comment="#")
        ppk = set(p.loc[p["ppk"] == 1, "ticker"].map(k.kode))
    return harga, bench, static, msci, ppk


def lebar(harga, kolom, kalender):
    return harga.pivot_table(index="date", columns="ticker", values=kolom).reindex(kalender)


def return_harian(level: pd.DataFrame) -> pd.DataFrame:
    # Hari suspensi diisi harga terakhir: return 0 selama suspensi, seluruh gerak tercatat saat dibuka lagi.
    return level.ffill().pct_change(fill_method=None)


def beta(y, x):
    ok = ~(np.isnan(y) | np.isnan(x))
    if ok.sum() < MIN_HARI_TRADING_ESTIMASI:
        return np.nan, np.nan
    b = np.cov(y[ok], x[ok])[0, 1] / np.var(x[ok], ddof=1)
    return y[ok].mean() - b * x[ok].mean(), b


def bangun_sampel(ev, cfg, r, px, vol, rb, static, msci, ppk):
    kal = r.index
    t0 = int(np.searchsorted(kal, pd.Timestamp(cfg["hari0"])))
    akhir = len(kal) - 1
    e0, e1 = t0 + k.JENDELA_ESTIMASI[0], t0 + k.JENDELA_ESTIMASI[1]
    p0, p1 = t0 + k.JENDELA_PRA[0], t0 + k.JENDELA_PRA[1]
    if e0 < 0:
        raise SystemExit(f"{ev}: data kurang panjang untuk jendela estimasi (perlu mulai lebih awal dari {kal[0]:%Y-%m-%d}).")
    # Hari [-1,+5] di sekitar event mana pun dikeluarkan dari jendela estimasi,
    # supaya crash E1 tidak menggelembungkan beta saat mengestimasi E2.
    kecuali = np.zeros(len(kal), dtype=bool)
    for c in k.EVENTS.values():
        te = int(np.searchsorted(kal, pd.Timestamp(c["hari0"])))
        kecuali[max(te - 1, 0):te + 6] = True
    est = np.arange(e0, e1 + 1)
    est = est[~kecuali[est]]
    rj, rm = rb["JCI"].to_numpy(), rb["MXEF"].to_numpy()
    anggota = msci[msci["event"] == ev].set_index("ticker")["bobot"]
    nilai_transaksi = px.ffill() * vol

    baris = []
    for t in r.columns:
        ri = r[t].to_numpy()
        traded = (vol[t].iloc[e0:e1 + 1] > 0).sum()
        if traded < MIN_HARI_TRADING_ESTIMASI or np.isnan(px[t].ffill().iloc[t0 - 1]):
            continue
        _, b_jci = beta(ri[est], rj[est])
        a_m, b_m = beta(ri[est], rm[est])
        d = {"ticker": t, "beta_jci": b_jci, "beta_mxef": b_m}
        for nama, (a, b) in k.JENDELA_CAR.items():
            lo, hi = t0 + a, t0 + b
            d[nama] = np.nansum(ri[lo:hi + 1]) * 100 if hi <= akhir else np.nan
            if hi <= akhir:
                ar = ri[lo:hi + 1] - (a_m + b_m * rm[lo:hi + 1])
                d["abn_" + nama] = np.nansum(ar) * 100
            else:
                d["abn_" + nama] = np.nan
        d["ret_pre"] = np.nansum(ri[p0:p1 + 1]) * 100
        nt = nilai_transaksi[t].iloc[p0:p1 + 1].to_numpy()
        ok = nt > 0
        d["amihud"] = np.nanmean(np.abs(ri[p0:p1 + 1][ok]) / nt[ok]) * 1e9 if ok.any() else np.nan
        d["px_pre"] = px[t].ffill().iloc[t0 - 1]
        d["vol_0"] = vol[t].iloc[t0]
        baris.append(d)

    s = pd.DataFrame(baris).set_index("ticker")
    s = s.join(static[["GICS_INDUSTRY_NAME", "EQY_FREE_FLOAT_PCT", "EQY_SH_OUT"]], how="left")
    # EQY_SH_OUT Bloomberg dalam juta lembar -> kapitalisasi dalam Rp.
    s["mcap_rp"] = s["px_pre"] * s["EQY_SH_OUT"] * 1e6
    s["log_mcap"] = np.log(s["mcap_rp"])
    s["log_amihud"] = np.log(s["amihud"].where(s["amihud"] > 0))
    s["free_float"] = s["EQY_FREE_FLOAT_PCT"]
    ff_path = k.DATA_OLAH / "ff_event.csv"  # free float BEI per tanggal snapshot event, bila ada
    if ff_path.exists():
        ffe = pd.read_csv(ff_path)
        ffe = ffe[ffe["event"] == ev].set_index("ticker")["free_float"]
        s["free_float"] = ffe.reindex(s.index).fillna(s["free_float"])
    s["bank"] = (s["GICS_INDUSTRY_NAME"] == "Banks").astype(int)
    s["msci"] = s.index.isin(anggota.index).astype(int)
    s["bobot_msci"] = anggota.reindex(s.index).fillna(0.0)
    if ppk is not None:
        s["ppk"] = s.index.isin(ppk.get(ev, set()) if isinstance(ppk, dict) else ppk).astype(int)
    s = s.dropna(subset=["log_mcap"])
    s["desil_ukuran"] = pd.qcut(s["log_mcap"], 10, labels=False, duplicates="drop")
    s["event"] = ev
    return s, kal[t0]


def regresi(s, ev, ada_ppk):
    kontrol = "bank + beta_jci + log_amihud + free_float + ret_pre" + (" + ppk" if ada_ppk else "")
    spesifikasi = {
        "M1 kontrol ukuran": f"msci + log_mcap + {kontrol}",
        "M2 FE desil ukuran": f"msci + {kontrol} + C(desil_ukuran)",
    }
    out = []
    for y in DEPENDEN:
        if s[y].isna().all():
            continue
        for nama, rhs in spesifikasi.items():
            # saham tanpa transaksi di hari-0 punya return basi (0%), jadi dikeluarkan dari regresi
            m = smf.ols(f"{y} ~ {rhs}", data=s[s["vol_0"].fillna(0) > 0]).fit(cov_type="HC3")
            for v in ["msci", "bank", "free_float", "beta_jci"] + (["ppk"] if ada_ppk else []):
                out.append({"event": ev, "dependen": y, "model": nama, "variabel": v,
                            "koef": m.params[v], "se": m.bse[v], "p": m.pvalues[v],
                            "n": int(m.nobs), "r2": m.rsquared})
    return pd.DataFrame(out)


def kelompok(s):
    g = np.where(s["msci"] == 1, np.where(s["bank"] == 1, "MSCI - bank", "MSCI - non-bank"), "Non-MSCI")
    lemah = (s["free_float"] < 15) | (s.get("ppk", 0) == 1)
    return pd.Series(np.where((g == "Non-MSCI") & lemah, "Non-MSCI - tata kelola lemah*", g), index=s.index)


def kerugian(s, ev):
    out = []
    for y in ["car_0", "car_0_1"]:
        if s[y].isna().all():
            continue
        rugi = s["mcap_rp"] * s[y] / 100 / 1e12
        tabel = rugi.groupby(kelompok(s)).agg(["sum", "size"])
        tabel["porsi_rugi_%"] = tabel["sum"] / rugi.sum() * 100
        tabel["porsi_kapitalisasi_%"] = s["mcap_rp"].groupby(kelompok(s)).sum() / s["mcap_rp"].sum() * 100
        tabel = tabel.rename(columns={"sum": "rugi_rp_triliun", "size": "jumlah_saham"}).reset_index(names="kelompok")
        tabel.insert(0, "jendela", y)
        tabel.insert(0, "event", ev)
        out.append(tabel)
    return pd.concat(out)


def jalur_car(ev, s, r, t0_tgl):
    kal = r.index
    t0 = kal.get_loc(t0_tgl)
    hari = range(-5, min(61, len(kal) - t0))
    rr = r.iloc[t0 - 5:t0 + len(hari) - 5][s.index].fillna(0).cumsum() * 100
    rr.index = list(hari)
    rr = rr - rr.loc[-1]  # basis: penutupan hari -1 = 0
    w = s["mcap_rp"]
    out = {}
    for nama, idx in kelompok(s).groupby(kelompok(s)).groups.items():
        out[nama] = rr[idx].mul(w[idx], axis=1).sum(axis=1) / w[idx].sum()
    df = pd.DataFrame(out)
    df.index.name = "hari_relatif"
    df.insert(0, "event", ev)
    return df


def tercemar(ev, kal):
    """Event lain yang hari-0-nya jatuh di dalam jendela CAR event ini."""
    pos = lambda tgl: int(np.searchsorted(kal, pd.Timestamp(tgl)))
    t0 = pos(k.EVENTS[ev]["hari0"])
    out = []
    for nama, (a, b) in k.JENDELA_CAR.items():
        lain = [f"{e} ({c['lembaga']}, hari {pos(c['hari0']) - t0:+d})" for e, c in k.EVENTS.items()
                if e != ev and t0 + a <= pos(c["hari0"]) <= t0 + b]
        if lain:
            out.append(f"- {ev} `{nama}` memuat: " + ", ".join(lain))
    return out


def format_md(df):
    sel = lambda v: f"{v:.3f}" if isinstance(v, float) else str(v)
    baris = ["| " + " | ".join(df.columns) + " |", "|" + "---|" * len(df.columns)]
    baris += ["| " + " | ".join(sel(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(baris)


def main():
    harga, bench, static, msci, ppk = muat()
    kal = bench.index
    rb = return_harian(bench)
    saham = sorted(harga["ticker"].unique())
    tri, px, vol = (lebar(harga, c, kal).reindex(columns=saham) for c in ["tri", "px_last", "px_volume"])
    tanpa_tri = tri.columns[tri.isna().all()]
    tri[tanpa_tri] = px[tanpa_tri]  # cadangan: pakai harga jika TRI tidak tersedia
    r = return_harian(tri)

    k.HASIL.mkdir(parents=True, exist_ok=True)
    reg, rugi, jalur, info = [], [], [], []
    for ev, cfg in k.EVENTS_MSCI.items():
        if pd.Timestamp(cfg["hari0"]) > kal[-1]:
            info.append(f"- {ev}: dilewati, data berakhir {kal[-1]:%Y-%m-%d}.")
            continue
        s, t0_tgl = bangun_sampel(ev, cfg, r, px, vol, rb, static, msci, ppk)
        s.to_csv(k.HASIL / f"sampel_{ev}.csv")
        reg.append(regresi(s, ev, ppk is not None))
        rugi.append(kerugian(s, ev))
        jalur.append(jalur_car(ev, s, r, t0_tgl))
        info.append(f"- {ev} ({cfg['label']}): hari-0 {t0_tgl:%Y-%m-%d}, {len(s)} saham, "
                    f"{s['msci'].sum()} anggota MSCI, {s['bank'].sum()} bank, "
                    f"kapitalisasi pra-event Rp{s['mcap_rp'].sum() / 1e12:,.0f} T "
                    f"(cek: harus mendekati kapitalisasi BEI), "
                    f"return hari-0 median {s['car_0'].median():.2f}%. "
                    f"Jendela yang melewati {kal[-1]:%Y-%m-%d} belum tersedia.")

    reg, rugi, jalur = pd.concat(reg), pd.concat(rugi), pd.concat(jalur)
    reg.to_csv(k.HASIL / "regresi.csv", index=False)
    rugi.to_csv(k.HASIL / "kerugian_kelompok.csv", index=False)
    jalur.to_csv(k.HASIL / "jalur_car.csv")

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        evs = jalur["event"].unique()
        fig, axes = plt.subplots(1, len(evs), figsize=(6 * len(evs), 4), squeeze=False)
        for ax, ev in zip(axes[0], evs):
            jalur[jalur["event"] == ev].drop(columns="event").plot(ax=ax)
            ax.axvline(0, color="grey", lw=0.8)
            ax.axhline(0, color="grey", lw=0.8)
            ax.set_title(f"{ev}: CAR tertimbang kapitalisasi (%)")
            ax.set_xlabel("Hari bursa relatif terhadap hari-0")
        fig.tight_layout()
        fig.savefig(k.HASIL / "jalur_car.png", dpi=150)
    except ImportError:
        pass

    utama = reg[reg["variabel"] == "msci"].drop(columns="variabel")
    cemar = [baris for ev in reg["event"].unique() for baris in tercemar(ev, kal)]
    md = ["# Ringkasan RQ C: siapa yang membayar?", "", "## Sampel", *info, "",
          "## Jendela yang tercemar event lain",
          "Koefisien pada jendela ini mencampur efek beberapa lembaga; tafsirkan dengan hati-hati.", "",
          *(cemar or ["- Tidak ada."]), "",
          "## Kerugian kapitalisasi per kelompok", "_*free float < 15% atau Papan Pemantauan Khusus._", "",
          format_md(rugi), "",
          "## Koefisien anggota MSCI (poin persen, SE HC3)",
          "H1 memprediksi negatif di jendela awal; H3 memprediksi positif di car_2_20 / car_2_60.", "",
          format_md(utama), "",
          "Koefisien lengkap (bank, free float, beta, PPK): `regresi.csv`. Jalur CAR: `jalur_car.png`."]
    (k.HASIL / "ringkasan.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
