# Apakah sinyal radar sekadar run-up reversal?

Koefisien = pp CAR per SD skor radar (S4 interaksi: per SD radar x SD run-up). p_placebo = porsi 38 hari crash biasa dengan koefisien <= event (minimum 0,026). Run-up = return pra-event (hari -60 s.d. -2), return 5 dan 20 hari terakhir, dan return harian maksimum 20 hari.

| skor | sel | spesifikasi | koef | p | n | p_placebo |
|---|---|---|---|---|---|---|
| nnpu_s0 | E1 car_0_5 | S1 dasar | -3.073 | 0.000 | 792 | 0.026 |
| nnpu_s0 | E1 car_0_5 | S2 + run-up fleksibel | -3.445 | 0.000 | 792 | 0.026 |
| nnpu_s0 | E1 car_0_5 | S3 radar ortogonal | -2.543 | 0.000 | 792 | 0.026 |
| nnpu_s0 | E1 car_0_5 | S4 interaksi (radar x run-up) | 1.152 | 0.180 | 792 | 0.974 |
| nnpu_s0 | E1 car_0_5 | S4 efek utama saat run-up = 0 | -3.513 | 0.000 | 792 | 0.026 |
| nnpu_s0 | E1 car_0_5 | S5 tanpa run-up (<= median) | -4.625 | 0.000 | 396 | 0.026 |
| nnpu_s0 | E1 car_0_1 | S1 dasar | -1.878 | 0.000 | 792 | 0.026 |
| nnpu_s0 | E1 car_0_1 | S2 + run-up fleksibel | -1.105 | 0.004 | 792 | 0.026 |
| nnpu_s0 | E1 car_0_1 | S3 radar ortogonal | -0.818 | 0.004 | 792 | 0.026 |
| nnpu_s0 | E1 car_0_1 | S4 interaksi (radar x run-up) | 0.541 | 0.300 | 792 | 0.949 |
| nnpu_s0 | E1 car_0_1 | S4 efek utama saat run-up = 0 | -1.407 | 0.000 | 792 | 0.026 |
| nnpu_s0 | E1 car_0_1 | S5 tanpa run-up (<= median) | -1.398 | 0.003 | 396 | 0.026 |
| nnpu_s0 | JPM car_0_1 | S1 dasar | -1.724 | 0.000 | 805 | 0.026 |
| nnpu_s0 | JPM car_0_1 | S2 + run-up fleksibel | -0.691 | 0.025 | 805 | 0.103 |
| nnpu_s0 | JPM car_0_1 | S3 radar ortogonal | -0.558 | 0.025 | 805 | 0.103 |
| nnpu_s0 | JPM car_0_1 | S4 interaksi (radar x run-up) | 0.146 | 0.737 | 805 | 0.692 |
| nnpu_s0 | JPM car_0_1 | S4 efek utama saat run-up = 0 | -0.752 | 0.004 | 805 | 0.077 |
| nnpu_s0 | JPM car_0_1 | S5 tanpa run-up (<= median) | -1.626 | 0.000 | 403 | 0.026 |
| bce_s0 | E1 car_0_5 | S1 dasar | -3.794 | 0.000 | 792 | 0.026 |
| bce_s0 | E1 car_0_5 | S2 + run-up fleksibel | -3.701 | 0.000 | 792 | 0.026 |
| bce_s0 | E1 car_0_5 | S3 radar ortogonal | -2.926 | 0.000 | 792 | 0.026 |
| bce_s0 | E1 car_0_5 | S4 interaksi (radar x run-up) | -0.198 | 0.842 | 792 | 0.385 |
| bce_s0 | E1 car_0_5 | S4 efek utama saat run-up = 0 | -4.154 | 0.000 | 792 | 0.026 |
| bce_s0 | E1 car_0_5 | S5 tanpa run-up (<= median) | -3.930 | 0.000 | 396 | 0.026 |
| bce_s0 | E1 car_0_1 | S1 dasar | -1.757 | 0.000 | 792 | 0.026 |
| bce_s0 | E1 car_0_1 | S2 + run-up fleksibel | -0.994 | 0.002 | 792 | 0.051 |
| bce_s0 | E1 car_0_1 | S3 radar ortogonal | -0.789 | 0.002 | 792 | 0.077 |
| bce_s0 | E1 car_0_1 | S4 interaksi (radar x run-up) | 0.642 | 0.163 | 792 | 0.949 |
| bce_s0 | E1 car_0_1 | S4 efek utama saat run-up = 0 | -1.170 | 0.000 | 792 | 0.051 |
| bce_s0 | E1 car_0_1 | S5 tanpa run-up (<= median) | -1.368 | 0.000 | 396 | 0.051 |
| bce_s0 | JPM car_0_1 | S1 dasar | -1.546 | 0.000 | 805 | 0.051 |
| bce_s0 | JPM car_0_1 | S2 + run-up fleksibel | -0.467 | 0.082 | 805 | 0.282 |
| bce_s0 | JPM car_0_1 | S3 radar ortogonal | -0.416 | 0.081 | 805 | 0.256 |
| bce_s0 | JPM car_0_1 | S4 interaksi (radar x run-up) | -0.090 | 0.817 | 805 | 0.462 |
| bce_s0 | JPM car_0_1 | S4 efek utama saat run-up = 0 | -0.498 | 0.066 | 805 | 0.308 |
| bce_s0 | JPM car_0_1 | S5 tanpa run-up (<= median) | -1.502 | 0.000 | 403 | 0.051 |
| ensembel_8 | E1 car_0_5 | S1 dasar | -3.836 | 0.000 | 792 | 0.026 |
| ensembel_8 | E1 car_0_5 | S2 + run-up fleksibel | -4.383 | 0.000 | 792 | 0.026 |
| ensembel_8 | E1 car_0_5 | S3 radar ortogonal | -3.182 | 0.000 | 792 | 0.026 |
| ensembel_8 | E1 car_0_5 | S4 interaksi (radar x run-up) | 0.202 | 0.818 | 792 | 0.718 |
| ensembel_8 | E1 car_0_5 | S4 efek utama saat run-up = 0 | -4.526 | 0.000 | 792 | 0.026 |
| ensembel_8 | E1 car_0_5 | S5 tanpa run-up (<= median) | -4.913 | 0.000 | 396 | 0.026 |
| ensembel_8 | E1 car_0_1 | S1 dasar | -2.130 | 0.000 | 792 | 0.026 |
| ensembel_8 | E1 car_0_1 | S2 + run-up fleksibel | -1.341 | 0.000 | 792 | 0.026 |
| ensembel_8 | E1 car_0_1 | S3 radar ortogonal | -0.976 | 0.000 | 792 | 0.026 |
| ensembel_8 | E1 car_0_1 | S4 interaksi (radar x run-up) | 0.388 | 0.445 | 792 | 0.872 |
| ensembel_8 | E1 car_0_1 | S4 efek utama saat run-up = 0 | -1.642 | 0.000 | 792 | 0.026 |
| ensembel_8 | E1 car_0_1 | S5 tanpa run-up (<= median) | -1.621 | 0.000 | 396 | 0.026 |
| ensembel_8 | JPM car_0_1 | S1 dasar | -1.854 | 0.000 | 805 | 0.026 |
| ensembel_8 | JPM car_0_1 | S2 + run-up fleksibel | -0.707 | 0.027 | 805 | 0.128 |
| ensembel_8 | JPM car_0_1 | S3 radar ortogonal | -0.558 | 0.027 | 805 | 0.128 |
| ensembel_8 | JPM car_0_1 | S4 interaksi (radar x run-up) | -0.051 | 0.904 | 805 | 0.513 |
| ensembel_8 | JPM car_0_1 | S4 efek utama saat run-up = 0 | -0.714 | 0.014 | 805 | 0.154 |
| ensembel_8 | JPM car_0_1 | S5 tanpa run-up (<= median) | -1.875 | 0.000 | 403 | 0.026 |