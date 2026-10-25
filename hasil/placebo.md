# Uji placebo hari buruk dan uji permutasi

Placebo: 150 hari non-event dengan IHSG terburuk (2020-07-24 s.d. 2026-09-28; IHSG antara -7.9% dan -1.0%). Model M1, CAR hari-0.

| Event | IHSG hari-0 % | Koef MSCI | p (MSCI lebih negatif dari placebo) | Koef bank | p (bank lebih negatif) | p (bank, dua sisi) |
|---|---|---|---|---|---|---|
| E1 2026-01-28 | -7.35 | -2.24 | 0.033 | +0.36 | 0.675 | 0.669 |
| E2 2026-10-16 | -11.57 | -1.09 | 0.126 | -1.18 | 0.079 | 0.172 |

Rata-rata koefisien di hari placebo: MSCI +0.10, bank +0.06.

## Uji permutasi reaksi [0,+1]
p dua sisi terhadap semua jendela dua hari non-event (±6 tahun terakhir).

| event | lembaga | plasebo | IHSG % | p IHSG % | Bank % | p Bank % | SBN bp | p SBN bp |
|---|---|---|---|---|---|---|---|---|
| E1 | MSCI | False | -8.408 | 0.002 | -3.741 | 0.054 | 1.000 | 0.847 |
| MDY | Moody's | False | -0.863 | 0.436 | -2.101 | 0.181 | 14.700 | 0.051 |
| FTSE1 | FTSE Russell | False | 3.201 | 0.036 | 0.094 | 0.937 | -2.800 | 0.602 |
| FCH | Fitch | False | -2.807 | 0.052 | -0.500 | 0.706 | 3.600 | 0.504 |
| JPM | J.P. Morgan | False | -5.538 | 0.007 | -4.558 | 0.027 | 7.700 | 0.229 |
| SP | S&P | True | 1.943 | 0.122 | 0.239 | 0.853 | 3.800 | 0.480 |
| FTSE2 | FTSE Russell | True | -2.624 | 0.061 | -1.895 | 0.224 | 6.900 | 0.264 |
| E2 | MSCI | False | -15.209 | 0.001 | -16.930 | 0.001 | nan | nan |