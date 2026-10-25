"""Siapa yang membeli ketika asing menjual bank di E1? (kepemilikan KSEI per tipe investor)

Data: posisi akhir bulan KSEI per tipe investor (01h), 28 Nov 2025 - 30 Sep 2026. Nov-Des 2025 hanya total per tipe
(lokal+asing digabung); mulai Jan 2026 lokal dan asing terpisah.
1. Perubahan kepemilikan per tipe (Rp T = perubahan lembar x rata-rata harga dua akhir bulan) di saham bank,
   anggota MSCI non-bank, dan saham lain, untuk tiap bulan. Bulan E1 = 30 Des 2025 -> 30 Jan 2026.
   Dibandingkan dengan 9 bulan lain (Nov-Des dan Jan-Feb s.d. Agu-Sep): z-skor dan peringkat.
2. Komposisi lokal/asing tiap tipe di saham bank per 30 Jan 2026 (untuk membaca apakah suatu tipe itu lokal).
3. Cek silang: perubahan kepemilikan asing KSEI per bulan vs jumlah beli-bersih asing harian BEI di bulan itu.

Output: hasil/lanjutan/{pembeli_bulanan.csv, pembeli_e1.csv, pembeli_e1.png, ringkasan_pembeli.md}
"""
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import konfigurasi as k

warnings.filterwarnings("ignore")
OUT = k.HASIL / "lanjutan"
NAMA = {"CP": "Korporasi", "FD": "Yayasan", "IB": "Lembaga keuangan", "ID": "Individu", "IS": "Asuransi",
        "MF": "Reksa dana", "OT": "Lainnya", "PF": "Dana pensiun", "SC": "Perusahaan efek"}
E1_AWAL, E1_AKHIR = "2025-12-30", "2026-01-30"


def muat():
    t = pd.read_csv(k.DATA_OLAH / "kepemilikan_tipe.csv.gz", parse_dates=["date"])
    harian = pd.concat([pd.read_csv(k.DATA_MENTAH / "idx" / f, usecols=["date", "ticker", "close", "foreign_buy", "foreign_sell"],
                                    parse_dates=["date"]) for f in ["harian_2023_2024_lengkap.csv.gz", "harian_2025_2026.csv.gz"]])
    harian = harian[harian["date"] >= "2025-11-01"].drop_duplicates(["date", "ticker"])
    static = pd.read_csv(k.DATA_OLAH / "static.csv").set_index("ticker")
    bank = set(static.index[static["GICS_INDUSTRY_NAME"] == "Banks"])
    msci = set(pd.read_csv(k.DATA_OLAH / "msci.csv").query("event == 'E1'")["ticker"])
    return t, harian, bank, msci


def harga_pada(harian, tgl):
    h = harian[harian["date"] <= pd.Timestamp(tgl)]
    return h[h["date"] == h["date"].max()].set_index("ticker")["close"]


def kelompok(tk, bank, msci):
    return np.where(pd.Series(tk).isin(bank), "Bank", np.where(pd.Series(tk).isin(msci), "MSCI non-bank", "Lainnya"))


def perubahan_bulanan(t, harian, bank, msci):
    tot = t.groupby(["date", "ticker", "tipe"])["saham"].sum().unstack("tipe").fillna(0)
    tanggal = sorted(t["date"].unique())
    baris = []
    for a, b in zip(tanggal[:-1], tanggal[1:]):
        xa, xb = tot.loc[a], tot.loc[b]
        idx = xa.index.intersection(xb.index)
        d = (xb.loc[idx] - xa.loc[idx])
        p = ((harga_pada(harian, a).reindex(idx) + harga_pada(harian, b).reindex(idx)) / 2).fillna(0)
        rp = d.mul(p, axis=0) / 1e12
        rp["kelompok"] = kelompok(idx, bank, msci)
        g = rp.groupby("kelompok").sum()
        for kel, r in g.iterrows():
            for tipe, v in r.items():
                baris.append({"awal": pd.Timestamp(a).date(), "akhir": pd.Timestamp(b).date(), "kelompok": kel,
                              "tipe": tipe, "nama_tipe": NAMA[tipe], "perubahan_rp_T": v})
    return pd.DataFrame(baris)


def ringkas_e1(bul):
    bul = bul.assign(e1=bul["awal"].astype(str) == E1_AWAL)
    out = []
    for (kel, tipe), g in bul.groupby(["kelompok", "tipe"]):
        e = g.loc[g["e1"], "perubahan_rp_T"]
        lain = g.loc[~g["e1"], "perubahan_rp_T"]
        if e.empty:
            continue
        v = float(e.iloc[0])
        out.append({"kelompok": kel, "tipe": tipe, "nama_tipe": NAMA[tipe], "e1_rp_T": v, "median_bulan_lain": lain.median(),
                    "z": (v - lain.mean()) / lain.std() if lain.std() > 0 else np.nan,
                    "peringkat_dari_atas": int((lain > v).sum() + 1), "n_bulan": len(lain) + 1})
    return pd.DataFrame(out)


def komposisi(t, bank):
    x = t[(t["date"] == E1_AKHIR) & t["ticker"].isin(bank)].groupby(["tipe", "asal"])["saham"].sum().unstack().fillna(0)
    x["porsi_asing"] = x["asing"] / (x["asing"] + x["lokal"])
    return x["porsi_asing"]


def cek_silang(t, harian):
    a = t[t["asal"] == "asing"].groupby(["date", "ticker"])["saham"].sum().unstack(0)
    tanggal = sorted(a.columns)
    baris = []
    for x, y in zip(tanggal[:-1], tanggal[1:]):
        ksei = (a[y] - a[x]).dropna()
        h = harian[(harian["date"] > x) & (harian["date"] <= y)]
        bei = (h["foreign_buy"] - h["foreign_sell"]).groupby(h["ticker"]).sum()
        j = pd.concat([ksei.rename("ksei"), bei.rename("bei")], axis=1).dropna()
        baris.append({"bulan": f"{pd.Timestamp(x):%b}->{pd.Timestamp(y):%b %Y}", "korelasi_lintas_saham": j.corr().iloc[0, 1],
                      "ksei_total_mlr_lembar": j["ksei"].sum() / 1e9, "bei_total_mlr_lembar": j["bei"].sum() / 1e9})
    return pd.DataFrame(baris)


def grafik(e1, path):
    b = e1[e1["kelompok"] == "Bank"].sort_values("e1_rp_T")
    fig, ax = plt.subplots(figsize=(8, 4.2))
    y = np.arange(len(b))
    ax.barh(y + 0.18, b["e1_rp_T"], height=0.36, color="#2f6db5", label="Des 2025 -> Jan 2026 (E1)")
    ax.barh(y - 0.18, b["median_bulan_lain"], height=0.36, color="#b8b8b8", label="Median 9 bulan lain")
    ax.set_yticks(y, b["nama_tipe"])
    ax.axvline(0, color="#666", lw=0.8)
    ax.set_xlabel("Perubahan kepemilikan saham bank, Rp triliun")
    ax.set_title("Siapa menambah dan mengurangi saham bank di bulan E1")
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def md(df, fmt="{:.2f}"):
    kol = df.columns.tolist()
    b = ["| " + " | ".join(kol) + " |", "|" + "---|" * len(kol)]
    for _, r in df.iterrows():
        b.append("| " + " | ".join(fmt.format(v) if isinstance(v, float) else str(v) for v in r) + " |")
    return "\n".join(b)


def main():
    t, harian, bank, msci = muat()
    bul = perubahan_bulanan(t, harian, bank, msci)
    bul.to_csv(OUT / "pembeli_bulanan.csv", index=False)
    e1 = ringkas_e1(bul)
    e1.to_csv(OUT / "pembeli_e1.csv", index=False)
    kom = komposisi(t, bank)
    cs = cek_silang(t, harian)
    grafik(e1, OUT / "pembeli_e1.png")
    jan = harian[(harian["date"] > E1_AWAL) & (harian["date"] <= E1_AKHIR) & harian["ticker"].isin(bank)]
    asing_bank_jan = ((jan["foreign_buy"] - jan["foreign_sell"]) * jan["close"]).sum() / 1e12
    tb = e1[e1["kelompok"] == "Bank"].sort_values("e1_rp_T", ascending=False).merge(kom.rename("porsi_asing_30jan"), left_on="tipe", right_index=True)
    print(tb.round(3).to_string(index=False))
    print(f"Beli-bersih asing di bank menurut BEI, 31 Des-30 Jan: Rp{asing_bank_jan:.1f} T")
    print(cs.round(3).to_string(index=False))
    teks = ["# Siapa yang membeli saham bank saat E1?", "",
            f"Perubahan kepemilikan KSEI per tipe investor di 49 saham bank, {E1_AWAL} -> {E1_AKHIR} (bulan E1), dalam Rp T, "
            "dibanding 9 bulan lain (Nov 2025-Sep 2026). Tipe = gabungan lokal dan asing (data 2025 tidak memisahkannya); "
            "kolom porsi asing menunjukkan seberapa asing tipe itu di saham bank per 30 Jan 2026.", "",
            f"Menurut transaksi harian BEI, asing beli-bersih saham bank Rp{asing_bank_jan:.1f} T sepanjang bulan itu.", "",
            md(tb[["nama_tipe", "e1_rp_T", "median_bulan_lain", "z", "peringkat_dari_atas", "porsi_asing_30jan"]].round(3)), "",
            "![pembeli](pembeli_e1.png)", "",
            "## Semua kelompok saham", "", md(e1.round(3)), "",
            "## Cek silang: perubahan kepemilikan asing KSEI vs beli-bersih asing BEI (lembar)", "", md(cs.round(3)), "",
            "Catatan: posisi akhir bulan menangkap seluruh bulan, bukan hanya hari E1 (28-29 Jan). Rp = lembar x rata-rata "
            "harga dua akhir bulan, jadi perubahan harga tidak dihitung sebagai beli/jual."]
    (OUT / "ringkasan_pembeli.md").write_text("\n".join(teks), encoding="utf-8")


if __name__ == "__main__":
    main()
