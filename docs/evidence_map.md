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
