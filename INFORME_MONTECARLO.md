# Monte Carlo robustness assessment: 1,000 runs × 17 pavement sections

## Design and traceability

The supplied workbook contains 1,000 simulated runs with 17 consecutive 300-m sections per run and six original indicators (CF, TX, IRI, JF, LTE, DEF). The original notebook functions were applied without changing the AHP weights, normative thresholds, strict/tolerant progression rules, DWT/CDA parameters, or original zone records and overlaps. The analyses below are post-processing only. M1 is a global AHP classification and therefore has no comparable dimension-specific hierarchical coverage or Poor-reporting rate; these are intentionally shown as missing, not zero.

**Important limitation:** the workbook alone does not establish the Monte Carlo generation mechanism or independence between runs. Confidence intervals describe variation across the supplied runs under a conditional run-level resampling assumption, not field-validated uncertainty.

## Results

| Metodo   |   Corridas |   Fronteras_media |   Fronteras_sd |   Reduccion_media_pct |   Reduccion_sd_pct |   Cobertura_media_pct |   Cobertura_sd_pct |   Reporte_criticos_media_pct |   Reporte_criticos_sd_pct |   Ambiguedades_media |   AUC_media |   Contraste_diferencia_media |
|:---------|-----------:|------------------:|---------------:|----------------------:|-------------------:|----------------------:|-------------------:|-----------------------------:|--------------------------:|---------------------:|------------:|-----------------------------:|
| M1       |       1000 |            16     |          0     |                 0     |              0     |               nan     |            nan     |                      nan     |                   nan     |              nan     |     nan     |                      nan     |
| M2       |       1000 |            16     |          0     |                 0     |              0     |                48.239 |              5.575 |                       11.723 |                     5.955 |                0     |     nan     |                      nan     |
| M3       |       1000 |            16     |          0     |                 0     |              0     |                86.19  |              5.604 |                       23.055 |                     6.609 |                0     |     nan     |                      nan     |
| M4       |       1000 |            11.724 |          2.073 |                26.725 |             12.954 |                47.98  |             10.156 |                       28.546 |                    11.572 |                6.992 |       0.535 |                        0.012 |
| M5       |       1000 |            11.724 |          2.073 |                26.725 |             12.954 |                75.645 |             13.087 |                       50.422 |                     8.733 |               13.439 |       0.535 |                        0.012 |

## Paired method comparisons

| Comparacion   | Metrica              |    N |   Diferencia_media |   Mediana |    Q025 |   Q975 |   IC95_bootstrap_media_inferior |   IC95_bootstrap_media_superior |   Proporcion_positiva |   Proporcion_cero |
|:--------------|:---------------------|-----:|-------------------:|----------:|--------:|-------:|--------------------------------:|--------------------------------:|----------------------:|------------------:|
| M4-M2         | Reduccion_pct        | 1000 |             26.725 |    25     |   6.25  | 56.25  |                          25.912 |                          27.575 |                 0.985 |             0.015 |
| M4-M2         | Cobertura_pct        | 1000 |             -0.259 |    -1.961 | -17.647 | 21.569 |                          -0.908 |                           0.392 |                 0.406 |             0.075 |
| M4-M2         | Reporte_criticos_pct | 1000 |             16.823 |    17.192 |  -9.528 | 40.741 |                          16.006 |                          17.624 |                 0.876 |             0.047 |
| M5-M3         | Reduccion_pct        | 1000 |             26.725 |    25     |   6.25  | 56.25  |                          25.912 |                          27.575 |                 0.985 |             0.015 |
| M5-M3         | Cobertura_pct        | 1000 |            -10.545 |    -9.804 | -39.216 | 11.765 |                         -11.392 |                          -9.722 |                 0.209 |             0.046 |
| M5-M3         | Reporte_criticos_pct | 1000 |             27.368 |    27.586 |   6.661 | 48.194 |                          26.724 |                          28.022 |                 0.996 |             0.001 |
| M5-M4         | Reduccion_pct        | 1000 |              0     |     0     |   0     |  0     |                           0     |                           0     |                 0     |             1     |
| M5-M4         | Cobertura_pct        | 1000 |             27.665 |    27.451 |   5.833 | 52.941 |                          26.859 |                          28.486 |                 0.989 |             0.011 |
| M5-M4         | Reporte_criticos_pct | 1000 |             21.876 |    20.833 |   0     | 48.392 |                          21.111 |                          22.671 |                 0.959 |             0.041 |
| M3-M2         | Reduccion_pct        | 1000 |              0     |     0     |   0     |  0     |                           0     |                           0     |                 0     |             1     |
| M3-M2         | Cobertura_pct        | 1000 |             37.951 |    37.255 |  25.441 | 50.98  |                          37.537 |                          38.378 |                 1     |             0     |
| M3-M2         | Reporte_criticos_pct | 1000 |             11.331 |    11.111 |   2.566 | 22.581 |                          11.003 |                          11.673 |                 0.975 |             0.025 |

## Metric definitions

- Boundary count: distinct original internal endpoints, deduplicated only for counting, among 16 possible positions; reduction = (16−count)/16 × 100.
- Coverage: number of unique (section, dimension) pairs having an original stage label (Bueno/Regular/Malo), divided by 51. Multiple overlapping original records are preserved, but a pair is counted once.
- Conservative critical reporting: for each dimension, at least one constituent original indicator is Malo; numerator counts those pairs with a dimension-specific final output label Malo. This is not validated sensitivity or a false-negative rate.
- Boundary contrast: Euclidean distance of adjacent six-indicator profiles after pooled min-max normalization over all 1,000 runs, divided by sqrt(6); AUC compares retained and omitted boundary positions within each run. Undefined when there are no omitted positions.
- Bootstrap intervals are percentile intervals for the paired run-level mean difference (3,000 resamples, fixed seed 1729).

## Interpretation restrictions

Boundary reduction is not demonstrated improved homogeneity, economic optimization, or diagnostic accuracy. Higher hierarchical coverage is not automatically better classification quality. Overlapping M4/M5 outputs are not reconciled. The original two scenarios remain separate from these Monte Carlo simulations.
