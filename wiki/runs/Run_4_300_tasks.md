# Run 4 — 300 Tasks

_Back to [index](../index.md) · Previous: [Run 1](./Run_1.md) · Next: [Run 6](./Run_6_1000_tasks.md) · Related: [Baseline vs PoR](../comparisons/Baseline_vs_PoR.md) · Audit: [Evidence Map](../meta/Evidence_Map.md)_

## Documented setup

- Run artifact used: `reports/eval_run4_300_threshold_035.jsonl`.
- Task count in artifact: **300** records.
- Model field in artifact: **gpt-5.4**.
- `silence_threshold` in artifact: **0.35**.
- `raw_success_threshold` in artifact: **0.55**.
- README labels this operating point as “Run #4 — 300 tasks (threshold 0.35)”.

## Reported results

Computed directly from `reports/eval_run4_300_threshold_035.jsonl` (300 rows):

- Silence count: **108/300** (36.0%).
- Proceed count (`silence=false`): **192/300** (64.0%).
- `raw_success=true`: **196/300** (65.3%).
- `with_control_success=true`: **192/300** (64.0%).
- `no_control_success=true`: **196/300** (65.3%).
- Accepted failures under control (`silence=false` and `raw_success=false`): **0**.
- Silenced-but-raw-success (`silence=true` and `raw_success=true`): **4**.

## What this run supports

- At the documented threshold (0.35), release is conditional rather than automatic.
- In this 300-task artifact, control-path accepted failures are zero.
- The run shows measurable silence as a control action (not just an implicit timeout).

## What this run does not support

- It does **not** prove correctness outside this recorded task mix.
- It does **not** prove that threshold 0.35 is optimal across all operating conditions.
- It does **not** provide a full per-class error analysis in the current committed summary docs.

## Artifact references / evidence note

Primary evidence: `reports/eval_run4_300_threshold_035.jsonl`.

Repository context: `README.md` names this run and lists the JSONL artifact under tracked reports.
