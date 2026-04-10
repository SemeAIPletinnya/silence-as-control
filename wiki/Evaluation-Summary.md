# Evaluation Summary

## What the repository already demonstrates

- Multiple repeated runs are committed at different scales and thresholds (`reports/eval_*.jsonl`).
- In documented safe modes (notably 0.35 and 0.39 operating points), accepted precision/risk capture reached 100% in tracked summaries.
- Baseline-vs-PoR comparison is visible through `no_control_success` vs `with_control_success` fields and run pages.
- Drift separation between success/failure cohorts is repeatedly observed in reports and plots.

## Why baseline vs PoR matters

The project’s core change is release policy:
- baseline: release by default,
- PoR: evaluate and decide release.

This makes tradeoffs explicit:
- lower accepted-risk exposure in safe regimes,
- at the cost of non-zero silence rate.

## Silence rate / coverage tradeoff

In the mapped 1000-task artifacts, silence is explicitly:
- 46.5% at threshold 0.35 (`eval_run5_1000_threshold_035.jsonl`)
- 45.6% at threshold 0.39 (`eval_run6_1000_threshold_039.jsonl`)
- 43.7% at threshold 0.42 (`eval_run5_1000_threshold_042.jsonl`)
- 45.0% at threshold 0.43 (`eval_run5_1000_threshold_043.jsonl`)

This indicates consistent withholding behavior rather than always-output behavior.
Coverage therefore depends on chosen threshold regime.

## Evidence discipline

This summary intentionally follows committed artifacts and run docs.
It does not claim universal optimality or deployment-complete proof beyond recorded runs.

## Primary evidence files

- `reports/eval_run4_300_threshold_035.jsonl`
- `reports/eval_run5_1000_threshold_035.jsonl`
- `reports/eval_run6_1000_threshold_039.jsonl`
- `reports/eval_run5_1000_threshold_042.jsonl`
- `reports/eval_run5_1000_threshold_043.jsonl`
- `wiki/runs/Run_4_300_tasks.md`
- `wiki/runs/Run_6_1000_tasks.md`
