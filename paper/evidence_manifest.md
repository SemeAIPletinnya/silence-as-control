# Evidence Manifest

This manifest maps paper claims to concrete repository artifacts.

## Core claim: decoupling generation from release

- Primitive framing and release gate behavior:
  - `paper/main.tex`
  - `docs/signal_and_threshold_contract.md`

## Metric provenance (tables)

### Run-scale snapshot table

- Generated file: `paper/figures/results_by_run_scale.csv`
- Source artifacts:
  - `reports/eval_35_tasks.jsonl`
  - `reports/eval_100_tasks.jsonl`
  - `reports/eval_run4_300_threshold_035.jsonl`
  - `reports/eval_run6_1000_threshold_039.jsonl`
- Generator script: `scripts/aggregate_paper_results.py`
- LaTeX table fragment: `paper/figures/table_run_scale.tex` via `scripts/make_paper_figures.py`

### 1000-task threshold sweep table (0.35/0.39/0.42/0.43)

- Generated file: `paper/figures/results_1000_threshold_sweep.csv`
- Source artifacts:
  - `reports/eval_run5_1000_threshold_035.jsonl`
  - `reports/eval_run6_1000_threshold_039.jsonl`
  - `reports/eval_run5_1000_threshold_042.jsonl`
  - `reports/eval_run5_1000_threshold_043.jsonl`
- Generator script: `scripts/aggregate_paper_results.py`
- LaTeX table fragment: `paper/figures/table_threshold_sweep.tex` via `scripts/make_paper_figures.py`

## Boundary pocket / MAYBE_SHORT_REGEN evidence

- Primary artifact:
  - `reports/borderline_maybe_short_regen.csv`
- Paper-packaged exports:
  - `paper/cases/borderline_maybe_short_regen.csv`
  - `paper/cases/borderline_maybe_short_regen_summary.json`
- Export script:
  - `scripts/export_boundary_cases.py`

This lane supports the boundary-pocket discussion near threshold 0.39. It is extension-layer evidence and does not alter primitive core behavior.

## Explicit non-claims

- No claim of universal truth guarantee.
- No claim that threshold 0.39 is globally optimal.
- No claim that binary PoR is already tri-action routing.
