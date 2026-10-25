"""Uji ketahanan dua temuan yang rapuh/baru: (A) fingerprint porsi asing bank, (B) saham gorengan di E1.

A. Fingerprint (bank x 6 event, 06): apakah "bank yang banyak diperdagangkan asing jatuh lebih dalam di event indeks,
   bukan di event rating" bertahan bila
   - porsi asing diukur dengan jendela 2/20/60/120/250 hari sebelum E1, atau per event (60 hari sebelum tiap event);
   - porsi berbasis volume atau nilai transaksi;
   - model penuh (7 karakteristik) atau porsi asing saja;
   - satu event dibuang bergantian (leave-one-event-out), atau 4 bank terbesar dibuang;
   - outcome CAR hari-0 atau [0,+1].
B. Gorengan E1 (08): apakah "saham yang pernah di-cooling down BEI jatuh lebih dalam di E1 [0,+5]" bertahan bila
   - riwayat 120/250/500 hari, UMA saja, suspensi saja, atau jumlah kejadian (intensitas);
   - FE desil ukuran, tanpa saham PPK, tanpa saham harga < Rp100, winsor CAR 1%, regresi median, CAR abnormal;
   - dibandingkan dengan 60 hari crash biasa untuk setiap varian (p placebo).

Output: hasil/lanjutan/{ketahanan_fingerprint.csv, ketahanan_gorengan.csv, ringkasan_ketahanan.md}
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
het = _modul("het", "06_heterogenitas.py")
gor = _modul("gor", "08_gorengan_event.py")
OUT = k.HASIL / "lanjutan"
FUND = ["surat_berharga_aset", "repo_aset", "pendanaan_wholesale", "casa", "modal_aset", "log_aset"]
UTAMA = [ev for ev, c in k.EVENTS.items() if not c.get("plasebo")]


# ================================================================ A. fingerprint porsi asing
def porsi_asing(a, tanggal, n, basis):
    hari = sorted(a.loc[a["date"] < pd.Timestamp(tanggal), "date"].unique())[-n:]
    x = a[a["date"].isin(hari)]
    if basis == "volume":
        porsi = (x["foreign_buy"] + x["foreign_sell"]) / (2 * x["volume"].where(x["volume"] > 0))
    else:
        porsi = (x["foreign_buy"] + x["foreign_sell"]) * x["close"] / (2 * x["value"].where(x["value"] > 0))
    return porsi.groupby(x["ticker"]).mean() * 100


def panel_dasar(data):
    baris = []
    for ev, cfg in k.EVENTS.items():
        s = het.sampel_event(ev, cfg, data)
        s = s[s["bank"] == 1].join(het.fundamental_untuk(cfg["hari0"])[FUND + ["aset_rp"]], how="inner")
        baris.append(s.reset_index()[["ticker", "car_0", "car_0_1", "aset_rp"] + FUND].assign(
            event=ev, grup=het.GRUP[cfg["jenis"]], plasebo=cfg.get("plasebo", False)))
    return pd.concat(baris, ignore_index=True)


def standar(p, kolom):
    p = p.dropna(subset=kolom + ["car_0_1"]).copy()
    for x in kolom:
        w = p[x].clip(p[x].quantile(0.01), p[x].quantile(0.99))
        p[x] = (w - w.mean()) / w.std()
    return p


def fp_satu(p, xs, y):
    t = p[~p["plasebo"]]
    suku = " + ".join(f"{x}:C(grup)" for x in xs)
    m = smf.ols(f"{y} ~ C(event) + {suku}", data=t).fit(cov_type="cluster", cov_kwds={"groups": t["ticker"]})
    nama = lambda g: f"asing:C(grup)[{g}]"
    hasil = {"n": int(m.nobs)}
    for g in ["indeks_saham", "indeks_obligasi", "rating"]:
        if nama(g) in m.params:
            hasil[f"asing_{g}"] = m.params[nama(g)]
            hasil[f"p_{g}"] = m.pvalues[nama(g)]
    if nama("indeks_saham") in m.params and nama("rating") in m.params:
        hasil["p_asing_saham=rating"] = float(m.wald_test(f"{nama('indeks_saham')} = {nama('rating')}", scalar=True).pvalue)
        h = ", ".join(f"{x}:C(grup)[indeks_saham] = {x}:C(grup)[rating]" for x in xs)
        hasil["p_wald_saham=rating"] = float(m.wald_test(h, scalar=True).pvalue)
    plas = p[p["plasebo"]]
    mp = smf.ols(f"{y} ~ C(event) + asing", data=plas).fit(cov_type="cluster", cov_kwds={"groups": plas["ticker"]})
    hasil["asing_placebo"], hasil["p_placebo"] = mp.params["asing"], mp.pvalues["asing"]
    return hasil


def ketahanan_fingerprint(data):
    a = pd.read_csv(k.DATA_OLAH / "asing_event.csv", parse_dates=["date"])
    dasar = panel_dasar(data)
    e1 = k.EVENTS["E1"]["hari0"]
    besar4 = set(dasar[dasar["event"] == "E1"].nlargest(4, "aset_rp")["ticker"])
    varian = []
    for n in [2, 20, 60, 120, 250]:
        for basis in ["volume", "nilai"]:
            varian.append((f"pra-E1 {n} hari, {basis}", "tetap", n, basis))
    varian += [("per event 60 hari, volume", "per_event", 60, "volume"), ("per event 20 hari, volume", "per_event", 20, "volume")]
    baris = []
    for nama, cara, n, basis in varian:
        p = dasar.copy()
        if cara == "tetap":
            p["asing"] = p["ticker"].map(porsi_asing(a, e1, n, basis))
        else:
            p["asing"] = np.nan
            for ev, c in k.EVENTS.items():
                s = porsi_asing(a, c["hari0"], n, basis)
                p.loc[p["event"] == ev, "asing"] = p.loc[p["event"] == ev, "ticker"].map(s)
        for model, xs in [("penuh", FUND + ["asing"]), ("asing saja", ["asing"])]:
            ps = standar(p, xs)
            for y in ["car_0_1", "car_0"]:
                baris.append({"varian": nama, "model": model, "y": y, "sampel": "semua", **fp_satu(ps, xs, y)})
            if nama == "pra-E1 60 hari, volume":
                for buang in UTAMA:
                    baris.append({"varian": nama, "model": model, "y": "car_0_1", "sampel": f"tanpa {buang}",
                                  **fp_satu(ps[ps["event"] != buang], xs, "car_0_1")})
                baris.append({"varian": nama, "model": model, "y": "car_0_1", "sampel": "tanpa 4 bank terbesar",
                              **fp_satu(ps[~ps["ticker"].isin(besar4)], xs, "car_0_1")})
    return pd.DataFrame(baris)


# ================================================================ B. gorengan E1
def riwayat(lab, kal, tgl, n, jenis):
    i = kal.searchsorted(pd.Timestamp(tgl))
    w = lab[(lab["date"] >= kal[max(i - n, 0)]) & (lab["date"] < kal[i])]
    kol = {"suspensi": ["suspensi_was"], "uma": ["uma"], "keduanya": ["uma", "suspensi_was"]}[jenis]
    return w.groupby("ticker")[kol].sum().sum(axis=1)


def kalender_label():
    kal = pd.DatetimeIndex(sorted(pd.read_csv(k.DATA_MENTAH / "idx" / "harian_2025_2026.csv.gz", usecols=["date"],
                                              parse_dates=["date"])["date"].unique()))
    lama = k.DATA_MENTAH / "idx" / "harian_2023_2024_lengkap.csv.gz"
    if lama.exists():
        kal = pd.DatetimeIndex(sorted(pd.read_csv(lama, usecols=["date"], parse_dates=["date"])["date"].unique())).append(kal)
    return kal


VARIAN_G = [  # nama, jendela riwayat, jenis, intensitas
    ("utama: suspensi 250 hari", 250, "suspensi", False),
    ("suspensi 120 hari", 120, "suspensi", False),
    ("suspensi 500 hari", 500, "suspensi", False),
    ("UMA saja 250 hari", 250, "uma", False),
    ("UMA atau suspensi 250 hari", 250, "keduanya", False),
    ("intensitas: log(1+jumlah) 250 hari", 250, "keduanya", True),
]
SPES_G = {  # nama: (rumus tambahan, filter, metode)
    "dasar": ("", None, "ols"),
    "FE desil ukuran": ("+ C(desil_ukuran)", None, "ols"),
    "tanpa saham PPK": ("", "ppk == 0", "ols"),
    "tanpa harga < Rp100": ("", "px_pre >= 100", "ols"),
    "winsor CAR 1%": ("", "winsor", "ols"),
    "regresi median": ("", None, "median"),
}


def koef_g(s, y, spes):
    tambah, filt, metode = SPES_G[spes]
    s = s.dropna(subset=[y, "x", "log_mcap", "beta_jci", "log_amihud", "free_float", "ret_pre"])
    if filt == "winsor":
        s = s.assign(**{y: s[y].clip(s[y].quantile(0.01), s[y].quantile(0.99))})
    elif filt:
        s = s.query(filt)
    rumus = f"{y} ~ x + ppk + {gor.KONTROL} {tambah}"
    if metode == "median":
        m = smf.quantreg(rumus, data=s).fit(q=0.5)
    else:
        m = smf.ols(rumus, data=s).fit(cov_type="HC3")
    return m.params["x"], m.pvalues["x"]


def ketahanan_gorengan(data):
    r, px, vol, rb, static, msci, kal = data
    lab = pd.read_csv(k.DATA_OLAH / "label_pengawasan.csv", parse_dates=["date"])
    notasi = pd.read_csv(k.DATA_OLAH / "notasi_harian.csv.gz", parse_dates=["date"], usecols=["date", "ticker", "ppk"])
    hist = pd.read_csv(k.DATA_OLAH / "msci_proksi_hist.csv")
    kal_lab = kalender_label()

    def siapkan(s, tgl):
        s = s[s["vol_0"].fillna(0) > 0].copy()
        sebelum = notasi[notasi["date"] < pd.Timestamp(tgl)]
        s["ppk"] = sebelum[sebelum["date"] == sebelum["date"].max()].set_index("ticker")["ppk"].reindex(s.index).fillna(0)
        return s

    s_e1, _ = es.bangun_sampel("E1", k.EVENTS["E1"], r, px, vol, rb, static, msci, None)
    s_e1 = siapkan(s_e1, k.EVENTS["E1"]["hari0"])
    placebo = []
    for i, _ in gor.hari_buruk(rb, kal):
        tgl = kal[i]
        snap = hist.loc[pd.to_datetime(hist["snapshot"]) <= tgl, "snapshot"].max()
        m = pd.DataFrame({"ticker": hist.loc[hist["snapshot"] == snap, "ticker"], "bobot": 1.0, "event": "PL"})
        s, _ = es.bangun_sampel("PL", {"hari0": f"{tgl:%Y-%m-%d}"}, r, px, vol, rb, static, m, None)
        placebo.append((tgl, siapkan(s, tgl)))

    def pasang_x(s, tgl, n, jenis, intens):
        jml = riwayat(lab, kal_lab, tgl, n, jenis).reindex(s.index).fillna(0)
        return s.assign(x=np.log1p(jml) if intens else (jml > 0).astype(int))

    baris = []
    for nama, n, jenis, intens in VARIAN_G:
        e = pasang_x(s_e1, k.EVENTS["E1"]["hari0"], n, jenis, intens)
        pls = [pasang_x(s, t, n, jenis, intens) for t, s in placebo]
        spes_list = SPES_G if nama.startswith("utama") else {"dasar": None}
        for spes in spes_list:
            for y in ["car_0", "car_0_1", "car_0_5", "abn_car_0_5"]:
                b, p = koef_g(e, y, spes)
                dist = np.array([koef_g(s, y, spes)[0] for s in pls])
                dist = dist[~np.isnan(dist)]
                baris.append({"varian": nama, "spesifikasi": spes, "y": y, "koef_E1": b, "p_hc3": p,
                              "rata_placebo": dist.mean(), "p_placebo": ((dist <= b).sum() + 1) / (len(dist) + 1),
                              "n_kelompok": int((e["x"] > 0).sum())})
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
    fp = ketahanan_fingerprint(data)
    fp.to_csv(OUT / "ketahanan_fingerprint.csv", index=False)
    kol = ["varian", "model", "y", "sampel", "asing_indeks_saham", "p_indeks_saham", "asing_rating", "p_rating",
           "asing_indeks_obligasi", "p_indeks_obligasi", "p_asing_saham=rating", "p_wald_saham=rating", "asing_placebo", "p_placebo"]
    print(fp[kol].round(3).to_string(index=False))
    g = ketahanan_gorengan(data)
    g.to_csv(OUT / "ketahanan_gorengan.csv", index=False)
    print(g.round(3).to_string(index=False))
    teks = ["# Uji ketahanan", "",
            "## A. Fingerprint porsi asing (bank x 6 event non-placebo; pp CAR per 1 SD porsi asing; SE cluster bank)", "",
            "`p_asing_saham=rating`: kemiringan porsi asing sama di indeks saham dan rating. `p_wald_saham=rating`: seluruh sidik jari sama. "
            "Placebo = event S&P dan FTSE Okt.", "", md(fp[kol].round(3)), "",
            "## B. Saham pernah di-cooling down/UMA di E1 (pp; p_placebo = porsi 60 hari crash biasa dengan koefisien <= E1)", "",
            md(g.round(3))]
    (OUT / "ringkasan_ketahanan.md").write_text("\n".join(teks), encoding="utf-8")


if __name__ == "__main__":
    main()
