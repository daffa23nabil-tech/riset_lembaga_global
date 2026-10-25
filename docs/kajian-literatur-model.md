# Kajian Literatur & Model: Apakah Proyek Ini Unik, dan Apakah Modelnya yang Terbaik?

_18 Okt 2026. Sumber: korpus Scopus di `08-riset-literatur/` dan pencarian web. Hasil pencarian web bukan tinjauan sistematis, jadi klaim kebaruan baru final setelah query Scopus baru (bagian 6) dijalankan._

## 1. Korpus Scopus yang ada: tidak mencakup topik ini
Korpus (5.319 paper) dibangun untuk topik **kerapuhan bank**. Isinya untuk proyek ini:

| Topik | Paper relevan | Catatan |
|---|---|---|
| Reklasifikasi MSCI / indeks / dana pasif | **0** | Kecocokan kata "benchmark" semuanya salah topik |
| Synthetic control | **0** | |
| Deteksi manipulasi saham | **1**: *Manipulation Detection of the Bank Sector* (RoEduNet 2025) | Pakai HMM pada order book (LOBSTER), fokus pada interpretabilitas. Butuh data tick, yang tidak kita punya |
| Rating negara | ±20, mayoritas prediksi rating | Bukan reaksi pasar terhadap pengumuman |
| DML / causal forest | 30, aplikasi di perbankan | Bisa jadi rujukan metode |
| GNN untuk fraud | Ada: *GNN for Fraud Detection via Spatial-Temporal Attention* (IEEE TKDE 2022) | Ide untuk ekstensi jaringan konglomerat |

**Kesimpulan:** korpus ini tidak bisa dipakai untuk membuktikan kebaruan. Perlu query Scopus baru (bagian 6).

## 2. Penelitian yang SUDAH membahas event MSCI 2026, penting untuk dibedakan
| Studi | Yang dilakukan | Temuan | Celah yang kita isi |
|---|---|---|---|
| Al-Kharaj (2026), *Reaksi Pasar Modal Indonesia terhadap Pengumuman MSCI terkait Transparansi dan Free Float* | Event study 39 saham LQ45, jendela 11 hari, uji beda rata-rata sebelum vs sesudah | AR tidak berbeda signifikan, volume berubah | Sampel kecil dan sudah tersaring. Tidak ada pembanding (siapa vs siapa), tidak ada uji placebo |
| JAP Unram (Mei 2026), *Reaksi Pasar terhadap Pengumuman MSCI Freeze Indonesia* | 17 konstituen MSCI: AR, volume, volatilitas | (belum dibaca lengkap) | Hanya anggota MSCI, jadi tidak bisa membandingkan anggota vs non-anggota |
| Fakhri dkk., Al-Kharaj, *MSCI Downgrade to Frontier Market: Lessons for Indonesia from Three Countries* | Event study downgrade Yordania, Argentina, Maroko | Yordania paling negatif; Argentina positif karena pemulihan pasca krisis | Negara lain, bukan Indonesia 2026 |

**Implikasinya:** "event study reaksi pasar terhadap MSCI di Indonesia" **sudah tidak baru**. Kebaruan kita harus ada di tempat lain (bagian 5). Ketiga paper ini wajib dikutip dan dibedakan secara eksplisit. Menariknya, temuan "tidak signifikan" pada LQ45 justru bisa kita jelaskan: rata-rata menutupi siapa yang kena dan siapa yang tidak.

## 3. Literatur reklasifikasi indeks: dasar H3
- **Burnham, Gakidis & Wurgler (2018, *Financial Analysts Journal*; NBER w23557):** 17 reklasifikasi MSCI 2000–2015.
  - Sekitar US$10 triliun dana mengacu ke indeks MSCI.
  - Harga *overshoot* di antara tanggal pengumuman dan tanggal efektif: turun jika pindah ke indeks dengan kepemilikan benchmark lebih kecil.
  - Sebagian besar pergerakan itu **berbalik dalam setahun**.
  - Artinya **H3 (pembalikan = tekanan harga non-fundamental) punya preseden kuat**. Kita memperluasnya ke dalam satu negara: saham mana yang kena, dan peran bank.
- **Rujukan lain yang masih harus dicek:** studi rebalancing indeks obligasi EM (mis. Pandolfi & Williams pada GBI-EM) dan literatur *inelastic markets* (Gabaix & Koijen). Keduanya belum diverifikasi di sesi ini.

## 4. Literatur pengumuman rating negara: sangat banyak, tapi tidak ada pembanding indeks
- Reaksi saham, obligasi, dan CDS EM terhadap pengumuman rating sudah banyak diteliti. Temuannya: asimetris (downgrade lebih berdampak), sering sudah diantisipasi, dan berbeda antara pasar saham dan obligasi.
- **Belum ditemukan studi yang membandingkan langsung reaksi terhadap penyedia indeks vs lembaga rating** untuk negara yang sama. Ini **calon kebaruan terkuat** untuk RQ1, tapi harus dikonfirmasi lewat Scopus (query Q10).

## 5. Model deteksi manipulasi: apa yang sudah ada, dan model terbaik untuk kasus kita
| Studi | Data | Model | Kelemahan untuk kasus kita |
|---|---|---|---|
| Ensemble supervised + unsupervised (*Expert Systems with Applications* 2023), bursa Thailand | Kasus manipulasi nyata, **hanya 6** | LSTM + LSTM-autoencoder + SVM stacker | Label sangat sedikit |
| Deep unsupervised anomaly detection, pasar frekuensi tinggi (2023/24) | Order book, manipulasi **sintetis** | Transformer-autoencoder + one-class SVM (AUROC 0,96) | Butuh data tick; label sintetis bisa melebih-lebihkan kinerja |
| Contrastive learning pada order book (arXiv 2025) | Order book | Cascaded contrastive representation | Butuh data tick |
| Bursa Teheran (pump & dump) | **Harian**, label dari pemicu pengawasan | GAN + MLP/RNN/LSTM | Paling mirip dengan kita, kualitas metodologi belum dicek |
| India (kasus SEBI), China (sanksi CSRC 2014–16, *IRFA* 2021) | Kasus sanksi regulator | Stacked NN / SVM + Borderline-SMOTE | Label sedikit, model relatif sederhana |
| Isolation forest ensemble (Chile) | Tanpa label | k-partitioned isolation forests | Baseline tanpa label yang bagus |

**Pola dari literatur:**
1. Sebagian besar memakai **data tick/order book**. Studi dengan data harian lebih sedikit.
2. Masalah terbesarnya **label**: kasus nyata sangat sedikit, atau datanya sintetis.
3. **Tidak ada studi untuk BEI** (pencarian Indonesia hanya menemukan artikel edukasi dan studi reaksi UMA tanpa ML).
4. **Tidak ditemukan studi yang memakai peringatan regulator sebagai label positif dengan PU learning.**

### Revisi model yang direkomendasikan (lebih baik dari rencana awal)
Rencana awal memperlakukan UMA sebagai label benar/salah biasa. Itu **keliru secara metodologis**: saham yang tidak kena UMA bukan berarti bersih, hanya *belum tertangkap*. Pendekatan yang tepat adalah **Positive-Unlabeled (PU) learning**.

| Lapisan | Model | Alasan |
|---|---|---|
| Baseline 1 | Aturan sederhana (frekuensi ARA, lonjakan volume) | Tolok ukur yang bisa dijelaskan ke regulator |
| Baseline 2 | Isolation forest + XGBoost | Model tabel yang kuat; DL wajib mengalahkan keduanya |
| **Model utama** | **Encoder Transformer/temporal-CNN + loss nnPU** (Kiryo dkk. 2017) | UMA, suspensi, dan sanksi OJK = positif; sisanya = *unlabeled*, bukan negatif |
| Pelengkap | Transformer/LSTM-autoencoder (tanpa label) | Menangkap pola baru yang belum pernah kena UMA. Digabung dengan model utama, mengikuti ide ensemble dari studi Thailand |
| Ekstensi (opsional) | GNN di atas jaringan kepemilikan konglomerat (data pemegang saham >5% KSEI/BEI) | MSCI menyoroti beneficial ownership yang buram, dan jaringan ini menangkap "goreng bersama" |

**Jebakan yang wajib dihindari:**
- **Model hanya belajar "saham kecil = mencurigakan".** Evaluasi harus dilakukan *di dalam* kelompok ukuran dan likuiditas yang sama.
- **Kebocoran waktu.** Split harus berbasis waktu, dan fitur hanya boleh memakai data sebelum tanggal UMA.
- **Ukuran keberhasilan:** precision@k, *lead time* sebelum UMA diumumkan, dan kalibrasi. Jangan memakai akurasi, karena kelasnya sangat tidak seimbang.

## 6. Status kebaruan per klaim
| Klaim | Status | Catatan |
|---|---|---|
| "Event study reaksi pasar Indonesia terhadap MSCI 2026" | **Tidak baru** | Sudah ada minimal 2 paper |
| "Harga turun lalu berbalik setelah reklasifikasi" | **Tidak baru** (Burnham dkk. 2018) | Dipakai sebagai landasan, bukan kontribusi |
| "Siapa yang membayar: biaya jatuh ke anggota indeks dan bank, bukan ke saham bermasalah", lengkap dengan placebo hari buruk | **Kemungkinan baru** | Kontribusi inti RQ2 |
| "Penyedia indeks vs lembaga rating untuk negara yang sama" | **Kemungkinan baru** | Konfirmasi dengan Q10 |
| "Detektor manipulasi DL untuk BEI dengan label UMA + PU learning" | **Kemungkinan baru** | Belum ditemukan untuk BEI, maupun PU dengan label regulator |
| "Menghubungkan ukuran manipulasi dengan biaya keputusan penyedia indeks" | **Kemungkinan baru** | Ini benang merah proyek |

### Query Scopus yang perlu dijalankan (lewat akses kampus), lalu ekspor ke `08-riset-literatur/scopus/`
- **Q8 (reklasifikasi):** `TITLE-ABS-KEY(("market reclassification" OR "index reclassification" OR "country classification" OR "MSCI" OR "FTSE Russell") AND ("emerging market*" OR "frontier market*") AND ("event study" OR "price pressure" OR "flows" OR "abnormal return*"))`
- **Q9 (manipulasi):** `TITLE-ABS-KEY(("market manipulation" OR "price manipulation" OR "pump and dump" OR "pump-and-dump" OR "trade-based manipulation") AND ("deep learning" OR "neural network" OR "LSTM" OR "transformer" OR "autoencoder" OR "machine learning" OR "positive-unlabeled"))`
- **Q10 (rating vs indeks):** `TITLE-ABS-KEY(("sovereign rating*" OR "credit rating agenc*" OR "rating announcement*") AND ("index provider*" OR "benchmark index" OR "index inclusion" OR "MSCI"))`
- **Q11 (indeks obligasi):** `TITLE-ABS-KEY(("index inclusion" OR "benchmark inclusion" OR "index rebalancing" OR "GBI-EM") AND ("sovereign" OR "government bond*" OR "local currency") AND ("flows" OR "price impact" OR "yield*"))`

## 7. Perubahan pada rencana proyek
1. **Framing kebaruan:** jangan menjual "event study MSCI". Jual: *siapa yang membayar*, *indeks vs rating*, dan *ukuran manipulasi berbasis DL*.
2. **Kutip dan bantah dengan sopan** paper LQ45 yang tidak signifikan: rata-rata menutupi heterogenitas.
3. **Model DL diganti dari klasifikasi biasa ke PU learning + ensemble autoencoder**, dengan evaluasi di dalam kelompok ukuran yang sama.
4. **Jalankan Q8–Q11 minggu ini**, sebaiknya bersamaan dengan tarik data Refinitiv di kampus hari Selasa.
