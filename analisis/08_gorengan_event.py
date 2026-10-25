"""Apakah keputusan lembaga global menghukum saham "gorengan"? (RQ2, tipe saham)

Riwayat pengawasan BEI 250 hari bursa sebelum event (01g): riwayat_suspensi = pernah disuspensi Divisi Pengawasan
Transaksi (cooling down), riwayat_uma = pernah UMA atau suspensi itu. PPK = status per hari sebelum event (01f).
Per event: CAR ~ riwayat + ppk + kontrol (ukuran, beta, likuiditas, free float, return pra-event, bank, MSCI), HC3.
Bertumpuk (6 event non-placebo): kemiringan riwayat_suspensi dan ppk berbeda per jenis keputusan, FE event,
cluster saham; Wald indeks saham = rating. Event placebo diuji terpisah.

Placebo: koefisien yang sama di 60 hari crash biasa 2025-2026 (bukan event), supaya "gorengan jatuh lebih dalam di
hari buruk mana pun" tidak dianggap efek lembaga global.

Output: hasil/lanjutan/{gorengan_event.csv, gorengan_uji.csv, gorengan_kerugian.csv, gorengan_placebo.csv,
        gorengan_placebo_hari.csv, ringkasan_gorengan.md}
"""
import importlib.util
import warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

import konfigurasi as k

warnings.filterwarnings("ignore")


def _modul(nama, file):
    spec = importlib.util.spec_from_file_location(nama, k.ROOT / "analisis" / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


es = _modul("es", "02_event_study.py")
pl = _modul("pl", "04_placebo_permutasi.py")
OUT = k.HASIL / "lanjutan"
GRUP = {"Indeks saham": "indeks_saham", "Indeks obligasi": "indeks_obligasi", "Rating": "rating"}
KONTROL = "log_mcap + beta_jci + log_amihud + free_float + ret_pre + bank + msci"
Y = ["car_0", "car_0_1", "car_0_5"]


def sampel(data):
    r, px, vol, rb, static, msci, kal = data
    riwayat = pd.read_csv(k.DATA_OLAH / "riwayat_pengawasan_event.csv")
    ppk = pd.read_csv(k.DATA_OLAH / "ppk_event.csv")
    out = []
    for ev, cfg in k.EVENTS.items():
        s, _ = es.bangun_sampel(ev, cfg, r, px, vol, rb, static, msci, None)
        s = s[s["vol_0"].fillna(0) > 0]
        rw = riwayat[riwayat["event"] == ev].set_index("ticker")
        s["riwayat_uma"] = rw["riwayat_uma"].reindex(s.index).fillna(0)
        s["riwayat_suspensi"] = rw["riwayat_suspensi"].reindex(s.index).fillna(0)
        s["ppk"] = s.index.isin(set(ppk.loc[(ppk["event"] == ev) & (ppk["ppk"] == 1), "ticker"])).astype(int)
        out.append(s.reset_index().assign(event=ev, grup=GRUP[cfg["jenis"]], plasebo=cfg.get("plasebo", False)))
    return pd.concat(out, ignore_index=True)


def per_event(d):
    baris = []
    for ev in k.EVENTS:
        s = d[d["event"] == ev]
        for y in Y:
            if s[y].isna().all():
                continue
            for x in ["riwayat_suspensi", "riwayat_uma"]:
                m = smf.ols(f"{y} ~ {x} + ppk + {KONTROL}", data=s).fit(cov_type="HC3")
                for v in [x, "ppk"]:
                    if x == "riwayat_uma" and v == "ppk":
                        continue
                    baris.append({"event": ev, "dependen": y, "variabel": v, "koef": m.params[v], "se": m.bse[v],
                                  "p": m.pvalues[v], "n_kelompok": int(s[v].sum()), "n": int(m.nobs)})
    return pd.DataFrame(baris)


def uji_tumpuk(d, y="car_0_1"):
    kolom = [y, "riwayat_suspensi", "ppk"] + [c.strip() for c in KONTROL.split("+")]
    d = d.dropna(subset=kolom)  # baris yang dibuang rumus harus ikut dibuang dari grup cluster
    t = d[~d["plasebo"]]
    m = smf.ols(f"{y} ~ C(event) + riwayat_suspensi:C(grup) + ppk:C(grup) + {KONTROL}", data=t).fit(
        cov_type="cluster", cov_kwds={"groups": t["ticker"]})
    baris = []
    for v in ["riwayat_suspensi", "ppk"]:
        for g in t["grup"].unique():
            n = f"{v}:C(grup)[{g}]"
            baris.append({"uji": f"{v} di {g}", "nilai": m.params[n], "p": m.pvalues[n]})
        for a, b in [("indeks_saham", "rating"), ("indeks_saham", "indeks_obligasi")]:
            w = m.wald_test(f"{v}:C(grup)[{a}] = {v}:C(grup)[{b}]", scalar=True)
            baris.append({"uji": f"{v}: {a} = {b} (chi2)", "nilai": float(w.statistic), "p": float(w.pvalue)})
    p = d[d["plasebo"]]
    mp = smf.ols(f"{y} ~ C(event) + riwayat_suspensi + ppk + {KONTROL}", data=p).fit(cov_type="cluster", cov_kwds={"groups": p["ticker"]})
    for v in ["riwayat_suspensi", "ppk"]:
        baris.append({"uji": f"{v} di placebo (S&P, FTSE Okt)", "nilai": mp.params[v], "p": mp.pvalues[v]})
    return pd.DataFrame(baris).assign(dependen=y)


N_HARI_BURUK = 60


def hari_buruk(rb, kal):
    """Hari non-event 2025-2026 dengan IHSG terburuk (riwayat UMA lengkap: data UMA sejak Okt 2023 + 250 hari)."""
    pos_event = [int(np.searchsorted(kal, pd.Timestamp(c["hari0"]))) for c in k.EVENTS.values()]
    terlarang = {p + d for p in pos_event for d in range(-5, 6)}
    calon = [(i, rb["JCI"].iloc[i]) for i in range(len(kal) - 5)
             if kal[i] >= pd.Timestamp("2025-01-02") and i not in terlarang and pd.notna(rb["JCI"].iloc[i])]
    return sorted(calon, key=lambda x: x[1])[:N_HARI_BURUK]


def placebo(d, data):
    """Koefisien riwayat_suspensi dan ppk di hari crash biasa, sebagai pembanding koefisien di hari event."""
    r, px, vol, rb, static, msci, kal = data
    lab = pd.read_csv(k.DATA_OLAH / "label_pengawasan.csv", parse_dates=["date"])
    notasi = pd.read_csv(k.DATA_OLAH / "notasi_harian.csv.gz", parse_dates=["date"], usecols=["date", "ticker", "ppk"])
    hist = pd.read_csv(k.DATA_OLAH / "msci_proksi_hist.csv")
    koef = []
    for i, ret in hari_buruk(rb, kal):
        tgl = kal[i]
        snap = hist.loc[pd.to_datetime(hist["snapshot"]) <= tgl, "snapshot"].max()
        m = pd.DataFrame({"ticker": hist.loc[hist["snapshot"] == snap, "ticker"], "bobot": 1.0, "event": "PL"})
        s, _ = es.bangun_sampel("PL", {"hari0": f"{tgl:%Y-%m-%d}"}, r, px, vol, rb, static, m, None)
        s = s[s["vol_0"].fillna(0) > 0]
        w = lab[(lab["date"] >= kal[i - 250]) & (lab["date"] < tgl)].groupby("ticker")["suspensi_was"].sum()
        s["riwayat_suspensi"] = (w.reindex(s.index).fillna(0) > 0).astype(int)
        sebelum = notasi[notasi["date"] < tgl]
        pk = sebelum[sebelum["date"] == sebelum["date"].max()].set_index("ticker")["ppk"]
        s["ppk"] = pk.reindex(s.index).fillna(0)
        for y in Y:
            if s[y].isna().all():
                continue
            fit = smf.ols(f"{y} ~ riwayat_suspensi + ppk + {KONTROL}", data=s).fit()
            koef.append({"tanggal": tgl, "ihsg_pct": ret * 100, "dependen": y,
                         "riwayat_suspensi": fit.params["riwayat_suspensi"], "ppk": fit.params["ppk"]})
    koef = pd.DataFrame(koef)
    baris = []
    for _, e in d.drop_duplicates("event")[["event"]].iterrows():
        for y in Y:
            pe = per_event(d[d["event"] == e["event"]])
            for v in ["riwayat_suspensi", "ppk"]:
                x = pe[(pe["dependen"] == y) & (pe["variabel"] == v)]
                if x.empty:
                    continue
                pl_ = koef.loc[koef["dependen"] == y, v]
                b = float(x["koef"].iloc[0])
                baris.append({"event": e["event"], "dependen": y, "variabel": v, "koef_event": b,
                              "rata_placebo": pl_.mean(), "p_lebih_negatif": ((pl_ <= b).sum() + 1) / (len(pl_) + 1),
                              "n_placebo": len(pl_)})
    return pd.DataFrame(baris), koef


def kerugian(d):
    baris = []
    for ev in k.EVENTS_MSCI:
        s = d[d["event"] == ev].dropna(subset=["car_0_1"])
        rugi = s["mcap_rp"] * s["car_0_1"] / 100 / 1e12
        for nama, mask in [("Riwayat suspensi pengawasan", s["riwayat_suspensi"] == 1), ("PPK", s["ppk"] == 1),
                           ("Lainnya", (s["riwayat_suspensi"] == 0) & (s["ppk"] == 0))]:
            baris.append({"event": ev, "kelompok": nama, "n": int(mask.sum()), "rugi_rp_T": rugi[mask].sum(),
                          "porsi_rugi_%": rugi[mask].sum() / rugi.sum() * 100,
                          "porsi_kapitalisasi_%": s.loc[mask, "mcap_rp"].sum() / s["mcap_rp"].sum() * 100,
                          "car_0_1_median": s.loc[mask, "car_0_1"].median()})
    return pd.DataFrame(baris)


def md(df, fmt="{:.3f}"):
    kol = df.columns.tolist()
    baris = ["| " + " | ".join(kol) + " |", "|" + "---|" * len(kol)]
    for _, r in df.iterrows():
        baris.append("| " + " | ".join(fmt.format(v) if isinstance(v, float) else str(v) for v in r) + " |")
    return "\n".join(baris)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = pl.siapkan()
    d = sampel(data)
    pe = per_event(d)
    uji = pd.concat([uji_tumpuk(d, "car_0_1"), uji_tumpuk(d, "car_0")], ignore_index=True)
    rg = kerugian(d)
    pb, koef_pl = placebo(d, data)
    pb.to_csv(OUT / "gorengan_placebo.csv", index=False)
    koef_pl.to_csv(OUT / "gorengan_placebo_hari.csv", index=False)
    pe.to_csv(OUT / "gorengan_event.csv", index=False)
    uji.to_csv(OUT / "gorengan_uji.csv", index=False)
    rg.to_csv(OUT / "gorengan_kerugian.csv", index=False)
    tabel = pe[pe["variabel"] != "riwayat_uma"].pivot_table(index=["event"], columns=["variabel", "dependen"], values="koef").reindex(list(k.EVENTS))
    ptab = pe[pe["variabel"] != "riwayat_uma"].pivot_table(index=["event"], columns=["variabel", "dependen"], values="p").reindex(list(k.EVENTS))
    bintang = ptab.map(lambda q: "**" if q < 0.05 else ("*" if q < 0.1 else ""))
    tampil = tabel.round(2).astype(str) + bintang
    tampil.columns = [f"{v} {y}" for v, y in tampil.columns]
    print(tampil.to_string())
    print(uji.round(3).to_string(index=False))
    print(rg.round(2).to_string(index=False))
    tpb = pb.pivot_table(index="event", columns=["variabel", "dependen"], values="p_lebih_negatif").reindex(list(k.EVENTS))
    tpb.columns = [f"{v} {y}" for v, y in tpb.columns]
    print(tpb.round(3).to_string())
    teks = ["# Apakah lembaga global menghukum saham gorengan?", "",
            "Riwayat pengawasan = UMA/suspensi BEI dalam 250 hari bursa sebelum event (data UMA dan suspensi BEI sejak Okt 2023). "
            "riwayat_suspensi = pernah di-cooling down Divisi Pengawasan Transaksi. PPK = status di hari bursa sebelum event. "
            f"Kontrol: {KONTROL}. Saham tanpa transaksi di hari-0 dikeluarkan. SE HC3.", "",
            "## Koefisien per event (pp; ** p<0,05, * p<0,1)", "", md(tampil.reset_index()), "",
            "## Uji bertumpuk (FE event, cluster saham)", "", md(uji.round(3)), "",
            f"## Placebo: dibanding {N_HARI_BURUK} hari crash biasa 2025-2026 (p = koefisien placebo <= koefisien event)", "",
            "Pertanyaannya: apakah saham bertanda pengawasan jatuh LEBIH dalam di hari event daripada di hari crash biasa?", "",
            md(tpb.round(3).reset_index()), "",
            f"Rata-rata koefisien di hari crash biasa: riwayat_suspensi car_0 "
            f"{koef_pl.loc[koef_pl['dependen'] == 'car_0', 'riwayat_suspensi'].mean():.2f}, ppk car_0 "
            f"{koef_pl.loc[koef_pl['dependen'] == 'car_0', 'ppk'].mean():.2f}.", "",
            "## Siapa menanggung kerugian kapitalisasi [0,+1] di event MSCI", "", md(rg.round(3)), "",
            "Catatan: label pengawasan dipakai hanya untuk analisis agregat; tidak ada skor per saham yang dipublikasikan."]
    (OUT / "ringkasan_gorengan.md").write_text("\n".join(teks), encoding="utf-8")


if __name__ == "__main__":
    main()
