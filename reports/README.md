# Reports

This directory is the repository's **evidence surface** for run artifacts, summary visuals, and small reproducibility inputs.

Signal and threshold semantics across layers are defined in `docs/signal_and_threshold_contract.md`. This reports directory corresponds to the evidence/eval contract.

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
- `short_regen_manual_scoring_template.csv`
  Manual scoring template for the 8 MAYBE_SHORT_REGEN cases (template only; not claimed scored results).

## Sandbox artifact policy (short_regen_sandbox)

- Default sandbox outputs are:
  - `reports/short_regen_sandbox_results.jsonl`
  - `reports/short_regen_sandbox_report.md`
- These files are **normally regenerated locally** and are not required committed evidence by default.
- Before treating sandbox outputs as evidence, runs should include reproducibility metadata at minimum:
  - model
  - run timestamp (UTC)
  - input CSV path
  - output/report paths
  - retry guidance version
  - run id (and git SHA when available)
- Sandbox outputs establish local lane behavior only; they do **not** by themselves establish primitive changes, threshold retuning, or production readiness.
- Optional retry-side scoring from sandbox runs is extension-layer evidence support, not primitive scoring or historical run replacement.
- See `docs/maybe_short_regen_formalization.md` for conservative formalization criteria and non-claims.

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


## Navigation note

For conservative claim-to-artifact mapping, see `docs/evidence_map.md` and `docs/threshold_regime_contract.md`.
Recent local SimpleQA/Ollama artifact directories are:

- `results/simpleqa_ollama_qwen3_4b_100_v2_retry/`
- `results/simpleqa_ollama_qwen3_8b_100_v2/`
