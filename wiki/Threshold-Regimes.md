# Threshold Regimes

Thresholds are behavior-control dials for release decisions (`PROCEED` vs `SILENCE`).

## Regime framing

Threshold interpretation is scoped to a specific:

- model,
- dataset,
- benchmark path,
- and PoR mode.

Do not treat these labels as universal settings.

## Practical regime labels

- **0.35**: conservative
- **0.39**: practical
- **0.42**: transitional / practical-high-coverage
- **0.43**: high-coverage boundary

## Canonical source

For contract language and canonical interpretation, use:

- [`docs/threshold_regime_contract.md`](../docs/threshold_regime_contract.md)

## Calibration reminder

The repository contains several threshold values because they come from different
runs and regimes. Treat each as evidence-scoped. Do not apply `0.39`, `0.35`,
`0.42`, or `0.43` universally without recalibrating the signal contract, model,
and task family. See [Threshold Calibration](./Threshold-Calibration.md).
