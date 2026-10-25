# Riset MSCI: Terjustifikasi, dan Siapa yang Membayar?

> **Catatan arsip.** Ini draf desain awal (18 Okt 2026), sebelum cakupan diperluas ke delapan keputusan enam lembaga. Desain terbaru ada di [desain-lembaga-global.md](desain-lembaga-global.md), dan hasilnya di [../hasil/laporan-hasil.md](../hasil/laporan-hasil.md). Bagian alur kerja di bawah sudah tidak berlaku; lihat README utama.

_Dibuat 18 Okt 2026. Pemicunya pertanyaan publik: "Is there a quantitative way of measuring this?"_

## Pertanyaan riset
| # | Pertanyaan | Status |
|---|---|---|
| **C** (mulai di sini) | **Siapa yang menanggung biaya guncangan MSCI?** Apakah saham yang masuk indeks MSCI (besar, likuid, didominasi bank) turun lebih dalam daripada saham kecil yang justru menjadi sumber masalah tata kelola? Apakah penurunannya berbalik (tanda tekanan harga non-fundamental)? | Pipeline siap, tinggal data Bloomberg |
| A (fase 2) | **Apakah Indonesia memang outlier?** Ukuran *market dysfunction* yang bisa dibandingkan untuk ±24 pasar MSCI EM, termasuk Turki | Desain saja, belum ditarik |
| B (fase 3) | Apakah peringkat *Market Accessibility Review* dan keputusan reklasifikasi MSCI konsisten dengan ukuran di A? | Setelah A |

## Event
| Event | Pengumuman MSCI | Hari-0 di BEI | Catatan |
|---|---|---|---|
| E1 | 27 Jan 2026 malam WIB: keputusan free float + pembekuan rebalancing | **28 Jan 2026** | IHSG −7,35%, trading halt 13.43–14.13; halt lagi 29 Jan; jual bersih asing Rp11,24 T dalam dua hari |
| E2 | 15 Okt 2026: konsultasi reklasifikasi ke Standalone | **16 Okt 2026** | IHSG ±−11%; keputusan final paling lambat 30 Jun 2027 |

MSCI menyebut tiga alasan: kepemilikan manfaat (*beneficial ownership*) yang buram, kualitas free float yang meragukan, dan dugaan perdagangan terkoordinasi yang meluas.

## Hipotesis RQ C
- **H1 (salah sasaran):** setelah mengontrol ukuran, beta, likuiditas, dan momentum, saham anggota MSCI Indonesia turun **lebih dalam** daripada non-anggota.
- **H2:** saham dengan tata kelola lemah (free float rendah, Papan Pemantauan Khusus) **tidak** turun lebih dalam.
- **H3 (non-fundamental):** penurunan anggota MSCI pada E1 sebagian **berbalik** dalam 20–60 hari bursa (pola tekanan harga ala literatur *index inclusion*).
- **Angka utama:** porsi kerugian kapitalisasi (Rp) pada hari-0 yang ditanggung anggota MSCI dan bank, dibanding saham PPK atau free float rendah.

## Identifikasi
Masalah utama: anggota MSCI adalah saham besar dengan beta tinggi, jadi mereka bisa turun lebih dalam hanya karena pasarnya jatuh. Cara mengatasinya:
1. Kontrol **beta terhadap IHSG** dan **beta terhadap MSCI EM**, keduanya diestimasi pada hari [−250, −30].
2. **Fixed effect desil ukuran.** Bandingkan anggota dan non-anggota MSCI dengan kapitalisasi serupa. Ini perbandingan paling bersih.
3. Variabel dependen ganda: return mentah dan *abnormal return* terhadap MSCI EM (apa yang tidak dialami pasar global).
4. **Uji pembalikan** (E1): CAR[+2,+20] dan CAR[+2,+60].
5. Hari [−1,+5] di sekitar event mana pun dikeluarkan dari jendela estimasi. Uji dummy menunjukkan kenapa: tanpa langkah ini, crash E1 menggelembungkan beta anggota MSCI, dan efek E2 tampak menyusut dari −4 menjadi −1,7 pp.

**Keterbatasan yang perlu dijawab di paper:**
- Keanggotaan MSCI hampir identik dengan ukuran. M2 (FE desil ukuran) hanya teridentifikasi dari desil yang berisi anggota dan non-anggota sekaligus, jadi laporkan berapa saham yang ada di desil batas itu.
- Free float dan status PPK kini diambil per tanggal event dari Ringkasan Saham BEI (2025-2026); keanggotaan MSCI masih proksi.
- MSCI EM ditutup setelah BEI, jadi beta terhadap MSCI EM di hari yang sama tidak sinkron. Uji ketahanan: pakai return MSCI EM hari sebelumnya.

## Alur kerja
| Langkah | File | Isi |
|---|---|---|
| 1. Tarik Refinitiv di kampus | [refinitiv/panduan-tarik-data.md](refinitiv/panduan-tarik-data.md) + `refinitiv/data-refinitiv.xlsx` → `data/mentah/data-refinitiv.xlsx` | harga/TR 2025-26, 69 seri pasar, static, bobot MSCI |
| 2. Data publik BEI (browser, idx.co.id) | `data/mentah/idx/`: `harian_2020_2024.csv.gz`, `harian_2025_2026.csv.gz` (urai: `00_urai_dump_idx.py [--periode 2025]`), `ringkasan_saham.csv`, `ihsg.csv`, `uma.csv`, `suspensi.csv`, `laporan_keuangan/*.zip` (XBRL 49 bank) | harga, asing, free float, Remarks, UMA, suspensi, laporan keuangan |
| 3. Baca + gabung | `01_baca_refinitiv.py` (otomatis memanggil `01c_tambah_idx.py` dan `01b_msci_proksi.py`) → `01f_notasi_bei.py` → `01g_label_gorengan.py` → `01d_idx_harian.py` → `01e_fundamental_bank.py` | `data/olah/` |
| 4. Analisis | `02_event_study.py` → `03_perbandingan_event.py` → `04_placebo_permutasi.py` → `05_metode_lanjutan.py` → `06_heterogenitas.py` → `07_aliran_asing.py` → `08_gorengan_event.py` → `09_ketahanan.py` | `hasil/`, `hasil/lanjutan/` |
| 5. Baca hasil | `hasil/laporan-hasil.md` (rangkuman), lalu ringkasan per metode | Bersama |

Untuk uji tanpa Bloomberg: `python analisis/00_buat_data_dummy.py`. Script ini membuat `data/mentah/dummy.xlsx` dengan tata letak yang sama. Efek dummy-nya ditanam (anggota MSCI −4 pp, lalu berbalik), jadi pipeline harus menemukannya kembali.

## Fase 2 (RQ A), ringkas
Ukuran per negara-tahun dari data mingguan saham ±24 pasar EM. Rujukan literatur dicek ulang saat menulis.
- *Stock price synchronicity*, R² model pasar, sebagai proksi opasitas (Morck, Yeung & Yu 2000)
- Ilikuiditas Amihud dan porsi hari tanpa return
- Frekuensi return ekstrem dan pola *pump-and-dump*. Di sini nanti masuk **autoencoder** (setelah DLAI C1–C2) untuk mendeteksi pola harga/volume anomali.
- Distribusi free float dan konsentrasi kepemilikan

Tarikan datanya berat (ribuan saham × 24 negara). Mulai setelah C selesai supaya kuota Bloomberg tidak habis.

## Literatur yang perlu ditambah
Korpus Scopus sekarang berfokus pada kerapuhan bank, jadi cuma ±25 entri yang menyebut MSCI atau indeks. Perlu query baru: *index reclassification*, *MSCI emerging market inclusion/exclusion*, *benchmark effect*, *passive fund flows price pressure*, *index provider power*.
