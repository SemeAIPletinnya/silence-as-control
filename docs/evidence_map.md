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
- `docs/provider_configuration.md` (navigation/support for no-key vs provider-backed runtime setup)
- `docs/first_run_checklist.md` (navigation/support for no-key first-run verification)

These define deployment-facing surfaces around, but not replacing, the primitive contract.

## Runtime observability / local telemetry

Runtime release-control decisions can be locally observed and summarized when telemetry is explicitly enabled.

Artifacts:

- `src/silence_as_control/telemetry.py`
- `scripts/runtime_observability_report.py`
- `docs/runtime_observability.md`
- `tests/test_telemetry.py`
- `tests/test_runtime_observability_report.py`

Interpretation boundaries:

- Telemetry is disabled by default.
- Telemetry is local JSONL only.
- Telemetry records compact decision metadata and numeric signals.
- Telemetry does not log full prompt/candidate text by default.
- This is not production monitoring.
- This is not a universal AI safety claim.

## Benchmark / evaluation files

- `benchmarks/simpleqa/run_simpleqa_por.py`
- `benchmarks/simpleqa/README.md`
- `data/simpleqa_clean_100.jsonl`
- `data/simpleqa_messy_100.jsonl`
- `reports/simpleqa_ollama_calibration_summary.md`

These tracked benchmark and dataset files support threshold-behavior inspection. For the compact claim-to-artifact topology, see `docs/evidence_graph.md`.

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



## Release-risk v1 deterministic benchmark

Scope:

- Local deterministic release-control behavior check over 50 handcrafted release-risk cases.
- Baseline release-by-default versus SaC-style routing (`PROCEED` / `NEEDS_REVIEW` / `SILENCE`).

Artifacts:

- `benchmarks/release_risk/README.md`
- `benchmarks/release_risk/run_release_risk.py`
- `benchmarks/release_risk/data/release_risk_50.jsonl`
- `benchmarks/release_risk/results/release_risk_summary.json`
- `benchmarks/release_risk/results/release_risk_summary.csv`
- `tests/test_release_risk_benchmark.py`
- `docs/release_risk_benchmark_report.md`

Recorded local run:

- total_cases: 50
- baseline_unsafe_released: 24
- sac_unsafe_released: 0
- unsafe_release_reduction_percent: 100.0
- safe_proceed_rate: 100.0

Interpretation boundary:

- Deterministic local release-routing evidence over included handcrafted cases.
- Not live provider/model generation evidence.
- Not production safety evidence.

Validation:

```bash
python -m pytest tests/test_release_risk_benchmark.py -q
python -m pytest tests/test_api.py -q
```

## Release-risk v2 fixture replay benchmark

Scope:

- Local deterministic fixture candidate-output replay over 50 prompts/candidates.
- Baseline release-by-default versus SaC-style routing.

Artifacts:

- `benchmarks/release_risk_v2/README.md`
- `benchmarks/release_risk_v2/run_release_risk_v2.py`
- `benchmarks/release_risk_v2/data/release_risk_prompts_50.jsonl`
- `benchmarks/release_risk_v2/candidates/fixture_candidates_50.jsonl`
- `benchmarks/release_risk_v2/results/release_risk_v2_summary.json`
- `benchmarks/release_risk_v2/results/release_risk_v2_summary.csv`
- `benchmarks/release_risk_v2/results/release_risk_v2_replay.jsonl`
- `tests/test_release_risk_v2_benchmark.py`
- `docs/release_risk_v2_benchmark_report.md`

Recorded local run:

- total_cases: 50
- baseline_unsafe_released: 20
- sac_unsafe_released: 0
- unsafe_release_reduction_percent: 100.0
- safe_proceed_rate: 90.0
- candidate_source: fixture
- generation_mode: fixture
- num_replayed_candidates: 50

Interpretation boundary:

- Deterministic fixture replay release-routing evidence.
- Not live provider/model generation evidence.
- Not production safety evidence.

Validation:

```bash
python -m pytest tests/test_release_risk_v2_benchmark.py -q
python -m pytest tests/test_release_risk_benchmark.py -q
python -m pytest tests/test_api.py -q
```

## Release-risk v3 fixture generation/replay benchmark

Scope:

- Generated-candidate schema validation.
- Fixture generation path and replay routing validation.
- Provider/local mode separation at interface level, while using fixture evidence.

Artifacts:

- `benchmarks/release_risk_v3/README.md`
- `benchmarks/release_risk_v3/generate_candidates_v3.py`
- `benchmarks/release_risk_v3/run_release_risk_v3.py`
- `benchmarks/release_risk_v3/data/release_risk_prompts_50.jsonl`
- `benchmarks/release_risk_v3/candidates/fixture_generated_candidates_50.jsonl`
- `benchmarks/release_risk_v3/candidates/generated_candidates_fixture.jsonl`
- `benchmarks/release_risk_v3/results/release_risk_v3_summary.json`
- `benchmarks/release_risk_v3/results/release_risk_v3_summary.csv`
- `benchmarks/release_risk_v3/results/release_risk_v3_replay.jsonl`
- `tests/test_release_risk_v3_benchmark.py`
- `docs/release_risk_v3_benchmark_report.md`

Recorded local run:

- total_cases: 50
- baseline_released: 50
- baseline_unsafe_released: 25
- sac_proceed: 9
- sac_needs_review: 22
- sac_silence: 19
- sac_unsafe_released: 0
- unsafe_release_reduction_percent: 100.0
- safe_proceed_rate: 90.0
- candidate_source: fixture
- generation_mode: fixture
- provider: null
- model: fixture-generated-candidates-v1
- num_generation_failures: 0
- num_empty_candidates: 0
- num_replayed_candidates: 50

Interpretation boundary:

- Deterministic fixture generation/replay release-routing evidence.
- Not live provider/model generation evidence.
- No API keys required for fixture mode.
- Not production safety evidence.

Validation:

```bash
python -m pytest tests/test_release_risk_v3_benchmark.py -q
python -m pytest tests/test_release_risk_v2_benchmark.py -q
python -m pytest tests/test_release_risk_benchmark.py -q
python -m pytest tests/test_api.py -q
```


## Release-risk v4 deterministic capture/replay evidence

Scope:

- Deterministic no-key 4-case fixture capture and replay.
- Optional 25-case local Ollama generated-candidate capture through the same replay script.

Artifacts:

- `benchmarks/release_risk_v4_capture_candidates.py`
- `benchmarks/release_risk_v4_fixture_replay.py`
- `docs/release_risk_v4_capture_to_replay.md`
- `docs/release_risk_benchmark_index.md`
- `tests/test_release_risk_v4_capture_candidates.py`
- `tests/test_release_risk_v4_fixture_replay.py`

Proof signals:

- `generation_mode`: `fixture_capture`
- `model`: `fixture-v4-capture-synthetic-1`
- `provider`: `None`

Interpretation boundaries:

- Deterministic fixture capture/replay evidence only.
- No API keys required.
- Not provider-backed evidence.
- Not production safety evidence.
- Optional local Ollama generated-candidate capture is supported for v4, including the bounded local25 task set, but remains local-model evidence only.
- local25 is not provider-backed evidence, production safety evidence, universal model evaluation, or a claim that thresholds generalize.
- In one observed local Ollama/Qwen local25 run, unchanged replay reduced unsafe release from 10 baseline unsafe cases to 5, routed all critical-risk cases to `SILENCE`, and left the remaining unsafe releases in high-risk operational advisory cases whose generated candidates were cautionary, review-oriented, or lacked explicit unsafe trigger terms.
- This local25 result is a design-iteration boundary, not a pipeline failure or production-safety claim; future work may separate `critical explicit danger -> SILENCE`, `high-risk operational context -> NEEDS_REVIEW`, and `safe/docs/general -> PROCEED`.
- Provider-backed capture remains future work.

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

- Claim: Runtime release-control decisions can be locally observed and summarized.
  - Evidence: opt-in JSONL telemetry writer, report script, smoke walkthrough, and tests.
  - Files: `src/silence_as_control/telemetry.py`, `scripts/runtime_observability_report.py`, `docs/runtime_observability.md`, `tests/test_telemetry.py`, `tests/test_runtime_observability_report.py`.

- Claim: Qwen3 4B reached zero accepted wrong at selected thresholds in this 100-example run.
  - Evidence: PR #131 artifacts and summary tables.
  - Files: `results/simpleqa_ollama_qwen3_4b_100_v2_retry/`.

- Claim: Qwen3 8B reached higher coverage but retained 1 accepted wrong at high-coverage boundary.
  - Evidence: PR #132 artifacts and summary tables.
  - Files: `results/simpleqa_ollama_qwen3_8b_100_v2/`.
