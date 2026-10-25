"""Skenario: berapa jual paksa bila MSCI benar-benar mengeluarkan Indonesia dari Emerging Markets (keputusan final
paling lambat Juni 2027), siapa yang menanggungnya, dan berapa lama pasar menyerapnya.

Asumsi (semua dapat diganti di SKENARIO):
- Total dana yang keluar (US$ miliar). Pasif: estimasi Goldman Sachs US$5,6 miliar bila Indonesia keluar penuh dari
  MSCI (NST, 16 Okt 2026). Skenario rendah memakai US$3,25 miliar (estimasi lain yang dilaporkan media, belum kami
  verifikasi ke riset aslinya). Aktif: dana aktif berpatokan MSCI memegang > US$8 miliar (Goldman, NST); diasumsikan
  sebagian (25-50%) ikut menjual.
- Pembagian ke saham mengikuti bobot iShares MSCI Indonesia ETF (EIDO, proksi indeks MSCI Indonesia IMI) per 21 Okt 2026.
- Kurs JISDOR 23 Okt 2026.
- Dampak harga: multiplier IV E2 (jual bersih 1% saham beredar -> harga sekitar -10%), dari 05_metode_lanjutan.py.
  Ini ekstrapolasi linear dari guncangan dua hari; untuk jual yang tersebar berminggu-minggu dampaknya bisa jauh lebih
  kecil, jadi angka harga dibaca sebagai batas atas kasar, bukan ramalan.

Output: hasil/lanjutan/{skenario_jual_paksa.csv, skenario_jual_paksa_saham.csv, skenario_jual_paksa.png,
        ringkasan_skenario_jual_paksa.md}
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

import konfigurasi as k

OUT = k.HASIL / "lanjutan"
TANGGAL = "2026-10-23"
SKENARIO = {  # nama: (pasif US$ mlr, aktif US$ mlr)
    "Rendah: pasif saja (US$3,25 mlr)": (3.25, 0.0),
    "Tengah: pasif Goldman (US$5,6 mlr)": (5.6, 0.0),
    "Tinggi: pasif + 25% dana aktif": (5.6, 2.0),
    "Sangat tinggi: pasif + 50% dana aktif": (5.6, 4.0),
}


def muat():
    eido = pd.read_csv(k.DATA_MENTAH / "eido_holdings_20261021.csv", comment="#")
    eido["w"] = eido["bobot"] / eido["bobot"].sum()
    h = pd.read_csv(k.DATA_MENTAH / "idx" / "harian_2025_2026.csv.gz", parse_dates=["date"],
                    usecols=["date", "ticker", "close", "value", "listed_shares", "weight_for_index"])
    akhir = h[h["date"] == TANGGAL].set_index("ticker")
    pra = h[(h["date"] >= "2026-07-01") & (h["date"] < "2026-10-15")]
    adv = pra.groupby("ticker")["value"].mean().rename("adv_rp")  # rata-rata nilai transaksi harian sebelum E2
    jisdor = pd.read_csv(k.DATA_MENTAH / "jisdor.csv", comment="#", parse_dates=["date"]).set_index("date")["jisdor"]
    iv = pd.read_csv(OUT / "iv.csv").query("event == 'E2' and jendela == 'hari-0'")["multiplier_iv"].iloc[0]
    st = pd.read_csv(k.DATA_OLAH / "static.csv").set_index("ticker")
    bank = set(st.index[st["GICS_INDUSTRY_NAME"] == "Banks"])
    return eido, akhir, adv, float(jisdor.loc[TANGGAL]), iv, bank


def main():
    eido, akhir, adv, kurs, iv, bank = muat()
    d = eido.set_index("ticker").join(akhir[["close", "listed_shares", "weight_for_index"]]).join(adv)
    d["bank"] = d.index.isin(bank)
    ring, rinci = [], []
    for nama, (pasif, aktif) in SKENARIO.items():
        total_rp = (pasif + aktif) * 1e9 * kurs
        x = d.assign(jual_rp=d["w"] * total_rp)
        x["jual_lembar"] = x["jual_rp"] / x["close"]
        x["pct_beredar"] = x["jual_lembar"] / x["listed_shares"] * 100
        x["pct_free_float"] = x["jual_lembar"] / x["weight_for_index"] * 100
        x["hari_adv"] = x["jual_rp"] / x["adv_rp"]
        x["dampak_harga_pct"] = (iv * x["pct_beredar"]).clip(lower=-50)  # batas atas kasar, linear
        x["skenario"] = nama
        rinci.append(x.reset_index())
        b = x[x["bank"]]
        ring.append({"skenario": nama, "total_us$_mlr": pasif + aktif, "total_rp_T": total_rp / 1e12,
                     "porsi_bank_%": b["jual_rp"].sum() / x["jual_rp"].sum() * 100,
                     "jual_bank_rp_T": b["jual_rp"].sum() / 1e12,
                     "hari_adv_median": x["hari_adv"].median(), "hari_adv_bank_tertimbang": (b["hari_adv"] * b["w"]).sum() / b["w"].sum(),
                     "pct_beredar_bank_tertimbang": (b["pct_beredar"] * b["w"]).sum() / b["w"].sum(),
                     "dampak_harga_bank_tertimbang_%": (b["dampak_harga_pct"] * b["w"]).sum() / b["w"].sum()})
    ring = pd.DataFrame(ring)
    rinci = pd.concat(rinci, ignore_index=True)
    ring.to_csv(OUT / "skenario_jual_paksa.csv", index=False)
    rinci.to_csv(OUT / "skenario_jual_paksa_saham.csv", index=False)
    pembanding_e2 = pd.read_csv(OUT / "pembeli_e2_harian.csv", parse_dates=["date"])
    jual_e2_bank = -pembanding_e2.loc[pembanding_e2["date"] >= "2026-10-16", "asing_net_bank_rp_T"].sum()

    tengah = rinci[rinci["skenario"] == list(SKENARIO)[1]].sort_values("jual_rp", ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(8, 4.4))
    ax.barh(tengah["ticker"][::-1], tengah["jual_rp"][::-1] / 1e12,
            color=["#2f6db5" if b else "#b8b8b8" for b in tengah["bank"][::-1]])
    for i, (v, hh) in enumerate(zip(tengah["jual_rp"][::-1] / 1e12, tengah["hari_adv"][::-1])):
        ax.text(v + 0.2, i, f"Rp{v:.1f} T · {hh:.0f} hari transaksi".replace(".", ","), va="center", fontsize=9)
    ax.set_xlabel("Perkiraan jual paksa, Rp triliun (skenario tengah, US$5,6 miliar)")
    ax.set_title("Jika MSCI mengeluarkan Indonesia: 10 saham dengan jual paksa terbesar (biru = bank)")
    ax.set_xlim(0, tengah["jual_rp"].max() / 1e12 * 1.45)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "skenario_jual_paksa.png", dpi=150)
    plt.close(fig)

    print(ring.round(2).to_string(index=False))
    print(f"Pembanding: jual bersih asing di bank 16-23 Okt = Rp{jual_e2_bank:.1f} T; kurs {kurs:,.0f}; multiplier IV {iv:.1f}")
    print(tengah[["ticker", "w", "jual_rp", "pct_beredar", "pct_free_float", "hari_adv", "dampak_harga_pct"]].round(3).to_string(index=False))

    fmt = lambda v, n=1: f"{v:,.{n}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    teks = ["# Skenario jual paksa bila MSCI mengeluarkan Indonesia", "",
            f"Kurs JISDOR {TANGGAL}: Rp{fmt(kurs, 0)}/US$. Pembagian per saham mengikuti bobot EIDO (proksi MSCI Indonesia IMI). "
            f"Dampak harga = multiplier IV E2 ({fmt(iv)} per 1% saham beredar) x porsi saham yang dijual: ekstrapolasi linear, "
            "batas atas kasar.", "",
            "| Skenario | Total (US$ mlr) | Total (Rp T) | Porsi bank | Jual di bank (Rp T) | Hari transaksi (median saham) | "
            "Hari transaksi (bank, tertimbang) | % saham beredar bank | Dampak harga bank (batas atas) |", "|---|---|---|---|---|---|---|---|---|"]
    for r in ring.itertuples():
        teks.append(f"| {r.skenario} | {fmt(getattr(r, '_2'), 2)} | {fmt(r.total_rp_T)} | {fmt(getattr(r, '_4'), 0)}% | {fmt(r.jual_bank_rp_T)} | "
                    f"{fmt(r.hari_adv_median)} | {fmt(r.hari_adv_bank_tertimbang)} | {fmt(r.pct_beredar_bank_tertimbang, 2)}% | "
                    f"{fmt(getattr(r, '_9'))}% |")
    teks += ["", f"Pembanding: dalam enam hari setelah konsultasi E2, asing sudah menjual bersih saham bank Rp{fmt(jual_e2_bank)} T.", "",
             "![skenario](skenario_jual_paksa.png)", "",
             "Sumber estimasi: Goldman Sachs via New Straits Times, 16 Okt 2026 (pasif US$5,6 miliar; dana aktif > US$8 miliar). "
             "Skenario rendah US$3,25 miliar dari laporan media yang belum diverifikasi ke riset aslinya."]
    (OUT / "ringkasan_skenario_jual_paksa.md").write_text("\n".join(teks), encoding="utf-8")


if __name__ == "__main__":
    main()
