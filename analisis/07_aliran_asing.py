"""Aliran dana asing di 8 event lembaga global (RQ3: lewat mekanisme apa?).

Data: jual-beli asing harian per saham dari Ringkasan Saham BEI 2025-2026 (asing_event.csv dari 01c).
A. Agregat: jual/beli bersih asing (Rp T) di jendela [0], [0,+1], [0,+5], [+2,+5] untuk seluruh pasar, bank,
   anggota MSCI, dan saham PPK; dibandingkan dengan semua jendela non-event sepanjang 2025-2026
   (p dua sisi = jumlah |placebo| >= |event| + 1, dibagi N + 1).
B. Lintas saham per event: jual bersih asing [0,+1] (% saham tercatat) ~ bank + msci + ppk + ukuran + free float
   + porsi asing pra-event (HC3). Siapa yang dibuang asing di tiap jenis keputusan?
C. Tekanan harga: CAR [0,+1] ~ jual bersih asing + kontrol, per event dan bertumpuk (FE event, cluster saham)
   dengan kemiringan berbeda per jenis keputusan. Ini asosiasi (OLS), bukan kausal; versi IV untuk MSCI ada di 05.
D. Grafik kumulatif jual-beli bersih asing di saham bank dan non-bank 2025-2026 dengan penanda event.

Output: hasil/lanjutan/{aliran_asing_agregat.csv, aliran_asing_lintas.csv, aliran_asing_tekanan.csv,
        aliran_asing.png, ringkasan_aliran_asing.md}
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
JENDELA = {"[0]": (0, 0), "[0,+1]": (0, 1), "[0,+5]": (0, 5), "[+2,+5]": (2, 5)}
JARAK_EVENT = 5
GRUP = {"Indeks saham": "indeks_saham", "Indeks obligasi": "indeks_obligasi", "Rating": "rating"}


def muat():
    a = pd.read_csv(k.DATA_OLAH / "asing_event.csv", parse_dates=["date"])
    a = a[a["date"] >= pd.Timestamp("2025-01-01")]
    static = pd.read_csv(k.DATA_OLAH / "static.csv").set_index("ticker")
    bank = set(static.index[static["GICS_INDUSTRY_NAME"] == "Banks"])
    msci = pd.read_csv(k.DATA_OLAH / "msci.csv")
    hist = pd.read_csv(k.DATA_OLAH / "msci_proksi_hist.csv")
    ppk = pd.read_csv(k.DATA_OLAH / "ppk_event.csv") if (k.DATA_OLAH / "ppk_event.csv").exists() else None
    return a, bank, msci, hist, ppk


def anggota_msci(ev, msci, hist):
    if ev in k.EVENTS_MSCI:
        return set(msci.loc[msci["event"] == ev, "ticker"])
    t0 = pd.Timestamp(k.EVENTS[ev]["hari0"])
    snap = hist.loc[pd.to_datetime(hist["snapshot"]) < t0, "snapshot"].max()
    return set(hist.loc[hist["snapshot"] == snap, "ticker"])


def kalender(a):
    return pd.DatetimeIndex(sorted(a["date"].unique()))


def bersih_harian(a, tickers=None):
    x = a if tickers is None else a[a["ticker"].isin(tickers)]
    return x.groupby("date")["asing_bersih_rp"].sum().div(1e12)


# ---------------------------------------------------------------- A. agregat
def agregat(a, bank, msci, hist, ppk):
    kal = kalender(a)
    pos_event = {ev: int(np.searchsorted(kal, pd.Timestamp(c["hari0"]))) for ev, c in k.EVENTS.items()}
    terlarang = {p + d for p in pos_event.values() for d in range(-JARAK_EVENT, JARAK_EVENT + 1)}
    baris = []
    for ev, cfg in k.EVENTS.items():
        t0 = pos_event[ev]
        kelompok = {"Pasar": None, "Bank": bank, "Anggota MSCI": anggota_msci(ev, msci, hist)}
        if ppk is not None:
            kelompok["PPK"] = set(ppk.loc[(ppk["event"] == ev) & (ppk["ppk"] == 1), "ticker"])
        for nama, tk in kelompok.items():
            seri = bersih_harian(a, tk).reindex(kal).fillna(0).to_numpy()
            for jn, (lo, hi) in JENDELA.items():
                if t0 + hi >= len(kal):
                    continue
                nilai = seri[t0 + lo:t0 + hi + 1].sum()
                plac = np.array([seri[i + lo:i + hi + 1].sum() for i in range(len(kal) - hi)
                                 if i not in terlarang and i + lo >= 0])
                baris.append({"event": ev, "lembaga": cfg["lembaga"], "plasebo": cfg.get("plasebo", False),
                              "kelompok": nama, "jendela": jn, "bersih_rp_T": nilai,
                              "persentil": (plac < nilai).mean() * 100,
                              "p_dua_sisi": ((np.abs(plac - np.median(plac)) >= abs(nilai - np.median(plac))).sum() + 1) / (len(plac) + 1),
                              "n_placebo": len(plac)})
    return pd.DataFrame(baris)


# ---------------------------------------------------------------- B. lintas saham
def karakteristik(a, ev):
    kal = kalender(a)
    t0 = int(np.searchsorted(kal, pd.Timestamp(k.EVENTS[ev]["hari0"])))
    pra = kal[max(t0 - 60, 0):t0]
    x = a[a["date"].isin(pra)].copy()
    x["porsi"] = (x["foreign_buy"] + x["foreign_sell"]) / (2 * x["volume"].where(x["volume"] > 0))
    c = x.groupby("ticker").agg(porsi_asing=("porsi", "mean"))
    akhir = a[a["date"] == kal[t0 - 1]].set_index("ticker")
    c["log_mcap"] = np.log((akhir["close"] * akhir["listed_shares"]).where(lambda v: v > 0))
    c["free_float"] = akhir["free_float"]
    c["porsi_asing"] *= 100
    return c


def jual_bersih(a, ev, lo, hi):
    kal = kalender(a)
    t0 = int(np.searchsorted(kal, pd.Timestamp(k.EVENTS[ev]["hari0"])))
    if t0 + hi >= len(kal):
        return None
    x = a[a["date"].isin(kal[t0 + lo:t0 + hi + 1])]
    x = x.assign(js=-x["asing_bersih_lembar"] / x["listed_shares"].where(x["listed_shares"] > 0) * 100)
    return x.groupby("ticker")["js"].sum()


def winsor(s, q=0.01):
    return s.clip(s.quantile(q), s.quantile(1 - q))


def lintas(a, bank, msci, hist, ppk):
    baris = []
    for ev, cfg in k.EVENTS.items():
        js = jual_bersih(a, ev, 0, 1)
        if js is None:
            continue
        c = karakteristik(a, ev).join(js.rename("jual_bersih"), how="inner")
        c["bank"] = c.index.isin(bank).astype(int)
        c["msci"] = c.index.isin(anggota_msci(ev, msci, hist)).astype(int)
        c["ppk"] = c.index.isin(set(ppk.loc[(ppk["event"] == ev) & (ppk["ppk"] == 1), "ticker"])).astype(int) if ppk is not None else 0
        c = c.dropna()
        c["jual_bersih"] = winsor(c["jual_bersih"])
        m = smf.ols("jual_bersih ~ bank + msci + ppk + log_mcap + free_float + porsi_asing", data=c).fit(cov_type="HC3")
        for v in ["bank", "msci", "ppk", "log_mcap", "free_float", "porsi_asing"]:
            baris.append({"event": ev, "lembaga": cfg["lembaga"], "plasebo": cfg.get("plasebo", False), "variabel": v,
                          "koef": m.params[v], "se": m.bse[v], "p": m.pvalues[v], "n": int(m.nobs)})
    return pd.DataFrame(baris)


# ---------------------------------------------------------------- C. tekanan harga
def tekanan(a, data):
    r, px, vol, rb, static, msci, kal = data
    tumpuk, baris = [], []
    for ev, cfg in k.EVENTS.items():
        js = jual_bersih(a, ev, 0, 1)
        if js is None:
            continue
        s, _ = es.bangun_sampel(ev, cfg, r, px, vol, rb, static, msci, None)
        s = s[s["vol_0"] > 0].join(js.rename("jual_bersih"), how="inner")
        s = s.dropna(subset=["car_0_1", "jual_bersih", "log_mcap", "beta_jci", "log_amihud", "free_float", "ret_pre"])
        s["jual_bersih"] = winsor(s["jual_bersih"])
        m = smf.ols("car_0_1 ~ jual_bersih + log_mcap + beta_jci + log_amihud + free_float + ret_pre + bank", data=s).fit(cov_type="HC3")
        m0 = smf.ols("car_0_1 ~ log_mcap + beta_jci + log_amihud + free_float + ret_pre + bank", data=s).fit()
        baris.append({"event": ev, "lembaga": cfg["lembaga"], "jenis": cfg["jenis"], "plasebo": cfg.get("plasebo", False),
                      "multiplier": m.params["jual_bersih"], "se": m.bse["jual_bersih"], "p": m.pvalues["jual_bersih"],
                      "r2_parsial": (m.rsquared - m0.rsquared) / (1 - m0.rsquared), "n": int(m.nobs)})
        tumpuk.append(s.reset_index().assign(event=ev, grup=GRUP[cfg["jenis"]], plasebo=cfg.get("plasebo", False)))
    t = pd.concat(tumpuk)
    t = t[~t["plasebo"]]
    mp = smf.ols("car_0_1 ~ C(event) + jual_bersih:C(grup) + log_mcap + beta_jci + log_amihud + free_float + ret_pre + bank",
                 data=t).fit(cov_type="cluster", cov_kwds={"groups": t["ticker"]})
    nama = {g: f"jual_bersih:C(grup)[{g}]" for g in t["grup"].unique()}
    uji = []
    for g, n in nama.items():
        uji.append({"uji": f"kemiringan {g}", "nilai": mp.params[n], "p": mp.pvalues[n]})
    for x, y in [("indeks_saham", "rating"), ("indeks_saham", "indeks_obligasi"), ("indeks_obligasi", "rating")]:
        w = mp.wald_test(f"{nama[x]} = {nama[y]}", scalar=True)
        uji.append({"uji": f"{x} = {y}", "nilai": float(w.statistic), "p": float(w.pvalue)})
    return pd.DataFrame(baris), pd.DataFrame(uji)


# ---------------------------------------------------------------- D. grafik
def grafik(a, bank, path):
    kal = kalender(a)
    b = bersih_harian(a, bank).reindex(kal).fillna(0).cumsum()
    nb = bersih_harian(a[~a["ticker"].isin(bank)]).reindex(kal).fillna(0).cumsum()
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.plot(kal, b, color="#c4453a", lw=1.6, label="Saham bank")
    ax.plot(kal, nb, color="#2f6db5", lw=1.6, label="Saham non-bank")
    ax.axhline(0, color="#888", lw=0.7)
    warna = {"Indeks saham": "#2f6db5", "Indeks obligasi": "#7b5ea7", "Rating": "#c4453a"}
    atas, bawah = ax.get_ylim()[1], ax.get_ylim()[0]
    for i, (ev, c) in enumerate(k.EVENTS.items()):
        t = pd.Timestamp(c["hari0"])
        ax.axvline(t, color=warna[c["jenis"]], lw=0.8, ls=":" if c.get("plasebo") else "--", alpha=0.8)
        y = atas - (atas - bawah) * (0.0 if i % 2 == 0 else 0.09)  # selang-seling supaya label event berdekatan tidak bertumpuk
        ax.text(t, y, ev, rotation=90, va="top", ha="right", fontsize=7, color="#444")
    ax.set_ylabel("Kumulatif beli bersih asing (Rp T)")
    ax.set_title("Aliran asing di saham Indonesia 2025-2026 (garis putus = event, titik-titik = placebo)")
    ax.legend(frameon=False, loc="lower left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def md(df, fmt="{:.3f}"):
    kol = df.columns.tolist()
    baris = ["| " + " | ".join(kol) + " |", "|" + "---|" * len(kol)]
    for _, r in df.iterrows():
        baris.append("| " + " | ".join(fmt.format(v) if isinstance(v, float) else str(v) for v in r) + " |")
    return "\n".join(baris)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    a, bank, msci, hist, ppk = muat()
    ag = agregat(a, bank, msci, hist, ppk)
    ag.to_csv(OUT / "aliran_asing_agregat.csv", index=False)
    li = lintas(a, bank, msci, hist, ppk)
    li.to_csv(OUT / "aliran_asing_lintas.csv", index=False)
    data = pl.siapkan()
    tk, uji = tekanan(a, data)
    tk.to_csv(OUT / "aliran_asing_tekanan.csv", index=False)
    uji.to_csv(OUT / "aliran_asing_tekanan_uji.csv", index=False)
    grafik(a, bank, OUT / "aliran_asing.png")

    pv = ag[ag["jendela"] == "[0,+1]"].pivot(index="event", columns="kelompok", values="bersih_rp_T").reindex(list(k.EVENTS))
    pp = ag[ag["jendela"] == "[0,+1]"].pivot(index="event", columns="kelompok", values="p_dua_sisi").reindex(list(k.EVENTS))
    tabel = pv.round(2).astype(str) + " (p=" + pp.round(3).astype(str) + ")"
    print(tabel.to_string())
    print(li[li["p"] < 0.1].round(3).to_string(index=False))
    print(tk.round(3).to_string(index=False))
    print(uji.round(3).to_string(index=False))

    teks = ["# Aliran dana asing di 8 event", "",
            f"Data: Ringkasan Saham BEI {a['date'].min():%d %b %Y} s.d. {a['date'].max():%d %b %Y}, {a['ticker'].nunique()} saham. "
            "Beli bersih = (beli asing - jual asing) x harga penutupan. Negatif = asing menjual bersih.", "",
            "## A. Beli bersih asing [0,+1] (Rp T; p dua sisi vs semua jendela non-event 2025-2026)", "",
            md(tabel.reset_index()), "",
            "Semua jendela: `aliran_asing_agregat.csv`.", "",
            "## B. Siapa yang dijual asing? Jual bersih [0,+1] (% saham tercatat), HC3", "",
            md(li.round(3)), "",
            "## C. Tekanan harga: CAR [0,+1] per 1 pp saham yang dijual bersih asing (OLS + kontrol)", "",
            md(tk.round(3)), "", "Bertumpuk (6 event non-placebo, FE event, cluster saham):", "", md(uji.round(3)), "",
            "Catatan: OLS ini asosiasi; arah sebab bisa dua arah (asing menjual saham yang jatuh). Versi IV untuk event MSCI di "
            "`ringkasan_lanjutan.md` bagian 10.", "",
            "![aliran asing](aliran_asing.png)"]
    (OUT / "ringkasan_aliran_asing.md").write_text("\n".join(teks), encoding="utf-8")


if __name__ == "__main__":
    main()
