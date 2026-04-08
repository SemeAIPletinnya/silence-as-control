# Baseline vs PoR

_Back to [index](../index.md) · Related: [Release Control Layer](../architecture/Release_Control_Layer.md) · Audit: [Evidence Map](../meta/Evidence_Map.md)_

## Comparison objective

This page contrasts two documented policies:

1. **Baseline (direct release)**: policy contrast for release-by-default behavior.
2. **PoR-gated release**: policy contrast for conditional release with explicit silence.

In the run artifacts, `no_control_success` and `with_control_success` are evaluation-path outcome fields used to compare those two paths.

## Policy-level difference

| Dimension | Baseline | PoR-gated |
|---|---|---|
| Default action | Release | Evaluate then decide |
| Non-release mode | Not explicit in baseline path | Explicit silence outcome |
| Risk handling location | After release | Before release |

## Run-grounded snapshots

From committed artifacts:

- Run 1 (`reports/eval_35_tasks.jsonl`):
  - `no_control_success`: 33/35
  - `with_control_success`: 30/35
  - silence: 5/35
- Run 4 (`reports/eval_run4_300_threshold_035.jsonl`):
  - `no_control_success`: 196/300
  - `with_control_success`: 192/300
  - silence: 108/300
- Run 6 (`reports/eval_run6_1000_threshold_039.jsonl`):
  - `no_control_success`: 559/1000
  - `with_control_success`: 544/1000
  - silence: 456/1000

Across these three artifacts, accepted failures under control (`silence=false` and `raw_success=false`) are zero.

All numeric snapshots above are taken from committed run artifacts and mirrored in the linked run pages.

## Interpretation boundary

PoR does not guarantee truth.
The documented evidence supports a release-policy shift with explicit silence and zero accepted failures in the listed artifacts.
It does not establish universal performance outside those setups.

See run pages for the full limitation statements:

- [Run 1](../runs/Run_1.md)
- [Run 4 (300 tasks)](../runs/Run_4_300_tasks.md)
- [Run 6 (1000 tasks)](../runs/Run_6_1000_tasks.md)
