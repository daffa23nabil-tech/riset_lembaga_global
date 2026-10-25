"""Menjalankan seluruh pipeline secara berurutan, dari data mentah sampai hasil.

Pemakaian (dari folder mana pun):
  python analisis/jalankan.py                 # tahap data + analisis inti (01-09)
  python analisis/jalankan.py --radar         # + Gorengan Radar (10-15; berjam-jam di CPU)
  python analisis/jalankan.py --dari 02       # mulai dari tahap tertentu (data olahan sudah ada)
  python analisis/jalankan.py --hanya 07 08   # tahap tertentu saja
  python analisis/jalankan.py --cek           # hanya cek berkas data mentah yang dibutuhkan

Setiap tahap adalah skrip mandiri; keluarannya dicatat ke hasil/log_jalankan.txt.
Pipeline berhenti pada tahap pertama yang gagal.
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

import konfigurasi as k

DIR = Path(__file__).resolve().parent

TAHAP = [
    # (kode, skrip, keterangan)
    ("01", "01_baca_refinitiv.py", "baca Refinitiv + sambung data BEI (01c) + proksi MSCI (01b)"),
    ("01f", "01f_notasi_bei.py", "papan, sektor, notasi khusus, PPK per event"),
    ("01g", "01g_label_gorengan.py", "label UMA/suspensi"),
    ("01d", "01d_idx_harian.py", "riwayat BEI 2020-2024, free float harian, proksi MSCI historis"),
    ("01e", "01e_fundamental_bank.py", "fundamental 49 bank dari XBRL"),
    ("01h", "01h_kepemilikan_ksei.py", "kepemilikan KSEI per tipe/klasifikasi investor"),
    ("02", "02_event_study.py", "event study lintas saham E1/E2"),
    ("03", "03_perbandingan_event.py", "perbandingan 8 event"),
    ("04", "04_placebo_permutasi.py", "placebo hari buruk + permutasi"),
    ("05", "05_metode_lanjutan.py", "synthetic control, DML, IV, LP, connectedness"),
    ("06", "06_heterogenitas.py", "causal forest + fingerprint bank"),
    ("07", "07_aliran_asing.py", "aliran asing 8 event"),
    ("08", "08_gorengan_event.py", "saham bertanda pengawasan di 8 event"),
    ("09", "09_ketahanan.py", "uji ketahanan fingerprint dan gorengan"),
    ("16", "16_pembeli_e1.py", "siapa pembeli bank saat E1 (KSEI)"),
    ("17", "17_pembeli_e2_harian.py", "pembeli bank saat E2: aliran harian + pemegang >5%"),
    ("18", "18_skenario_jual_paksa.py", "skenario jual paksa bila MSCI mengeluarkan Indonesia"),
    ("inf", "buat_infografik.py", "infografik LinkedIn"),
]
TAHAP_RADAR = [
    ("10", "10_radar_data.py", "dataset jendela saham-hari"),
    ("11", "11_radar_model.py", "pembanding klasik + Transformer BCE/nnPU"),
    ("12", "12_radar_event.py", "skor radar vs kerugian event"),
    ("13", "13_radar_ketahanan.py", "seed, prior pi, atribusi"),
    ("14", "14_radar_runup.py", "uji run-up reversal"),
    ("15", "15_radar_autoencoder.py", "autoencoder tanpa label"),
]

WAJIB = [
    ("data-refinitiv.xlsx", "Refinitiv (kampus), lihat refinitiv/panduan-tarik-data.md"),
    ("idx/ringkasan_saham.csv", "BEI Ringkasan Saham, hari jendela event"),
    ("idx/ihsg.csv", "BEI Ringkasan Indeks (IHSG setelah data Refinitiv berakhir)"),
    ("idx/harian_2020_2024.csv.gz", "BEI Ringkasan Saham 2020-2024 (00_urai_dump_idx.py --periode 2020)"),
    ("idx/harian_2025_2026.csv.gz", "BEI Ringkasan Saham 2025-2026 (00_urai_dump_idx.py --periode 2025)"),
    ("idx/uma.csv", "BEI pengumuman UMA (tarik_bei/uma_suspensi.js)"),
    ("idx/suspensi.csv", "BEI pengumuman suspensi (tarik_bei/uma_suspensi.js)"),
    ("idx/laporan_keuangan", "BEI XBRL laporan keuangan bank (tarik_bei/xbrl_bank.js)"),
    ("eido_holdings_20261021.csv", "iShares EIDO holdings (proksi konstituen MSCI)"),
    ("idx_ppk.csv", "BEI Daftar Saham, papan PPK (cadangan bila Remarks tidak ada)"),
    ("idx/kepemilikan", "KSEI via BEI, Data Kepemilikan Saham bulanan (*-tipe.xlsx, *-klasifikasi.xlsx)"),
]
WAJIB_RADAR = [("idx/harian_2023_2024_lengkap.csv.gz", "BEI Ringkasan Saham Okt 2023-2024, 16 kolom (--periode 2023)")]


def cek(radar):
    kurang = [(f, s) for f, s in WAJIB + (WAJIB_RADAR if radar else []) if not (k.DATA_MENTAH / f).exists()]
    for f, s in kurang:
        print(f"  KURANG  data/mentah/{f}  <- {s}")
    if not kurang:
        print("  Semua data mentah yang dibutuhkan ada.")
    return not kurang


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--radar", action="store_true", help="ikutkan Gorengan Radar (10-15)")
    ap.add_argument("--dari", help="kode tahap awal, mis. 02")
    ap.add_argument("--hanya", nargs="+", help="kode tahap yang dijalankan saja")
    ap.add_argument("--cek", action="store_true", help="hanya cek data mentah")
    a = ap.parse_args()
    daftar = TAHAP + (TAHAP_RADAR if a.radar or (a.hanya and any("10" <= h <= "15" for h in a.hanya)) else [])
    print("Cek data mentah:")
    lengkap = cek(a.radar)
    if a.cek:
        sys.exit(0 if lengkap else 1)
    if a.hanya:
        daftar = [t for t in daftar if t[0] in a.hanya]
    elif a.dari:
        kode = [t[0] for t in daftar]
        if a.dari not in kode:
            sys.exit(f"Tahap {a.dari} tidak dikenal. Pilihan: {', '.join(kode)}")
        daftar = daftar[kode.index(a.dari):]
    k.HASIL.mkdir(parents=True, exist_ok=True)
    log = k.HASIL / "log_jalankan.txt"
    with open(log, "w", encoding="utf-8") as f:
        for kode, skrip, ket in daftar:
            t0 = time.time()
            print(f"[{kode}] {ket} ...", end=" ", flush=True)
            f.write(f"===== [{kode}] {skrip}\n")
            f.flush()
            r = subprocess.run([sys.executable, "-W", "ignore", str(DIR / skrip)], cwd=DIR, stdout=f, stderr=subprocess.STDOUT)
            print(f"{'ok' if r.returncode == 0 else 'GAGAL'} ({time.time() - t0:.0f} dtk)")
            if r.returncode != 0:
                sys.exit(f"Berhenti di {skrip}. Lihat {log}.")
    print(f"Selesai. Log: {log}")


if __name__ == "__main__":
    main()
