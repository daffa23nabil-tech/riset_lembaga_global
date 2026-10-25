"""Uji placebo hari buruk (metode 3) dan uji permutasi reaksi event (metode 4).

Placebo: regresi lintas saham yang sama dengan 02 (model M1, CAR hari-0) dijalankan di hari-hari
non-event yang IHSG-nya turun paling dalam. Koefisien MSCI dan bank di hari event lalu dibandingkan
dengan distribusi koefisien di hari-hari buruk biasa itu.
  p (satu sisi, efek negatif) = (jumlah placebo <= event + 1) / (N + 1)

Permutasi: return [0,+1] IHSG, indeks bank (tertimbang kapitalisasi), dan yield SBN di tiap event
dibandingkan dengan semua jendela dua hari non-event.
  p (dua sisi) = (jumlah |placebo| >= |event| + 1) / (N + 1)

Input : data/olah/ (hasil 01 dan msci.csv), keanggotaan MSCI placebo memakai daftar event terdekat.
Output: hasil/placebo.csv, hasil/permutasi.csv, hasil/placebo.md, hasil/placebo.png
"""
import importlib.util

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

import konfigurasi as k

spec = importlib.util.spec_from_file_location("es", k.ROOT / "analisis" / "02_event_study.py")
es = importlib.util.module_from_spec(spec)
spec.loader.exec_module(es)

N_PLACEBO = 150         # jumlah hari buruk non-event (dibatasi oleh panjang data)
JARAK_EVENT = 5          # hari bursa di sekitar event yang tidak boleh jadi placebo
RUMUS = "car_0 ~ msci + log_mcap + bank + beta_jci + log_amihud + free_float + ret_pre"


def siapkan():
    harga, bench, static, msci, ppk = es.muat()
    kal = bench.index
    rb = es.return_harian(bench)
    saham = sorted(harga["ticker"].unique())
    tri, px, vol = (es.lebar(harga, c, kal).reindex(columns=saham) for c in ["tri", "px_last", "px_volume"])
    tanpa_tri = tri.columns[tri.isna().all()]
    tri[tanpa_tri] = px[tanpa_tri]
    r = es.return_harian(tri)
    return r, px, vol, rb, static, msci, kal


def koef(s):
    m = smf.ols(RUMUS, data=s).fit(cov_type="HC3")
    return m.params.get("msci", np.nan), m.params.get("bank", np.nan), int(m.nobs)


def hari_placebo(rb, r, kal):
    """Hari non-event dengan return IHSG terendah, yang punya cukup sejarah saham untuk estimasi beta."""
    pos_event = [int(np.searchsorted(kal, pd.Timestamp(c["hari0"]))) for c in k.EVENTS.values()]
    terlarang = {p + d for p in pos_event for d in range(-JARAK_EVENT, JARAK_EVENT + 1)}
    ada = r.notna().sum(axis=1)  # jumlah saham yang punya return di hari itu
    mulai = int(np.argmax(ada.to_numpy() > 300)) + abs(k.JENDELA_ESTIMASI[0]) // 2  # perlu >=100 hari sejarah
    calon = [(i, rb["JCI"].iloc[i]) for i in range(max(mulai, abs(k.JENDELA_ESTIMASI[0])), len(kal))
             if i not in terlarang and pd.notna(rb["JCI"].iloc[i])]
    calon.sort(key=lambda x: x[1])
    return calon[:N_PLACEBO]


def placebo(r, px, vol, rb, static, msci, kal):
    hasil = []
    for ev, cfg in k.EVENTS_MSCI.items():
        s, _ = es.bangun_sampel(ev, cfg, r, px, vol, rb, static, msci, None)
        b_m, b_b, n = koef(s)
        hasil.append({"jenis": "event", "id": ev, "tanggal": cfg["hari0"], "ihsg_pct": rb["JCI"].loc[pd.Timestamp(cfg["hari0"])] * 100,
                      "beta_msci": b_m, "beta_bank": b_b, "n": n})
    hist_path = k.DATA_OLAH / "msci_proksi_hist.csv"
    hist = pd.read_csv(hist_path) if hist_path.exists() else None
    for i, ret in hari_placebo(rb, r, kal):
        tgl = kal[i]
        if hist is not None and (pd.to_datetime(hist["snapshot"]) <= tgl).any():
            # keanggotaan MSCI = snapshot review terakhir sebelum hari placebo
            snap = hist.loc[pd.to_datetime(hist["snapshot"]) <= tgl, "snapshot"].max()
            m = pd.DataFrame({"ticker": hist.loc[hist["snapshot"] == snap, "ticker"], "bobot": 1.0, "event": "PL"})
        else:
            ev_ref = "E1" if tgl < pd.Timestamp("2026-07-01") else "E2"
            m = msci[msci["event"] == ev_ref].assign(event="PL")
        try:
            s, _ = es.bangun_sampel("PL", {"hari0": tgl.strftime("%Y-%m-%d")}, r, px, vol, rb, static, m, None)
            if len(s) < 200:
                continue
            b_m, b_b, n = koef(s)
        except Exception as e:  # noqa: BLE001
            print(f"  lewati {tgl:%Y-%m-%d}: {e}")
            continue
        hasil.append({"jenis": "placebo", "id": "PL", "tanggal": f"{tgl:%Y-%m-%d}", "ihsg_pct": ret * 100,
                      "beta_msci": b_m, "beta_bank": b_b, "n": n})
    return pd.DataFrame(hasil)


def permutasi(r, px, rb, static, kal):
    bank = [t for t in static.index[static["GICS_INDUSTRY_NAME"] == "Banks"] if t in r.columns]
    # indeks bank harian tertimbang kapitalisasi hari sebelumnya (harga penutupan x jumlah saham)
    mcap = px[bank].ffill().shift(1).mul(static["EQY_SH_OUT"].reindex(bank), axis=1)
    mcap = mcap.where(r[bank].notna())
    rbank = (r[bank] * mcap).sum(axis=1) / mcap.sum(axis=1)
    seri = {"IHSG %": rb["JCI"] * 100, "Bank %": rbank * 100}
    if "SBN10Y" in rb:
        y0 = pd.read_csv(k.DATA_OLAH / "bench.csv", parse_dates=["date"]).set_index("date")["SBN10Y"]
        y = y0.reindex(kal).ffill().where(kal <= y0.last_valid_index())
        seri["SBN bp"] = y.diff() * 100
    dua = {n: s.rolling(2).sum() for n, s in seri.items()}  # jendela [0,+1]: nilai di hari +1
    pos = {e: int(np.searchsorted(kal, pd.Timestamp(c["hari0"]))) for e, c in k.EVENTS.items()}
    terlarang = {p + d for p in pos.values() for d in range(-JARAK_EVENT, JARAK_EVENT + 1)}
    baris = []
    for e, p in pos.items():
        if p + 1 >= len(kal):
            continue
        d = {"event": e, "lembaga": k.EVENTS[e]["lembaga"], "plasebo": k.EVENTS[e].get("plasebo", False)}
        for n, s in dua.items():
            nilai = s.iloc[p + 1]
            pembanding = s.iloc[[i for i in range(len(kal)) if i not in terlarang and i >= len(kal) - 1500]].dropna()
            d[n] = nilai
            d[f"p {n}"] = ((pembanding.abs() >= abs(nilai)).sum() + 1) / (len(pembanding) + 1) if pd.notna(nilai) else np.nan
        baris.append(d)
    return pd.DataFrame(baris)


def grafik(pl, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    TINTA, TINTA_2, PERMUKAAN, C1 = "#0b0b0b", "#52514e", "#fcfcfb", "#2a78d6"
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
    fig.patch.set_facecolor(PERMUKAAN)
    for ax, kol, judul in zip(axes, ["beta_msci", "beta_bank"], ["Koefisien anggota MSCI", "Koefisien bank"]):
        ax.set_facecolor(PERMUKAAN)
        x = pl.loc[pl["jenis"] == "placebo", kol].dropna()
        ax.hist(x, bins=15, color="#b9b8b2", edgecolor=PERMUKAAN, linewidth=1.5)
        for _, e in pl[pl["jenis"] == "event"].iterrows():
            ax.axvline(e[kol], color=C1, lw=2)
            ax.text(e[kol], ax.get_ylim()[1] * 0.92, f" {e['id']}", color=TINTA, fontsize=9, fontweight="bold")
        ax.axvline(0, color=TINTA_2, lw=0.8)
        ax.set_title(judul, loc="left", fontsize=10, fontweight="bold", color=TINTA)
        ax.set_xlabel("poin persen (CAR hari-0)", color=TINTA_2, fontsize=9)
        for s in ["top", "right"]:
            ax.spines[s].set_visible(False)
    fig.suptitle(f"Koefisien di hari event (garis biru) vs {int((pl['jenis'] == 'placebo').sum())} hari buruk biasa (abu-abu)",
                 x=0.01, ha="left", fontsize=11, fontweight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=180, facecolor=PERMUKAAN)


def main():
    r, px, vol, rb, static, msci, kal = siapkan()
    pl = placebo(r, px, vol, rb, static, msci, kal)
    pm = permutasi(r, px, rb, static, kal)
    k.HASIL.mkdir(parents=True, exist_ok=True)
    pl.to_csv(k.HASIL / "placebo.csv", index=False)
    pm.to_csv(k.HASIL / "permutasi.csv", index=False)
    grafik(pl, k.HASIL / "placebo.png")

    plc = pl[pl["jenis"] == "placebo"]
    md = ["# Uji placebo hari buruk dan uji permutasi", "",
          f"Placebo: {len(plc)} hari non-event dengan IHSG terburuk ({plc['tanggal'].min()} s.d. {plc['tanggal'].max()}; "
          f"IHSG antara {plc['ihsg_pct'].min():.1f}% dan {plc['ihsg_pct'].max():.1f}%). Model M1, CAR hari-0.", "",
          "| Event | IHSG hari-0 % | Koef MSCI | p (MSCI lebih negatif dari placebo) | Koef bank | p (bank lebih negatif) | p (bank, dua sisi) |",
          "|---|---|---|---|---|---|---|"]
    for _, e in pl[pl["jenis"] == "event"].iterrows():
        pm_ = ((plc["beta_msci"] <= e["beta_msci"]).sum() + 1) / (len(plc) + 1)
        pb_ = ((plc["beta_bank"] <= e["beta_bank"]).sum() + 1) / (len(plc) + 1)
        pb2 = ((plc["beta_bank"].abs() >= abs(e["beta_bank"])).sum() + 1) / (len(plc) + 1)
        md.append(f"| {e['id']} {e['tanggal']} | {e['ihsg_pct']:.2f} | {e['beta_msci']:+.2f} | {pm_:.3f} | {e['beta_bank']:+.2f} | {pb_:.3f} | {pb2:.3f} |")
    md += ["", f"Rata-rata koefisien di hari placebo: MSCI {plc['beta_msci'].mean():+.2f}, bank {plc['beta_bank'].mean():+.2f}.", "",
           "## Uji permutasi reaksi [0,+1]", "p dua sisi terhadap semua jendela dua hari non-event (±6 tahun terakhir).", "",
           "| " + " | ".join(pm.columns) + " |", "|" + "---|" * len(pm.columns)]
    for row in pm.itertuples(index=False):
        md.append("| " + " | ".join(f"{v:.3f}" if isinstance(v, float) else str(v) for v in row) + " |")
    (k.HASIL / "placebo.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
