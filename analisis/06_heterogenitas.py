"""Heterogenitas: causal forest (metode 8) dan uji fingerprint lintas jenis keputusan (metode 9).

8. Causal forest (econml CausalForestDML). Sampel bertumpuk: semua saham di hari event MSCI (T=1)
   vs hari buruk biasa (T=0, placebo dari 04). Y = return hari-0 dikurangi median lintas saham di hari
   itu, jadi efek = siapa yang membayar LEBIH di hari "dihakimi" dibanding hari crash biasa.
   CATE per saham diringkas per kelompok (anggota MSCI, bank, ukuran) + kepentingan variabel.

9. Fingerprint (bank saja). Panel bank x event (6 event non-placebo), Y = CAR [0,+1].
   car ~ FE event + sum_g sum_j 1[jenis = g] * X_j, X = fundamental XBRL terstandar.
   Wald: apakah sidik jari (vektor koefisien X) sama antara keputusan indeks saham, indeks obligasi,
   dan rating? Event placebo (S&P, FTSE Okt) dipakai sebagai uji palsu: sidik jarinya mestinya nol.

Input : data/olah/fundamental_bank.csv (01e), asing_event.csv (01c), hasil 02/04
Output: hasil/lanjutan/{causal_forest.csv, causal_forest_cate.csv, fingerprint.csv, fingerprint_wald.csv,
        fingerprint.png, ringkasan_heterogenitas.md}
"""
import importlib.util
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
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
N_PLACEBO_CF = 40
X_CF = ["msci", "bank", "log_mcap", "free_float", "log_amihud", "beta_mxef", "ret_pre"]
X_FP = ["surat_berharga_aset", "repo_aset", "pendanaan_wholesale", "casa", "modal_aset", "log_aset", "asing"]
GRUP = {"Indeks saham": "indeks_saham", "Indeks obligasi": "indeks_obligasi", "Rating": "rating"}


def sampel_event(ev, cfg, data, msci_ev=None):
    r, px, vol, rb, static, msci, kal = data
    s, _ = es.bangun_sampel(ev, cfg, r, px, vol, rb, static, msci if msci_ev is None else msci_ev, None)
    return s[s["vol_0"] > 0]


# ---------------------------------------------------------------- 8. causal forest
def causal_forest(data):
    from econml.dml import CausalForestDML
    from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor

    r, px, vol, rb, static, msci, kal = data
    hist = pd.read_csv(k.DATA_OLAH / "msci_proksi_hist.csv")
    tumpuk = []
    for ev, cfg in k.EVENTS_MSCI.items():
        tumpuk.append(sampel_event(ev, cfg, data).assign(T=1, hari=ev))
    for i, _ in pl.hari_placebo(rb, r, kal)[:N_PLACEBO_CF]:
        tgl = kal[i]
        snap = hist.loc[pd.to_datetime(hist["snapshot"]) <= tgl, "snapshot"].max()
        m = pd.DataFrame({"ticker": hist.loc[hist["snapshot"] == snap, "ticker"], "bobot": 1.0, "event": "PL"})
        try:
            tumpuk.append(sampel_event("PL", {"hari0": f"{tgl:%Y-%m-%d}"}, data, m).assign(T=0, hari=f"{tgl:%Y-%m-%d}"))
        except SystemExit:
            continue
    d = pd.concat(tumpuk).reset_index()
    # peringkat persentil lintas saham per hari: kebal terhadap batas ARB dan skala crash yang berbeda-beda
    d["y"] = d.groupby("hari")["car_0"].rank(pct=True) * 100
    d = d.dropna(subset=X_CF + ["y"])
    X = d[X_CF].to_numpy()
    cf = CausalForestDML(model_y=GradientBoostingRegressor(max_depth=3, n_estimators=200, random_state=0),
                         model_t=GradientBoostingClassifier(max_depth=3, n_estimators=200, random_state=0),
                         discrete_treatment=True, n_estimators=2000, min_samples_leaf=10, cv=5, random_state=0)
    cf.fit(d["y"].to_numpy(), d["T"].to_numpy(), X=X)
    d["cate"] = cf.effect(X)
    lo, hi = cf.effect_interval(X, alpha=0.05)
    d["cate_lo"], d["cate_hi"] = lo, hi
    ev = d[d["T"] == 1].copy()
    ev["ukuran"] = pd.qcut(ev["log_mcap"], 3, labels=["kecil", "menengah", "besar"])
    ate = cf.ate_inference(X=ev[X_CF].to_numpy())
    baris = [{"kelompok": "Semua saham (hari event)", "n": len(ev), "cate": ate.mean_point,
              "lo": ate.conf_int_mean()[0], "hi": ate.conf_int_mean()[1]}]
    for nama, mask in [("Anggota MSCI", ev["msci"] == 1), ("Non-MSCI", ev["msci"] == 0),
                       ("Bank", ev["bank"] == 1), ("Non-bank", ev["bank"] == 0),
                       ("Bank anggota MSCI", (ev["bank"] == 1) & (ev["msci"] == 1)),
                       ("Ukuran kecil", ev["ukuran"] == "kecil"), ("Ukuran menengah", ev["ukuran"] == "menengah"),
                       ("Ukuran besar", ev["ukuran"] == "besar")]:
        inf = cf.ate_inference(X=ev.loc[mask, X_CF].to_numpy())
        baris.append({"kelompok": nama, "n": int(mask.sum()), "cate": inf.mean_point,
                      "lo": inf.conf_int_mean()[0], "hi": inf.conf_int_mean()[1]})
    ringkas = pd.DataFrame(baris)
    penting = pd.Series(cf.feature_importances_, index=X_CF).sort_values(ascending=False)
    ev[["ticker", "hari", "msci", "bank", "log_mcap", "cate", "cate_lo", "cate_hi"]].to_csv(OUT / "causal_forest_cate.csv", index=False)
    ringkas.to_csv(OUT / "causal_forest.csv", index=False)
    return ringkas, penting, int((d["T"] == 0).groupby(d["hari"]).first().eq(1).sum()), d["hari"].nunique() - len(k.EVENTS_MSCI)


# ---------------------------------------------------------------- 9. fingerprint
def fundamental_untuk(tgl):
    f = pd.read_csv(k.DATA_OLAH / "fundamental_bank.csv")
    periode = "2025-12-31" if pd.Timestamp(tgl) < pd.Timestamp("2026-07-01") else "2026-06-30"
    f = f[f["periode"] == periode].set_index("ticker")
    f["log_aset"] = np.log(f["aset_rp"])
    return f


def porsi_asing():
    """Porsi asing dalam volume transaksi bank, 60 hari bursa sebelum E1 (karakteristik tetap per bank)."""
    a = pd.read_csv(k.DATA_OLAH / "asing_event.csv", parse_dates=["date"])
    hari = sorted(a.loc[a["date"] < pd.Timestamp(k.EVENTS["E1"]["hari0"]), "date"].unique())[-60:]
    a = a[a["date"].isin(hari)]  # 60 hari bursa terakhir sebelum E1
    a["porsi"] = (a["foreign_buy"] + a["foreign_sell"]) / (2 * a["volume"].where(a["volume"] > 0))
    return a.groupby("ticker")["porsi"].mean() * 100


def panel_bank(data):
    asing = porsi_asing()
    baris = []
    for ev, cfg in k.EVENTS.items():
        s = sampel_event(ev, cfg, data)
        s = s[s["bank"] == 1].join(fundamental_untuk(cfg["hari0"])[X_FP[:-1]], how="inner")
        s["asing"] = asing.reindex(s.index)
        s["event"], s["grup"], s["plasebo"] = ev, GRUP[cfg["jenis"]], cfg.get("plasebo", False)
        baris.append(s.reset_index()[["ticker", "event", "grup", "plasebo", "car_0", "car_0_1"] + X_FP])
    p = pd.concat(baris).dropna(subset=X_FP + ["car_0_1"])
    for x in X_FP:  # standardisasi (winsor 1%) supaya koefisien = pp per 1 SD
        w = p[x].clip(p[x].quantile(0.01), p[x].quantile(0.99))
        p[x] = (w - w.mean()) / w.std()
    return p


def fingerprint(p, y="car_0_1"):
    utama = p[~p["plasebo"]].copy()
    suku = " + ".join(f"{x}:C(grup)" for x in X_FP)
    m = smf.ols(f"{y} ~ C(event) + {suku}", data=utama).fit(cov_type="cluster", cov_kwds={"groups": utama["ticker"]})
    koef = []
    for nama, b in m.params.items():
        if ":C(grup)" in nama:
            x, g = nama.split(":C(grup)[")
            koef.append({"variabel": x, "grup": g.rstrip("]"), "koef": b, "se": m.bse[nama], "p": m.pvalues[nama]})
    koef = pd.DataFrame(koef)
    wald = []
    for a, b in [("indeks_saham", "rating"), ("indeks_saham", "indeks_obligasi"), ("indeks_obligasi", "rating")]:
        h = ", ".join(f"{x}:C(grup)[{a}] = {x}:C(grup)[{b}]" for x in X_FP)
        t = m.wald_test(h, scalar=True)
        wald.append({"uji": f"{a} = {b}", "chi2": float(t.statistic), "df": len(X_FP), "p": float(t.pvalue)})
    for g in koef["grup"].unique():
        t = m.wald_test(", ".join(f"{x}:C(grup)[{g}] = 0" for x in X_FP), scalar=True)
        wald.append({"uji": f"semua X = 0 di {g}", "chi2": float(t.statistic), "df": len(X_FP), "p": float(t.pvalue)})
    plas = p[p["plasebo"]]
    mp = smf.ols(f"{y} ~ C(event) + " + " + ".join(X_FP), data=plas).fit(cov_type="cluster", cov_kwds={"groups": plas["ticker"]})
    t = mp.wald_test(", ".join(f"{x} = 0" for x in X_FP), scalar=True)
    wald.append({"uji": "placebo (S&P, FTSE Okt): semua X = 0", "chi2": float(t.statistic), "df": len(X_FP), "p": float(t.pvalue)})
    return koef, pd.DataFrame(wald), int(m.nobs), utama["ticker"].nunique()


def grafik(koef, path):
    warna = {"indeks_saham": "#2f6db5", "indeks_obligasi": "#7b5ea7", "rating": "#c4453a"}
    fig, ax = plt.subplots(figsize=(8, 5))
    y0 = np.arange(len(X_FP))
    for i, (g, w) in enumerate(warna.items()):
        c = koef[koef["grup"] == g].set_index("variabel").reindex(X_FP)
        ax.errorbar(c["koef"], y0 + (i - 1) * 0.22, xerr=1.96 * c["se"], fmt="o", color=w, label=g.replace("_", " "), capsize=2)
    ax.axvline(0, color="#888", lw=0.8)
    ax.set_yticks(y0, [x.replace("_", " ") for x in X_FP])
    ax.set_xlabel("pp CAR [0,+1] per 1 SD karakteristik (CI 95%, cluster bank)")
    ax.set_title("Sidik jari keputusan lembaga global pada saham bank")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def md(df, fmt="{:.3f}"):
    kol = df.columns.tolist()
    baris = ["| " + " | ".join(kol) + " |", "|" + "---|" * len(kol)]
    for _, r in df.iterrows():
        baris.append("| " + " | ".join(fmt.format(v) if isinstance(v, float) else str(v) for v in r) + " |")
    return "\n".join(baris)


def bivariat(p, y="car_0_1"):
    """Per event, satu karakteristik per regresi (HC3): lebih bertenaga daripada panel 7 variabel."""
    baris = []
    for ev in k.EVENTS:
        s = p[p["event"] == ev]
        for x in X_FP:
            m = smf.ols(f"{y} ~ {x}", data=s).fit(cov_type="HC3")
            baris.append({"event": ev, "variabel": x, "koef": m.params[x], "p": m.pvalues[x], "n": int(m.nobs)})
    return pd.DataFrame(baris)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = pl.siapkan()
    p = panel_bank(data)
    bv = bivariat(p)
    bv.to_csv(OUT / "fingerprint_bivariat.csv", index=False)
    tabel_bv = bv.pivot(index="variabel", columns="event", values="koef").reindex(X_FP)[list(k.EVENTS)]
    bintang = bv.pivot(index="variabel", columns="event", values="p").reindex(X_FP)[list(k.EVENTS)]
    tabel_bv = tabel_bv.round(2).astype(str) + bintang.map(lambda q: "**" if q < 0.05 else ("*" if q < 0.1 else ""))
    print(tabel_bv.to_string())
    koef, wald, n, nb = fingerprint(p)
    koef0, wald0, _, _ = fingerprint(p, "car_0")
    wald = wald.assign(y="car_0_1")
    wald = pd.concat([wald, wald0.assign(y="car_0")], ignore_index=True)
    print(p.groupby("event").size().to_string())
    koef.to_csv(OUT / "fingerprint.csv", index=False)
    wald.to_csv(OUT / "fingerprint_wald.csv", index=False)
    grafik(koef, OUT / "fingerprint.png")
    print(wald.round(3).to_string(index=False))
    print(koef[koef["p"] < 0.1].round(3).to_string(index=False))

    ringkas, penting, _, n_pl = causal_forest(data)
    print(ringkas.round(2).to_string(index=False))
    print(penting.round(3).to_string())

    teks = ["# Heterogenitas: causal forest dan fingerprint", "",
            "## 8. Causal forest (CausalForestDML, 2.000 pohon, cross-fitting 5 lipatan)", "",
            f"Tumpukan saham di 2 hari event MSCI (T=1) vs {n_pl} hari buruk biasa (T=0). Y = peringkat persentil return hari-0 "
            "lintas saham hari itu (0-100; kebal batas ARB). CATE = pergeseran peringkat di hari 'dihakimi' dibanding crash biasa "
            "(negatif = membayar lebih dari biasanya).", "",
            md(ringkas.round(3)), "", "Kepentingan variabel (porsi split terbobot):", "",
            md(penting.round(3).rename("kepentingan").reset_index().rename(columns={"index": "variabel"})), "",
            "## 9. Fingerprint lintas jenis keputusan (bank saja)", "",
            f"Panel {n} observasi bank x event dari {nb} bank, 6 event non-placebo. Y = CAR [0,+1], FE event, "
            "X terstandar (1 SD), SE cluster per bank. Fundamental: Des 2025 untuk event s.d. Apr 2026, Jun 2026 sesudahnya.", "",
            md(wald.round(3)), "", "Koefisien (pp per 1 SD):", "", md(koef.round(3)), "",
            "![fingerprint](fingerprint.png)", "",
            "Regresi bivariat per event (pp CAR [0,+1] per 1 SD; ** p<0,05, * p<0,1; HC3):", "",
            md(tabel_bv.reset_index()), "",
            "Catatan: n bank per event kecil (~45), jadi koefisien individual lebar; yang diuji terutama sidik jari bersama (Wald). "
            "surat_berharga_aset = proksi eksposur SBN dari XBRL (surat berharga + obligasi pemerintah bila dilaporkan terpisah). "
            "asing = porsi asing dalam volume transaksi, 60 hari bursa sebelum E1."]
    (OUT / "ringkasan_heterogenitas.md").write_text("\n".join(teks), encoding="utf-8")


if __name__ == "__main__":
    main()
