# Ringkasan RQ C: siapa yang membayar?

## Sampel
- E1 (Free float + pembekuan rebalancing (27 Jan 2026)): hari-0 2026-01-28, 823 saham, 18 anggota MSCI, 46 bank, kapitalisasi pra-event Rp15,849 T (cek: harus mendekati kapitalisasi BEI), return hari-0 median -6.64%. Jendela yang melewati 2026-10-23 belum tersedia.
- E2 (Konsultasi reklasifikasi ke Standalone (15 Okt 2026)): hari-0 2026-10-16, 824 saham, 9 anggota MSCI, 48 bank, kapitalisasi pra-event Rp9,896 T (cek: harus mendekati kapitalisasi BEI), return hari-0 median -13.45%. Jendela yang melewati 2026-10-23 belum tersedia.

## Jendela yang tercemar event lain
Koefisien pada jendela ini mencampur efek beberapa lembaga; tafsirkan dengan hati-hati.

- E1 `car_2_20` memuat: MDY (Moody's, hari +7), FTSE1 (FTSE Russell, hari +9)
- E1 `car_2_60` memuat: MDY (Moody's, hari +7), FTSE1 (FTSE Russell, hari +9), FCH (Fitch, hari +23), JPM (J.P. Morgan, hari +53)

## Kerugian kapitalisasi per kelompok
_*free float < 15% atau Papan Pemantauan Khusus._

| event | jendela | kelompok | rugi_rp_triliun | jumlah_saham | porsi_rugi_% | porsi_kapitalisasi_% |
|---|---|---|---|---|---|---|
| E1 | car_0 | MSCI - bank | -118.569 | 4 | 9.673 | 13.332 |
| E1 | car_0 | MSCI - non-bank | -591.330 | 14 | 48.243 | 37.690 |
| E1 | car_0 | Non-MSCI | -300.687 | 462 | 24.531 | 28.865 |
| E1 | car_0 | Non-MSCI - tata kelola lemah* | -215.135 | 343 | 17.552 | 20.113 |
| E1 | car_0_1 | MSCI - bank | -59.015 | 4 | 4.190 | 13.332 |
| E1 | car_0_1 | MSCI - non-bank | -614.113 | 14 | 43.604 | 37.690 |
| E1 | car_0_1 | Non-MSCI | -440.906 | 462 | 31.306 | 28.865 |
| E1 | car_0_1 | Non-MSCI - tata kelola lemah* | -294.343 | 343 | 20.899 | 20.113 |
| E2 | car_0 | MSCI - bank | -251.281 | 4 | 22.907 | 17.295 |
| E2 | car_0 | MSCI - non-bank | -90.417 | 5 | 8.242 | 6.913 |
| E2 | car_0 | Non-MSCI | -497.483 | 511 | 45.351 | 49.798 |
| E2 | car_0 | Non-MSCI - tata kelola lemah* | -257.777 | 304 | 23.499 | 25.994 |
| E2 | car_0_1 | MSCI - bank | -323.882 | 4 | 22.351 | 17.295 |
| E2 | car_0_1 | MSCI - non-bank | -116.574 | 5 | 8.045 | 6.913 |
| E2 | car_0_1 | Non-MSCI | -675.728 | 511 | 46.632 | 49.798 |
| E2 | car_0_1 | Non-MSCI - tata kelola lemah* | -332.884 | 304 | 22.972 | 25.994 |

## Koefisien anggota MSCI (poin persen, SE HC3)
H1 memprediksi negatif di jendela awal; H3 memprediksi positif di car_2_20 / car_2_60.

| event | dependen | model | koef | se | p | n | r2 |
|---|---|---|---|---|---|---|---|
| E1 | car_0 | M1 kontrol ukuran | -2.809 | 1.312 | 0.032 | 792 | 0.193 |
| E1 | car_0 | M2 FE desil ukuran | -0.602 | 1.244 | 0.628 | 792 | 0.207 |
| E1 | car_0_1 | M1 kontrol ukuran | -0.116 | 1.832 | 0.949 | 792 | 0.187 |
| E1 | car_0_1 | M2 FE desil ukuran | 2.695 | 1.889 | 0.154 | 792 | 0.209 |
| E1 | car_0_5 | M1 kontrol ukuran | 0.883 | 3.736 | 0.813 | 792 | 0.200 |
| E1 | car_0_5 | M2 FE desil ukuran | 1.689 | 3.926 | 0.667 | 792 | 0.203 |
| E1 | car_2_20 | M1 kontrol ukuran | -6.337 | 4.428 | 0.152 | 792 | 0.066 |
| E1 | car_2_20 | M2 FE desil ukuran | -9.448 | 4.824 | 0.050 | 792 | 0.076 |
| E1 | car_2_60 | M1 kontrol ukuran | -11.895 | 7.495 | 0.112 | 792 | 0.047 |
| E1 | car_2_60 | M2 FE desil ukuran | -15.583 | 8.014 | 0.052 | 792 | 0.070 |
| E1 | abn_car_0_1 | M1 kontrol ukuran | 0.390 | 1.905 | 0.838 | 792 | 0.221 |
| E1 | abn_car_0_1 | M2 FE desil ukuran | 3.306 | 1.980 | 0.095 | 792 | 0.241 |
| E2 | car_0 | M1 kontrol ukuran | -1.079 | 1.074 | 0.315 | 785 | 0.233 |
| E2 | car_0 | M2 FE desil ukuran | 0.366 | 0.993 | 0.713 | 785 | 0.239 |
| E2 | car_0_1 | M1 kontrol ukuran | -0.230 | 1.821 | 0.900 | 785 | 0.247 |
| E2 | car_0_1 | M2 FE desil ukuran | 1.039 | 1.745 | 0.551 | 785 | 0.252 |
| E2 | car_0_5 | M1 kontrol ukuran | 4.126 | 3.617 | 0.254 | 785 | 0.045 |
| E2 | car_0_5 | M2 FE desil ukuran | 3.398 | 3.659 | 0.353 | 785 | 0.062 |
| E2 | abn_car_0_1 | M1 kontrol ukuran | 0.056 | 1.859 | 0.976 | 785 | 0.276 |
| E2 | abn_car_0_1 | M2 FE desil ukuran | 1.219 | 1.788 | 0.495 | 785 | 0.281 |

Koefisien lengkap (bank, free float, beta, PPK): `regresi.csv`. Jalur CAR: `jalur_car.png`.