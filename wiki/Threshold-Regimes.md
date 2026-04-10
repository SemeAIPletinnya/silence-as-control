# Threshold Regimes

Threshold is an **operational control dial** for release behavior.
Raising/lowering threshold shifts the safety-vs-coverage profile.

## Mapped operating points

- **0.35** -> safe / conservative regime
- **0.39** -> practical safe anchor
- **0.42** -> transitional / balanced (boundary starts to appear)
- **0.43** -> boundary / leakage zone

These labels summarize observed behavior in committed run artifacts and should be interpreted as repository-scoped evidence, not universal settings.

## Coverage vs safety tradeoff

Across mapped runs:
- Safer settings maintain stronger accepted-output precision/risk capture but silence more candidates.
- Boundary settings recover some coverage but begin allowing accepted failures.

Use threshold operationally:
- choose lower-risk profiles for strict release control,
- then tune for acceptable coverage in the target domain.

## Evidence basis

Primary threshold artifacts:
- `reports/eval_run5_1000_threshold_035.jsonl`
- `reports/eval_run6_1000_threshold_039.jsonl`
- `reports/eval_run5_1000_threshold_042.jsonl`
- `reports/eval_run5_1000_threshold_043.jsonl`

Related context:
- `wiki/runs/Run_4_300_tasks.md`
- `wiki/runs/Run_6_1000_tasks.md`
