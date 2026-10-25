"""Gorengan Radar, langkah 1: dataset jendela saham-hari untuk deep learning.

Input : data/mentah/idx/harian_2023_2024_lengkap.csv.gz + harian_2025_2026.csv.gz (Ringkasan Saham BEI, 16 kolom),
        data/olah/label_pengawasan.csv (01g: UMA dan suspensi pengawasan per hari bursa)
Output: data/olah/radar/radar.npz  - X (hari x fitur harian), S (hari x fitur statis), y, kunci, indeks jendela
        data/olah/radar/fitur.json

Satu sampel = saham i pada hari t, dibaca dari L hari bursa terakhir (t-L+1 .. t).
Label y = 1 bila saham itu terkena UMA atau suspensi Divisi Pengawasan Transaksi pada hari t+1 .. t+H
(peringatan dini). Label BEI tidak lengkap (tidak semua saham gorengan ditandai), jadi y = 0 berarti
"tidak berlabel", bukan "bersih": inilah alasan memakai PU learning di langkah 2.
Pembagian waktu (out-of-time): latih <= 30 Jun 2025, validasi Jul-Des 2025, uji 2026 (termasuk E1 dan E2).
"""
import importlib.util
import json

import numpy as np
import pandas as pd

import konfigurasi as k

L, H = 30, 5
DIR = k.DATA_OLAH / "radar"
BATAS = {"latih": "2025-06-30", "validasi": "2025-12-31"}
HARIAN = ["r", "rentang", "gap_buka", "log_nilai_rel", "log_frek_rel", "turnover", "asing_porsi", "asing_bersih",
          "nego_porsi", "tanpa_transaksi"]
STATIS = ["log_mcap", "free_float", "log_harga", "papan_utama", "papan_pengembangan", "papan_akselerasi", "papan_ppk",
          "notasi_buruk"]


def muat():
    kol = ["date", "ticker", "close", "prev", "open", "high", "low", "volume", "value", "frequency", "foreign_buy",
           "foreign_sell", "listed_shares", "weight_for_index", "nonregular_volume", "remarks"]
    fr = [pd.read_csv(k.DATA_MENTAH / "idx" / f, usecols=kol, parse_dates=["date"], dtype={"remarks": str})
          for f in ["harian_2023_2024_lengkap.csv.gz", "harian_2025_2026.csv.gz"]]
    h = pd.concat(fr).drop_duplicates(["date", "ticker"]).sort_values(["ticker", "date"]).reset_index(drop=True)
    return h[h["ticker"].str.fullmatch(r"[A-Z]{4}")]


def fitur(h):
    spec = importlib.util.spec_from_file_location("nt", k.ROOT / "analisis" / "01f_notasi_bei.py")
    nt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nt)
    n = nt.urai(h["remarks"])
    prev = h["prev"].where(h["prev"] > 0)
    dagang = h["volume"] > 0
    f = pd.DataFrame(index=h.index)
    f["r"] = (h["close"] / prev - 1).clip(-0.5, 0.5).fillna(0)
    f["rentang"] = ((h["high"] - h["low"]) / prev).where(dagang, 0).clip(0, 1).fillna(0)
    f["gap_buka"] = ((h["open"] / prev - 1).where(dagang & (h["open"] > 0), 0)).clip(-0.5, 0.5).fillna(0)
    g = h.groupby("ticker")
    lv = np.log1p(h["value"])
    lf = np.log1p(h["frequency"])
    # lonjakan relatif terhadap rata-rata 60 hari sebelumnya (tanpa hari ini: tidak bocor)
    f["log_nilai_rel"] = (lv - lv.groupby(h["ticker"]).transform(lambda s: s.shift(1).rolling(60, min_periods=10).mean())).fillna(0).clip(-10, 10)
    f["log_frek_rel"] = (lf - lf.groupby(h["ticker"]).transform(lambda s: s.shift(1).rolling(60, min_periods=10).mean())).fillna(0).clip(-10, 10)
    ffs = h["weight_for_index"].where(h["weight_for_index"] > 0)
    f["turnover"] = np.log1p((h["volume"] / ffs * 100).fillna(0)).clip(0, 6)
    vol = h["volume"].where(dagang)
    f["asing_porsi"] = ((h["foreign_buy"] + h["foreign_sell"]) / (2 * vol)).fillna(0).clip(0, 1)
    f["asing_bersih"] = ((h["foreign_buy"] - h["foreign_sell"]) / vol).fillna(0).clip(-1, 1)
    f["nego_porsi"] = (h["nonregular_volume"] / vol).fillna(0).clip(0, 1)
    f["tanpa_transaksi"] = (~dagang).astype(float)
    f["log_mcap"] = np.log((h["close"] * h["listed_shares"]).clip(lower=1))
    f["free_float"] = (h["weight_for_index"] / h["listed_shares"].where(h["listed_shares"] > 0)).fillna(0).clip(0, 1)
    f["log_harga"] = np.log(h["close"].clip(lower=1))
    for p, nama in [("Utama", "papan_utama"), ("Pengembangan", "papan_pengembangan"), ("Akselerasi", "papan_akselerasi"),
                    ("Pemantauan Khusus", "papan_ppk")]:
        f[nama] = (n["papan"] == p).astype(float)
    f["notasi_buruk"] = n["notasi_buruk"].astype(float)
    return f


def label(h):
    lab = pd.read_csv(k.DATA_OLAH / "label_pengawasan.csv", parse_dates=["date"])
    lab = lab[(lab["uma"] + lab["suspensi_was"]) > 0][["ticker", "date"]].assign(kejadian=1)
    x = h[["ticker", "date"]].merge(lab, on=["ticker", "date"], how="left")["kejadian"].fillna(0).to_numpy()
    # y_t = 1 bila ada kejadian di t+1..t+H pada saham yang sama
    y = np.zeros(len(h))
    tk = h["ticker"].to_numpy()
    for j in range(1, H + 1):
        geser = np.roll(x, -j)
        sama = np.roll(tk, -j) == tk
        sama[-j:] = False
        y = np.maximum(y, geser * sama)
    return y, x


def main():
    DIR.mkdir(parents=True, exist_ok=True)
    h = muat()
    f = fitur(h)
    y, kejadian = label(h)
    tk = h["ticker"].to_numpy()
    tgl = h["date"].to_numpy()
    # jendela valid: L hari pertama dari saham yang sama, dan t+H masih dalam data saham itu
    pos = np.arange(len(h))
    awal_ok = np.r_[np.zeros(L - 1, bool), tk[L - 1:] == tk[:-(L - 1)]]
    akhir_ok = np.r_[tk[:-H] == tk[H:], np.zeros(H, bool)]
    ok = awal_ok & akhir_ok
    t_ok = pd.to_datetime(tgl)
    bagian = np.where(t_ok <= pd.Timestamp(BATAS["latih"]), 0, np.where(t_ok <= pd.Timestamp(BATAS["validasi"]), 1, 2))
    # hari t yang sudah jadi kejadian dibuang (sudah diumumkan, bukan peringatan dini)
    ok &= kejadian == 0
    idx = pos[ok]
    X = f[HARIAN].to_numpy(np.float32)
    S = f[STATIS].to_numpy(np.float32)
    # standardisasi dengan statistik data latih saja
    latih = bagian == 0
    mu_x, sd_x = X[latih].mean(0), X[latih].std(0) + 1e-6
    mu_s, sd_s = S[latih].mean(0), S[latih].std(0) + 1e-6
    np.savez_compressed(DIR / "radar.npz", X=(X - mu_x) / sd_x, S=(S - mu_s) / sd_s, y=y.astype(np.float32),
                        idx=idx, bagian=bagian[idx], ticker=tk, tanggal=t_ok.strftime("%Y-%m-%d").to_numpy(),
                        mcap=f["log_mcap"].to_numpy(np.float32))
    json.dump({"L": L, "H": H, "harian": HARIAN, "statis": STATIS, "batas": BATAS}, open(DIR / "fitur.json", "w"), indent=1)
    for b, nama in enumerate(["latih", "validasi", "uji"]):
        m = bagian[idx] == b
        print(f"{nama:9s}: {m.sum():,} jendela, positif {y[idx][m].mean() * 100:.2f}% ({int(y[idx][m].sum())})")


if __name__ == "__main__":
    main()
