# Uji ketahanan

## A. Fingerprint porsi asing (bank x 6 event non-placebo; pp CAR per 1 SD porsi asing; SE cluster bank)

`p_asing_saham=rating`: kemiringan porsi asing sama di indeks saham dan rating. `p_wald_saham=rating`: seluruh sidik jari sama. Placebo = event S&P dan FTSE Okt.

| varian | model | y | sampel | asing_indeks_saham | p_indeks_saham | asing_rating | p_rating | asing_indeks_obligasi | p_indeks_obligasi | p_asing_saham=rating | p_wald_saham=rating | asing_placebo | p_placebo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pra-E1 2 hari, volume | penuh | car_0_1 | semua | -0.957 | 0.121 | -0.097 | 0.764 | -0.874 | 0.165 | 0.137 | 0.242 | 0.097 | 0.539 |
| pra-E1 2 hari, volume | penuh | car_0 | semua | -0.711 | 0.071 | -0.171 | 0.599 | -1.123 | 0.039 | 0.110 | 0.166 | 0.238 | 0.112 |
| pra-E1 2 hari, volume | asing saja | car_0_1 | semua | -0.550 | 0.095 | 0.188 | 0.300 | -0.855 | 0.055 | 0.025 | 0.025 | 0.097 | 0.539 |
| pra-E1 2 hari, volume | asing saja | car_0 | semua | -0.316 | 0.190 | 0.199 | 0.243 | -0.320 | 0.249 | 0.020 | 0.020 | 0.238 | 0.112 |
| pra-E1 2 hari, nilai | penuh | car_0_1 | semua | -0.952 | 0.123 | -0.102 | 0.753 | -0.877 | 0.165 | 0.142 | 0.248 | 0.094 | 0.552 |
| pra-E1 2 hari, nilai | penuh | car_0 | semua | -0.712 | 0.071 | -0.175 | 0.592 | -1.123 | 0.040 | 0.112 | 0.167 | 0.237 | 0.114 |
| pra-E1 2 hari, nilai | asing saja | car_0_1 | semua | -0.546 | 0.096 | 0.186 | 0.307 | -0.853 | 0.056 | 0.026 | 0.026 | 0.094 | 0.552 |
| pra-E1 2 hari, nilai | asing saja | car_0 | semua | -0.316 | 0.189 | 0.198 | 0.246 | -0.317 | 0.253 | 0.020 | 0.020 | 0.237 | 0.114 |
| pra-E1 20 hari, volume | penuh | car_0_1 | semua | -1.713 | 0.023 | 0.148 | 0.705 | -1.777 | 0.018 | 0.006 | 0.023 | -0.002 | 0.990 |
| pra-E1 20 hari, volume | penuh | car_0 | semua | -1.128 | 0.020 | 0.051 | 0.896 | -1.500 | 0.022 | 0.002 | 0.004 | 0.233 | 0.138 |
| pra-E1 20 hari, volume | asing saja | car_0_1 | semua | -0.691 | 0.021 | 0.321 | 0.172 | -1.104 | 0.018 | 0.002 | 0.002 | -0.002 | 0.990 |
| pra-E1 20 hari, volume | asing saja | car_0 | semua | -0.373 | 0.080 | 0.339 | 0.102 | -0.261 | 0.350 | 0.001 | 0.001 | 0.233 | 0.138 |
| pra-E1 20 hari, nilai | penuh | car_0_1 | semua | -1.712 | 0.023 | 0.148 | 0.705 | -1.772 | 0.019 | 0.007 | 0.023 | -0.003 | 0.986 |
| pra-E1 20 hari, nilai | penuh | car_0 | semua | -1.126 | 0.021 | 0.054 | 0.891 | -1.498 | 0.022 | 0.002 | 0.004 | 0.232 | 0.138 |
| pra-E1 20 hari, nilai | asing saja | car_0_1 | semua | -0.689 | 0.021 | 0.322 | 0.172 | -1.100 | 0.018 | 0.002 | 0.002 | -0.003 | 0.986 |
| pra-E1 20 hari, nilai | asing saja | car_0 | semua | -0.371 | 0.081 | 0.340 | 0.101 | -0.259 | 0.354 | 0.001 | 0.001 | 0.232 | 0.138 |
| pra-E1 60 hari, volume | penuh | car_0_1 | semua | -1.767 | 0.033 | -0.062 | 0.885 | -2.265 | 0.001 | 0.019 | 0.027 | 0.055 | 0.713 |
| pra-E1 60 hari, volume | penuh | car_0 | semua | -1.250 | 0.017 | -0.005 | 0.991 | -1.527 | 0.010 | 0.005 | 0.008 | 0.264 | 0.095 |
| pra-E1 60 hari, volume | penuh | car_0_1 | tanpa E1 | -2.354 | 0.009 | -0.062 | 0.886 | -2.265 | 0.001 | 0.012 | 0.003 | 0.055 | 0.713 |
| pra-E1 60 hari, volume | penuh | car_0_1 | tanpa MDY | -1.767 | 0.034 | 0.571 | 0.293 | -2.265 | 0.001 | 0.002 | 0.004 | 0.055 | 0.713 |
| pra-E1 60 hari, volume | penuh | car_0_1 | tanpa FTSE1 | -2.905 | 0.022 | -0.062 | 0.886 | -2.265 | 0.001 | 0.011 | 0.097 | 0.055 | 0.713 |
| pra-E1 60 hari, volume | penuh | car_0_1 | tanpa FCH | -1.767 | 0.034 | -0.731 | 0.136 | -2.265 | 0.001 | 0.191 | 0.158 | 0.055 | 0.713 |
| pra-E1 60 hari, volume | penuh | car_0_1 | tanpa JPM | -1.767 | 0.031 | -0.062 | 0.884 | nan | nan | 0.018 | 0.025 | 0.055 | 0.713 |
| pra-E1 60 hari, volume | penuh | car_0_1 | tanpa E2 | -0.137 | 0.825 | -0.062 | 0.886 | -2.265 | 0.001 | 0.883 | 0.001 | 0.055 | 0.713 |
| pra-E1 60 hari, volume | penuh | car_0_1 | tanpa 4 bank terbesar | -2.582 | 0.044 | 0.143 | 0.851 | -2.293 | 0.080 | 0.035 | 0.286 | 0.348 | 0.402 |
| pra-E1 60 hari, volume | asing saja | car_0_1 | semua | -0.646 | 0.026 | 0.256 | 0.226 | -1.179 | 0.009 | 0.002 | 0.002 | 0.055 | 0.713 |
| pra-E1 60 hari, volume | asing saja | car_0 | semua | -0.373 | 0.077 | 0.319 | 0.101 | -0.229 | 0.424 | 0.000 | 0.000 | 0.264 | 0.095 |
| pra-E1 60 hari, volume | asing saja | car_0_1 | tanpa E1 | -1.158 | 0.001 | 0.256 | 0.227 | -1.179 | 0.009 | 0.000 | 0.000 | 0.055 | 0.713 |
| pra-E1 60 hari, volume | asing saja | car_0_1 | tanpa MDY | -0.646 | 0.026 | 0.525 | 0.025 | -1.179 | 0.009 | 0.001 | 0.001 | 0.055 | 0.713 |
| pra-E1 60 hari, volume | asing saja | car_0_1 | tanpa FTSE1 | -0.696 | 0.119 | 0.256 | 0.227 | -1.179 | 0.009 | 0.024 | 0.024 | 0.055 | 0.713 |
| pra-E1 60 hari, volume | asing saja | car_0_1 | tanpa FCH | -0.646 | 0.026 | -0.018 | 0.959 | -1.179 | 0.009 | 0.080 | 0.080 | 0.055 | 0.713 |
| pra-E1 60 hari, volume | asing saja | car_0_1 | tanpa JPM | -0.646 | 0.025 | 0.256 | 0.226 | nan | nan | 0.002 | 0.002 | 0.055 | 0.713 |
| pra-E1 60 hari, volume | asing saja | car_0_1 | tanpa E2 | -0.085 | 0.707 | 0.256 | 0.227 | -1.179 | 0.009 | 0.192 | 0.192 | 0.055 | 0.713 |
| pra-E1 60 hari, volume | asing saja | car_0_1 | tanpa 4 bank terbesar | -1.537 | 0.043 | 0.373 | 0.563 | -2.217 | 0.064 | 0.048 | 0.048 | 0.348 | 0.402 |
| pra-E1 60 hari, nilai | penuh | car_0_1 | semua | -1.766 | 0.033 | -0.061 | 0.887 | -2.262 | 0.001 | 0.019 | 0.027 | 0.055 | 0.715 |
| pra-E1 60 hari, nilai | penuh | car_0 | semua | -1.248 | 0.017 | -0.003 | 0.994 | -1.529 | 0.010 | 0.005 | 0.008 | 0.264 | 0.096 |
| pra-E1 60 hari, nilai | asing saja | car_0_1 | semua | -0.645 | 0.026 | 0.256 | 0.225 | -1.177 | 0.009 | 0.002 | 0.002 | 0.055 | 0.715 |
| pra-E1 60 hari, nilai | asing saja | car_0 | semua | -0.371 | 0.078 | 0.319 | 0.100 | -0.228 | 0.425 | 0.000 | 0.000 | 0.264 | 0.096 |
| pra-E1 120 hari, volume | penuh | car_0_1 | semua | -1.824 | 0.051 | -0.011 | 0.980 | -2.009 | 0.021 | 0.029 | 0.060 | 0.047 | 0.760 |
| pra-E1 120 hari, volume | penuh | car_0 | semua | -1.334 | 0.020 | 0.006 | 0.989 | -1.763 | 0.008 | 0.004 | 0.007 | 0.259 | 0.098 |
| pra-E1 120 hari, volume | asing saja | car_0_1 | semua | -0.639 | 0.028 | 0.280 | 0.220 | -1.098 | 0.002 | 0.002 | 0.002 | 0.047 | 0.760 |
| pra-E1 120 hari, volume | asing saja | car_0 | semua | -0.375 | 0.077 | 0.322 | 0.106 | -0.306 | 0.246 | 0.000 | 0.000 | 0.259 | 0.098 |
| pra-E1 120 hari, nilai | penuh | car_0_1 | semua | -1.823 | 0.051 | -0.010 | 0.982 | -2.005 | 0.022 | 0.029 | 0.060 | 0.047 | 0.761 |
| pra-E1 120 hari, nilai | penuh | car_0 | semua | -1.333 | 0.020 | 0.007 | 0.987 | -1.764 | 0.008 | 0.004 | 0.007 | 0.259 | 0.098 |
| pra-E1 120 hari, nilai | asing saja | car_0_1 | semua | -0.638 | 0.028 | 0.280 | 0.219 | -1.096 | 0.002 | 0.002 | 0.002 | 0.047 | 0.761 |
| pra-E1 120 hari, nilai | asing saja | car_0 | semua | -0.373 | 0.078 | 0.322 | 0.105 | -0.306 | 0.247 | 0.000 | 0.000 | 0.259 | 0.098 |
| pra-E1 250 hari, volume | penuh | car_0_1 | semua | -1.646 | 0.114 | -0.016 | 0.973 | -1.814 | 0.097 | 0.069 | 0.107 | -0.002 | 0.990 |
| pra-E1 250 hari, volume | penuh | car_0 | semua | -1.329 | 0.029 | -0.104 | 0.825 | -2.015 | 0.005 | 0.012 | 0.015 | 0.251 | 0.109 |
| pra-E1 250 hari, volume | asing saja | car_0_1 | semua | -0.528 | 0.065 | 0.289 | 0.204 | -0.985 | 0.001 | 0.005 | 0.005 | -0.002 | 0.990 |
| pra-E1 250 hari, volume | asing saja | car_0 | semua | -0.360 | 0.081 | 0.304 | 0.114 | -0.350 | 0.186 | 0.001 | 0.001 | 0.251 | 0.109 |
| pra-E1 250 hari, nilai | penuh | car_0_1 | semua | -1.645 | 0.114 | -0.015 | 0.974 | -1.805 | 0.099 | 0.069 | 0.108 | -0.002 | 0.990 |
| pra-E1 250 hari, nilai | penuh | car_0 | semua | -1.328 | 0.029 | -0.104 | 0.825 | -2.015 | 0.005 | 0.012 | 0.015 | 0.251 | 0.110 |
| pra-E1 250 hari, nilai | asing saja | car_0_1 | semua | -0.527 | 0.065 | 0.289 | 0.203 | -0.981 | 0.001 | 0.005 | 0.005 | -0.002 | 0.990 |
| pra-E1 250 hari, nilai | asing saja | car_0 | semua | -0.360 | 0.082 | 0.304 | 0.114 | -0.349 | 0.187 | 0.001 | 0.001 | 0.251 | 0.110 |
| per event 60 hari, volume | penuh | car_0_1 | semua | -1.639 | 0.048 | -0.111 | 0.808 | -1.479 | 0.103 | 0.036 | 0.018 | 0.184 | 0.231 |
| per event 60 hari, volume | penuh | car_0 | semua | -0.979 | 0.059 | -0.124 | 0.786 | -1.544 | 0.006 | 0.052 | 0.052 | 0.306 | 0.034 |
| per event 60 hari, volume | asing saja | car_0_1 | semua | -0.653 | 0.036 | 0.243 | 0.291 | -1.218 | 0.000 | 0.003 | 0.003 | 0.184 | 0.231 |
| per event 60 hari, volume | asing saja | car_0 | semua | -0.317 | 0.163 | 0.285 | 0.181 | -0.475 | 0.168 | 0.004 | 0.004 | 0.306 | 0.034 |
| per event 20 hari, volume | penuh | car_0_1 | semua | -1.436 | 0.058 | -0.300 | 0.459 | -1.376 | 0.164 | 0.076 | 0.064 | 0.149 | 0.301 |
| per event 20 hari, volume | penuh | car_0 | semua | -1.001 | 0.037 | -0.425 | 0.314 | -1.573 | 0.006 | 0.142 | 0.173 | 0.291 | 0.042 |
| per event 20 hari, volume | asing saja | car_0_1 | semua | -0.672 | 0.033 | 0.125 | 0.594 | -1.011 | 0.001 | 0.004 | 0.004 | 0.149 | 0.301 |
| per event 20 hari, volume | asing saja | car_0 | semua | -0.390 | 0.087 | 0.113 | 0.627 | -0.459 | 0.191 | 0.036 | 0.036 | 0.291 | 0.042 |

## B. Saham pernah di-cooling down/UMA di E1 (pp; p_placebo = porsi 60 hari crash biasa dengan koefisien <= E1)

| varian | spesifikasi | y | koef_E1 | p_hc3 | rata_placebo | p_placebo | n_kelompok |
|---|---|---|---|---|---|---|---|
| utama: suspensi 250 hari | dasar | car_0 | -1.521 | 0.004 | -0.708 | 0.246 | 195 |
| utama: suspensi 250 hari | dasar | car_0_1 | -2.355 | 0.001 | -0.538 | 0.131 | 195 |
| utama: suspensi 250 hari | dasar | car_0_5 | -8.026 | 0.000 | -0.195 | 0.016 | 195 |
| utama: suspensi 250 hari | dasar | abn_car_0_5 | -10.628 | 0.000 | -2.523 | 0.016 | 195 |
| utama: suspensi 250 hari | FE desil ukuran | car_0 | -1.473 | 0.005 | -0.704 | 0.246 | 195 |
| utama: suspensi 250 hari | FE desil ukuran | car_0_1 | -2.289 | 0.001 | -0.529 | 0.148 | 195 |
| utama: suspensi 250 hari | FE desil ukuran | car_0_5 | -7.990 | 0.000 | -0.146 | 0.016 | 195 |
| utama: suspensi 250 hari | FE desil ukuran | abn_car_0_5 | -10.552 | 0.000 | -2.476 | 0.016 | 195 |
| utama: suspensi 250 hari | tanpa saham PPK | car_0 | -1.897 | 0.001 | -0.688 | 0.164 | 195 |
| utama: suspensi 250 hari | tanpa saham PPK | car_0_1 | -2.614 | 0.001 | -0.548 | 0.098 | 195 |
| utama: suspensi 250 hari | tanpa saham PPK | car_0_5 | -7.127 | 0.000 | -0.368 | 0.016 | 195 |
| utama: suspensi 250 hari | tanpa saham PPK | abn_car_0_5 | -10.055 | 0.000 | -2.775 | 0.016 | 195 |
| utama: suspensi 250 hari | tanpa harga < Rp100 | car_0 | -2.243 | 0.000 | -0.676 | 0.066 | 195 |
| utama: suspensi 250 hari | tanpa harga < Rp100 | car_0_1 | -3.072 | 0.000 | -0.561 | 0.049 | 195 |
| utama: suspensi 250 hari | tanpa harga < Rp100 | car_0_5 | -7.843 | 0.000 | -0.349 | 0.016 | 195 |
| utama: suspensi 250 hari | tanpa harga < Rp100 | abn_car_0_5 | -10.896 | 0.000 | -2.987 | 0.016 | 195 |
| utama: suspensi 250 hari | winsor CAR 1% | car_0 | -1.801 | 0.000 | -0.800 | 0.197 | 195 |
| utama: suspensi 250 hari | winsor CAR 1% | car_0_1 | -2.439 | 0.000 | -0.614 | 0.131 | 195 |
| utama: suspensi 250 hari | winsor CAR 1% | car_0_5 | -7.878 | 0.000 | -0.267 | 0.016 | 195 |
| utama: suspensi 250 hari | winsor CAR 1% | abn_car_0_5 | -10.452 | 0.000 | -2.510 | 0.016 | 195 |
| utama: suspensi 250 hari | regresi median | car_0 | -2.697 | 0.000 | -0.894 | 0.049 | 195 |
| utama: suspensi 250 hari | regresi median | car_0_1 | -3.159 | 0.000 | -0.870 | 0.033 | 195 |
| utama: suspensi 250 hari | regresi median | car_0_5 | -7.194 | 0.000 | -0.963 | 0.016 | 195 |
| utama: suspensi 250 hari | regresi median | abn_car_0_5 | -9.407 | 0.000 | -3.091 | 0.033 | 195 |
| suspensi 120 hari | dasar | car_0 | -2.300 | 0.000 | -0.801 | 0.098 | 152 |
| suspensi 120 hari | dasar | car_0_1 | -2.980 | 0.000 | -0.583 | 0.066 | 152 |
| suspensi 120 hari | dasar | car_0_5 | -9.415 | 0.000 | -0.025 | 0.016 | 152 |
| suspensi 120 hari | dasar | abn_car_0_5 | -12.208 | 0.000 | -2.423 | 0.016 | 152 |
| suspensi 500 hari | dasar | car_0 | -1.537 | 0.001 | -0.677 | 0.180 | 228 |
| suspensi 500 hari | dasar | car_0_1 | -2.183 | 0.002 | -0.591 | 0.148 | 228 |
| suspensi 500 hari | dasar | car_0_5 | -7.270 | 0.000 | -0.329 | 0.016 | 228 |
| suspensi 500 hari | dasar | abn_car_0_5 | -9.457 | 0.000 | -2.116 | 0.016 | 228 |
| UMA saja 250 hari | dasar | car_0 | -2.360 | 0.000 | -0.472 | 0.033 | 342 |
| UMA saja 250 hari | dasar | car_0_1 | -3.147 | 0.000 | -0.424 | 0.016 | 342 |
| UMA saja 250 hari | dasar | car_0_5 | -6.754 | 0.000 | -0.198 | 0.016 | 342 |
| UMA saja 250 hari | dasar | abn_car_0_5 | -8.687 | 0.000 | -1.688 | 0.016 | 342 |
| UMA atau suspensi 250 hari | dasar | car_0 | -2.302 | 0.000 | -0.474 | 0.033 | 344 |
| UMA atau suspensi 250 hari | dasar | car_0_1 | -3.101 | 0.000 | -0.419 | 0.016 | 344 |
| UMA atau suspensi 250 hari | dasar | car_0_5 | -6.644 | 0.000 | -0.206 | 0.016 | 344 |
| UMA atau suspensi 250 hari | dasar | abn_car_0_5 | -8.575 | 0.000 | -1.717 | 0.016 | 344 |
| intensitas: log(1+jumlah) 250 hari | dasar | car_0 | -1.642 | 0.000 | -0.431 | 0.033 | 344 |
| intensitas: log(1+jumlah) 250 hari | dasar | car_0_1 | -2.334 | 0.000 | -0.347 | 0.016 | 344 |
| intensitas: log(1+jumlah) 250 hari | dasar | car_0_5 | -6.158 | 0.000 | -0.056 | 0.016 | 344 |
| intensitas: log(1+jumlah) 250 hari | dasar | abn_car_0_5 | -8.002 | 0.000 | -1.651 | 0.016 | 344 |