"""Metode lanjutan (tingkat 2): synthetic control, DML, IV aliran asing, local projections, connectedness.

Input : data/olah/ (harga, bench, static, msci, asing_event) dan hasil/sampel_<event>.csv dari 02.
Output: hasil/lanjutan/*.csv, *.png, ringkasan_lanjutan.md

Jalankan setelah 02_event_study.py.
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.optimize import minimize
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.model_selection import KFold

import konfigurasi as k

OUT = k.HASIL / "lanjutan"
EVENT_INDEKS = [e for e, c in k.EVENTS.items() if "Indeks" in c["jenis"] and not c.get("plasebo")]
EVENT_RATING = [e for e, c in k.EVENTS.items() if c["jenis"] == "Rating" and not c.get("plasebo")]
EVENT_PLASEBO = [e for e, c in k.EVENTS.items() if c.get("plasebo")]
NEGARA = ["TH", "MY", "PH", "IN", "BR", "MX", "TR", "ZA", "KR", "TW", "VN", "PL", "CL"]


# ---------------------------------------------------------------- data dasar
def muat():
    bench = pd.read_csv(k.DATA_OLAH / "bench.csv", parse_dates=["date"]).set_index("date").sort_index()
    kal = bench.index[bench["JCI"].notna()]
    bench = bench.reindex(kal)
    harga = pd.read_csv(k.DATA_OLAH / "harga.csv.gz", parse_dates=["date"])
    static = pd.read_csv(k.DATA_OLAH / "static.csv").set_index("ticker")
    tri = harga.pivot_table(index="date", columns="ticker", values="tri").reindex(kal).ffill()
    px = harga.pivot_table(index="date", columns="ticker", values="px_last").reindex(kal).ffill()
    r = tri.pct_change(fill_method=None)
    sah = static["EQY_SH_OUT"].reindex(r.columns)
    mcap = px.shift(1).mul(sah, axis=1).where(r.notna())
    bank = static.index[static["GICS_INDUSTRY_NAME"] == "Banks"].intersection(r.columns)
    nonbank = r.columns.difference(bank)
    indeks = pd.DataFrame({
        "BANK": (r[bank] * mcap[bank]).sum(axis=1) / mcap[bank].sum(axis=1),
        "NONBANK": (r[nonbank] * mcap[nonbank]).sum(axis=1) / mcap[nonbank].sum(axis=1),
    })
    indeks[r.notna().sum(axis=1) < 300] = np.nan  # hari sebelum data saham tersedia
    return bench, kal, indeks


def pos(kal, tanggal):
    return int(np.searchsorted(kal, pd.Timestamp(tanggal)))


# ---------------------------------------------------------------- 6. synthetic control
def bobot_sc(Y, X):
    n = X.shape[1]
    f = lambda w: np.sum((Y - X @ w) ** 2)
    hasil = minimize(f, np.full(n, 1 / n), method="SLSQP", bounds=[(0, 1)] * n,
                     constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1}], options={"maxiter": 500})
    return hasil.x


def sc_satu(seri, donor, t0, pre=(-120, -6), horizon=(0, 1, 5), level=False):
    """Efek SC untuk satu seri. level=False: indeks harga (efek dalam %); level=True: yield (efek dalam bp)."""
    a, b = t0 + pre[0], t0 + max(horizon)
    # celah (hari libur, yield basi yang dikosongkan) diisi nilai terakhir sebelumnya, maks. 5 hari bursa
    jendela = pd.concat([seri.rename("ID"), donor], axis=1).ffill(limit=5).iloc[a:b + 1]
    jendela = jendela.loc[:, jendela.iloc[: (pre[1] - pre[0]) + 1].notna().all()]
    if "ID" not in jendela or jendela.shape[1] < 4:
        return None
    if level:
        Z = (jendela - jendela.iloc[0]) * 100  # perubahan bp sejak awal jendela
    else:
        Z = jendela / jendela.iloc[0]
    n_pre = pre[1] - pre[0] + 1
    don = Z.drop(columns="ID")
    w = bobot_sc(Z["ID"].iloc[:n_pre].to_numpy(), don.iloc[:n_pre].to_numpy())
    sint = don.to_numpy() @ w
    asli = Z["ID"].to_numpy()
    rmspe = np.sqrt(np.mean((asli[:n_pre] - sint[:n_pre]) ** 2))
    i_base = t0 - 1 - a
    efek = {}
    for h in horizon:
        i = t0 + h - a
        if i >= len(asli) or np.isnan(asli[i]) or np.isnan(sint[i]):
            continue
        if level:
            efek[h] = (asli[i] - asli[i_base]) - (sint[i] - sint[i_base])
        else:
            efek[h] = ((asli[i] / asli[i_base]) - (sint[i] / sint[i_base])) * 100
    return {"efek": efek, "rmspe": rmspe, "bobot": dict(zip(don.columns, np.round(w, 3)))}


def synthetic_control(bench, kal, indeks):
    seri_id = {"IHSG": bench["JCI"], "Bank": (1 + indeks["BANK"].fillna(0)).cumprod().where(indeks["BANK"].notna()),
               "SBN10Y": bench["SBN10Y"]}
    donor_eq = bench[[f"EQ_{c}" for c in NEGARA if f"EQ_{c}" in bench]]
    donor_bank = pd.concat([donor_eq, bench[[c for c in bench.columns if c.startswith("BANK_")]]], axis=1)
    donor_y = bench[[f"Y10_{c}" for c in NEGARA if f"Y10_{c}" in bench]]
    baris = []
    for ev, c in k.EVENTS.items():
        t0 = pos(kal, c["hari0"])
        for nama, seri, donor, level in [("IHSG", seri_id["IHSG"], donor_eq, False),
                                         ("Bank", seri_id["Bank"], donor_bank, False),
                                         ("SBN10Y", seri_id["SBN10Y"], donor_y, True)]:
            hasil = sc_satu(seri, donor, t0, level=level)
            if hasil is None or not hasil["efek"]:
                continue
            # placebo dalam ruang: tiap donor diperlakukan sebagai "Indonesia"
            rasio_id = {h: abs(v) / max(hasil["rmspe"], 1e-9) for h, v in hasil["efek"].items()}
            pl = {h: [] for h in hasil["efek"]}
            for d in donor.columns:
                lain = donor.drop(columns=d)
                hp = sc_satu(donor[d], lain, t0, level=level)
                if hp:
                    for h, v in hp["efek"].items():
                        if h in pl:
                            pl[h].append(abs(v) / max(hp["rmspe"], 1e-9))
            for h, v in hasil["efek"].items():
                p = (sum(x >= rasio_id[h] for x in pl[h]) + 1) / (len(pl[h]) + 1)
                baris.append({"event": ev, "lembaga": c["lembaga"], "plasebo": c.get("plasebo", False), "seri": nama,
                              "hari": h, "efek": v, "satuan": "bp" if level else "%", "p_placebo_negara": p,
                              "n_donor": len(pl[h]),
                              "donor_utama": ", ".join(f"{a}:{b}" for a, b in sorted(hasil["bobot"].items(), key=lambda x: -x[1])[:3])})
    return pd.DataFrame(baris)


# ---------------------------------------------------------------- 7. double/debiased ML
def dml(ev, y, d, X, n_split=5, n_ulang=5, seed=0):
    thetas, ses = [], []
    for u in range(n_ulang):
        kf = KFold(n_split, shuffle=True, random_state=seed + u)
        yr, dr = np.zeros(len(y)), np.zeros(len(y))
        for tr, te in kf.split(X):
            my = GradientBoostingRegressor(n_estimators=200, max_depth=3, learning_rate=0.05, subsample=0.8, random_state=u)
            my.fit(X[tr], y[tr])
            yr[te] = y[te] - my.predict(X[te])
            md = GradientBoostingClassifier(n_estimators=200, max_depth=3, learning_rate=0.05, subsample=0.8, random_state=u)
            md.fit(X[tr], d[tr])
            dr[te] = d[te] - md.predict_proba(X[te])[:, 1]
        theta = np.sum(dr * yr) / np.sum(dr ** 2)
        psi = (yr - theta * dr) * dr
        se = np.sqrt(np.mean(psi ** 2) / np.mean(dr ** 2) ** 2 / len(y))
        thetas.append(theta)
        ses.append(se)
    return float(np.median(thetas)), float(np.median(ses))


def jalankan_dml():
    static = pd.read_csv(k.DATA_OLAH / "static.csv").set_index("ticker")
    baris = []
    for ev in k.EVENTS_MSCI:
        f = k.HASIL / f"sampel_{ev}.csv"
        if not f.exists():
            continue
        s = pd.read_csv(f).set_index("ticker")
        s = s[s["vol_0"].fillna(0) > 0]
        sektor = pd.get_dummies(static["GICS_SECTOR_NAME"].reindex(s.index).fillna("lain"), prefix="sek", dtype=float)
        dasar = ["log_mcap", "beta_jci", "beta_mxef", "log_amihud", "free_float", "ret_pre"] + (["ppk"] if "ppk" in s else [])
        for perlakuan in ["msci", "bank"]:
            lain = [c for c in ["msci", "bank"] if c != perlakuan]
            for y in ["car_0", "car_0_1", "car_0_5"]:
                if y not in s or s[y].isna().all():
                    continue
                dd = pd.concat([s[[y, perlakuan] + dasar + lain], sektor], axis=1).dropna()
                if dd[perlakuan].nunique() < 2:
                    continue
                X = dd.drop(columns=[y, perlakuan]).to_numpy(dtype=float)
                th, se = dml(ev, dd[y].to_numpy(dtype=float), dd[perlakuan].to_numpy(dtype=int), X)
                from scipy.stats import norm
                baris.append({"event": ev, "perlakuan": perlakuan, "dependen": y, "theta_pp": th, "se": se,
                              "p": 2 * (1 - norm.cdf(abs(th / se))), "n": len(dd)})
    return pd.DataFrame(baris)


# ---------------------------------------------------------------- 10. IV aliran asing -> harga
def jalankan_iv():
    from linearmodels.iv import IV2SLS
    asing = pd.read_csv(k.DATA_OLAH / "asing_event.csv", parse_dates=["date"])
    if "listed_shares" not in asing:
        rs = pd.read_csv(k.DATA_MENTAH / "idx" / "ringkasan_saham.csv", parse_dates=["date"])[["date", "ticker", "listed_shares"]]
        asing = asing.merge(rs, on=["date", "ticker"], how="left")
    asing["jual_bersih_pct"] = -(asing["asing_bersih_lembar"]) / asing["listed_shares"] * 100  # % saham beredar
    kal_idx = sorted(asing["date"].unique())
    baris = []
    for ev in k.EVENTS_MSCI:
        f = k.HASIL / f"sampel_{ev}.csv"
        if not f.exists():
            continue
        s = pd.read_csv(f).set_index("ticker")
        s = s[s["vol_0"].fillna(0) > 0]
        t0 = pd.Timestamp(k.EVENTS[ev]["hari0"])
        hari = [d for d in kal_idx if d >= t0][:2]
        for jendela, hh, y in [("hari-0", hari[:1], "car_0"), ("hari 0 s.d. +1", hari[:2], "car_0_1")]:
            if y not in s or s[y].isna().all():
                continue
            js = asing[asing["date"].isin(hh)].groupby("ticker")["jual_bersih_pct"].sum()
            dd = s.assign(jual_bersih_pct=js.reindex(s.index))
            dd["bobot_msci"] = dd["bobot_msci"].fillna(0)
            kontrol = ["log_mcap", "beta_jci", "log_amihud", "free_float", "ret_pre", "bank"]
            dd = dd[[y, "jual_bersih_pct", "bobot_msci", "msci"] + kontrol].dropna()
            dd = dd.assign(const=1.0)
            m = IV2SLS(dd[y], dd[["const"] + kontrol], dd[["jual_bersih_pct"]], dd[["bobot_msci", "msci"]]).fit(cov_type="robust")
            fs = m.first_stage.diagnostics
            ols = sm.OLS(dd[y], dd[["const", "jual_bersih_pct"] + kontrol]).fit(cov_type="HC3")
            baris.append({"event": ev, "jendela": jendela, "multiplier_iv": m.params["jual_bersih_pct"],
                          "se_iv": m.std_errors["jual_bersih_pct"], "p_iv": m.pvalues["jual_bersih_pct"],
                          "F_tahap1": float(fs["f.stat"].iloc[0]), "multiplier_ols": ols.params["jual_bersih_pct"],
                          "p_ols": ols.pvalues["jual_bersih_pct"], "n": int(m.nobs)})
    return pd.DataFrame(baris)


# ---------------------------------------------------------------- 11. local projections
def local_projections(bench, kal, indeks, H=20):
    seri = {"IHSG (%)": np.log(bench["JCI"]) * 100,
            "Saham bank (%)": np.log((1 + indeks["BANK"].fillna(0)).cumprod().where(indeks["BANK"].notna())) * 100,
            "Yield SBN 10 th (bp)": bench["SBN10Y"] * 100,
            "USD/IDR (%)": np.log(bench["USDIDR"]) * 100}
    r_em = np.log(bench["MXEF"]).diff() * 100
    D = pd.DataFrame(0.0, index=kal, columns=["indeks", "rating", "plasebo"])
    for grup, evs in [("indeks", EVENT_INDEKS), ("rating", EVENT_RATING), ("plasebo", EVENT_PLASEBO)]:
        for e in evs:
            D.iloc[pos(kal, k.EVENTS[e]["hari0"]), D.columns.get_loc(grup)] = 1.0
    baris = []
    for nama, y in seri.items():
        y = y.ffill().where(kal <= y.last_valid_index())
        dy = y.diff()
        for h in range(H + 1):
            dep = y.shift(-h) - y.shift(1)
            X = pd.concat([D, r_em.rename("r_em"), dy.shift(1).rename("l1"), dy.shift(2).rename("l2")], axis=1)
            dd = pd.concat([dep.rename("y"), X], axis=1).dropna()
            if len(dd) < 200:
                continue
            m = sm.OLS(dd["y"], sm.add_constant(dd.drop(columns="y"))).fit(cov_type="HAC", cov_kwds={"maxlags": h + 1})
            for g in D.columns:
                if dd[g].sum() > 0:
                    baris.append({"seri": nama, "h": h, "grup": g, "beta": m.params[g], "se": m.bse[g],
                                  "n_event": int(dd[g].sum())})
    return pd.DataFrame(baris)


# ---------------------------------------------------------------- 12. connectedness (Diebold-Yilmaz, VAR bergulir)
def gfevd(res, H=10):
    A = res.ma_rep(H - 1)
    S = res.sigma_u.to_numpy() if hasattr(res.sigma_u, "to_numpy") else res.sigma_u
    n = S.shape[0]
    th = np.zeros((n, n))
    for i in range(n):
        penyebut = sum(A[h][i] @ S @ A[h][i] for h in range(H))
        for j in range(n):
            th[i, j] = sum((A[h][i] @ S[:, j]) ** 2 for h in range(H)) / S[j, j] / penyebut
    return th / th.sum(axis=1, keepdims=True)


def connectedness(bench, kal, indeks, jendela=200):
    from statsmodels.tsa.api import VAR
    df = pd.DataFrame({"Bank": indeks["BANK"] * 100, "NonBank": indeks["NONBANK"] * 100,
                       "SBN": bench["SBN10Y"].diff() * 100, "IDR": np.log(bench["USDIDR"]).diff() * 100}).dropna()
    df = (df - df.mean()) / df.std()
    baris = []
    for i in range(jendela, len(df) + 1):
        sub = df.iloc[i - jendela:i]
        try:
            res = VAR(sub).fit(2)
            th = gfevd(res) * 100
        except Exception:  # noqa: BLE001
            continue
        n = th.shape[0]
        tci = (th.sum() - np.trace(th)) / n
        ke = th.sum(axis=0) - np.diag(th)    # dari variabel j ke yang lain
        dari = th.sum(axis=1) - np.diag(th)  # yang diterima variabel i
        d = {"date": sub.index[-1], "TCI": tci}
        for j, c in enumerate(df.columns):
            d[f"net_{c}"] = ke[j] - dari[j]
        baris.append(d)
    tc = pd.DataFrame(baris).set_index("date")
    ringkas = []
    for ev, c in k.EVENTS.items():
        t = pd.Timestamp(c["hari0"])
        sebelum = tc.loc[(tc.index < t)].tail(10)
        sesudah = tc.loc[(tc.index >= t)].head(10)
        if len(sebelum) < 5 or len(sesudah) < 1:
            continue
        ringkas.append({"event": ev, "lembaga": c["lembaga"], "TCI_sebelum": sebelum["TCI"].mean(),
                        "TCI_sesudah": sesudah["TCI"].mean(), "perubahan": sesudah["TCI"].mean() - sebelum["TCI"].mean(),
                        "net_Bank_sesudah": sesudah["net_Bank"].mean(), "net_SBN_sesudah": sesudah["net_SBN"].mean(),
                        "hari_sesudah": len(sesudah)})
    return tc, pd.DataFrame(ringkas)


# ---------------------------------------------------------------- grafik
def grafik_lp(lp, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    warna = {"indeks": "#2a78d6", "rating": "#eb6834"}
    seri = lp["seri"].unique()
    fig, axes = plt.subplots(1, len(seri), figsize=(4 * len(seri), 3.4))
    for ax, s in zip(np.atleast_1d(axes), seri):
        for g, c in warna.items():
            x = lp[(lp["seri"] == s) & (lp["grup"] == g)]
            if x.empty:
                continue
            ax.plot(x["h"], x["beta"], color=c, lw=2, label=f"event {g}")
            ax.fill_between(x["h"], x["beta"] - 1.96 * x["se"], x["beta"] + 1.96 * x["se"], color=c, alpha=0.12, lw=0)
        ax.axhline(0, color="#52514e", lw=0.8)
        ax.set_title(s, loc="left", fontsize=10, fontweight="bold")
        ax.set_xlabel("hari setelah event")
        for sp in ["top", "right"]:
            ax.spines[sp].set_visible(False)
    np.atleast_1d(axes)[0].legend(frameon=False, fontsize=8)
    fig.suptitle("Local projections: respons rata-rata terhadap keputusan penyedia indeks vs lembaga rating (pita 95%)",
                 x=0.01, ha="left", fontsize=11, fontweight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=170)


def grafik_tci(tc, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(11, 3.4))
    ax.plot(tc.index, tc["TCI"], color="#2a78d6", lw=1.5)
    for ev, c in k.EVENTS.items():
        t = pd.Timestamp(c["hari0"])
        if tc.index.min() <= t <= tc.index.max():
            ax.axvline(t, color="#eb6834" if c["jenis"] == "Rating" else "#52514e", lw=0.8, ls="--")
            ax.text(t, ax.get_ylim()[1], f" {ev}", fontsize=7, va="top")
    ax.set_title("Indeks keterhubungan total saham bank, saham non-bank, SBN, rupiah (VAR bergulir 200 hari)",
                 loc="left", fontsize=10, fontweight="bold")
    ax.set_ylabel("% variasi dari pasar lain")
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=170)


def md_tabel(df, fmt="{:.3f}"):
    baris = ["| " + " | ".join(df.columns) + " |", "|" + "---|" * len(df.columns)]
    for r in df.itertuples(index=False):
        baris.append("| " + " | ".join(fmt.format(v) if isinstance(v, float) else str(v) for v in r) + " |")
    return "\n".join(baris)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    bench, kal, indeks = muat()
    print("6. synthetic control ...")
    sc = synthetic_control(bench, kal, indeks)
    sc.to_csv(OUT / "synthetic_control.csv", index=False)
    print("7. DML ...")
    dm = jalankan_dml()
    dm.to_csv(OUT / "dml.csv", index=False)
    print("10. IV ...")
    iv = jalankan_iv()
    iv.to_csv(OUT / "iv.csv", index=False)
    print("11. local projections ...")
    lp = local_projections(bench, kal, indeks)
    lp.to_csv(OUT / "local_projections.csv", index=False)
    grafik_lp(lp, OUT / "local_projections.png")
    print("12. connectedness ...")
    tc, tcr = connectedness(bench, kal, indeks)
    tc.to_csv(OUT / "connectedness_harian.csv")
    tcr.to_csv(OUT / "connectedness_event.csv", index=False)
    grafik_tci(tc, OUT / "connectedness.png")

    lp_ringkas = lp[lp["h"].isin([0, 1, 5, 10, 20])].pivot_table(index=["seri", "h"], columns="grup", values="beta").reset_index()
    md = ["# Ringkasan metode lanjutan", "",
          "## 6. Synthetic control (efek = Indonesia asli - Indonesia tiruan dari 13 negara EM; p = placebo negara)", "",
          md_tabel(sc.drop(columns=["plasebo"])), "",
          "## 7. Double/debiased ML (efek dalam poin persen; gradient boosting, 5-fold, 5 ulangan)", "",
          md_tabel(dm), "",
          "## 10. IV: jual bersih asing (% saham beredar) -> CAR; instrumen = bobot dan status MSCI", "",
          md_tabel(iv), "",
          "## 11. Local projections (koefisien; % atau bp)", "", md_tabel(lp_ringkas), "",
          "Grafik: `local_projections.png`.", "",
          "## 12. Connectedness (VAR bergulir 200 hari, GFEVD H=10)", "", md_tabel(tcr), "",
          "Grafik: `connectedness.png`."]
    (OUT / "ringkasan_lanjutan.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
