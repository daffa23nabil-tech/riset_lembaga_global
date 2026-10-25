# Perluasan: Para "Penjaga Gerbang" Global, Tidak Hanya MSCI

_Draf 18 Okt 2026. Tanggal event berasal dari berita dan belum dicek ke rilis resmi tiap lembaga._

## Pertanyaan
Lembaga global yang menilai Indonesia ada dua jenis:
- **Lembaga rating** menilai **risiko kredit** negara. Keputusannya membawa *informasi fundamental*.
- **Penyedia indeks** menilai **aksesibilitas pasar**. Keputusannya memicu *jual-beli mekanis* oleh dana pasif.

> **RQ:** Apakah pasar, dan khususnya bank, bereaksi berbeda terhadap kedua jenis keputusan ini? Apakah keputusan penyedia indeks, yang bukan soal fundamental, justru memukul lebih keras daripada keputusan lembaga rating?

Kalau ya, ini sejalan dengan pertanyaan di tweet: penyedia indeks punya kekuatan seperti regulator tanpa akuntabilitas yang setara.

## Kriteria sampel (alasan inklusi)
Sebuah lembaga masuk sampel jika memenuhi **ketiga** syarat:

1. **Keputusannya terkunci di aturan investasi.** Ada saluran mekanis yang memaksa dana bergerak, bukan sekadar opini:
   - Penyedia indeks: dana pasif wajib mengikuti komposisi indeks.
   - Lembaga rating: batas *investment grade* di mandat investor, bobot risiko Basel, dan syarat agunan bank sentral merujuk ke rating mereka.
2. **Dominan secara global.** Indeksnya menjadi acuan utama untuk kelas aset Indonesia, atau rating-nya dipakai di mandat dan regulasi.
3. **Ada keputusan bertanggal soal Indonesia** dalam periode data (Jan 2025–Okt 2026).

| Lembaga | Jenis | Aset | Syarat 1 | Syarat 2 | Syarat 3 | Masuk? |
|---|---|---|---|---|---|---|
| **MSCI** | Indeks | Saham | Ya, acuan utama dana pasif EM | Ya | Ya: 28 Jan, 16 Okt 2026 | **Ya** |
| **FTSE Russell** | Indeks | Saham | Ya | Ya, acuan EM kedua terbesar | Ya: penundaan Feb 2026, status dipertahankan 6 Okt 2026 | **Ya** |
| **J.P. Morgan GBI-EM** | Indeks | Obligasi (SBN) | Ya, acuan utama obligasi EM mata uang lokal | Ya | Ya: batas bobot 10→9%, bertahap semester I 2026 | **Ya** (sisi SBN) |
| **Moody's** | Rating | Negara | Ya | Ya, Big 3 menguasai ±95% pasar rating | Ya: outlook negatif 5 Feb 2026 | **Ya** |
| **Fitch** | Rating | Negara | Ya | Ya | Ya: outlook negatif 4 Mar 2026 | **Ya** |
| **S&P** | Rating | Negara | Ya | Ya | Ya: afirmasi BBB stabil 13 Jul 2026 | **Ya** (event tanpa perubahan) |
| R&I, JCR (Jepang) | Rating | Negara | Lemah, jarang dirujuk mandat global | Tidak | — | Tidak |
| S&P DJI, indeks saham Bloomberg | Indeks | Saham | Lemah, dana pasif EM yang mengikuti kecil | Tidak | — | Tidak |
| Pefindo | Rating | Domestik | — | Bukan lembaga global | — | Tidak |

Lembaga lain cukup disebut di bagian keterbatasan sebagai "tidak memenuhi syarat 1 atau 2". Itu sudah menjawab kenapa tidak semua lembaga dimasukkan.

## Daftar event (dicek 18 Okt 2026; dipakai di `analisis/konfigurasi.py`)
Hari-0 = hari bursa BEI pertama yang bisa bereaksi terhadap pengumuman.

| # | Pengumuman | Hari-0 | Lembaga | Keputusan | Status verifikasi |
|---|---|---|---|---|---|
| 1 | 27 Jan 2026 malam WIB | 28 Jan | MSCI | Pembekuan rebalancing, isu free float | Pasti: IHSG −7,35%, halt |
| 2 | 5 Feb 2026 | **6 Feb** | Moody's | Baa2, outlook stabil → negatif | Pasti: pasar bereaksi Jumat 6 Feb (IHSG −2,1%, yield 10 th +11 bp) |
| 3 | Notice 9 Feb 2026 | 10 Feb | FTSE | Tunda review Maret | Sedang: satu sumber menyebut 29 Jan. IHSG justru naik 1,24% (sudah diantisipasi) |
| 4 | Rilis bertanggal 3 Mar 2026 | 4 Mar | Fitch | BBB, outlook stabil → negatif | Pasti untuk reaksi (IHSG −4,57% pada 4 Mar), tapi **tercampur** eskalasi konflik Timur Tengah di hari yang sama |
| 5 | 22–23 Apr 2026 | 23 Apr | J.P. Morgan | Batas bobot GBI-EM 10→9% + Filipina & Saudi masuk Jan 2027 | Sedang: batas 9% sudah bocor Sep 2025; cek tanggal rilis JPM |
| 6 | 13 Jul 2026 | 13 Jul | S&P | Afirmasi BBB stabil (**plasebo**) | Tanggal pasti; jam rilis belum pasti (jendela [0,+1] menangkap keduanya) |
| 7 | 6 Okt 2026, setelah tutup AS | 7 Okt | FTSE | Tetap Secondary Emerging, tidak masuk Watch List (**plasebo**) | Pasti (notice resmi LSEG) |
| 8 | 15 Okt 2026 | 16 Okt | MSCI | Konsultasi turun ke Standalone | Pasti: IHSG ±−11% |

**Event yang sengaja tidak dimasukkan** (alasannya ditulis di paper):
- FTSE interim 7–8 Apr 2026 (status dipertahankan): tercampur gencatan senjata AS–Iran di hari yang sama.
- FTSE 13 Mei dan Sep 2026 (penghapusan saham HSC / 29 saham): keputusan **tingkat saham**, bukan vonis tingkat negara.
- Bocoran batas J.P. Morgan Sep 2025: dipakai sebagai uji ketahanan untuk event 5.

**Tumpang-tindih yang terdeteksi otomatis oleh pipeline:**
- Jendela pembalikan MSCI Jan (`car_2_20`, `car_2_60`) memuat Moody's (hari +7), FTSE (hari +9), dan Fitch (hari +25).
- Jadi H3 (pembalikan) untuk E1 tidak bisa dibaca sebagai efek MSCI murni. Untuk brief, cukup pakai jendela [0,+5].

**Kontras yang paling menarik:** FTSE (±6 Okt) dan MSCI (15 Okt) menilai pasar yang sama dalam rentang 9 hari, tapi vonisnya berlawanan. Itu versi "di dalam Indonesia" dari pertanyaan Turki di tweet tadi.

## Desain: uji sidik jari (fingerprint)
Event-nya hanya ±8, jadi kekuatan analisis tidak berasal dari banyaknya event. Kekuatannya dari **pola lintas saham di dalam tiap event**. Tiap jenis lembaga meninggalkan "sidik jari" berbeda:

| Jika keputusannya... | Yang memprediksi saham mana jatuh lebih dalam | Pola setelahnya |
|---|---|---|
| Informasi kredit (rating) | Eksposur ke risiko negara: kepemilikan SBN bank, ketergantungan dana asing, sensitivitas ke rupiah | Bertahan (tidak berbalik) |
| Mekanika indeks | Bobot di indeks dan kepemilikan pasif/asing, **bukan** fundamental | Berbalik sebagian |

Regresi yang sama dijalankan untuk tiap event. Lalu bandingkan koefisien mana yang signifikan di event rating dan mana yang signifikan di event indeks. Event plasebo (S&P Jul, FTSE Okt) seharusnya tidak menunjukkan pola apa pun.

## Data tambahan
| Data | Untuk | Sumber |
|---|---|---|
| Keanggotaan FTSE Indonesia per event | Event FTSE | Refinitiv (FTSE Russell ada di LSEG) |
| Kepemilikan SBN dan dana asing per bank | Sidik jari rating | Laporan keuangan bank / OJK |
| Yield SBN 10 tahun harian + kepemilikan asing SBN | Sisi obligasi (J.P. Morgan, rating) | Refinitiv + DJPPR |
| Harga saham | Semua event | **Sudah termasuk** di tarikan Jan 2025–Okt 2026 |

## Risiko desain yang harus ditangani
- **Event berdekatan.** Moody's (5 Feb) jatuh di hari +6 setelah MSCI E1, jadi jendela pembalikan E1 tercemar. Jendela pembalikan perlu dipotong sebelum event berikutnya, atau hasilnya dilaporkan dengan catatan.
- **Antisipasi.** Outlook rating dan batas bobot J.P. Morgan sudah bisa diduga jauh hari, jadi reaksi di hari-0 bisa kecil. Pakai **tanggal pengumuman**, bukan tanggal efektif, dan akui bahwa reaksi kecil tidak berarti tidak ada efek.
- **Jam pengumuman.** Lembaga global sering mengumumkan setelah BEI tutup. Hari-0 = hari bursa pertama setelah pengumuman, jadi jam tiap event perlu dicek.
