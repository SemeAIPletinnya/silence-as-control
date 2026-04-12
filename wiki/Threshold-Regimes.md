# Threshold Regimes

Threshold is an **operational control dial** for release behavior.
Raising or lowering threshold shifts the safety-vs-coverage profile.

## Mapped operating points

- **0.35** -> conservative / strict release-control regime
- **0.39** -> practical safe anchor
- **0.42** -> transitional / balanced regime where leakage pressure begins to appear
- **0.43** -> boundary / leakage-visible regime

These labels summarize observed behavior in committed run artifacts and should be interpreted as repository-scoped evidence, not universal settings.

## Coverage vs safety tradeoff

Across mapped runs:

- Safer settings maintain stronger accepted-output precision and risk capture, but silence more candidates.
- Transitional and boundary settings recover some coverage, but accepted failures begin to reappear.

Use threshold operationally:

- choose lower-risk profiles for strict release control,
- then tune for acceptable coverage in the target domain.

## Evidence basis

Primary threshold artifacts:

- `reports/eval_run5_1000_threshold_035.jsonl`
- `reports/eval_run6_1000_threshold_039.jsonl`
- `reports/eval_run5_1000_threshold_042.jsonl`
- `reports/eval_run5_1000_threshold_043.jsonl`

Related run context:

- `wiki/runs/Run_4_300_tasks.md`
- `wiki/runs/Run_6_1000_tasks.md`

Related visual summaries in `reports/`:

- `reports/threshold_control_curve.png`
- `reports/accepted_failures_comparison.png`
- `reports/drift_separation_comparison.png`

## Interpretation discipline

This page documents repository-observed operating behavior.

It does **not** establish:

- a universal best threshold,
- guaranteed transfer across domains,
- or a one-time calibration that remains correct under all runtime conditions.
