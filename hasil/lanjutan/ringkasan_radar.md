# Gorengan Radar v0 (deep learning)

Sampel: jendela 30 hari bursa per saham-hari; label = UMA/suspensi pengawasan BEI dalam 1-5 hari ke depan. Latih s.d. 2025-06-30, validasi s.d. 2025-12-31 (pemilihan epoch), uji 2026 (179,558 jendela, positif 1.28%). nnPU prior pi = 0.01.

## Evaluasi out-of-time (periode uji 2026)

| model | roc_auc | ap | presisi_top1pct | lift_top1pct | basis_positif | auc_kecil | auc_menengah | auc_besar |
|---|---|---|---|---|---|---|---|---|
| logistik | 0.811 | 0.093 | 0.173 | 13.496 | 0.013 | 0.823 | 0.816 | 0.785 |
| gradient_boosting | 0.866 | 0.153 | 0.252 | 19.736 | 0.013 | 0.871 | 0.850 | 0.873 |
| transformer_bce | 0.828 | 0.100 | 0.163 | 12.711 | 0.013 | 0.834 | 0.832 | 0.810 |
| transformer_nnpu | 0.804 | 0.041 | 0.037 | 2.866 | 0.013 | 0.816 | 0.792 | 0.806 |

Catatan: label BEI tidak lengkap, jadi presisi terhadap label adalah batas bawah. AUC per tersil ukuran menunjukkan apakah model membedakan saham di dalam kelompok ukuran yang sama, bukan sekadar menebak saham kecil.

Skor per saham disimpan lokal untuk analisis agregat dan tidak dipublikasikan.

## Uji event: apakah skor radar 20 hari sebelum event memprediksi siapa yang jatuh?

Koefisien = pp CAR per 1 SD skor radar (kontrol 08, HC3). p_placebo = porsi 38 hari crash biasa Agu 2025-Sep 2026 dengan
koefisien <= event (minimum yang mungkin 0,026). "+ label BEI" = setelah mengendalikan riwayat suspensi BEI.

| Model | E1 [0,+5] | p placebo | E1 [0,+5] + label BEI | p placebo | JPM [0,+1] | p placebo | E2 [0,+1] | p placebo |
|---|---|---|---|---|---|---|---|---|
| Gradient boosting | -1,7 | 0,103 | -0,8 | 0,333 | -2,2 | 0,026 | -0,7 | 0,256 |
| Transformer BCE | -3,8 | 0,026 | -2,7 | 0,026 | -1,5 | 0,051 | 0,0 | 0,641 |
| Transformer nnPU | -3,1 | 0,026 | -1,8 | 0,051 | -1,7 | 0,026 | -0,9 | 0,128 |

Bacaan: model dengan skor label terbaik (gradient boosting) BUKAN yang paling menjelaskan kerugian E1. Skor Transformer
menangkap sesuatu yang dihukum E1 di luar label BEI dan lebih ekstrem dari semua hari crash biasa. Di event rating dan
placebo pola ini tidak ada. Rincian: radar_event_<model>.csv.
