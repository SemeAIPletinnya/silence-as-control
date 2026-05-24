# Release-risk v4 capture-to-replay guide

## Purpose

This guide documents the deterministic, no-key release-risk v4 capture-to-replay path.

It shows how to create a generated-candidate JSONL with the v4 capture CLI, replay that JSONL through the v4 release-risk replay script, and verify the expected proof signals without provider access or API keys.

Core framing:

```text
generation capability != release authority
```

The v4 no-key path keeps candidate creation and release evaluation separate:

```text
fixture capture -> generated-candidate JSONL -> replay -> summary + replay artifacts
```

## What this path proves

This path proves that the repository has a reproducible, no-key evidence lane for release-risk v4:

- a caller can generate replay-compatible candidate records with fixture capture;
- replay can consume a caller-provided `--input` JSONL;
- replay can write artifacts to a caller-provided `--results-dir`;
- replay preserves the captured `generation_mode` and `model` metadata in the summary;
- fixture capture and replay can run without OpenAI, provider calls, local model calls, or API keys.

## What this path does not prove

This path does **not** claim:

- provider-backed evidence;
- local-model evidence;
- live generation quality;
- production safety;
- exploit prevention;
- universal AI safety;
- model correctness;
- model improvement;
- hallucination elimination;
- threshold generalization across all models or tasks.

It is deterministic fixture evidence for the capture-to-replay mechanics and release-routing surface.

## No-key fixture capture

From the repository root, run:

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

Provider/local capture remains separate and opt-in. See:

- `docs/release_risk_v4_provider_capture_plan.md`

Do not treat fixture capture as provider-backed evidence. The fixture path is the deterministic reproducibility lane for reviewers who want to inspect the capture/replay mechanics without secrets or network calls.

## Suggested reading order

1. `docs/release_risk_benchmark_index.md`
2. `docs/release_risk_v4_capture_to_replay.md`
3. `docs/release_risk_v4_provider_capture_plan.md`
4. `benchmarks/release_risk_v4_capture_candidates.py`
5. `benchmarks/release_risk_v4_fixture_replay.py`
6. `tests/test_release_risk_v4_capture_candidates.py`
7. `tests/test_release_risk_v4_fixture_replay.py`
