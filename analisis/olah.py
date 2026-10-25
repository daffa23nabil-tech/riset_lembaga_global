"""Fungsi bersama untuk jalur Refinitiv (API maupun Excel): susun TRI dan tulis data/olah/."""
import pandas as pd

import konfigurasi as k


def ke_tanggal(s: pd.Series) -> pd.Series:
    """Tanggal dari Excel bisa berupa serial angka, datetime, atau teks ISO ('2025-01-02T00:00:00Z')."""
    angka = pd.to_numeric(s, errors="coerce")
    if angka.notna().any() and angka.notna().sum() >= s.notna().sum() * 0.9:
        return pd.to_datetime(angka, unit="D", origin="1899-12-30")
    return pd.to_datetime(s, errors="coerce", utc=True).dt.tz_localize(None).dt.normalize()


def bangun_tri(h: pd.DataFrame) -> pd.DataFrame:
    """Level total return harian. Hari dengan TR.TotalReturn (%) memakainya; hari tanpa itu
    (workbook periode lama yang hanya berisi harga) memakai perubahan harga penutupan."""
    def per_saham(g):
        g = g.sort_values("date")
        r = (pd.to_numeric(g["tr_pct"], errors="coerce") / 100).fillna(g["px_last"].ffill().pct_change(fill_method=None))
        g["tri"] = (1 + r.fillna(0)).cumprod().where(g["px_last"].notna())
        return g
    return h.groupby("ticker", group_keys=False).apply(per_saham)


def tulis(harga, bench, static, msci, sumber_msci=None):
    """harga: date,ticker,px_last,px_volume,tr_pct | bench: date,JCI,MXEF | static: ticker + FIELD_STATIS
    (EQY_SH_OUT dalam juta lembar) | msci: ticker,bobot,event."""
    k.DATA_OLAH.mkdir(parents=True, exist_ok=True)
    harga = bangun_tri(harga.drop_duplicates(["ticker", "date"]))
    harga[["date", "ticker", "px_last", "px_volume", "tri"]].sort_values(["ticker", "date"]).to_csv(
        k.DATA_OLAH / "harga.csv.gz", index=False)
    bench.sort_values("date").to_csv(k.DATA_OLAH / "bench.csv", index=False)
    static.drop_duplicates("ticker").to_csv(k.DATA_OLAH / "static.csv", index=False)
    msci.to_csv(k.DATA_OLAH / "msci.csv", index=False)

    dari_tr = harga.groupby("ticker")["tr_pct"].apply(lambda s: s.notna().any()).sum()
    print(f"harga : {harga['ticker'].nunique()} saham, {harga['date'].min():%Y-%m-%d} s.d. "
          f"{harga['date'].max():%Y-%m-%d}, TRI dari TotalReturn untuk {dari_tr} saham")
    print(f"bench : {len(bench)} hari, MSCI EM terisi {bench['MXEF'].notna().sum()} hari")
    print(f"static: {len(static)} saham, {static['EQY_FREE_FLOAT_PCT'].notna().sum()} dengan free float, "
          f"{(static['GICS_INDUSTRY_NAME'] == 'Banks').sum()} bank")
    print(f"msci  : sumber {sumber_msci}, " + ", ".join(f"{e} {n} anggota" for e, n in msci.groupby('event').size().items()))
    if msci.empty:
        print("PERINGATAN: anggota MSCI kosong. Isi data/mentah/msci_manual.csv (event,ticker,bobot) lalu jalankan ulang.")
