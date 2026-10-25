"""Mengurai kolom Remarks Ringkasan Saham BEI menjadi papan pencatatan, sektor IDX-IC, dan notasi khusus harian.

Input : data/mentah/idx/harian_2025_2026.csv.gz (kolom remarks, 30 karakter per saham per hari)
Output: data/olah/notasi_harian.csv.gz (date, ticker, papan, sektor_idxic, notasi, ppk, notasi_buruk)
        data/olah/ppk_event.csv        (status PPK dan notasi per saham pada hari bursa sebelum tiap event)

Posisi karakter (dicocokkan dengan daftar PPK BEI 19 Okt 2026 dan SE-00009/BEI/07-2026):
  0-1   aksi korporasi (XD = ex dividen, XR = ex right, ...)
  4     papan: 1 Utama, 2 Pengembangan, 3 Akselerasi, 4 Pemantauan Khusus, 5 Ekonomi Baru
  14    sektor IDX-IC (A Energi ... K Transportasi)
  18-29 notasi khusus: B/M pailit-PKPU, E ekuitas negatif, A/D opini tidak wajar/tidak menyatakan pendapat,
        L terlambat laporan keuangan, S tanpa pendapatan usaha, C kasus hukum, Q pembatasan usaha,
        Y belum RUPS, F/G/V sanksi OJK, P free float kurang (berlaku bertahap 2026-27), N/K/I saham MVS / Papan
        Ekonomi Baru, X Papan Pemantauan Khusus
"""
import pandas as pd

import konfigurasi as k

PAPAN = {"1": "Utama", "2": "Pengembangan", "3": "Akselerasi", "4": "Pemantauan Khusus", "5": "Ekonomi Baru"}
SEKTOR = {"A": "Energi", "B": "Barang Baku", "C": "Perindustrian", "D": "Konsumen Primer", "E": "Konsumen Non-Primer",
          "F": "Kesehatan", "G": "Keuangan", "H": "Properti", "I": "Teknologi", "J": "Infrastruktur", "K": "Transportasi"}
NOTASI_BURUK = set("BMEADLSCQYFGVP")  # tanda masalah tata kelola/keuangan (N/K/I hanya struktur saham)


def urai(rem: pd.Series) -> pd.DataFrame:
    r = rem.fillna("").str.pad(30, side="right", fillchar="-")
    notasi = r.str[18:30].str.replace("-", "", regex=False)
    out = pd.DataFrame({
        "aksi_korporasi": r.str[0:2].replace("--", ""),
        "papan": r.str[4].map(PAPAN),
        "sektor_idxic": r.str[14].map(SEKTOR),
        "notasi": notasi,
    })
    out["ppk"] = ((out["papan"] == "Pemantauan Khusus") | notasi.str.contains("X")).astype(int)
    out["notasi_buruk"] = notasi.apply(lambda s: int(bool(set(s) & NOTASI_BURUK)))
    return out


def main():
    src = k.DATA_MENTAH / "idx" / "harian_2025_2026.csv.gz"
    if not src.exists():
        print("Notasi BEI: harian_2025_2026.csv.gz belum ada, dilewati.")
        return
    h = pd.read_csv(src, usecols=["date", "ticker", "remarks"], parse_dates=["date"], dtype={"remarks": str})
    h = pd.concat([h[["date", "ticker"]], urai(h["remarks"])], axis=1)
    h.to_csv(k.DATA_OLAH / "notasi_harian.csv.gz", index=False)

    baris = []
    for ev, c in k.EVENTS.items():
        sebelum = h[h["date"] < pd.Timestamp(c["hari0"])]
        if sebelum.empty:
            continue
        hari = sebelum["date"].max()
        baris.append(sebelum[sebelum["date"] == hari].assign(event=ev, tanggal=hari))
    pe = pd.concat(baris)[["event", "tanggal", "ticker", "papan", "ppk", "notasi_buruk", "notasi"]]
    pe.to_csv(k.DATA_OLAH / "ppk_event.csv", index=False)
    ringkas = pe.groupby("event")[["ppk", "notasi_buruk"]].sum().reindex(list(k.EVENTS))
    print(f"Notasi BEI: {h['date'].nunique()} hari, {h['ticker'].nunique()} saham. PPK per event: "
          + ", ".join(f"{e} {int(r.ppk)}" for e, r in ringkas.iterrows()))


if __name__ == "__main__":
    main()
