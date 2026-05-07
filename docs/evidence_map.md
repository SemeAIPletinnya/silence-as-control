# Evidence Map

This map is a navigation layer for claims and evidence artifacts.

## Core claim

**Generation != release.**

Silence-as-Control (PoR) is a release-control layer: generation quality and release safety are related but not identical.

## Core primitive files

- `src/silence_as_control/control.py`
- `api/core_primitive.py`

These define the primitive thresholded release behavior (`PROCEED` / `SILENCE`).

## Runtime / API files

- `api/por_runtime.py`
- `api/main.py`
- `api/experimental_recovery.py` (explicitly experimental lane)

These define deployment-facing surfaces around, but not replacing, the primitive contract.

## Benchmark / evaluation files

- `eval_simpleqa_ollama.py`
- `benchmark/eval_100_milestone.py`
- `benchmark/eval_100_messy.py`

These files produce evaluation outputs used for threshold-behavior inspection.

## Demo evidence note

The baseline-vs-PoR artifact is local demo evidence only.

- Scope: v0.2 negative-control demo.
- Not a replacement for benchmark artifacts.
- Purpose: show release-control distinction.
  - Baseline: generate -> release
  - PoR: generate -> evaluate -> PROCEED/SILENCE

## Result artifact directories (recent local SimpleQA/Ollama)

- Qwen3 4B run artifacts: `results/simpleqa_ollama_qwen3_4b_100_v2_retry/`
- Qwen3 8B run artifacts: `results/simpleqa_ollama_qwen3_8b_100_v2/`

Treat these directories as the primary source for PR #131 / #132 run summaries.


## LangChain/OpenAI action-risk Run 06 progression

Run 06 action-risk evidence is an integration/deployment validation surface for release control, not a primitive-core result and not a universal AI safety claim. The strongest supported claim is: same model, same dataset, same threshold, no PoR core change; release-layer hardening changed the review/release profile.

Progression artifacts and documentation:

- Summary documentation: [`docs/langchain_openai_action_risk_benchmark.md`](langchain_openai_action_risk_benchmark.md)
- Dataset documentation: [`docs/action_risk_1000_dataset.md`](action_risk_1000_dataset.md)
- Initial report: [`reports/langchain_openai_summary_06_1000case.md`](../reports/langchain_openai_summary_06_1000case.md)
- Hardened v1 values: recorded progression context only; no separate `reports/langchain_openai_summary_06_1000case_hardened_v1.md` artifact is currently tracked.
- Hardened v2 report: [`reports/langchain_openai_summary_06_1000case_hardened_v2.md`](../reports/langchain_openai_summary_06_1000case_hardened_v2.md)
- Hardened v3 report: [`reports/langchain_openai_summary_06_1000case_hardened_v3.md`](../reports/langchain_openai_summary_06_1000case_hardened_v3.md)
- Hardened v4 report: [`reports/langchain_openai_summary_06_1000case_hardened_v4.md`](../reports/langchain_openai_summary_06_1000case_hardened_v4.md)

Interpretation boundaries:

- `NEEDS_REVIEW` is a release-control outcome, not a model failure.
- `SILENCE` remains separate from `NEEDS_REVIEW`.
- False accepts are risky cases incorrectly allowed to `PROCEED`.
- Safe overblocks are safe read-only cases sent to `NEEDS_REVIEW`.
- The progression does not imply model improvement, threshold tuning, external validation, dataset changes, benchmark-runner changes, or PoR primitive-core changes.

## Claim -> artifact mapping (short)

- Claim: PoR is release control, not generation improvement.
  - Evidence: primitive rule implementation and architecture split docs.
  - Files: `src/silence_as_control/control.py`, `api/core_primitive.py`, `docs/architecture.md`.

- Claim: Threshold behavior is regime/scoped, not universal.
  - Evidence: threshold contract + run-specific artifacts.
  - Files: `docs/threshold_regime_contract.md`, `results/simpleqa_ollama_qwen3_4b_100_v2_retry/`, `results/simpleqa_ollama_qwen3_8b_100_v2/`.

- Claim: Qwen3 4B reached zero accepted wrong at selected thresholds in this 100-example run.
  - Evidence: PR #131 artifacts and summary tables.
  - Files: `results/simpleqa_ollama_qwen3_4b_100_v2_retry/`.

- Claim: Qwen3 8B reached higher coverage but retained 1 accepted wrong at high-coverage boundary.
  - Evidence: PR #132 artifacts and summary tables.
  - Files: `results/simpleqa_ollama_qwen3_8b_100_v2/`.
