# Apakah lembaga global menghukum saham gorengan?

Riwayat pengawasan = UMA/suspensi BEI dalam 250 hari bursa sebelum event (data UMA dan suspensi BEI sejak Okt 2023). riwayat_suspensi = pernah di-cooling down Divisi Pengawasan Transaksi. PPK = status di hari bursa sebelum event. Kontrol: log_mcap + beta_jci + log_amihud + free_float + ret_pre + bank + msci. Saham tanpa transaksi di hari-0 dikeluarkan. SE HC3.

## Koefisien per event (pp; ** p<0,05, * p<0,1)

| event | ppk car_0 | ppk car_0_1 | ppk car_0_5 | riwayat_suspensi car_0 | riwayat_suspensi car_0_1 | riwayat_suspensi car_0_5 |
|---|---|---|---|---|---|---|
| E1 | -0.84 | -4.89** | -2.37 | -1.52** | -2.35** | -8.03** |
| MDY | -1.9** | -2.03* | 5.6** | -1.78** | -0.22 | 3.49** |
| FTSE1 | 1.79** | 3.59** | 6.57** | 1.11** | 3.6** | 6.41** |
| FCH | -1.53* | -0.81 | -1.83 | -1.57** | -0.64 | -3.69** |
| JPM | 1.82** | 1.78* | 1.58 | -1.46** | -3.48** | -3.81** |
| SP | 1.1 | 2.89** | 0.07 | 0.15 | -0.16 | -0.86 |
| FTSE2 | 1.69 | 2.96 | 1.8 | -0.28 | -0.79 | -1.88* |
| E2 | 1.69 | -3.26* | -6.19 | -0.91** | -1.01 | -3.14** |

## Uji bertumpuk (FE event, cluster saham)

| uji | nilai | p | dependen |
|---|---|---|---|
| riwayat_suspensi di indeks_saham | -0.187 | 0.610 | car_0_1 |
| riwayat_suspensi di rating | -0.402 | 0.323 | car_0_1 |
| riwayat_suspensi di indeks_obligasi | -3.796 | 0.000 | car_0_1 |
| riwayat_suspensi: indeks_saham = rating (chi2) | 0.152 | 0.697 | car_0_1 |
| riwayat_suspensi: indeks_saham = indeks_obligasi (chi2) | 27.574 | 0.000 | car_0_1 |
| ppk di indeks_saham | -1.258 | 0.034 | car_0_1 |
| ppk di rating | -1.836 | 0.010 | car_0_1 |
| ppk di indeks_obligasi | 1.293 | 0.137 | car_0_1 |
| ppk: indeks_saham = rating (chi2) | 0.480 | 0.488 | car_0_1 |
| ppk: indeks_saham = indeks_obligasi (chi2) | 5.707 | 0.017 | car_0_1 |
| riwayat_suspensi di placebo (S&P, FTSE Okt) | -0.335 | 0.435 | car_0_1 |
| ppk di placebo (S&P, FTSE Okt) | 2.450 | 0.028 | car_0_1 |
| riwayat_suspensi di indeks_saham | -0.527 | 0.033 | car_0 |
| riwayat_suspensi di rating | -1.784 | 0.000 | car_0 |
| riwayat_suspensi di indeks_obligasi | -1.449 | 0.000 | car_0 |
| riwayat_suspensi: indeks_saham = rating (chi2) | 10.845 | 0.001 | car_0 |
| riwayat_suspensi: indeks_saham = indeks_obligasi (chi2) | 3.807 | 0.051 | car_0 |
| ppk di indeks_saham | 0.288 | 0.444 | car_0 |
| ppk di rating | -2.108 | 0.000 | car_0 |
| ppk di indeks_obligasi | 1.521 | 0.020 | car_0 |
| ppk: indeks_saham = rating (chi2) | 17.366 | 0.000 | car_0 |
| ppk: indeks_saham = indeks_obligasi (chi2) | 2.811 | 0.094 | car_0 |
| riwayat_suspensi di placebo (S&P, FTSE Okt) | 0.015 | 0.962 | car_0 |
| ppk di placebo (S&P, FTSE Okt) | 0.932 | 0.161 | car_0 |

## Placebo: dibanding 60 hari crash biasa 2025-2026 (p = koefisien placebo <= koefisien event)

Pertanyaannya: apakah saham bertanda pengawasan jatuh LEBIH dalam di hari event daripada di hari crash biasa?

| event | ppk car_0 | ppk car_0_1 | ppk car_0_5 | riwayat_suspensi car_0 | riwayat_suspensi car_0_1 | riwayat_suspensi car_0_5 |
|---|---|---|---|---|---|---|
| E1 | 0.311 | 0.033 | 0.180 | 0.246 | 0.131 | 0.016 |
| MDY | 0.082 | 0.148 | 0.852 | 0.164 | 0.557 | 0.984 |
| FTSE1 | 0.934 | 0.951 | 0.852 | 0.984 | 1.000 | 1.000 |
| FCH | 0.148 | 0.377 | 0.262 | 0.230 | 0.492 | 0.148 |
| JPM | 0.934 | 0.852 | 0.689 | 0.246 | 0.033 | 0.148 |
| SP | 0.836 | 0.951 | 0.590 | 0.820 | 0.607 | 0.361 |
| FTSE2 | 0.934 | 0.951 | 0.705 | 0.590 | 0.459 | 0.246 |
| E2 | 0.934 | 0.082 | 0.033 | 0.426 | 0.377 | 0.148 |

Rata-rata koefisien di hari crash biasa: riwayat_suspensi car_0 -0.71, ppk car_0 0.11.

## Siapa menanggung kerugian kapitalisasi [0,+1] di event MSCI

| event | kelompok | n | rugi_rp_T | porsi_rugi_% | porsi_kapitalisasi_% | car_0_1_median |
|---|---|---|---|---|---|---|
| E1 | Riwayat suspensi pengawasan | 195 | -430.983 | 30.623 | 19.712 | -12.560 |
| E1 | PPK | 83 | -45.493 | 3.232 | 1.720 | -17.419 |
| E1 | Lainnya | 540 | -970.795 | 68.978 | 79.796 | -6.527 |
| E2 | Riwayat suspensi pengawasan | 150 | -139.652 | 9.640 | 8.230 | -20.936 |
| E2 | PPK | 5 | -3.944 | 0.272 | 0.233 | -17.424 |
| E2 | Lainnya | 631 | -1305.086 | 90.091 | 91.539 | -15.400 |

Catatan: label pengawasan dipakai hanya untuk analisis agregat; tidak ada skor per saham yang dipublikasikan.