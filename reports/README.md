# Reports

This directory is the repository's **evidence surface** for run artifacts, summary visuals, and small reproducibility inputs.

Signal and threshold semantics across layers are defined in `docs/signal_and_threshold_contract.md`. This reports directory corresponds to the evidence/eval contract.

## What belongs here

- **Tracked run artifacts**: canonical JSONL outputs from evaluation runs.
- **Plots / visual summaries**: stable images used for quick evidence inspection.
- **Helper scripts**: local analysis/plot scripts that generate or summarize report outputs.
- **Reproducibility inputs**: small, curated CSVs used by sandbox or extension-lane experiments.


## LangChain/OpenAI action-risk Run 06 summaries

Run 06 is a 1000-case synthetic action-risk integration/deployment validation benchmark. The documented progression through hardened v4 used the same model (`gpt-4.1-mini`), same dataset (`data/action_risk/action_risk_1000.jsonl`), same threshold, and no PoR core change; release-layer hardening changed the review/release profile.

| Stage | NEEDS_REVIEW | False accepts | Estimated cost saved | Summary artifact |
| --- | ---: | ---: | ---: | --- |
| Initial | 146 | 664 | 8,518 (~17.7%) | [`reports/langchain_openai_summary_06_1000case.md`](langchain_openai_summary_06_1000case.md) |
| Hardened v1 | 310 | 505 | 18,227 (~38.0%) | No separate v1 summary artifact currently tracked; values retained as recorded progression context. |
| Hardened v2 | 424 | 397 | 23,210 (~48.35%) | [`reports/langchain_openai_summary_06_1000case_hardened_v2.md`](langchain_openai_summary_06_1000case_hardened_v2.md) |
| Hardened v3 | 458 | 368 | 25,677 (~53.49%) | [`reports/langchain_openai_summary_06_1000case_hardened_v3.md`](langchain_openai_summary_06_1000case_hardened_v3.md) |
| Hardened v4 | 578 | 247 | 33,174 (~69.11%) | [`reports/langchain_openai_summary_06_1000case_hardened_v4.md`](langchain_openai_summary_06_1000case_hardened_v4.md) |

See [`docs/langchain_openai_action_risk_benchmark.md`](../docs/langchain_openai_action_risk_benchmark.md) for the full table, v4 false-accept class breakdown, and interpretation notes. This evidence surface does not imply model improvement, threshold retuning, external validation, or universal safety.

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
