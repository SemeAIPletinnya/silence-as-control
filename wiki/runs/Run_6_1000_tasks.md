# Run 6 — 1000 Tasks

_Back to [index](../index.md) · Previous: [Run 4](./Run_4_300_tasks.md) · Related: [Baseline vs PoR](../comparisons/Baseline_vs_PoR.md) · Audit: [Evidence Map](../meta/Evidence_Map.md)_

## Documented setup

- Run artifact used: `reports/eval_run6_1000_threshold_039.jsonl`.
- Task count in artifact: **1000** records.
- Model field in artifact: **gpt-5.4**.
- `silence_threshold` in artifact: **0.39**.
- `raw_success_threshold` in artifact: **0.55**.
- README labels this operating point as “Run #6 — 1000 tasks (threshold 0.39)”.

## Reported results

Computed directly from `reports/eval_run6_1000_threshold_039.jsonl` (1000 rows):

- Silence count: **456/1000** (45.6%).
- Proceed count (`silence=false`): **544/1000** (54.4%).
- `raw_success=true`: **559/1000** (55.9%).
- `with_control_success=true`: **544/1000** (54.4%).
- `no_control_success=true`: **559/1000** (55.9%).
- Accepted failures under control (`silence=false` and `raw_success=false`): **0**.
- Silenced-but-raw-success (`silence=true` and `raw_success=true`): **15**.

## What this run supports

- At 1000 tasks and threshold 0.39, the artifact still shows explicit gated release with non-trivial silence volume.
- In this artifact, accepted failures under the control path are zero.
- The run supports interpreting silence as an implemented release-control outcome, not only a narrative claim.

## What this run does not support

- It does **not** prove universal robustness beyond this dataset and metric design.
- It does **not** establish that 0.39 is globally optimal; it is only a documented operating point.
- It does **not** establish sufficiency of these metrics for all deployment risk models.

## Artifact references / evidence note

Primary evidence: `reports/eval_run6_1000_threshold_039.jsonl`.

Repository context: `README.md` names this run and lists the JSONL artifact under tracked reports.
