"""Menambahkan data publik BEI (Ringkasan Saham harian) ke data/olah/ hasil Refinitiv.

Sumber: data/mentah/idx/ringkasan_saham.csv (hari-hari jendela event), harian_2025_2026.csv.gz (semua hari
bursa 2025-2026, bila ada) dan ihsg.csv (diambil dari idx.co.id).
1. harga.csv.gz: hari setelah data Refinitiv berakhir ditambahkan; total return disambung dari close/previous.
2. bench.csv   : IHSG untuk hari yang belum ada.
3. ff_event.csv: free float per tanggal snapshot event = WeightForIndex / ListedShares (versi BEI, per tanggal).
4. asing_event.csv: jual-beli asing per saham per hari (lembar dan rupiah), untuk bukti mekanisme.
   Dengan harian_2025_2026 tersedia, berkas ini mencakup semua hari bursa 2025-2026, bukan hanya jendela event.
"""
import pandas as pd

import konfigurasi as k

DIR = k.DATA_MENTAH / "idx"


KOLOM = ["date", "ticker", "close", "prev", "volume", "value", "foreign_buy", "foreign_sell", "listed_shares",
         "weight_for_index"]


def ringkasan_bei():
    """Gabungan ringkasan saham BEI: jendela event + riwayat harian 2025-2026 (riwayat menang bila tumpang tindih)."""
    rs = pd.read_csv(DIR / "ringkasan_saham.csv", parse_dates=["date"])[KOLOM]
    harian = DIR / "harian_2025_2026.csv.gz"
    if harian.exists():
        h = pd.read_csv(harian, parse_dates=["date"], usecols=KOLOM)
        rs = pd.concat([h, rs[~rs["date"].isin(h["date"].unique())]], ignore_index=True)
    return rs.sort_values(["ticker", "date"])


def main():
    rs = ringkasan_bei()
    harga = pd.read_csv(k.DATA_OLAH / "harga.csv.gz", parse_dates=["date"])
    bench = pd.read_csv(k.DATA_OLAH / "bench.csv", parse_dates=["date"])

    # 1. sambung harga: data BEI menimpa semua hari sejak POTONG (tarikan Refinitiv terakhir dilakukan
    #    saat bursa belum tutup, sehingga hari itu bisa kosong/parsial), disambung dari hari sebelumnya.
    POTONG = pd.Timestamp("2026-10-19")
    harga = harga[harga["date"] < POTONG]
    terakhir = harga.dropna(subset=["px_last"]).sort_values("date").groupby("ticker").tail(1).set_index("ticker")
    baru = []
    for t, g in rs[rs["date"] >= POTONG].groupby("ticker"):
        if t not in terakhir.index:
            continue
        g = g.sort_values("date")
        tri = terakhir.at[t, "tri"]
        for row in g.itertuples(index=False):
            if pd.notna(tri) and row.prev and row.prev > 0:
                tri = tri * row.close / row.prev
            baru.append({"date": row.date, "ticker": t, "px_last": row.close, "px_volume": row.volume, "tri": tri})
    if baru:
        harga = pd.concat([harga, pd.DataFrame(baru)], ignore_index=True).sort_values(["ticker", "date"])
        harga.to_csv(k.DATA_OLAH / "harga.csv.gz", index=False)

    # 2. IHSG untuk hari yang belum ada di bench
    ihsg = pd.read_csv(DIR / "ihsg.csv", parse_dates=["date"])
    tambah = ihsg[ihsg["date"] > bench.dropna(subset=["JCI"])["date"].max()]
    bench = bench[~bench["date"].isin(tambah["date"])]
    if len(tambah):
        bench = pd.concat([bench, tambah], ignore_index=True).sort_values("date")
    # yield yang persis sama dengan hari bursa sebelumnya = kuotasi tidak diperbarui (basi), bukan perubahan 0 bp
    basi = 0
    for c in [c for c in bench.columns if c == "SBN10Y" or c.startswith("Y10_")]:
        s = bench[c]
        sama = s.notna() & (s == s.ffill().shift(1))
        basi += int(sama.sum())
        bench.loc[sama, c] = float("nan")
    bench.to_csv(k.DATA_OLAH / "bench.csv", index=False)
    print(f"Yield basi dikosongkan: {basi} titik")

    # 3. free float per tanggal snapshot event (versi BEI)
    rs["free_float"] = rs["weight_for_index"] / rs["listed_shares"].where(rs["listed_shares"] > 0) * 100
    ff = []
    for ev, c in k.EVENTS.items():
        snap = pd.Timestamp(f"{c.get('snapshot_msci', '')[:4]}-{c.get('snapshot_msci', '')[4:6]}-{c.get('snapshot_msci', '')[6:]}") \
            if "snapshot_msci" in c else pd.Timestamp(c["hari0"]) - pd.offsets.BDay(1)
        sebelum = rs[rs["date"] <= snap]
        if sebelum.empty:
            continue
        hari = sebelum["date"].max()
        x = sebelum[sebelum["date"] == hari][["ticker", "free_float"]].assign(event=ev, tanggal=hari)
        ff.append(x)
    if ff:
        pd.concat(ff).to_csv(k.DATA_OLAH / "ff_event.csv", index=False)

    # 4. jual-beli asing per saham per hari
    rs["asing_bersih_lembar"] = rs["foreign_buy"] - rs["foreign_sell"]
    rs["asing_bersih_rp"] = rs["asing_bersih_lembar"] * rs["close"]
    rs["asing_jual_porsi_volume"] = rs["foreign_sell"] / rs["volume"].where(rs["volume"] > 0)
    rs[["date", "ticker", "close", "volume", "value", "foreign_buy", "foreign_sell", "asing_bersih_lembar",
        "asing_bersih_rp", "asing_jual_porsi_volume", "free_float", "listed_shares"]].to_csv(k.DATA_OLAH / "asing_event.csv", index=False)

    print(f"BEI: +{len(baru)} baris harga, +{len(tambah)} hari IHSG, free float {len(ff)} event, "
          f"jual-beli asing {rs['date'].nunique()} hari ({rs['date'].min():%Y-%m-%d} s.d. {rs['date'].max():%Y-%m-%d})")


if __name__ == "__main__":
    main()
