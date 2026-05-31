# Appendix Tables

These tables were moved out of the camera-ready proceedings PDF to satisfy the
22-page ACNS limit. They correspond to the validation, sensitivity, and
regression details summarized in the main paper.

## Inter-Rater Reliability

Human manual coding was compared against GPT-4o on a stratified random sample
of 50 papers.

| Dim. | Description | Agree | Kappa | Alpha_K | AC1 | PABAK | Interpretation |
|---|---|---:|---:|---:|---:|---:|---|
| G1 | Focus (atk/def/both) | 88% | 0.80 | 0.80 | 0.85 | 0.76 | Almost Perfect |
| G3 | Data Modality | 86% | 0.80 | 0.81 | 0.84 | 0.72 | Almost Perfect |
| G6 | Real System | 90% | 0.75 | 0.75 | 0.83 | 0.80 | Substantial |
| G2 | Attack Type | 80% | 0.74 | 0.74 | 0.75 | 0.60 | Substantial |
| Q1 | Gradients | 82% | 0.73 | 0.73 | 0.73 | 0.64 | Substantial |
| T1 | Threat Model | 78% | 0.71 | 0.71 | 0.73 | 0.56 | Substantial |
| G5 | Code Release | 84% | 0.69 | 0.68 | 0.68 | 0.68 | Substantial |
| Q2 | Query Budget | 88% | 0.66 | 0.66 | 0.85 | 0.76 | Substantial |
| G4 | Economic Analysis | 100% | N/A | N/A | 1.00 | 1.00 | Perfect |

For Q2, the reported values collapse `None` and `NA`; the strict four-category
kappa is 0.25. For G4, kappa and Krippendorff's alpha are undefined because
both raters coded all 50 papers as `No`.

## Gap Score Sensitivity

| Weighting Scheme | Weights [WB, Grad, Q, RS, Econ] | Mean (normalized) |
|---|---|---:|
| Equal (default) | [1, 1, 1, 1, 1] | 0.505 |
| Practitioner-weighted | [1, 1, 1, 2, 2] | 0.620 |
| Without economic | [1, 1, 1, 1, 0] | 0.388 |
| Threat-model focused | [2, 2, 1, 1, 1] | 0.438 |

The alternative weighting schemes produced highly correlated rankings
(Spearman rho = 0.96, p < 1e-256 between equal and practitioner-weighted
schemes).

## Multivariate Logistic Regression

Models were fit on papers from complete years 2022--2024 (N = 426), controlling
for year, venue, data domain, and paper focus where applicable.

| Predictor | White-box OR [95% CI] | Real-system OR [95% CI] | Gradient OR [95% CI] |
|---|---:|---:|---:|
| Year (per year) | 0.95 [0.71, 1.28] | 1.02 [0.70, 1.49] | 1.25 [0.89, 1.76] |
| Images (vs Audio) | 2.15 [0.82, 5.63] | 0.09 [0.04, 0.23] | 5.46 [1.46, 20.4] |
| Text (vs Audio) | 0.35 [0.09, 1.41] | 0.25 [0.09, 0.72] | 2.04 [0.45, 9.33] |
| Malware (vs Audio) | 1.02 [0.26, 3.98] | 0.19 [0.05, 0.70] | 3.08 [0.53, 18.0] |
| Other (vs Audio) | 1.12 [0.40, 3.13] | 0.06 [0.02, 0.17] | 3.55 [0.89, 14.1] |
| Defense (vs Attack) | -- | -- | 4.94 [1.32, 18.6] |

Venue dummy variables were included and were not significant (p > 0.10) for all
outcomes.
