# Data

Repo ini tidak menyertakan data. Data Refinitiv berlisensi dan tidak boleh diredistribusi, sedangkan data publik BEI berukuran ratusan MB. Berkas di bawah perlu ditaruh di `data/mentah/`; semua isi `data/olah/` dibuat ulang oleh pipeline.

Cek apa yang masih kurang: `python analisis/jalankan.py --cek`.

## Berkas mentah

| Berkas | Isi | Sumber | Cara mendapatkan |
|---|---|---|---|
| `data-refinitiv.xlsx` | total return dan harga 890 saham BEI 2025–2026, 69 seri pasar sejak 2010 (indeks, yield 10 th, kurs 13 negara EM), static, bobot MSCI | LSEG Workspace / Refinitiv Eikon Excel | Isi template `refinitiv/data-refinitiv.xlsx` dengan add-in LSEG; panduan di `refinitiv/panduan-tarik-data.md` |
| `idx/harian_2020_2024.csv.gz` | Ringkasan Saham harian 2020–2024: close, prev, volume, nilai, beli/jual asing, saham tercatat, free float | BEI, API publik `GetStockSummary` | `analisis/tarik_bei/ringkasan_saham.js` (`LENGKAP=false`), lalu `00_urai_dump_idx.py --periode 2020` |
| `idx/harian_2023_2024_lengkap.csv.gz` | sama, 16 kolom (OHLC, frekuensi, nego, Remarks), Okt 2023–Des 2024 | BEI | `ringkasan_saham.js` (`LENGKAP=true`), lalu `--periode 2023` |
| `idx/harian_2025_2026.csv.gz` | sama, 16 kolom, Jan 2025–23 Okt 2026 | BEI | `ringkasan_saham.js`, lalu `--periode 2025` |
| `idx/ringkasan_saham.csv` | hari-hari jendela event (dipakai bila riwayat harian belum ada) | BEI | turunan dari dump yang sama |
| `idx/ihsg.csv` | penutupan IHSG setelah data Refinitiv berakhir | BEI `GetIndexSummary` | `tarik_bei/ihsg.js` |
| `idx/uma.csv`, `idx/suspensi.csv` | 1.191 pengumuman UMA dan 1.926 suspensi/pembukaan, Okt 2023–Okt 2026 | BEI `GetUma`, `GetSuspension` | `tarik_bei/uma_suspensi.js` |
| `idx/laporan_keuangan/*.zip` | XBRL `instance.zip` 49 bank, Des 2025 (audit) dan Jun 2026 (TW2) | BEI `GetFinancialReport` | `tarik_bei/xbrl_bank.js` |
| `idx/kepemilikan/*-tipe.xlsx`, `*-klasifikasi.xlsx` | kepemilikan saham akhir bulan per tipe investor (Nov 2025–Sep 2026; lokal/asing mulai Jan 2026) dan per klasifikasi (Mar–Sep 2026) | KSEI, dirilis BEI | idx.co.id → Perusahaan Tercatat → Data Kepemilikan Saham (unduh berkas 'tipe' dan 'klasifikasi') |
| `idx/pemegang_5persen/*lima-persen.xlsx` | pemegang saham di atas 5% per akun, dua tanggal per berkas (15 dan 22 Okt 2026) | KSEI, dirilis BEI | idx.co.id → Perusahaan Tercatat → Data Kepemilikan Saham (berkas harian 'lima-persen') |
| `eido_holdings_20261021.csv` | kepemilikan iShares MSCI Indonesia ETF, proksi konstituen MSCI | iShares (latest holdings CSV) | unduh dari halaman produk EIDO; kolom `ticker,bobot` |
| `negara_lain/yahoo_argentina_2020_2022.csv` | harga harian ARGT, ^MERV, ARS=X, EEM 2020–2022 | Yahoo Finance (chart API) | dibaca lewat browser dari halaman finance.yahoo.com |
| `idx_ppk.csv` | daftar saham Papan Pemantauan Khusus 19 Okt 2026 | BEI Daftar Saham | cadangan; status per tanggal diambil dari kolom Remarks |
| `jisdor.csv`, `igsyc_phei.csv` | kurs JISDOR 12–23 Okt 2026; kurva SBN 10 th 22–23 Okt 2026 | Bank Indonesia; PHEI | dibaca dari halaman publik, hanya untuk pelaporan |

## Catatan kualitas

- Return BEI 2020–2024 adalah return harga (tanpa dividen); 2025–2026 memakai total return Refinitiv. Sambungan dibuat agar return 2 Jan 2025 sama dengan return BEI hari itu.
- Yield 10 tahun yang persis sama dengan hari sebelumnya dianggap kuotasi basi dan dikosongkan (`01c_tambah_idx.py`).
- Konstituen MSCI Indonesia belum tersedia dari Refinitiv (kode konstituen kembali `NULL`); keanggotaan memakai proksi kepemilikan EIDO dan kapitalisasi free float (`01b_msci_proksi.py`, `01d_idx_harian.py`).
- Label UMA/suspensi dan skor Gorengan Radar per saham hanya dipakai secara agregat dan tidak disertakan di repo.
