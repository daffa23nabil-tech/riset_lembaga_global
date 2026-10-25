"""Menyambung riwayat harian BEI 2020-2024 (Ringkasan Saham publik) ke data harga Refinitiv (2025-sekarang),
dan membuat proksi keanggotaan MSCI Indonesia untuk setiap snapshot review (dipakai uji placebo).

Input : data/mentah/idx/harian_2020_2024.csv.gz  (date,ticker,close,prev,volume,value,foreign_buy,
        foreign_sell,listed_shares,weight_for_index), opsional harian_2025_2026.csv.gz (free float 2025-2026),
        data/olah/harga.csv.gz, msci (Refinitiv: jumlah anggota).
Output: harga.csv.gz diperpanjang ke 2020; ff_harian.csv.gz (2020-2026); msci_proksi_hist.csv (snapshot,ticker).

Return BEI = close/prev - 1 (prev BEI sudah disesuaikan untuk stock split); dividen tidak termasuk.
Sambungan: level lama diskalakan sehingga return hari pertama Refinitiv (2 Jan 2025) = return BEI hari itu.
"""
import importlib.util

import numpy as np
import pandas as pd

import konfigurasi as k

MULAI_REFINITIV = pd.Timestamp("2025-01-01")


def main():
    src = k.DATA_MENTAH / "idx" / "harian_2020_2024.csv.gz"
    idx = pd.read_csv(src, parse_dates=["date"]).sort_values(["ticker", "date"])
    idx = idx[idx["date"] < MULAI_REFINITIV]
    idx["r"] = (idx["close"] / idx["prev"].where(idx["prev"] > 0) - 1).fillna(0.0)
    idx["lvl"] = idx.groupby("ticker")["r"].transform(lambda r: (1 + r).cumprod())

    harga = pd.read_csv(k.DATA_OLAH / "harga.csv.gz", parse_dates=["date"])
    harga = harga[harga["date"] >= MULAI_REFINITIV]  # buang baris lama Refinitiv yang hanya berisi volume
    pertama = harga.dropna(subset=["tri"]).sort_values("date").groupby("ticker").head(1).set_index("ticker")
    awal = pertama["tri"]
    akhir_lama = idx.groupby("ticker")["lvl"].last()
    # level lama x (1 + return BEI di hari pertama Refinitiv) = level Refinitiv hari itu,
    # supaya return hari pertama sambungan (2 Jan 2025) tidak dipaksa nol
    baru = k.DATA_MENTAH / "idx" / "harian_2025_2026.csv.gz"
    r0 = pd.Series(0.0, index=awal.index)
    if baru.exists():
        h0 = pd.read_csv(baru, usecols=["date", "ticker", "close", "prev"], parse_dates=["date"])
        h0 = h0.merge(pertama["date"].rename("d0").reset_index(), on="ticker")
        h0 = h0[h0["date"] == h0["d0"]].set_index("ticker")
        r0 = (h0["close"] / h0["prev"].where(h0["prev"] > 0) - 1).reindex(awal.index).fillna(0.0)
    skala = (awal / (akhir_lama.reindex(awal.index) * (1 + r0))).reindex(idx["ticker"].unique())
    idx["tri"] = idx["lvl"] * idx["ticker"].map(skala)
    # saham yang tidak ada di Refinitiv 2025+ (sudah delisting) tetap disimpan dengan skala 1
    idx["tri"] = idx["tri"].fillna(idx["lvl"])
    lama = idx.rename(columns={"close": "px_last", "volume": "px_volume"})[["date", "ticker", "px_last", "px_volume", "tri"]]
    gabung = pd.concat([lama, harga], ignore_index=True).sort_values(["ticker", "date"])
    gabung.to_csv(k.DATA_OLAH / "harga.csv.gz", index=False)

    # free float harian: riwayat 2020-2024 + harian 2025-2026 (harga di sini hanya untuk kapitalisasi, bukan return)
    ffsrc = idx[["date", "ticker", "close", "listed_shares", "weight_for_index"]]
    baru = k.DATA_MENTAH / "idx" / "harian_2025_2026.csv.gz"
    if baru.exists():
        ffsrc = pd.concat([ffsrc, pd.read_csv(baru, parse_dates=["date"], usecols=list(ffsrc.columns))], ignore_index=True)
    ffsrc = ffsrc.copy()
    ffsrc["free_float"] = ffsrc["weight_for_index"] / ffsrc["listed_shares"].where(ffsrc["listed_shares"] > 0) * 100
    ffsrc[["date", "ticker", "close", "listed_shares", "free_float"]].to_csv(k.DATA_OLAH / "ff_harian.csv.gz", index=False)

    # proksi anggota MSCI per snapshot review 2020-2024: n teratas kapitalisasi free float (n dari Refinitiv)
    spec = importlib.util.spec_from_file_location("px", k.ROOT / "analisis" / "01b_msci_proksi.py")
    px = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(px)
    bobot = px.bobot_per_snapshot()
    ffsrc["ffcap"] = ffsrc["close"] * ffsrc["listed_shares"] * ffsrc["free_float"] / 100
    snap_eido = {f"{c['snapshot_msci'][:4]}-{c['snapshot_msci'][4:6]}-{c['snapshot_msci'][6:]}" for c in k.EVENTS_MSCI.values()}
    baris = []
    for snap, w in sorted(bobot.items()):
        t = pd.Timestamp(snap)
        if not w or snap in snap_eido or t < ffsrc["date"].min() or t > ffsrc["date"].max():
            continue
        hari = ffsrc.loc[ffsrc["date"] <= t, "date"].max()
        top = ffsrc[ffsrc["date"] == hari].nlargest(len(w), "ffcap")
        baris += [{"snapshot": snap, "ticker": tk} for tk in top["ticker"]]
    hist = pd.DataFrame(baris)
    # snapshot event: pakai proksi berbasis EIDO dari msci.csv (E1 = snapshot Jan 2026, E2 = snapshot Okt 2026)
    m26 = pd.read_csv(k.DATA_OLAH / "msci.csv")
    for ev, c in k.EVENTS_MSCI.items():
        snap = f"{c['snapshot_msci'][:4]}-{c['snapshot_msci'][4:6]}-{c['snapshot_msci'][6:]}"
        hist = pd.concat([hist, pd.DataFrame({"snapshot": snap, "ticker": m26.loc[m26["event"] == ev, "ticker"]})])
    hist.to_csv(k.DATA_OLAH / "msci_proksi_hist.csv", index=False)
    print(f"Riwayat BEI: {idx['ticker'].nunique()} saham, {idx['date'].min():%Y-%m-%d} s.d. {idx['date'].max():%Y-%m-%d}; "
          f"harga gabungan {gabung['date'].min():%Y-%m-%d} s.d. {gabung['date'].max():%Y-%m-%d}; "
          f"proksi MSCI {hist['snapshot'].nunique()} snapshot")


if __name__ == "__main__":
    main()
