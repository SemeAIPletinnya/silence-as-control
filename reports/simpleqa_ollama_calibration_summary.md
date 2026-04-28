# SimpleQA / Ollama Calibration Summary

This report compares three calibration variants for the SimpleQA/Ollama benchmark path:

- `v2`
- `v2.1`
- `v2.2`

The goal is to evaluate the risk-coverage tradeoff of the Silence-as-Control / PoR release gate across multiple thresholds.

## Summary

| Version | Threshold | Answer Rate | Silence Rate | Accepted Correct | Accepted Wrong | Accepted Precision | False Silence |
|---|---:|---:|---:|---:|---:|---:|---:|
| v2 | 0.35 | 62% | 38% | 60 | 2 | 96.77% | 34 |
| v2 | 0.39 | 70% | 30% | 67 | 3 | 95.71% | 27 |
| v2 | 0.42 | 78% | 22% | 75 | 3 | 96.15% | 19 |
| v2 | 0.43 | 80% | 20% | 77 | 3 | 96.25% | 17 |
| v2.1 | 0.35 | 68% | 32% | 64 | 4 | 94.12% | 30 |
| v2.1 | 0.39 | 73% | 27% | 69 | 4 | 94.52% | 25 |
| v2.1 | 0.42 | 81% | 19% | 76 | 5 | 93.83% | 18 |
| v2.1 | 0.43 | 81% | 19% | 76 | 5 | 93.83% | 18 |
| v2.2 | 0.35 | 64% | 36% | 60 | 4 | 93.75% | 34 |
| v2.2 | 0.39 | 70% | 30% | 66 | 4 | 94.29% | 28 |
| v2.2 | 0.42 | 72% | 28% | 68 | 4 | 94.44% | 26 |
| v2.2 | 0.43 | 73% | 27% | 69 | 4 | 94.52% | 25 |

## Interpretation

`v2` is the strongest current calibration variant. It provides the best risk-coverage tradeoff, reaching up to 80% answer coverage with 96.25% accepted precision and 3 accepted wrong cases at threshold 0.43.

The conservative `v2 @ 0.35` setting produces the lowest leakage among the evaluated v2-family variants, with 62% answer coverage, 96.77% accepted precision, and 2 accepted wrong cases.

`v2.1` behaves as an aggressive coverage boundary. It reaches 81% answer coverage, but accepted wrong cases increase to 5 and accepted precision drops to 93.83% at thresholds 0.42 and 0.43.

`v2.2` is a negative calibration result. It does not improve the risk-coverage tradeoff relative to v2: accepted wrong cases remain at 4 across all thresholds, while answer coverage is lower than v2 at higher thresholds.

## Current calibration labels

| Label | Configuration | Meaning |
|---|---|---|
| Conservative anchor | v2 @ 0.35 | Lowest observed leakage in this calibration family |
| Practical anchor | v2 @ 0.43 | Best current deployment-like risk-coverage tradeoff |
| Aggressive boundary | v2.1 @ 0.42 / 0.43 | Maximum coverage, higher leakage |
| Regression / negative result | v2.2 | Weaker calibration than v2 |

## Research note

These results show that Silence-as-Control does not behave as a single magic threshold. It exposes a calibration surface: different versions and thresholds produce different tradeoffs between coverage, silence, false silence, and accepted wrong cases.

For this SimpleQA/Ollama benchmark path, v2 should remain the preferred configuration until a later calibration variant improves either accepted precision, leakage count, or answer coverage without weakening release control.
