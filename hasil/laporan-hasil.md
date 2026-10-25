# Laporan hasil sementara — "Ketika lembaga global menghakimi Indonesia, siapa yang membayar?"

Status per 25 Okt 2026 (versi 3: data dibersihkan, + deep learning). Data saham sampai **23 Okt 2026**, jadi jendela E2 kini sampai hari +5. Ini laporan hasil analisis, belum brief.
Angka masih bisa berubah setelah daftar konstituen MSCI asli ditarik ulang di kampus. Saat ini keanggotaan MSCI memakai proksi EIDO + free-float cap.

## Perbaikan data versi 3 (25 Okt)
- **Sambungan BEI → Refinitiv:** return 2 Jan 2025 sebelumnya dipaksa nol untuk semua saham. Sekarang sama dengan return BEI hari itu.
- **Yield basi:** 4.260 titik yield 10 tahun (SBN dan 13 negara pembanding) yang persis sama dengan hari sebelumnya dikosongkan, karena itu kuotasi yang tidak diperbarui, bukan perubahan 0 bp.
  - Efek SBN pada Moody's menjadi +12 bp (sebelumnya +15) dan Fitch +9 bp. Arahnya sama, tetapi tidak lagi paling ekstrem dibanding negara pembanding (p 0,15–0,23).
- **Audit:** tidak ada duplikat. Return Refinitiv dan BEI berbeda >2 pp hanya di 0,2% saham-hari. Lonjakan ±100% hanya pada saham Rp1–2 (efek tick), dan tidak ada yang masuk sampel event.
- **Hasil saham tidak berubah:** bank, PPK, gorengan E1, aliran asing, dan fingerprint semuanya sama setelah pipeline dijalankan ulang.

## Data yang sudah masuk

| Sumber | Isi | Cakupan |
|---|---|---|
| Refinitiv (tarikan kampus 19 Okt) | harga/total return 890 saham, 69 seri pasar (13 negara EM, kurs, yield 10 th), static | 2025–16 Okt 2026 (pasar sejak 2010) |
| BEI Ringkasan Saham, riwayat | close, volume, jual/beli asing, free float | 2020-01-02 s.d. 2024-12-30 (1.211 hari) |
| **BEI Ringkasan Saham, lengkap (baru)** | + OHLC, frekuensi, saham tradeable, **Remarks** (papan, sektor IDX-IC, notasi khusus) | Okt 2023–23 Okt 2026 (729 hari bursa) |
| **BEI UMA (baru)** | 1.191 pengumuman Unusual Market Activity | Okt 2023–22 Okt 2026 |
| **BEI Suspensi (baru)** | 1.926 pengumuman (996 suspensi, 850 dari Divisi Pengawasan Transaksi) | Okt 2023–23 Okt 2026 |
| BEI XBRL laporan keuangan | 49 bank, Des 2025 dan Jun 2026 | 96 laporan |
| **BI JISDOR, PHEI IGSYC (baru)** | kurs USD/IDR; kurva yield SBN | 12–23 Okt 2026; 22–23 Okt 2026 |
| iShares EIDO holdings | proksi konstituen MSCI Indonesia | 21 Okt 2026 |

**Perbaikan penting dari data baru:**
- **Status PPK kini sesuai tanggal event.** Datanya diambil dari kolom Remarks BEI, bukan daftar 19 Okt. Saat E1 ada **181 saham PPK**, sedangkan sekarang tinggal 69. Pada 28 Sep 2026, 92 saham keluar dari PPK setelah BEI merevisi kriterianya.
- **Free float dan aliran asing kini tersedia untuk setiap hari bursa 2025–2026,** bukan hanya jendela event. Proksi MSCI untuk snapshot 2025 dihitung ulang.
- **Label pengawasan BEI (UMA dan suspensi) sudah siap** untuk uji "gorengan" dan untuk Gorengan Radar (Mar–Apr 2027).

## RQ1 — Seberapa besar? (8 event, 6 lembaga)

Synthetic control (Indonesia asli vs Indonesia tiruan dari 13 negara EM), hari-0:

| Event | IHSG | Saham bank | Yield SBN 10 th |
|---|---|---|---|
| E1 MSCI, 28 Jan 2026 (free float) | **−7,9%** (paling ekstrem dari semua donor) | **−6,6%** | +2,8 bp |
| Moody's, 6 Feb 2026 | −2,0% | −1,5% | **+12 bp** (+14 bp di hari +5; p negara 0,23) |
| FTSE, 10 Feb 2026 | +1,1% | −1,0% | −2,5 bp |
| Fitch, 4 Mar 2026 | −4,5% | −1,3% | **+9,2 bp** (p negara 0,15) |
| J.P. Morgan GBI-EM, 23 Apr 2026 | −1,7% (−6,5% di hari +5) | −0,2% (−5,9% di hari +5) | +2,0 bp |
| S&P (placebo), 13 Jul 2026 | +1,9% | +1,8% | −7,5 bp |
| FTSE (placebo), 7 Okt 2026 | 0,0% | +1,7% | −1,8 bp |
| E2 MSCI, 16 Okt 2026 (Standalone) | **−12,1%** | **−13,9%** | tidak valid* |

\*Seri SBN 10 th Refinitiv basi sejak 13 Okt. Data negara pembanding juga berhenti 16 Okt, jadi synthetic control E2 hanya valid untuk hari-0.

**Jalur E2 sampai hari +5** (buy-and-hold sejak penutupan 15 Okt):

| | 16 Okt (0) | 19 Okt (+1) | 20 Okt | 21 Okt | 22 Okt | 23 Okt (+5) |
|---|---|---|---|---|---|---|
| IHSG | −11,6% | −14,8% | −10,0% | −9,1% | −8,1% | **−7,2%** |
| Indeks bank (bobot kapitalisasi) | −13,3% | −16,5% | −10,1% | −9,0% | −8,1% | **−8,6%** |
| USD/IDR (JISDOR) | +0,6% | +0,6% | +0,3% | +0,2% | +0,6% | +0,7% |

Sekitar separuh kejatuhan pulih dalam seminggu, tetapi bank tetap tertinggal dari IHSG. Rupiah hanya melemah tipis. Kejutan E2 adalah kejutan pasar saham, bukan krisis kurs.

Kerugian kapitalisasi hari-0: E1 ≈ Rp1.226 T, E2 ≈ Rp1.097 T (Rp1.449 T dalam dua hari).

**Bacaan:** Keputusan penyedia indeks saham (MSCI) menggerakkan saham 3–6 kali lebih besar daripada lembaga rating. Lembaga rating bergerak lewat yield SBN. Event placebo tidak menunjukkan apa-apa.

## RQ2 — Siapa yang membayar?

### Hasil yang kuat (lolos ≥ 3 uji)
1. **E2: bank yang membayar.**
   - Dummy bank −1,2 pp hari-0 (p=0,039), DML −3,1 pp (p=0,03), placebo p=0,079.
   - Empat bank anggota MSCI mewakili 17% kapitalisasi, tetapi menanggung 22–23% kerugian.
   - Di [0,+5] efeknya melemah: −1,7 pp (p=0,12), karena bank ikut pulih.
2. **E1: bank justru terlindung.** +2,9 pp di [0,+1] dan +5,9 pp di [0,+5] (keduanya p<0,001; DML +3,0 pp, p=0,04).
3. **E1: saham bertata kelola lemah yang membayar (diperkuat oleh data baru).**
   - Saham PPK (status saat E1, 181 saham): **−4,7 pp di [0,+1] (p<0,001)**. Jauh lebih dalam dari hari crash biasa (placebo p=0,033).
   - Saham PPK lalu memantul +13,3 pp di [2,20] (p<0,001). Jendela ini tercemar Moody's dan FTSE.
   - Saham yang pernah di-cooling down BEI dalam setahun terakhir: **−8,0 pp di [0,+5]** (p<0,05). Lebih dalam dari 98% hari crash biasa (placebo p=0,016).
   - Kelompok ini hanya 19,7% kapitalisasi, tetapi menanggung **30,6% kerugian** [0,+1].
   - Ini cocok dengan isi keputusan E1, yaitu soal free float dan pembentukan harga.
   - **Uji ketahanan (09): sangat kuat.** Dari 6 definisi (riwayat 120/250/500 hari, UMA saja, UMA atau suspensi, intensitas) × 6 spesifikasi (FE desil ukuran, tanpa PPK, tanpa harga < Rp100, winsor 1%, regresi median, CAR abnormal), efek [0,+5] berkisar **−6,2 s.d. −12,2 pp** dan selalu p<0,001.
   - Di setiap varian, efek [0,+5] **lebih ekstrem dari seluruh 60 hari crash biasa** (p placebo = 0,016, nilai minimum yang mungkin dengan 60 hari).
   - Efek hari-0 dan [0,+1] lebih sensitif terhadap definisi: p placebo 0,02–0,25. Yang paling kuat adalah definisi UMA.

*Revisi:* versi 1 menulis "PPK −5,9 pp di [0,+5]", hasil dari daftar PPK Oktober. Dengan status PPK per tanggal, efeknya terkonsentrasi di [0,+1]. Di [0,+5] tinggal −1,8 pp (ns) karena pantulan.

### Hasil yang TIDAK kuat — jangan diklaim
- **Dummy anggota MSCI:**
  - E1 hari-0 −2,8 pp hanya muncul dengan kontrol ukuran linear. Dengan FE desil ukuran ns, dan dengan DML ns.
  - E2 tidak signifikan di semua spesifikasi, termasuk [0,+5]: +4,1 pp, ns.
- **Saham bertanda pengawasan di event lain:** di hari crash biasa pun saham ini jatuh lebih dalam (rata-rata −0,7 pp di hari-0). Efek hari-0 di event rating (Moody's −1,8 pp, Fitch −1,6 pp) tidak lebih ekstrem dari hari crash biasa (placebo p=0,16–0,23).

### Heterogenitas bank (metode 8 dan 9)
- **Fingerprint** (46 bank × 6 event, 7 karakteristik neraca XBRL + porsi asing). Porsi asing kini dihitung dari 60 hari bursa sebelum E1 dengan data harian BEI.
  - Sidik jari keputusan indeks saham **berbeda dari rating**: Wald p=0,027 di [0,+1] dan p=0,008 di hari-0. Placebo null (p=0,19–0,30).
  - Pembedanya adalah **porsi asing**. Bank yang lebih banyak diperdagangkan asing turun lebih dalam di event indeks saham (−1,8 pp per SD, p=0,03) dan J.P. Morgan (−2,3 pp, p=0,001), tetapi tidak di event rating.
  - **Uji ketahanan (09, `lanjutan/ringkasan_ketahanan.md`):**
    - *Tahan* terhadap cara ukur. Jendela 20/60/120/250 hari, basis volume atau nilai, porsi per event, model penuh atau porsi asing saja: semuanya memberi kemiringan indeks saham negatif dan rating ≈0, dengan beda p=0,002–0,07.
    - Versi 1 null karena porsi asingnya hanya dari **2 hari** sebelum E1 (data harian waktu itu belum ada). Dengan 2 hari, p=0,03–0,14.
    - Juga tahan kalau 4 bank terbesar dibuang (−2,6 pp, p=0,04).
    - *Tidak tahan* bila E2 dibuang: kemiringan indeks saham hilang (−0,1 pp, p=0,83). Jadi ini **efek E2 (dan J.P. Morgan, −2,3 pp, p=0,001), bukan sidik jari umum semua keputusan indeks**. E1 tidak menunjukkan pola ini.
    - Event placebo: ≈0 di [0,+1].
  - **Klaim yang aman:** di E2 dan J.P. Morgan, bank yang lebih banyak diperdagangkan asing jatuh lebih dalam. Di keputusan rating pola ini tidak ada. Ini cocok dengan kanal aliran asing di RQ3.
  - Utang repo dan surat berharga (proksi SBN) tidak menjelaskan siapa yang jatuh.
- **Causal forest** (2 hari MSCI vs 40 hari crash biasa, outcome = peringkat persentil): bank +7 peringkat, saham kecil −1,8. Semua CI melewati nol, dan penentu terbesar adalah likuiditas. Power-nya kecil (hanya 2 hari perlakuan).

## RQ3 — Lewat mekanisme apa?

1. **Aliran asing — data baru untuk 8 event** (jual/beli bersih asing [0,+1], dibanding semua jendela non-event 2025–2026):

   | Event | Pasar | Bank | p (bank) |
   |---|---|---|---|
   | E1 MSCI | **−Rp11,2 T** | **−Rp9,8 T** | 0,003 |
   | Moody's | +Rp0,2 T | −Rp0,7 T | 0,83 |
   | FTSE Feb | −Rp1,2 T | −Rp0,5 T | 0,99 |
   | Fitch | −Rp0,5 T | −Rp0,8 T | 0,70 |
   | J.P. Morgan | **−Rp4,3 T** | **−Rp4,1 T** | 0,017 |
   | S&P (placebo) | −Rp1,3 T | −Rp1,3 T | 0,40 |
   | FTSE Okt (placebo) | −Rp1,7 T | −Rp0,7 T | 0,81 |
   | E2 MSCI | **−Rp5,6 T** | **−Rp6,4 T** | 0,003 |

   - **Keputusan indeks (MSCI, J.P. Morgan) memicu jual asing yang tidak biasa.** Keputusan rating tidak.
   - **Hampir seluruh jual asing jatuh di saham bank.**
   - **Paradoks E1:** asing menjual bersih bank Rp9,8 T dalam dua hari, tetapi harga bank justru turun *lebih sedikit* dari pasar. Artinya ada pembeli domestik yang menyerap. Siapa pembelinya (BUMN/dana pensiun/Danantara?) adalah pertanyaan lanjutan yang menarik.
   - Lintas saham: per persen saham beredar, asing menjual bank lebih banyak di E1, E2, J.P. Morgan, dan Moody's (p 0,03–0,10).
   - Gambaran besar 2025–Okt 2026: asing menjual bersih **±Rp130 T saham bank secara kumulatif**, sedangkan non-bank −Rp27 T. Setiap event indeks terlihat sebagai anak tangga turun (`lanjutan/aliran_asing.png`).
1b. **Siapa pembelinya? (kepemilikan KSEI per tipe investor, 16, `lanjutan/ringkasan_pembeli.md`).** Posisi akhir bulan 30 Des 2025 → 30 Jan 2026 di 49 saham bank:
   - **Pembeli terbesar adalah individu: +Rp8,7 T.** Tipe ini 98% lokal, dan nilainya hampir 3× median bulan lain.
   - Lembaga keuangan +Rp3,8 T.
   - Yang menjual adalah tipe yang didominasi asing: Lainnya −Rp6,2 T, reksa dana −Rp4,4 T, dan dana pensiun −Rp1,9 T (porsi asingnya 74–89%). Ini konsisten dengan jual-bersih asing di bank menurut BEI sepanjang Januari (−Rp16,5 T).
   - **Asuransi dan korporasi** (tempat entitas negara biasanya tercatat) **tidak menyerap lebih dari biasanya.**
   - Jadi yang menahan harga bank di E1 terutama **investor ritel domestik**, bukan institusi negara.
   - **Batasan:** data bulanan mencakup seluruh Januari, bukan hanya 28–29 Jan. Lonjakan individu tidak ekstrem (z 0,75; peringkat 4 dari 10 bulan). Data 2025 tidak memisahkan lokal/asing per tipe.
   - **Cek silang:** perubahan kepemilikan asing KSEI cocok dengan aliran asing harian BEI pada Jan–Mar (korelasi 0,84), tetapi tidak sejak April (≈0). Ada kemungkinan reklasifikasi di KSEI, dan ini perlu dicek sebelum dipakai untuk bulan-bulan itu.
2. **IV aliran asing → harga** (tidak berubah):
   - E2: jual bersih asing 1% saham beredar → harga **−10%** (p<0,001, F=170). OLS biasa tidak negatif, jadi bias seleksinya besar.
   - Hasil OLS lintas 8 event juga tidak negatif (indeks saham +4,3, p=0,016; rating −0,7, ns). Ini menegaskan bahwa hubungan aliran–harga tanpa instrumen menyesatkan.
3. **Reversal vs drift (local projections):** setelah event indeks, bank pulih sebagian. Setelah event rating, bank terus turun (−7,2% di h=20, SBN +16 bp). Jalur E2 di atas (pulih ±separuh dalam seminggu) konsisten dengan pola guncangan aliran dana.
4. **Penularan (connectedness):** keterkaitan saham–bank–SBN–rupiah naik dari ~13 ke ~33. Setelah E2, bank adalah net transmitter terbesar (+4,8).
5. **Neraca bank (XBRL):** utang repo bank melonjak ≈ Rp130 T → Rp473 T (Des 2025 → Jun 2026). Hipotesis "bank ber-repo tinggi paling terpukul di E2" tidak terbukti.

## Deep learning: Gorengan Radar v0 (baru)

- **Tugas:** memprediksi apakah saham akan terkena UMA atau suspensi pengawasan BEI dalam 5 hari bursa ke depan, dari jendela 30 hari (harga, rentang, lonjakan nilai/frekuensi, turnover, asing, pasar negosiasi, papan, notasi).
- **Data:** 650 ribu jendela saham-hari. Dilatih Okt 2023–Jun 2025, dipilih di Jul–Des 2025, dan diuji pada 2026. Semua event berada di periode uji.
- **Akurasi label (uji 2026, basis positif 1,3%):**
  - Gradient boosting terbaik: AUC 0,87, presisi pada 1% skor tertinggi 25% (lift 20×).
  - Transformer BCE: AUC 0,83, presisi 16%.
  - Transformer nnPU: AUC 0,80. Presisi terhadap label rendah, sesuai harapan karena model ini tidak menganggap "tidak berlabel" sebagai "bersih".
  - Regresi logistik: AUC 0,81.
  - Jujur: untuk data tabular berukuran ini, deep learning tidak mengalahkan boosting dalam menebak label BEI.
- **Yang lebih penting, uji event:**
  - Skor Transformer 20 hari sebelum E1 memprediksi siapa yang jatuh: −3,1 s.d. −3,8 pp per SD di [0,+5]. Efek ini lebih ekstrem dari seluruh 38 hari crash biasa (p placebo 0,026, nilai minimum).
  - Efek tetap ada setelah riwayat suspensi BEI dikendalikan (−1,8 s.d. −2,7 pp). Artinya radar menangkap "kelemahan" yang dihukum MSCI di luar label resmi BEI.
  - Skor gradient boosting tidak sekuat itu (p placebo 0,10–0,33).
  - Pola serupa muncul di J.P. Morgan [0,+1], tetapi tidak di keputusan rating maupun placebo.
- **Uji ketahanan (13, `lanjutan/ringkasan_radar_ketahanan.md`):**
  - **3 seed BCE + 3 seed nnPU + prior π 0,005/0,01/0,03 (8 varian Transformer):**
    - Akurasi label stabil (AUC uji 0,80–0,84).
    - Efek E1 [0,+5] stabil: **−3,1 s.d. −3,8 pp per SD**, p placebo 0,026–0,051 di semua varian.
    - Setelah label BEI dikendalikan: −1,8 s.d. −2,7 pp, p placebo 0,026–0,051.
    - E1 [0,+1]: p placebo 0,026 di semua varian Transformer.
  - **Pembanding klasik:** gradient boosting dan logistik tidak lolos untuk E1 [0,+5] (p placebo 0,10–0,69).
  - **Event lain:** J.P. Morgan [0,+1] lolos di hampir semua model (p 0,026–0,10). E2 dan keputusan rating tidak lolos di model mana pun.
  - **Atribusi (permutasi fitur):**
    - Sinyal E1 dari nnPU terutama berasal dari **rentang harga harian** (volatilitas intrahari). Kalau fitur ini diacak, koefisien melemah 1,3 pp.
    - Sinyal E1 dari BCE bersumber dari porsi asing, rentang, papan pengembangan, dan return.
  - **Profil skor pra-E1:** skor tinggi = saham lebih kecil, kurang likuid, free float lebih rendah, **naik tajam sebelum event** (return pra-event +0,4 SD), dan pernah disuspensi.
  - **Uji run-up reversal (14, `lanjutan/ringkasan_radar_runup.md`): sinyal E1 BUKAN sekadar pembalikan setelah kenaikan tajam.** Hasil untuk ensembel 8 Transformer, E1 [0,+5]:
    - Dengan kontrol run-up fleksibel (desil return pra-event, return 5/20 hari, return harian maksimum): −4,4 pp per SD.
    - Dengan skor radar yang dibersihkan dari semua ukuran run-up: −3,2 pp.
    - Interaksi radar × run-up ≈ 0 (p placebo 0,72).
    - Di saham **tanpa** run-up (≤ median): −4,9 pp.
    - Semua p placebo = 0,026 (minimum). Hasil sama untuk nnPU dan BCE seed 0, dan untuk E1 [0,+1].
  - **Pembanding tanpa label: autoencoder (15, `lanjutan/ringkasan_radar_autoencoder.md`).** Ada 2 arsitektur (MLP, GRU) × 2 seed, dilatih tanpa label; skornya adalah galat rekonstruksi.
    - Lemah menebak label BEI (AUC uji 0,66–0,67).
    - **Tidak memprediksi kerugian E1:** −0,5 s.d. −0,8 pp per SD, p placebo 0,23–0,31. Dengan kontrol run-up ≈ 0.
    - Hanya J.P. Morgan [0,+1] yang ikut lolos (−1,6 pp, p 0,026), karena hampir semua skor lolos di sana.
    - **Artinya:** yang dihukum E1 bukan "pola perdagangan aneh" secara umum, melainkan pola yang dipelajari Transformer dari label pengawasan BEI. Hukuman itu tetap ada di luar label itu sendiri (bertahan setelah riwayat suspensi dikendalikan). Label pengawasan memberi arah; deep learning memperluasnya ke saham serupa yang belum ditandai.
  - **J.P. Morgan sebagian memang run-up:** setelah run-up dikendalikan, efeknya turun dari −1,9 ke −0,7 pp (p placebo 0,13). Jadi untuk J.P. Morgan, yang aman diklaim hanya E1.
- **Batasan:** resolusi placebo terbatas (38 hari, p minimum 0,026). Skor per saham tidak dipublikasikan.
- Rincian: `lanjutan/ringkasan_radar.md`.

## Cerita yang didukung data saat ini

> Jenis keputusan menentukan siapa yang membayar. Keputusan MSCI soal tata kelola (E1) menghukum saham bertata kelola
> lemah (saham PPK dan saham yang pernah di-cooling down BEI) jauh melebihi hari crash biasa. Asing menjual bank besar-besaran,
> tetapi pembeli domestik, terutama investor ritel, menahan harganya. Ancaman reklasifikasi (E2) memindahkan beban ke bank: asing kembali menjual
> bank (yang paling banyak diperdagangkan asing jatuh paling dalam), multiplier aliran−harga −10%, dan bank menjadi sumber penularan. Separuh kejatuhan pulih dalam seminggu, tanda guncangan
> aliran dana. Lembaga rating tidak memicu jual asing di saham. Mereka bergerak lewat yield SBN, dengan dampak saham kecil
> tetapi lebih persisten.

## Batasan yang harus disebut
- Konstituen MSCI masih proksi.
- Seri SBN 10 th, MSCI EM, dan negara pembanding dari Refinitiv berhenti 16 Okt. Efek E2 terhadap SBN belum bisa diukur.
- Event rating hanya 2–3 dan event MSCI hanya 2, jadi uji lintas event berpower rendah.
- Return hari-0 terpotong oleh batas auto-reject. Banyak saham PPK tidak bertransaksi di hari E2 (hanya 5 yang bertransaksi).
- Jual/beli asing BEI mencakup pasar negosiasi. Label pengawasan hanya tersedia sejak Okt 2023.
- Return 2020–2024 dari BEI adalah return harga (tanpa dividen).

## Yang belum diolah
1. Nama konstituen MSCI asli (tarik ulang di kampus, sheet `msci` sudah memuat `TR.IndexConstituentName`).
2. Seri pasar setelah 16 Okt (MSCI EM, negara EM, SBN 10 th, CDS, VIX, komoditas), serta AUM ETF dan riwayat rating. Bisa ditarik di kampus. Sumber publik untuk VIX/komoditas (FRED/CBOE) berupa unduhan file dan perlu izinmu.
3. Gorengan Radar: v0 dan uji ketahanan selesai. Run-up reversal dan autoencoder tanpa label sudah diuji; radar v0 siap dimasukkan ke brief/working paper.

File rinci: `ringkasan.md`, `placebo.md`, `perbandingan_event.md`, `lanjutan/ringkasan_lanjutan.md`, `lanjutan/ringkasan_heterogenitas.md`, `lanjutan/ringkasan_aliran_asing.md`, `lanjutan/ringkasan_gorengan.md`, `lanjutan/ringkasan_ketahanan.md`.
