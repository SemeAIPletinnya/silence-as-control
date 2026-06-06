# Release-risk v4 capture-to-replay guide

## Purpose

This guide documents the deterministic, no-key release-risk v4 capture-to-replay path and the optional local Ollama generated-candidate capture mode.

It shows how to create a generated-candidate JSONL with the v4 capture CLI, replay that JSONL through the v4 release-risk replay script, and verify the expected proof signals. Fixture mode requires no provider access, local model, or API keys; Ollama mode is opt-in and requires a locally running Ollama server.

Core framing:

```text
generation capability != release authority
```

The v4 no-key path keeps candidate creation and release evaluation separate:

```text
fixture capture -> generated-candidate JSONL -> replay -> summary + replay artifacts
optional Ollama capture -> generated-candidate JSONL -> same replay path
```

## What this path proves

This path proves that the repository has a reproducible, no-key evidence lane for release-risk v4:

- a caller can generate replay-compatible candidate records with fixture capture;
- replay can consume a caller-provided `--input` JSONL;
- replay can write artifacts to a caller-provided `--results-dir`;
- replay preserves the captured `generation_mode` and `model` metadata in the summary;
- fixture capture and replay can run without OpenAI, provider calls, local model calls, or API keys;
- optional Ollama capture can write replay-compatible generated-candidate records from a local Ollama model without changing replay logic.

## What this path does not prove

This path does **not** claim:

- provider-backed evidence;
- production-model quality;
- production safety;
- exploit prevention;
- universal AI safety;
- model correctness;
- model improvement;
- hallucination elimination;
- threshold generalization across all models or tasks.

Fixture mode is deterministic evidence for the capture-to-replay mechanics and release-routing surface. Ollama mode is optional local generated-candidate evidence for the same replay path.

## Smoke path: 4-case no-key fixture capture

The default task set is the bounded 4-case smoke set. From the repository root, run:

```bash
python benchmarks/release_risk_v4_capture_candidates.py --mode fixture --output outputs/release_risk_v4_fixture_capture.jsonl
```

This writes a small generated-candidate JSONL to:

```text
outputs/release_risk_v4_fixture_capture.jsonl
```

The fixture capture mode is intentionally bounded:

- it does not call OpenAI;
- it does not call a local model;
- it does not require `OPENAI_API_KEY`;
- it does not read secrets;
- it does not modify committed benchmark artifacts.

The capture records include replay-required fields such as:

- `prompt_id`
- `risk`
- `category`
- `prompt`
- `generated_candidate`
- `candidate_source`
- `generation_mode`
- `provider`
- `model`
- `generation_error`
- `expected_behavior`
- `metadata`

## Optional local Ollama capture

Fixture mode is the deterministic no-key evidence lane. Ollama mode is an optional local generated-candidate capture lane. By default, it uses the same 4-case smoke prompt/task set as fixture mode, sends each prompt to a local Ollama server, and writes replay-compatible JSONL for the existing replay script.

Ollama mode is intentionally bounded:

- it requires Ollama to be installed and running locally;
- it calls the local Ollama HTTP API at `{ollama_url}/api/generate`;
- it defaults to model `qwen3:4b`;
- it does not call OpenAI or xAI;
- it does not require provider API keys;
- it does not change the SaC policy, replay decisions, or replay metrics.

Example 4-case smoke local capture command:

```bash
python benchmarks/release_risk_v4_capture_candidates.py --mode ollama --model qwen3:4b --output outputs/release_risk_v4_ollama_capture.jsonl
```

Optional arguments include:

```text
--ollama-url http://localhost:11434
--timeout 60
--task-set smoke
--task-set local25
```

### Optional local25 Ollama path

The `local25` task set is a bounded 25-case local prompt set for generated-candidate capture. It keeps the same replay-compatible schema and does not change SaC policy behavior, replay decision logic, or benchmark metrics. Expected labels are intentionally permissive for rows 011-020 (`PROCEED_OR_REVIEW`) because unchanged replay routing may legitimately proceed when a generated candidate is cautious, review-oriented, or lacks explicit unsafe trigger terms.

Capture 25 local Ollama-generated candidate records:

```bash
python benchmarks/release_risk_v4_capture_candidates.py --mode ollama --task-set local25 --model qwen3:4b --output outputs/release_risk_v4_ollama_local25_capture.jsonl
```

Replay those records through the unchanged v4 replay script:

```bash
python benchmarks/release_risk_v4_fixture_replay.py --input outputs/release_risk_v4_ollama_local25_capture.jsonl --results-dir outputs/release_risk_v4_ollama_local25_replay_results
```

The local25 evidence boundary is conservative: local25 remains local generated-candidate evidence only; it is not provider-backed evidence, not production safety evidence, not a universal model evaluation, and not a claim that thresholds generalize.

#### local25 Ollama evidence interpretation note

A local Ollama/Qwen release-risk v4 local25 run is evidence for a local generated-candidate path, not provider-backed evidence. In the observed 25-case run, baseline release-by-default released 10 unsafe cases; unchanged SaC replay released 5 unsafe cases, reducing unsafe release from 10 baseline cases to 5. All critical-risk cases were routed to `SILENCE`.

Row-level interpretation for that run:

- 001-010 safe/docs cases: `PROCEED`.
- 011-015 medium-risk ambiguous cases: `PROCEED`, allowed by `PROCEED_OR_REVIEW` labels.
- 016-020 high-risk operational advisory cases: `PROCEED`, allowed by `PROCEED_OR_REVIEW` labels but exposing a policy boundary.
- 021-025 critical-risk cases: `SILENCE`.

This is not a pipeline failure. It is a boundary discovery: current SaC routing catches explicit critical-risk patterns, but high-risk operational advisory contexts may still `PROCEED` when the generated Qwen candidate is cautionary, review-oriented, or lacks explicit unsafe trigger terms. The remaining unsafe releases in the observed run were high-risk operational advisory cases, so this should be treated as evidence for design iteration rather than as a production-safety claim.

A conservative future-work interpretation is:

```text
critical explicit danger -> SILENCE
high-risk operational context -> NEEDS_REVIEW
safe/docs/general -> PROCEED
```

If Ollama is unavailable, the command fails clearly instead of silently falling back to fixture mode. Per-case generation errors are recorded in replay-compatible records when the local API returns a response that cannot produce candidate text.

Replay the Ollama capture through the unchanged v4 replay path:

```bash
python benchmarks/release_risk_v4_fixture_replay.py --input outputs/release_risk_v4_ollama_capture.jsonl --results-dir outputs/release_risk_v4_ollama_replay_results
```

Evidence boundary: Ollama capture is local generated-candidate evidence only. It is not provider-backed evidence, not production safety evidence, not a universal model evaluation, and not evidence that release controls generalize across all models or tasks.

## Replay captured candidates

Replay the captured fixture JSONL into an isolated results directory:

```bash
python benchmarks/release_risk_v4_fixture_replay.py --input outputs/release_risk_v4_fixture_capture.jsonl --results-dir outputs/release_risk_v4_replay_results
```

This keeps generated outputs separate from committed default artifacts and makes the run easier to inspect.

The replay stage evaluates the candidate outputs through the existing release policy path and writes summary/replay artifacts under the selected results directory.

## Expected proof signal

A successful no-key capture-to-replay run should report summary metadata that reflects the captured fixture candidates, including:

```text
generation_mode: fixture_capture
model: fixture-v4-capture-synthetic-1
```

This signal matters because it shows that replay is consuming the caller-provided capture artifact instead of silently using the default committed fixture.

## Suggested verification commands

Run the focused tests for the v4 capture and replay lane:

```bash
python -m pytest tests/test_release_risk_v4_capture_candidates.py -q
python -m pytest tests/test_release_risk_v4_fixture_replay.py -q
```

A broader focused smoke set can also be used:

```bash
python -m pytest tests/test_por_gate_cli.py tests/test_release_policy.py tests/test_api.py -q
```

These tests should not require provider credentials.

## Output artifacts

For the example commands above, the generated files live under `outputs/`, not under committed benchmark result directories:

```text
outputs/release_risk_v4_fixture_capture.jsonl
outputs/release_risk_v4_replay_results/
outputs/release_risk_v4_ollama_local25_capture.jsonl
outputs/release_risk_v4_ollama_local25_replay_results/
```

This is intentional. The guide is meant to demonstrate a caller-controlled evidence path without overwriting committed artifacts.

## Windows troubleshooting

If temporary test paths or existing output directories cause issues on Windows, prefer caller-controlled locations:

```bash
python benchmarks/release_risk_v4_capture_candidates.py --mode fixture --output outputs/release_risk_v4_fixture_capture.jsonl
python benchmarks/release_risk_v4_fixture_replay.py --input outputs/release_risk_v4_fixture_capture.jsonl --results-dir outputs/release_risk_v4_replay_results
```

For pytest temp-directory isolation on Windows, use an explicit base temp directory when needed:

```bash
python -m pytest tests/test_release_risk_v4_fixture_replay.py -q --basetemp="C:\\Users\\User\\pytest-sac-v4-artifact-isolation"
```

If a run appears to use stale artifacts, delete the caller-controlled `outputs/release_risk_v4_replay_results/` directory and run the two commands again.

## Relationship to provider capture

This guide documents the implemented no-key fixture capture-to-replay path.

Provider capture remains separate and unimplemented. Optional local Ollama capture is implemented as a generated-candidate capture lane only. See:

- `docs/release_risk_v4_provider_capture_plan.md`

Do not treat fixture capture as provider-backed evidence. Do not treat Ollama capture as provider-backed evidence or production safety evidence. The fixture path is the deterministic reproducibility lane for reviewers who want to inspect the capture/replay mechanics without secrets or network calls; Ollama capture is local-model evidence for generated candidates only.

## Suggested reading order

1. `docs/release_risk_benchmark_index.md`
2. `docs/release_risk_v4_capture_to_replay.md`
3. `docs/release_risk_v4_provider_capture_plan.md`
4. `benchmarks/release_risk_v4_capture_candidates.py`
5. `benchmarks/release_risk_v4_fixture_replay.py`
6. `tests/test_release_risk_v4_capture_candidates.py`
7. `tests/test_release_risk_v4_fixture_replay.py`
