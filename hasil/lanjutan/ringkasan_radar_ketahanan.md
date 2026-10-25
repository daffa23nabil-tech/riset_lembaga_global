# Gorengan Radar: uji ketahanan

## Akurasi label (uji 2026)

| varian | auc_uji | ap_uji |
|---|---|---|
| bce_s0 | 0.828 | 0.100 |
| bce_s1 | 0.824 | 0.100 |
| bce_s2 | 0.838 | 0.096 |
| nnpu_s0 | 0.804 | 0.041 |
| nnpu_s1 | 0.814 | 0.046 |
| nnpu_s2 | 0.819 | 0.047 |
| nnpu_pi005_s0 | 0.795 | 0.037 |
| nnpu_pi03_s0 | 0.795 | 0.039 |
| gradient_boosting | 0.866 | 0.153 |
| logistik | 0.811 | 0.093 |

## Koefisien skor radar pra-event (pp per SD) dan p placebo (38 hari crash biasa; minimum 0,026)

| varian | E1 car_0 | E1 car_0_1 | E1 car_0_5 | E1 car_0_5 +BEI | E2 car_0_1 | E2 car_0_5 | FCH car_0_5 | JPM car_0_1 | JPM car_0_1 +BEI | MDY car_0_5 |
|---|---|---|---|---|---|---|---|---|---|---|
| bce_s0 | -1.21 (0.051) | -1.76 (0.026) | -3.79 (0.026) | -2.65 (0.026) | -0.02 (0.641) | -1.08 (0.231) | -1.55 (0.231) | -1.55 (0.051) | -0.99 (0.077) | 2.14 (0.949) |
| bce_s1 | -1.25 (0.051) | -1.73 (0.026) | -3.26 (0.026) | -2.27 (0.026) | -0.14 (0.59) | -1.39 (0.231) | -1.17 (0.231) | -1.5 (0.051) | -0.96 (0.103) | 1.45 (0.949) |
| bce_s2 | -1.08 (0.077) | -1.55 (0.026) | -3.28 (0.026) | -2.17 (0.051) | 0.1 (0.846) | -0.95 (0.231) | -1.25 (0.231) | -1.85 (0.026) | -1.32 (0.026) | 1.74 (0.923) |
| gradient_boosting | -1.21 (0.026) | -1.25 (0.077) | -1.69 (0.103) | -0.76 (0.333) | -0.68 (0.256) | -0.52 (0.385) | -1.88 (0.103) | -2.24 (0.026) | -1.92 (0.026) | 1.63 (0.949) |
| logistik | -1.33 (0.026) | -1.42 (0.051) | -1.38 (0.231) | 0.07 (0.692) | -1.53 (0.051) | -1.86 (0.128) | -1.78 (0.179) | -1.88 (0.026) | -1.5 (0.026) | 1.02 (0.846) |
| nnpu_pi005_s0 | -1.65 (0.026) | -2.25 (0.026) | -3.41 (0.026) | -2.26 (0.051) | -0.76 (0.256) | -1.28 (0.231) | -1.44 (0.231) | -1.87 (0.026) | -1.47 (0.026) | 1.83 (0.949) |
| nnpu_pi03_s0 | -1.51 (0.026) | -1.93 (0.026) | -3.44 (0.026) | -2.06 (0.026) | -0.61 (0.333) | -1.36 (0.231) | -1.7 (0.154) | -1.43 (0.026) | -0.94 (0.051) | 2.03 (0.974) |
| nnpu_s0 | -1.53 (0.026) | -1.88 (0.026) | -3.07 (0.026) | -1.79 (0.051) | -0.94 (0.128) | -1.55 (0.205) | -1.46 (0.205) | -1.72 (0.026) | -1.29 (0.026) | 1.79 (0.949) |
| nnpu_s1 | -1.38 (0.026) | -1.81 (0.026) | -3.16 (0.051) | -2.0 (0.051) | -0.64 (0.308) | -1.43 (0.231) | -1.45 (0.231) | -1.67 (0.026) | -1.21 (0.026) | 1.46 (0.949) |
| nnpu_s2 | -1.49 (0.026) | -1.99 (0.026) | -3.54 (0.026) | -2.37 (0.026) | -0.36 (0.41) | -1.1 (0.231) | -1.48 (0.231) | -1.69 (0.026) | -1.24 (0.026) | 1.92 (0.974) |

## Atribusi: permutasi fitur (turun AUC label; perubahan koefisien E1 [0,+5], positif = sinyal E1 melemah)

| model | fitur | jenis | turun_auc | perubahan_koef_e1 |
|---|---|---|---|---|
| bce_s0 | r | harian | 0.079 | 0.452 |
| bce_s0 | rentang | harian | 0.021 | 0.645 |
| bce_s0 | gap_buka | harian | 0.000 | -0.079 |
| bce_s0 | log_nilai_rel | harian | 0.022 | -0.122 |
| bce_s0 | log_frek_rel | harian | 0.010 | -0.138 |
| bce_s0 | turnover | harian | 0.038 | 0.278 |
| bce_s0 | asing_porsi | harian | 0.023 | 0.712 |
| bce_s0 | asing_bersih | harian | 0.002 | -0.074 |
| bce_s0 | nego_porsi | harian | -0.001 | -0.068 |
| bce_s0 | tanpa_transaksi | harian | 0.007 | -0.215 |
| bce_s0 | log_mcap | statis | 0.010 | 0.117 |
| bce_s0 | free_float | statis | 0.006 | -0.079 |
| bce_s0 | log_harga | statis | 0.027 | -0.290 |
| bce_s0 | papan_utama | statis | 0.016 | 0.185 |
| bce_s0 | papan_pengembangan | statis | 0.010 | 0.604 |
| bce_s0 | papan_akselerasi | statis | 0.011 | 0.047 |
| bce_s0 | papan_ppk | statis | 0.020 | 0.331 |
| bce_s0 | notasi_buruk | statis | 0.003 | 0.100 |
| nnpu_s0 | r | harian | 0.037 | 0.065 |
| nnpu_s0 | rentang | harian | 0.041 | 1.265 |
| nnpu_s0 | gap_buka | harian | 0.003 | -0.296 |
| nnpu_s0 | log_nilai_rel | harian | 0.002 | -0.329 |
| nnpu_s0 | log_frek_rel | harian | 0.002 | -0.396 |
| nnpu_s0 | turnover | harian | 0.031 | -0.316 |
| nnpu_s0 | asing_porsi | harian | 0.025 | 0.157 |
| nnpu_s0 | asing_bersih | harian | 0.000 | -0.138 |
| nnpu_s0 | nego_porsi | harian | 0.004 | 0.063 |
| nnpu_s0 | tanpa_transaksi | harian | -0.007 | -0.269 |
| nnpu_s0 | log_mcap | statis | 0.010 | -0.362 |
| nnpu_s0 | free_float | statis | -0.001 | 0.026 |
| nnpu_s0 | log_harga | statis | 0.028 | 0.162 |
| nnpu_s0 | papan_utama | statis | 0.006 | -0.172 |
| nnpu_s0 | papan_pengembangan | statis | 0.004 | -0.094 |
| nnpu_s0 | papan_akselerasi | statis | 0.007 | -0.038 |
| nnpu_s0 | papan_ppk | statis | -0.001 | -0.032 |
| nnpu_s0 | notasi_buruk | statis | 0.002 | 0.017 |

## Profil skor pra-E1 (radar_z ~ karakteristik terstandar)

| karakteristik | koef_per_sd | p | model | r2 |
|---|---|---|---|---|
| log_mcap | -0.390 | 0.000 | bce_s0 | 0.420 |
| log_amihud | -0.121 | 0.012 | bce_s0 | 0.420 |
| free_float | -0.100 | 0.010 | bce_s0 | 0.420 |
| beta_jci | 0.029 | 0.391 | bce_s0 | 0.420 |
| ret_pre | 0.435 | 0.000 | bce_s0 | 0.420 |
| harga_log | 0.100 | 0.032 | bce_s0 | 0.420 |
| ppk | -0.161 | 0.000 | bce_s0 | 0.420 |
| riwayat_suspensi | 0.326 | 0.000 | bce_s0 | 0.420 |
| bank | -0.002 | 0.957 | bce_s0 | 0.420 |
| log_mcap | -0.297 | 0.000 | nnpu_s0 | 0.407 |
| log_amihud | -0.151 | 0.002 | nnpu_s0 | 0.407 |
| free_float | -0.074 | 0.026 | nnpu_s0 | 0.407 |
| beta_jci | 0.027 | 0.488 | nnpu_s0 | 0.407 |
| ret_pre | 0.399 | 0.000 | nnpu_s0 | 0.407 |
| harga_log | -0.004 | 0.931 | nnpu_s0 | 0.407 |
| ppk | -0.046 | 0.208 | nnpu_s0 | 0.407 |
| riwayat_suspensi | 0.356 | 0.000 | nnpu_s0 | 0.407 |
| bank | -0.008 | 0.732 | nnpu_s0 | 0.407 |