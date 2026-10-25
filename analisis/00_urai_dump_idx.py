"""Mengurai file hasil tarikan Ringkasan Saham BEI (dump teks dari browser) menjadi CSV.

Pemakaian: python 00_urai_dump_idx.py [--periode 2020|2023|2025] <file_dump> [...]
Tiap dump berisi blok 'YYYYMMDD\\n<baris CSV>' yang dipisah '\\n#\\n'.
  periode 2020 (9 kolom) : ticker,close,prev,volume,value,foreign_buy,foreign_sell,listed_shares,weight_for_index
  periode 2025 (16 kolom): + open, high, low, frequency, tradeable_shares, nonregular_volume, remarks
  periode 2023 (16 kolom): sama dengan 2025, untuk Okt 2023-Des 2024 (periode berlabel UMA/suspensi)
Hasil potongan disimpan ke data/mentah/idx/potongan[_2023|_2025]/, lalu semua potongan digabung menjadi
data/mentah/idx/harian_2020_2024.csv.gz, harian_2023_2024_lengkap.csv.gz, atau harian_2025_2026.csv.gz.
"""
import io
import json
import sys
from pathlib import Path

import pandas as pd

import konfigurasi as k

DIR = k.DATA_MENTAH / "idx"
PERIODE = {
    "2020": {"kolom": ["ticker", "close", "prev", "volume", "value", "foreign_buy", "foreign_sell", "listed_shares",
                       "weight_for_index"],
             "potongan": "potongan", "keluaran": "harian_2020_2024.csv.gz"},
    "2025": {"kolom": ["ticker", "close", "prev", "open", "high", "low", "volume", "value", "frequency", "foreign_buy",
                       "foreign_sell", "listed_shares", "tradeable_shares", "weight_for_index", "nonregular_volume",
                       "remarks"],
             "potongan": "potongan_2025", "keluaran": "harian_2025_2026.csv.gz"},
}
# Okt 2023-Des 2024 dengan 16 kolom yang sama: fitur lengkap untuk periode berlabel UMA/suspensi (Gorengan Radar)
PERIODE["2023"] = {**PERIODE["2025"], "potongan": "potongan_2023", "keluaran": "harian_2023_2024_lengkap.csv.gz"}


def baca_dump(path):
    """Dump teks biasa (tarik_bei/ringkasan_saham.js) atau dump yang dibungkus JSON [{"type":"text","text":...}]."""
    teks = open(path, encoding="utf-8").read()
    if teks.lstrip().startswith("["):  # dump plain selalu diawali tanggal YYYYMMDD
        teks = json.loads(teks)[0]["text"].lstrip()
        if teks.startswith('"'):
            teks, _ = json.JSONDecoder().raw_decode(teks)
    return teks


def urai(path, kolom):
    teks = baca_dump(path)
    frames = []
    for blok in teks.split("\n#\n"):
        baris = blok.strip().split("\n")
        if len(baris) < 2:
            continue
        df = pd.read_csv(io.StringIO("\n".join(baris[1:])), header=None, names=kolom, dtype={"remarks": str})
        df.insert(0, "date", pd.to_datetime(baris[0].strip()))
        frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def main(args):
    periode = "2020"
    if args[:1] == ["--periode"]:
        periode, args = args[1], args[2:]
    cfg = PERIODE[periode]
    (DIR / cfg["potongan"]).mkdir(parents=True, exist_ok=True)
    for p in args:
        df = urai(p, cfg["kolom"])
        if df.empty:
            print(f"{Path(p).name}: kosong")
            continue
        nama = f"{df['date'].min():%Y%m%d}_{df['date'].max():%Y%m%d}.csv.gz"
        df.to_csv(DIR / cfg["potongan"] / nama, index=False)
        print(f"{nama}: {df['date'].nunique()} hari, {len(df):,} baris")
    semua = pd.concat([pd.read_csv(f, parse_dates=["date"], dtype={"remarks": str})
                       for f in sorted((DIR / cfg["potongan"]).glob("*.csv.gz"))])
    semua = semua.drop_duplicates(["date", "ticker"]).sort_values(["date", "ticker"])
    semua.to_csv(DIR / cfg["keluaran"], index=False)
    print(f"Gabungan: {semua['date'].nunique()} hari, {semua['date'].min():%Y-%m-%d} s.d. {semua['date'].max():%Y-%m-%d}")


if __name__ == "__main__":
    main(sys.argv[1:])
