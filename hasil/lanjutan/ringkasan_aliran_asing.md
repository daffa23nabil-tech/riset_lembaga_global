# Aliran dana asing di 8 event

Data: Ringkasan Saham BEI 02 Jan 2025 s.d. 23 Oct 2026, 980 saham. Beli bersih = (beli asing - jual asing) x harga penutupan. Negatif = asing menjual bersih.

## A. Beli bersih asing [0,+1] (Rp T; p dua sisi vs semua jendela non-event 2025-2026)

| event | Anggota MSCI | Bank | PPK | Pasar |
|---|---|---|---|---|
| E1 | -9.86 (p=0.003) | -9.75 (p=0.003) | 0.01 (p=0.811) | -11.16 (p=0.003) |
| MDY | -0.28 (p=0.866) | -0.68 (p=0.827) | 0.01 (p=0.387) | 0.22 (p=0.613) |
| FTSE1 | -0.06 (p=0.735) | -0.45 (p=0.986) | -0.03 (p=0.175) | -1.22 (p=0.574) |
| FCH | -0.76 (p=0.766) | -0.8 (p=0.696) | 0.01 (p=0.242) | -0.46 (p=0.989) |
| JPM | -4.34 (p=0.022) | -4.05 (p=0.017) | 0.0 (p=0.446) | -4.28 (p=0.031) |
| SP | -1.18 (p=0.446) | -1.25 (p=0.401) | 0.0 (p=0.855) | -1.28 (p=0.538) |
| FTSE2 | -0.68 (p=0.73) | -0.69 (p=0.808) | -0.0 (p=0.911) | -1.65 (p=0.387) |
| E2 | -6.6 (p=0.003) | -6.44 (p=0.003) | 0.0 (p=0.875) | -5.6 (p=0.011) |

Semua jendela: `aliran_asing_agregat.csv`.

## B. Siapa yang dijual asing? Jual bersih [0,+1] (% saham tercatat), HC3

| event | lembaga | plasebo | variabel | koef | se | p | n |
|---|---|---|---|---|---|---|---|
| E1 | MSCI | False | bank | 0.022 | 0.013 | 0.089 | 872 |
| E1 | MSCI | False | msci | 0.041 | 0.037 | 0.270 | 872 |
| E1 | MSCI | False | ppk | 0.082 | 0.014 | 0.000 | 872 |
| E1 | MSCI | False | log_mcap | 0.018 | 0.004 | 0.000 | 872 |
| E1 | MSCI | False | free_float | -0.002 | 0.000 | 0.000 | 872 |
| E1 | MSCI | False | porsi_asing | -0.001 | 0.001 | 0.154 | 872 |
| MDY | Moody's | False | bank | 0.013 | 0.008 | 0.098 | 870 |
| MDY | Moody's | False | msci | -0.018 | 0.014 | 0.199 | 870 |
| MDY | Moody's | False | ppk | 0.014 | 0.007 | 0.039 | 870 |
| MDY | Moody's | False | log_mcap | 0.002 | 0.002 | 0.477 | 870 |
| MDY | Moody's | False | free_float | -0.000 | 0.000 | 0.273 | 870 |
| MDY | Moody's | False | porsi_asing | 0.000 | 0.000 | 0.128 | 870 |
| FTSE1 | FTSE Russell | False | bank | -0.021 | 0.011 | 0.046 | 871 |
| FTSE1 | FTSE Russell | False | msci | -0.036 | 0.019 | 0.052 | 871 |
| FTSE1 | FTSE Russell | False | ppk | 0.028 | 0.009 | 0.002 | 871 |
| FTSE1 | FTSE Russell | False | log_mcap | 0.008 | 0.003 | 0.008 | 871 |
| FTSE1 | FTSE Russell | False | free_float | -0.000 | 0.000 | 0.602 | 871 |
| FTSE1 | FTSE Russell | False | porsi_asing | -0.000 | 0.000 | 0.915 | 871 |
| FCH | Fitch | False | bank | 0.006 | 0.005 | 0.246 | 872 |
| FCH | Fitch | False | msci | 0.015 | 0.014 | 0.301 | 872 |
| FCH | Fitch | False | ppk | 0.026 | 0.008 | 0.002 | 872 |
| FCH | Fitch | False | log_mcap | 0.001 | 0.002 | 0.650 | 872 |
| FCH | Fitch | False | free_float | -0.001 | 0.000 | 0.000 | 872 |
| FCH | Fitch | False | porsi_asing | 0.000 | 0.000 | 0.251 | 872 |
| JPM | J.P. Morgan | False | bank | 0.017 | 0.008 | 0.040 | 874 |
| JPM | J.P. Morgan | False | msci | 0.038 | 0.025 | 0.120 | 874 |
| JPM | J.P. Morgan | False | ppk | -0.004 | 0.008 | 0.566 | 874 |
| JPM | J.P. Morgan | False | log_mcap | -0.007 | 0.002 | 0.002 | 874 |
| JPM | J.P. Morgan | False | free_float | -0.000 | 0.000 | 0.648 | 874 |
| JPM | J.P. Morgan | False | porsi_asing | 0.001 | 0.000 | 0.002 | 874 |
| SP | S&P | True | bank | 0.008 | 0.003 | 0.009 | 874 |
| SP | S&P | True | msci | 0.007 | 0.012 | 0.563 | 874 |
| SP | S&P | True | ppk | 0.009 | 0.004 | 0.016 | 874 |
| SP | S&P | True | log_mcap | 0.000 | 0.001 | 0.859 | 874 |
| SP | S&P | True | free_float | -0.000 | 0.000 | 0.327 | 874 |
| SP | S&P | True | porsi_asing | 0.000 | 0.000 | 0.122 | 874 |
| FTSE2 | FTSE Russell | True | bank | 0.005 | 0.004 | 0.213 | 848 |
| FTSE2 | FTSE Russell | True | msci | 0.004 | 0.014 | 0.801 | 848 |
| FTSE2 | FTSE Russell | True | ppk | -0.015 | 0.010 | 0.127 | 848 |
| FTSE2 | FTSE Russell | True | log_mcap | -0.008 | 0.002 | 0.001 | 848 |
| FTSE2 | FTSE Russell | True | free_float | 0.001 | 0.000 | 0.004 | 848 |
| FTSE2 | FTSE Russell | True | porsi_asing | 0.001 | 0.000 | 0.002 | 848 |
| E2 | MSCI | False | bank | 0.022 | 0.010 | 0.031 | 848 |
| E2 | MSCI | False | msci | 0.066 | 0.055 | 0.227 | 848 |
| E2 | MSCI | False | ppk | 0.019 | 0.009 | 0.048 | 848 |
| E2 | MSCI | False | log_mcap | 0.006 | 0.002 | 0.008 | 848 |
| E2 | MSCI | False | free_float | -0.001 | 0.000 | 0.001 | 848 |
| E2 | MSCI | False | porsi_asing | -0.001 | 0.000 | 0.008 | 848 |

## C. Tekanan harga: CAR [0,+1] per 1 pp saham yang dijual bersih asing (OLS + kontrol)

| event | lembaga | jenis | plasebo | multiplier | se | p | r2_parsial | n |
|---|---|---|---|---|---|---|---|---|
| E1 | MSCI | Indeks saham | False | 3.798 | 2.074 | 0.067 | 0.006 | 792 |
| MDY | Moody's | Rating | False | -1.947 | 3.258 | 0.550 | 0.001 | 806 |
| FTSE1 | FTSE Russell | Indeks saham | False | 3.308 | 3.327 | 0.320 | 0.003 | 802 |
| FCH | Fitch | Rating | False | -0.776 | 2.677 | 0.772 | 0.000 | 807 |
| JPM | J.P. Morgan | Indeks obligasi | False | 0.987 | 3.951 | 0.803 | 0.000 | 805 |
| SP | S&P | Rating | True | -0.614 | 7.564 | 0.935 | 0.000 | 778 |
| FTSE2 | FTSE Russell | Indeks saham | True | -5.152 | 3.576 | 0.150 | 0.005 | 783 |
| E2 | MSCI | Indeks saham | False | -4.376 | 3.407 | 0.199 | 0.003 | 785 |

Bertumpuk (6 event non-placebo, FE event, cluster saham):

| uji | nilai | p |
|---|---|---|
| kemiringan indeks_saham | 4.252 | 0.016 |
| kemiringan rating | -0.679 | 0.725 |
| kemiringan indeks_obligasi | -0.021 | 0.996 |
| indeks_saham = rating | 3.192 | 0.074 |
| indeks_saham = indeks_obligasi | 0.957 | 0.328 |
| indeks_obligasi = rating | 0.024 | 0.877 |

Catatan: OLS ini asosiasi; arah sebab bisa dua arah (asing menjual saham yang jatuh). Versi IV untuk event MSCI di `ringkasan_lanjutan.md` bagian 10.

![aliran asing](aliran_asing.png)