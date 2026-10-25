"""Pembanding kasus nyata: Argentina diturunkan MSCI dari Emerging ke Standalone (2020-2021).

Tanggal (siaran pers MSCI):
  A1 23 Jun 2020 (malam waktu AS): peringatan, Argentina bisa dikeluarkan dari EM; konsultasi dijanjikan untuk 2021.
     Reaksi pertama: 24 Jun 2020.
  A2 24 Jun 2021 (malam waktu AS): keputusan EM -> Standalone, berlaku di review Nov 2021. Reaksi pertama: 25 Jun 2021.
  A3 30 Nov 2021: tanggal efektif (rebalancing review semi-tahunan November).
Data: Yahoo Finance (ARGT = Global X MSCI Argentina ETF, US$; EEM = iShares MSCI EM ETF, US$; Merval dan ARS=X
sebagai pelengkap). Return di atas EM = ARGT - EEM. Indeks MSCI Argentina hanya berisi saham Argentina yang tercatat
di luar negeri, jadi ARGT adalah proksi yang wajar, tetapi juga memuat perusahaan Argentina yang tercatat di AS.

Output: hasil/lanjutan/{argentina.csv, argentina.png, ringkasan_argentina.md}
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import konfigurasi as k

OUT = k.HASIL / "lanjutan"
EVENT = {"A1 peringatan (Jun 2020)": "2020-06-24", "A2 keputusan (Jun 2021)": "2021-06-25", "A3 efektif (Nov 2021)": "2021-11-30"}


def muat():
    d = pd.read_csv(k.DATA_MENTAH / "negara_lain" / "yahoo_argentina_2020_2022.csv", comment="#", parse_dates=["date"])
    w = d.pivot(index="date", columns="simbol", values="adjclose")
    w = w[w["ARGT"].notna() & w["EEM"].notna()]
    return w


def jendela(w, tgl, a, b):
    i = w.index.searchsorted(pd.Timestamp(tgl))
    lo, hi = w.index[i - 1 + a] if a > 0 else w.index[i - 1], w.index[min(i + b, len(w) - 1)]
    r = w.loc[hi] / w.loc[lo] - 1
    return r


def main():
    w = muat()
    baris = []
    for nama, tgl in EVENT.items():
        for jn, (a, b) in {"[0]": (0, 0), "[0,+1]": (0, 1), "[0,+5]": (0, 5), "[0,+20]": (0, 20)}.items():
            r = jendela(w, tgl, a, b)
            baris.append({"event": nama, "hari0": tgl, "jendela": jn, "ARGT_%": r["ARGT"] * 100, "EEM_%": r["EEM"] * 100,
                          "di_atas_EM_pp": (r["ARGT"] - r["EEM"]) * 100})
    # pengumuman keputusan -> efektif, dan efektif -> +1 tahun
    def antar(a, b):
        a, b = pd.Timestamp(a), pd.Timestamp(b)
        x = w.loc[w.index[w.index.searchsorted(b, side="right") - 1]] / w.loc[w.index[w.index.searchsorted(a) - 1]] - 1
        return x
    for nama, (a, b) in {"Keputusan -> efektif": ("2021-06-25", "2021-11-30"), "Efektif -> +1 tahun": ("2021-12-01", "2022-11-30"),
                         "Peringatan -> keputusan": ("2020-06-24", "2021-06-24")}.items():
        r = antar(a, b)
        baris.append({"event": nama, "hari0": a, "jendela": f"{a} s.d. {b}", "ARGT_%": r["ARGT"] * 100, "EEM_%": r["EEM"] * 100,
                      "di_atas_EM_pp": (r["ARGT"] - r["EEM"]) * 100})
    h = pd.DataFrame(baris)
    h.to_csv(OUT / "argentina.csv", index=False)

    # jalur relatif ARGT/EEM sekitar keputusan, berdampingan dengan Indonesia E2 (IHSG relatif MSCI EM tidak tersedia
    # setelah 16 Okt, jadi Indonesia memakai IHSG mentah)
    i0 = w.index.searchsorted(pd.Timestamp("2021-06-25"))
    rel = (w["ARGT"] / w["EEM"]).iloc[i0 - 1:i0 + 21]
    rel = (rel / rel.iloc[0] - 1) * 100
    j = pd.read_csv(k.DATA_OLAH / "bench.csv", parse_dates=["date"]).set_index("date")["JCI"].dropna()
    jj = j.loc["2026-10-15":]
    jj = (jj / jj.iloc[0] - 1) * 100
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.plot(range(len(rel)), rel.values, color="#b05a2f", lw=2.2, label="Argentina: keputusan MSCI 24 Jun 2021 (ARGT di atas EEM)")
    ax.plot(range(len(jj)), jj.values, color="#2f6db5", lw=2.6, label="Indonesia: konsultasi MSCI 15 Okt 2026 (IHSG)")
    ax.axhline(0, color="#999", lw=0.8)
    ax.set_xlabel("Hari bursa setelah pengumuman (0 = penutupan sebelum pengumuman)")
    ax.set_ylabel("Perubahan kumulatif, %")
    ax.set_title("Diperkirakan vs kejutan: Argentina 2021 dan Indonesia 2026")
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "argentina.png", dpi=150)
    plt.close(fig)
    print(h.round(2).to_string(index=False))

    def md(df):
        kol = df.columns.tolist()
        out = ["| " + " | ".join(kol) + " |", "|" + "---|" * len(kol)]
        for _, r in df.iterrows():
            out.append("| " + " | ".join(f"{v:.2f}" if isinstance(v, float) else str(v) for v in r) + " |")
        return "\n".join(out)
    teks = ["# Argentina 2020-2021: pembanding penurunan status MSCI yang benar-benar terjadi", "",
            "Sumber tanggal: siaran pers MSCI 2021 Market Classification Review (24 Jun 2021) dan 2020 review (23 Jun 2020). "
            "Data: Yahoo Finance (ARGT, EEM). Return di atas EM = ARGT - EEM.", "", md(h.round(2)), "",
            "![argentina](argentina.png)"]
    (OUT / "ringkasan_argentina.md").write_text("\n".join(teks), encoding="utf-8")


if __name__ == "__main__":
    main()
