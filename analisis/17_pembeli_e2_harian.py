"""Siapa yang membeli saham bank saat E2? Bukti yang sudah tersedia sebelum data KSEI Oktober terbit.

1. Aliran harian BEI 12-23 Okt 2026 di 49 saham bank: beli-bersih asing (Rp T) dan cerminannya, beli-bersih
   domestik (setiap lembar yang dijual asing dibeli investor domestik), nilai transaksi, porsi asing.
2. Pemegang saham di atas 5% (KSEI via BEI, data/mentah/idx/pemegang_5persen/*lima-persen.xlsx): perubahan
   kepemilikan per pemegang di saham bank antara dua tanggal (berkas pertama: tanggal kedua di berkas itu;
   berkas terakhir: tanggal kedua di berkas itu). Hanya agregat dan nama institusi yang dilaporkan.

Output: hasil/lanjutan/{pembeli_e2_harian.csv, pemegang_5persen_bank.csv, ringkasan_pembeli_e2_harian.md}
"""
import pandas as pd

import konfigurasi as k

OUT = k.HASIL / "lanjutan"
DIR5 = k.DATA_MENTAH / "idx" / "pemegang_5persen"
AWAL, AKHIR = "2026-10-12", "2026-10-23"


def bank_set():
    st = pd.read_csv(k.DATA_OLAH / "static.csv").set_index("ticker")
    return set(st.index[st["GICS_INDUSTRY_NAME"] == "Banks"])


def aliran_harian(bank):
    h = pd.read_csv(k.DATA_MENTAH / "idx" / "harian_2025_2026.csv.gz", parse_dates=["date"],
                    usecols=["date", "ticker", "close", "value", "foreign_buy", "foreign_sell"])
    x = h[(h["date"] >= AWAL) & (h["date"] <= AKHIR)].copy()
    x["bank"] = x["ticker"].isin(bank)
    x["asing_net"] = (x["foreign_buy"] - x["foreign_sell"]) * x["close"] / 1e12
    x["asing_trx"] = (x["foreign_buy"] + x["foreign_sell"]) * x["close"] / 2 / 1e12
    x["nilai"] = x["value"] / 1e12
    g = x.groupby(["date", "bank"])[["asing_net", "asing_trx", "nilai"]].sum().unstack()
    return pd.DataFrame({
        "asing_net_bank_rp_T": g[("asing_net", True)], "domestik_net_bank_rp_T": -g[("asing_net", True)],
        "nilai_transaksi_bank_rp_T": g[("nilai", True)], "porsi_asing_transaksi_bank_%": g[("asing_trx", True)] / g[("nilai", True)] * 100,
        "asing_net_nonbank_rp_T": g[("asing_net", False)]}).reset_index()


def baca_5persen(f):
    df = pd.read_excel(f, header=None)
    tgl = [str(h).split("Per ")[-1] for h in df.iloc[2] if "Kepemilikan Per" in str(h)]
    x = df.iloc[4:].copy()
    for c in [1, 4, 10]:
        x[c] = x[c].ffill()
    angka = lambda s: pd.to_numeric(s.astype(str).str.replace(",", ""), errors="coerce").fillna(0)
    x["s1"], x["s2"] = angka(x[11]), angka(x[14])
    g = x.groupby([1, 4, 10])[["s1", "s2"]].sum().reset_index()
    g.columns = ["ticker", "pemegang", "status", "saham_1", "saham_2"]
    return g, pd.to_datetime(tgl[1], format="%d-%b-%Y")


def pemegang_besar(bank):
    berkas = sorted(DIR5.glob("*lima-persen.xlsx"))
    if len(berkas) < 2:
        return pd.DataFrame(), None, None
    (a, ta), (b, tb) = baca_5persen(berkas[0]), baca_5persen(berkas[-1])
    # nama pemegang dinormalkan supaya variasi penulisan (PT di depan/belakang, TBK) tidak terbaca sebagai beli/jual
    norm = lambda s: s.astype(str).str.upper().str.replace(r"\bPT\b|\bTBK\b|[.,]", "", regex=True).str.split().str.join(" ")
    a["kunci"], b["kunci"] = norm(a["pemegang"]), norm(b["pemegang"])
    m = a.groupby(["ticker", "kunci", "status"])["saham_2"].sum().rename("saham_awal").to_frame().join(
        b.groupby(["ticker", "kunci", "status"])["saham_2"].sum().rename("saham_akhir"), how="outer").fillna(0).reset_index()
    m = m[m["ticker"].isin(bank)]
    m["perubahan"] = m["saham_akhir"] - m["saham_awal"]
    return m, ta, tb


def main():
    bank = bank_set()
    harian = aliran_harian(bank)
    harian.to_csv(OUT / "pembeli_e2_harian.csv", index=False)
    pb, ta, tb = pemegang_besar(bank)
    pb.to_csv(OUT / "pemegang_5persen_bank.csv", index=False)
    pasca = harian[harian["date"] >= "2026-10-16"]
    berubah = pb[pb["perubahan"].abs() > 0] if not pb.empty else pb
    teks = ["# Siapa yang membeli saham bank saat E2? (sebelum data KSEI Oktober terbit)", "",
            "## Aliran harian BEI di 49 saham bank (Rp T)", "",
            "| tanggal | asing net | domestik net | nilai transaksi | porsi asing % | asing net non-bank |", "|---|---|---|---|---|---|"]
    for r in harian.itertuples():
        teks.append(f"| {r.date:%d %b} | {r.asing_net_bank_rp_T:+.2f} | {r.domestik_net_bank_rp_T:+.2f} | {r.nilai_transaksi_bank_rp_T:.2f} | "
                    f"{getattr(r, '_5'):.0f} | {r.asing_net_nonbank_rp_T:+.2f} |")
    teks += ["", f"Kumulatif 16-23 Okt: asing {pasca['asing_net_bank_rp_T'].sum():+.1f} T di bank, diserap investor domestik.", ""]
    if not pb.empty:
        teks += [f"## Pemegang di atas 5% di saham bank, {ta:%d %b} -> {tb:%d %b %Y}", "",
                 f"{len(pb)} posisi pemegang di {pb['ticker'].nunique()} bank. Posisi yang berubah: {len(berubah)} "
                 f"(total {berubah['perubahan'].abs().sum():,.0f} lembar).",
                 "Catatan: daftar KSEI ini tidak memuat pemegang pengendali beberapa bank besar (mis. BBCA, BBRI, BBNI), "
                 "jadi perilaku mereka tidak terbaca dari data ini."]
    (OUT / "ringkasan_pembeli_e2_harian.md").write_text("\n".join(teks), encoding="utf-8")
    print("\n".join(teks))


if __name__ == "__main__":
    main()
