"""Infografik satu halaman (1080x1350, rasio LinkedIn) untuk rilis brief Oktober.

Angka diambil dari hasil pipeline (hasil/ dan data/olah/), bukan diketik ulang, kecuali label teks.
Output: hasil/infografik_linkedin.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import konfigurasi as k

TINTA, LEMBUT, AKSEN, ABU, LATAR = "#1c2230", "#5b6272", "#2f6db5", "#a3a8b3", "#fbfaf7"
SERIF, SANS = "Georgia", "Segoe UI"


def angka():
    rug = pd.read_csv(k.HASIL / "kerugian_kelompok.csv")
    e2_rugi = -rug.query("event == 'E2' and jendela == 'car_0'")["rugi_rp_triliun"].sum()
    gor = pd.read_csv(k.HASIL / "lanjutan" / "ketahanan_gorengan.csv")
    gor = gor.query("varian == 'utama: suspensi 250 hari' and spesifikasi == 'dasar' and y == 'car_0_5'")["koef_E1"].iloc[0]
    ag = pd.read_csv(k.HASIL / "lanjutan" / "pembeli_e2_harian.csv", parse_dates=["date"])
    asing_e2 = -ag.loc[ag["date"] >= "2026-10-16", "asing_net_bank_rp_T"].sum()
    rad = pd.read_csv(k.HASIL / "lanjutan" / "radar_autoencoder.csv")
    rad = rad.query("skor == 'transformer_ensembel' and sel == 'E1 car_0_5'")["koef"].iloc[0]
    # jalur E2: IHSG dan indeks bank (bobot kapitalisasi 15 Okt), dari data olahan
    h = pd.read_csv(k.DATA_OLAH / "harga.csv.gz", parse_dates=["date"])
    h = h[h["date"] >= "2026-10-15"]
    st = pd.read_csv(k.DATA_OLAH / "static.csv").set_index("ticker")
    bank = set(st.index[st["GICS_INDUSTRY_NAME"] == "Banks"])
    ls = pd.read_csv(k.DATA_MENTAH / "idx" / "harian_2025_2026.csv.gz", usecols=["date", "ticker", "listed_shares"], parse_dates=["date"])
    sh = ls[ls["date"] == "2026-10-15"].set_index("ticker")["listed_shares"]
    px = h.pivot(index="date", columns="ticker", values="px_last")
    tri = h.pivot(index="date", columns="ticker", values="tri")
    b = [t for t in tri.columns if t in bank and t in sh.index]
    w = (px.loc["2026-10-15", b] * sh[b]).dropna()
    w = w / w.sum()
    r = tri[w.index].pct_change(fill_method=None).fillna(0)
    jalur_bank = (1 + (r * w).sum(axis=1)).cumprod() - 1
    j = pd.read_csv(k.DATA_OLAH / "bench.csv", parse_dates=["date"]).set_index("date")["JCI"]
    j = j.loc["2026-10-15":]
    jalur_ihsg = j / j.iloc[0] - 1
    return e2_rugi, gor, asing_e2, rad, jalur_bank * 100, jalur_ihsg * 100


def rp(v):
    return f"Rp{v:,.0f}".replace(",", ".")


def main():
    e2_rugi, gor, asing_e2, rad, jb, ji = angka()
    fig = plt.figure(figsize=(10.8, 13.5), dpi=100, facecolor=LATAR)
    t = lambda x, y, s, **kw: fig.text(x, y, s, color=kw.pop("color", TINTA), family=kw.pop("family", SANS), **kw)

    t(0.07, 0.945, "POLICY BRIEF  ·  OKTOBER 2026", size=13, color=AKSEN, weight="bold")
    t(0.07, 0.865, "Ketika lembaga global menghakimi\nIndonesia, siapa yang membayar?", size=33, family=SERIF, linespacing=1.15, va="bottom")
    t(0.07, 0.795, f"{rp(e2_rugi)} triliun", size=54, family=SERIF, color=AKSEN, va="bottom")
    t(0.07, 0.787, "kapitalisasi pasar saham hilang dalam sehari setelah usulan MSCI menurunkan\nIndonesia ke Standalone (16 Okt 2026)", size=14, color=LEMBUT, va="top", linespacing=1.4)

    kartu = [
        ("2–6×", "Keputusan penyedia indeks menggerakkan\nsaham jauh lebih besar daripada\nkeputusan lembaga rating."),
        (f"{gor:+.1f} pp".replace(".", ",").replace("-", "−"), "Januari: saham yang pernah di-cooling\ndown BEI tertinggal dalam 6 hari,\nlebih ekstrem dari semua hari crash biasa."),
        (f"Rp{asing_e2:.1f} T".replace(".", ","), "Oktober: asing melepas saham bank\n16–23 Okt, dan investor domestik\nyang menyerapnya."),
        (f"{rad:+.1f} pp".replace(".", ",").replace("-", "−"), "Deep learning: skor Transformer sebelum\nE1 memprediksi kerugian per simpangan\nbaku, melampaui label resmi BEI."),
    ]
    for i, (n, ket) in enumerate(kartu):
        x = 0.07 + (i % 2) * 0.45
        y = 0.655 - (i // 2) * 0.165
        fig.patches.append(matplotlib.patches.Rectangle((x - 0.012, y - 0.135), 0.42, 0.155, transform=fig.transFigure,
                                                        facecolor="white", edgecolor="#e4e1d8", linewidth=1))
        t(x + 0.008, y - 0.005, n, size=30, family=SERIF, color=TINTA, va="top")
        t(x + 0.008, y - 0.065, ket, size=12.5, color=LEMBUT, va="top", linespacing=1.4)

    ax = fig.add_axes([0.09, 0.115, 0.83, 0.2], facecolor=LATAR)
    hari = np.arange(len(ji))
    label = [f"{d.day} Okt" for d in ji.index]
    ax.plot(hari, ji.values, color=ABU, lw=2.5, ls=(0, (5, 4)), solid_capstyle="round")
    ax.plot(hari[: len(jb)], jb.values[: len(hari)], color=AKSEN, lw=3, solid_capstyle="round")
    ax.axhline(0, color="#c9c6bd", lw=1)
    ax.set_xticks(hari, label, fontsize=11, color=LEMBUT, family=SANS)
    ax.set_yticks([0, -5, -10, -15], ["0%", "−5%", "−10%", "−15%"], fontsize=11, color=LEMBUT, family=SANS)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    ax.grid(axis="y", color="#e7e4dc", lw=0.8)
    ax.text(hari[-1] + 0.15, jb.values[len(hari) - 1], f"Bank {jb.values[len(hari) - 1]:.1f}%".replace(".", ",").replace("-", "−"),
            color=AKSEN, fontsize=12, va="center", family=SANS, weight="bold")
    ax.text(hari[-1] + 0.15, ji.values[-1] + 1.4, f"IHSG {ji.values[-1]:.1f}%".replace(".", ",").replace("-", "−"),
            color=LEMBUT, fontsize=12, va="center", family=SANS)
    ax.set_xlim(-0.2, hari[-1] + 1.6)
    t(0.07, 0.335, "Setelah 16 Okt: separuh kejatuhan pulih dalam seminggu, bank tertinggal lagi", size=14, weight="bold", va="bottom")
    t(0.07, 0.318, "Perubahan kumulatif sejak penutupan 15 Okt 2026", size=12, color=LEMBUT, va="bottom")

    t(0.07, 0.045, "Daffa · Ekonomi Pembangunan, Universitas Negeri Semarang", size=12.5, weight="bold", va="bottom")
    t(0.07, 0.025, "Data: Refinitiv, Bursa Efek Indonesia, KSEI. Hasil sementara; konstituen MSCI masih proksi.", size=11, color=LEMBUT, va="bottom")
    out = k.HASIL / "infografik_linkedin.png"
    fig.savefig(out, dpi=100, facecolor=LATAR)
    print(out, f"rugi E2 {e2_rugi:.0f}, gorengan {gor:.2f}, asing E2 {asing_e2:.2f}, radar {rad:.2f}")


if __name__ == "__main__":
    main()
