"""Perbandingan antarnegara: seberapa langka, seperti apa, dan seberapa cepat pulih guncangan E1/E2 dibanding
kejatuhan besar di 13 pasar berkembang lain sejak 2010.

Data: indeks saham, kurs (mata uang lokal per US$) dan MSCI EM dari bench.csv (Refinitiv, 2010-16 Okt 2026),
IHSG sampai 23 Okt dari BEI, JISDOR untuk kurs rupiah setelah 16 Okt.
Episode = hari ketika indeks saham satu negara turun >= 5%. Untuk tiap episode:
  - return hari-0, return di luar MSCI EM hari itu (idiosinkratik), dan perubahan kurs hari-0 (+ = mata uang melemah);
  - global = MSCI EM turun >= 3% di hari yang sama (mis. Maret 2020);
  - pemulihan di hari +5 = porsi titik terdalam [0,+1] yang sudah kembali pada hari +5.

Output: hasil/lanjutan/{banding_negara_episode.csv, banding_negara.png, ringkasan_banding_negara.md}
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import konfigurasi as k

OUT = k.HASIL / "lanjutan"
NAMA = {"JCI": "Indonesia", "EQ_TH": "Thailand", "EQ_MY": "Malaysia", "EQ_PH": "Filipina", "EQ_IN": "India",
        "EQ_BR": "Brasil", "EQ_MX": "Meksiko", "EQ_TR": "Turki", "EQ_ZA": "Afrika Selatan", "EQ_KR": "Korea",
        "EQ_TW": "Taiwan", "EQ_VN": "Vietnam", "EQ_PL": "Polandia", "EQ_CL": "Chile"}
FX = {"JCI": "USDIDR", **{e: "FX_" + e[3:] for e in NAMA if e != "JCI"}}
AMBANG = -0.05


def muat():
    b = pd.read_csv(k.DATA_OLAH / "bench.csv", parse_dates=["date"]).set_index("date").sort_index()
    jis = pd.read_csv(k.DATA_MENTAH / "jisdor.csv", comment="#", parse_dates=["date"]).set_index("date")["jisdor"]
    # rupiah setelah 16 Okt dari JISDOR (perubahan harian), disambung ke seri Refinitiv
    usd = b["USDIDR"].copy()
    for d in jis.index[jis.index > usd.last_valid_index()]:
        prev = jis.index[jis.index < d].max()
        usd.loc[d] = usd.ffill().loc[:d].iloc[-1] * jis.loc[d] / jis.loc[prev]
    b["USDIDR"] = usd
    return b


def episode(b):
    baris = []
    mx = b["MXEF"].pct_change(fill_method=None)
    for eq, negara in NAMA.items():
        s = b[eq].dropna()
        r = s.pct_change()
        fx = b[FX[eq]].reindex(s.index).ffill().pct_change()
        posisi = np.where(r.values <= AMBANG)[0]
        for i in posisi:
            if i + 5 >= len(s) and eq != "JCI":
                continue
            d = s.index[i]
            jalur = s.iloc[i - 1:i + 6] / s.iloc[i - 1] - 1
            terdalam = jalur.iloc[1:3].min()
            h5 = jalur.iloc[6] if len(jalur) > 6 else np.nan
            baris.append({"negara": negara, "tanggal": d.date(), "r0_%": r.iloc[i] * 100,
                          "idiosinkratik_%": (r.iloc[i] - mx.get(d, np.nan)) * 100,
                          "kurs_0_%": fx.get(d, np.nan) * 100, "global": bool(mx.get(d, 0) <= -0.03),
                          "terdalam_01_%": terdalam * 100, "h5_%": h5 * 100,
                          "pulih_h5": (h5 - terdalam) / -terdalam if pd.notna(h5) and terdalam < 0 else np.nan})
    e = pd.DataFrame(baris)
    e["event_indonesia"] = e.apply(lambda r: "E1" if (r.negara == "Indonesia" and str(r.tanggal) == "2026-01-28")
                                   else ("E2" if (r.negara == "Indonesia" and str(r.tanggal) == "2026-10-16") else ""), axis=1)
    return e


def kelangkaan(b):
    hari = []
    for eq, negara in NAMA.items():
        r = b[eq].dropna().pct_change().dropna() * 100
        hari.append(pd.DataFrame({"negara": negara, "tanggal": r.index, "r": r.values}))
    return pd.concat(hari)


def grafik(e, path):
    lain = e[(e["event_indonesia"] == "") & e["kurs_0_%"].notna()]
    fig, ax = plt.subplots(figsize=(8, 5))
    g = lain[lain["global"]]
    l = lain[~lain["global"]]
    ax.scatter(l["kurs_0_%"], l["r0_%"], s=22, color="#b8b8b8", label="Kejatuhan lokal, negara lain")
    ax.scatter(g["kurs_0_%"], g["r0_%"], s=22, facecolors="none", edgecolors="#8a8a8a", label="Kejatuhan global (MSCI EM ≤ −3%)")
    ind = e[e["event_indonesia"] != ""]
    ax.scatter(ind["kurs_0_%"], ind["r0_%"], s=90, color="#2f6db5", zorder=3, label="Indonesia: keputusan MSCI")
    for r in ind.itertuples():
        ax.annotate(r.event_indonesia, (r._5, r._3), xytext=(8, -4), textcoords="offset points", color="#2f6db5", weight="bold")
    ax.axvline(0, color="#999", lw=0.8)
    ax.set_xlabel("Perubahan kurs hari itu, % (+ = mata uang melemah terhadap US$)")
    ax.set_ylabel("Return indeks saham hari itu, %")
    ax.set_title("Kejatuhan saham ≥5% dalam sehari di 14 pasar berkembang, 2010–2026")
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def md(df, fmt="{:.2f}"):
    kol = df.columns.tolist()
    out = ["| " + " | ".join(kol) + " |", "|" + "---|" * len(kol)]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(fmt.format(v) if isinstance(v, float) else str(v) for v in r) + " |")
    return "\n".join(out)


def main():
    b = muat()
    e = episode(b)
    e.to_csv(OUT / "banding_negara_episode.csv", index=False)
    semua = kelangkaan(b)
    n = len(semua)
    hasil = []
    for ev, tgl in [("E1", "2026-01-28"), ("E2", "2026-10-16")]:
        r0 = semua[(semua["negara"] == "Indonesia") & (semua["tanggal"] == tgl)]["r"].iloc[0]
        lebih_buruk = semua[semua["r"] < r0]
        hasil.append({"event": ev, "IHSG_%": r0, "hari_lebih_buruk_dari_semua_negara": len(lebih_buruk),
                      "persentil_terburuk_%": (len(lebih_buruk) + 1) / n * 100,
                      "hari_lebih_buruk_non_global": int((~lebih_buruk["tanggal"].isin(
                          b.index[b["MXEF"].pct_change(fill_method=None) <= -0.03])).sum())})
    hasil = pd.DataFrame(hasil)
    lain = e[e["event_indonesia"] == ""]
    ringkas = pd.DataFrame([
        {"kelompok": "Kejatuhan global (negara lain)", "n": int(lain["global"].sum()),
         "kurs_median_%": lain.loc[lain["global"], "kurs_0_%"].median(), "idiosinkratik_median_%": lain.loc[lain["global"], "idiosinkratik_%"].median(),
         "pulih_h5_median": lain.loc[lain["global"], "pulih_h5"].median()},
        {"kelompok": "Kejatuhan lokal (negara lain)", "n": int((~lain["global"]).sum()),
         "kurs_median_%": lain.loc[~lain["global"], "kurs_0_%"].median(), "idiosinkratik_median_%": lain.loc[~lain["global"], "idiosinkratik_%"].median(),
         "pulih_h5_median": lain.loc[~lain["global"], "pulih_h5"].median()},
    ] + [{"kelompok": f"Indonesia {r.event_indonesia}", "n": 1, "kurs_median_%": r._5, "idiosinkratik_median_%": r._4,
          "pulih_h5_median": r.pulih_h5} for r in e[e["event_indonesia"] != ""].itertuples()])
    lokal = lain[~lain["global"]].copy()
    rasio_lokal = (lokal["kurs_0_%"] / -lokal["r0_%"]).median()
    terburuk = e[~e["global"]].nsmallest(12, "idiosinkratik_%")[["negara", "tanggal", "r0_%", "idiosinkratik_%", "kurs_0_%", "pulih_h5"]]
    grafik(e, OUT / "banding_negara.png")
    print(hasil.round(3).to_string(index=False))
    print(ringkas.round(3).to_string(index=False))
    print(terburuk.round(2).to_string(index=False))
    print("episode per negara:", e.groupby("negara").size().to_dict(), "rasio kurs/saham median lokal:", round(rasio_lokal, 3))
    teks = ["# Indonesia dibanding 13 pasar berkembang lain (2010–2026)", "",
            f"Semua hari bursa 14 negara: {n:,} negara-hari. Episode = indeks saham turun ≥5% dalam sehari ({len(e)} episode).", "",
            "## Seberapa langka", "", md(hasil.round(3)), "",
            "## Seperti apa dan seberapa cepat pulih (median)", "",
            "kurs_median_% = perubahan kurs hari-0 (+ melemah); pulih_h5 = porsi titik terdalam [0,+1] yang kembali di hari +5.", "",
            md(ringkas.round(3)), "",
            "## 12 kejatuhan idiosinkratik terdalam (di luar hari kejatuhan global)", "", md(terburuk.round(2)), "",
            "![banding](banding_negara.png)", "",
            "Catatan: kurs dan indeks negara lain dari Refinitiv (berhenti 16 Okt 2026); rupiah setelah itu dari JISDOR. "
            "Negara yang pernah diturunkan MSCI (Argentina, Pakistan, Yunani) belum ada di data ini."]
    (OUT / "ringkasan_banding_negara.md").write_text("\n".join(teks), encoding="utf-8")


if __name__ == "__main__":
    main()
