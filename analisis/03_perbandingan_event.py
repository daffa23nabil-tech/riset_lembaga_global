"""Perbandingan reaksi pasar terhadap 8 keputusan lembaga global (grafik untuk brief Oktober).

Input : data/olah/{harga.csv.gz, bench.csv, static.csv}
Output: hasil/perbandingan_event.csv, hasil/perbandingan_event.md, hasil/perbandingan_event.png
Ukuran per event dan jendela: IHSG (%), saham bank tertimbang kapitalisasi (%), MSCI EM (%),
perubahan yield SBN 10 tahun (bp), dan USD/IDR (%, positif = rupiah melemah).
"""
import numpy as np
import pandas as pd

import konfigurasi as k

JENDELA = {"h0": (0, 0), "h0_1": (0, 1), "hm1_1": (-1, 1)}
JENDELA_GRAFIK = "h0_1"
BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]

# Palet referensi (dataviz skill), divalidasi: slot 1-3, mode terang.
WARNA = {"IHSG": "#2a78d6", "Bank": "#eb6834", "SBN": "#1baf7a"}
TINTA, TINTA_2, GRID, PERMUKAAN, PITA_PLASEBO = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb", "#f1f0ec"


def muat():
    harga = pd.read_csv(k.DATA_OLAH / "harga.csv.gz", parse_dates=["date"])
    bench = pd.read_csv(k.DATA_OLAH / "bench.csv", parse_dates=["date"]).dropna(subset=["JCI"])
    bench = bench.sort_values("date").set_index("date")
    static = pd.read_csv(k.DATA_OLAH / "static.csv").set_index("ticker")
    return harga, bench, static


def ukur(harga, bench, static):
    kal = bench.index
    tri = harga.pivot_table(index="date", columns="ticker", values="tri").reindex(kal).ffill()
    px = harga.pivot_table(index="date", columns="ticker", values="px_last").reindex(kal).ffill()
    bank = [t for t in static.index[static["GICS_INDUSTRY_NAME"] == "Banks"] if t in tri.columns]
    saham = static["EQY_SH_OUT"].reindex(bank)

    baris = []
    for ev, c in k.EVENTS.items():
        t0 = int(np.searchsorted(kal, pd.Timestamp(c["hari0"])))
        d = {"event": ev, "lembaga": c["lembaga"], "jenis": c["jenis"], "plasebo": c.get("plasebo", False),
             "label": c["label"], "hari0": kal[t0] if t0 < len(kal) else pd.NaT, "catatan": c.get("catatan", "")}
        for nama, (a, b) in JENDELA.items():
            lo, hi = t0 + a - 1, t0 + b  # dari penutupan hari sebelum jendela s.d. penutupan akhir jendela
            if lo < 0 or hi >= len(kal):
                continue
            rasio = lambda s: (s.iloc[hi] / s.iloc[lo] - 1) * 100
            d[f"ihsg_{nama}"] = rasio(bench["JCI"])
            if "MXEF" in bench:
                d[f"mxef_{nama}"] = rasio(bench["MXEF"])
            if "USDIDR" in bench and bench["USDIDR"].last_valid_index() is not None and hi <= bench.index.get_loc(bench["USDIDR"].last_valid_index()):
                d[f"usdidr_{nama}"] = rasio(bench["USDIDR"])
            if "SBN10Y" in bench and bench["SBN10Y"].notna().any():
                y = bench["SBN10Y"].ffill().where(bench.index <= bench["SBN10Y"].last_valid_index())
                d[f"sbn_bp_{nama}"] = (y.iloc[hi] - y.iloc[lo]) * 100
            w = (px[bank].iloc[t0 - 1] * saham).dropna()
            rb = (tri[w.index].iloc[hi] / tri[w.index].iloc[lo] - 1).dropna()
            d[f"bank_{nama}"] = (rb * w[rb.index]).sum() / w[rb.index].sum() * 100 if len(rb) else np.nan
        d["n_bank"] = len(bank)
        baris.append(d)
    return pd.DataFrame(baris)


def label_event(r):
    t = r["hari0"]
    tgl = f"{t.day} {BULAN[t.month - 1]}" if pd.notna(t) else "?"
    return f"{r['lembaga']} · {tgl}\n{r['jenis']}" + (" · plasebo" if r["plasebo"] else "")


def grafik(df, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    w = JENDELA_GRAFIK
    df = df[df.get(f"ihsg_{w}").notna()].reset_index(drop=True) if f"ihsg_{w}" in df else df.iloc[0:0]
    if df.empty:
        print("Belum ada event dengan jendela lengkap; grafik dilewati.")
        return
    ada_sbn = f"sbn_bp_{w}" in df and df[f"sbn_bp_{w}"].notna().any()
    y = np.arange(len(df))

    plt.rcParams.update({"font.size": 9, "axes.edgecolor": GRID, "axes.labelcolor": TINTA_2,
                         "xtick.color": TINTA_2, "ytick.color": TINTA, "text.color": TINTA})
    fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(11, 0.62 * len(df) + 2.2),
                                   gridspec_kw={"width_ratios": [3, 2], "wspace": 0.08})
    fig.patch.set_facecolor(PERMUKAAN)

    tebal, geser = 0.34, 0.19  # celah putih di antara dua batang satu event
    for ax in (ax1, ax2):
        ax.set_facecolor(PERMUKAAN)
        for i, p in enumerate(df["plasebo"]):
            if p:
                ax.axhspan(i - 0.5, i + 0.5, color=PITA_PLASEBO, zorder=0, lw=0)
        ax.axvline(0, color=TINTA_2, lw=0.8, zorder=2)
        ax.grid(axis="x", color=GRID, lw=0.6)
        ax.set_axisbelow(True)
        for s in ["top", "right", "left"]:
            ax.spines[s].set_visible(False)
        ax.tick_params(axis="y", length=0)

    def label_nilai(ax, ys, vals, fmt):
        rentang = np.nanmax(np.abs(ax.get_xlim()))
        for yy, v in zip(ys, vals):
            if np.isnan(v):
                continue
            ax.text(v + (0.015 * rentang if v >= 0 else -0.015 * rentang), yy, fmt.format(v),
                    va="center", ha="left" if v >= 0 else "right", fontsize=8, color=TINTA_2)

    ax1.barh(y - geser, df[f"ihsg_{w}"], height=tebal, color=WARNA["IHSG"], label="IHSG", zorder=3)
    ax1.barh(y + geser, df[f"bank_{w}"], height=tebal, color=WARNA["Bank"],
             label="Saham bank (tertimbang kapitalisasi)", zorder=3)
    lim = np.nanmax(np.abs(df[[f"ihsg_{w}", f"bank_{w}"]].to_numpy())) * 1.25
    ax1.set_xlim(-lim, lim)
    label_nilai(ax1, y + geser, df[f"bank_{w}"].to_numpy(), "{:+.1f}")
    ax1.set_xlabel("Return hari-0 s.d. hari +1 (%)")
    ax1.set_yticks(y, [label_event(r) for _, r in df.iterrows()])
    ax1.invert_yaxis()
    ax1.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, frameon=False, fontsize=8.5)
    ax1.set_title("Saham", loc="left", fontsize=10, fontweight="bold", pad=22)

    if ada_sbn:
        v = df[f"sbn_bp_{w}"]
        ax2.barh(y, v, height=tebal, color=WARNA["SBN"], zorder=3)
        lim2 = np.nanmax(np.abs(v)) * 1.35
        ax2.set_xlim(-lim2, lim2)
        label_nilai(ax2, y, v.to_numpy(), "{:+.0f}")
    else:
        ax2.text(0.5, 0.5, "Data yield SBN belum tersedia", transform=ax2.transAxes, ha="center", color=TINTA_2)
        ax2.set_xticks([])
    ax2.set_xlabel("Perubahan yield SBN 10 tahun (bp)")
    ax2.set_title("SBN", loc="left", fontsize=10, fontweight="bold", pad=22)

    fig.suptitle("Reaksi pasar Indonesia terhadap keputusan lembaga global, 2026",
                 x=0.01, ha="left", fontsize=12, fontweight="bold")
    catatan = ("Jendela: penutupan hari sebelum pengumuman s.d. penutupan hari bursa +1. "
               "Baris berlatar abu-abu = keputusan tanpa perubahan (plasebo).\n"
               "Fitch (4 Mar) bersamaan dengan eskalasi konflik Timur Tengah. "
               "Tanggal: rilis resmi lembaga dan pemberitaan; detail di desain-lembaga-global.md.")
    fig.text(0.01, 0.005, catatan, fontsize=7.5, color=TINTA_2, va="bottom")
    fig.subplots_adjust(left=0.2, right=0.98, top=0.86, bottom=0.17)
    fig.savefig(path, dpi=200, facecolor=PERMUKAAN)
    plt.close(fig)


def main():
    harga, bench, static = muat()
    df = ukur(harga, bench, static)
    k.HASIL.mkdir(parents=True, exist_ok=True)
    df.to_csv(k.HASIL / "perbandingan_event.csv", index=False)

    w = JENDELA_GRAFIK
    kolom = {"lembaga": "Lembaga", "jenis": "Jenis", "label": "Keputusan", f"ihsg_{w}": "IHSG %",
             f"bank_{w}": "Bank %", f"mxef_{w}": "MSCI EM %", f"sbn_bp_{w}": "SBN 10th bp", f"usdidr_{w}": "USD/IDR %"}
    t = df.assign(hari0=df["hari0"].dt.strftime("%Y-%m-%d"))[["hari0"] + [c for c in kolom if c in df]]
    t = t.rename(columns=kolom)
    baris = ["| " + " | ".join(t.columns) + " |", "|" + "---|" * len(t.columns)]
    for r in t.itertuples(index=False):
        sel = lambda v: ("belum ada" if np.isnan(v) else f"{v:+.2f}") if isinstance(v, float) else str(v)
        baris.append("| " + " | ".join(sel(v) for v in r) + " |")
    catatan = [f"- **{r.event}**: {r.catatan}" for r in df.itertuples() if r.catatan]
    md = ["# Perbandingan reaksi pasar terhadap 8 keputusan lembaga global", "",
          f"Jendela [0,+1]: penutupan hari sebelum pengumuman s.d. penutupan hari +1. "
          f"Bank = {df['n_bank'].iloc[0]} saham GICS 'Banks', tertimbang kapitalisasi. "
          "USD/IDR positif = rupiah melemah. MSCI EM ditutup setelah BEI, jadi tidak sinkron.", "",
          *baris, "", "## Catatan per event", *catatan, "",
          "Jendela lain (hari-0 saja, [-1,+1]): `perbandingan_event.csv`. Grafik: `perbandingan_event.png`."]
    (k.HASIL / "perbandingan_event.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))
    grafik(df, k.HASIL / "perbandingan_event.png")


if __name__ == "__main__":
    main()
