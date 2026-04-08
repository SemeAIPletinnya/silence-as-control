# Run 1

_Back to [index](../index.md) · Next: [Run 4](./Run_4_300_tasks.md) · Related: [Baseline vs PoR](../comparisons/Baseline_vs_PoR.md) · Audit: [Evidence Map](../meta/Evidence_Map.md)_

## Documented setup

- Run artifact used: `reports/eval_35_tasks.jsonl`.
- Task count in artifact: **35** records.
- Model field in artifact: **gpt-5.4**.
- `silence_threshold` in artifact: **0.3**.
- `raw_success_threshold` in artifact: **0.55**.

## Reported results

Computed directly from `reports/eval_35_tasks.jsonl` (35 rows):

- Silence count: **5/35** (14.3%).
- Proceed count (`silence=false`): **30/35** (85.7%).
- `raw_success=true`: **33/35** (94.3%).
- `with_control_success=true`: **30/35** (85.7%).
- `no_control_success=true`: **33/35** (94.3%).
- Accepted failures under control (`silence=false` and `raw_success=false`): **0**.
- Silenced-but-raw-success (`silence=true` and `raw_success=true`): **3**.

## What this run supports

- In this 35-task artifact, PoR-style gating is observable as an explicit silence outcome.
- In this artifact, no incorrect output is released under the control path (`accepted failures = 0`).
- The artifact demonstrates a release-vs-silence trade-off in a small run.

## What this run does not support

- It does **not** establish generalization beyond this 35-task set.
- It does **not** establish per-category robustness (no per-category summary is committed for this run page).
- It does **not** establish causal superiority for all thresholds or deployments.

## Artifact references / evidence note

Primary evidence: `reports/eval_35_tasks.jsonl` (record-level fields including `silence`, `raw_success`, `with_control_success`, `no_control_success`, thresholds, and model).

Repository context: `README.md` lists `reports/eval_35_tasks.jsonl` as a tracked artifact.
