# Reports

This directory is the repository's **evidence surface** for run artifacts, summary visuals, and small reproducibility inputs.

## What belongs here

- **Tracked run artifacts**: canonical JSONL outputs from evaluation runs.
- **Plots / visual summaries**: stable images used for quick evidence inspection.
- **Helper scripts**: local analysis/plot scripts that generate or summarize report outputs.
- **Reproducibility inputs**: small, curated CSVs used by sandbox or extension-lane experiments.

## Tracked run artifacts (JSONL)

- `eval_35_tasks.jsonl`
- `eval_100_tasks.jsonl`
- `eval_run2_100_tasks.jsonl`
- `eval_run3.jsonl`
- `eval_run4_300_threshold_035.jsonl`
- `eval_run5_1000_threshold_035.jsonl`
- `eval_run5_1000_threshold_042.jsonl`
- `eval_run5_1000_threshold_043.jsonl`
- `eval_run6_1000_threshold_039.jsonl`

## Reproducibility lane artifacts (CSV)

- `borderline_maybe_short_regen.csv`  
  Curated MAYBE_SHORT_REGEN lane input (8 task IDs) used by the short-regen sandbox workstream.
- `borderline_pocket_labels.csv`  
  Full 16-case manual label table for the near-boundary borderline pocket (RECOVERABLE / MAYBE_SHORT_REGEN / KEEP_SILENCE).

## Plot files (tracked visual summaries)

- `threshold_control_curve.png`
- `accepted_failures_comparison.png`
- `drift_separation_comparison.png`
- `metrics.png`
- `drift.png`
- `drift_clean.png`

## Helper scripts

- `plot_threshold_comparison.py`

## Interpretation notes

- JSONL files are **run outputs** and should be treated as primary evidence.
- CSV files are **curated reproducibility inputs**, not runtime logic.
- PNG files are **visual summaries**; interpretation should be anchored to the corresponding JSONL artifacts.

## Maintenance policy

Keep this directory disciplined:

- Prefer small, auditable artifacts.
- Do not add generated noise files or scratch outputs.
- Keep filenames explicit about run context (task count, threshold, or lane purpose).
