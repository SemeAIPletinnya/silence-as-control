# Release-risk v4 provider capture plan

## Purpose

This document plans **Phase 2** of release-risk v4: optional generated-candidate capture for later replay through the existing v4 replay surface.

This page is a **design plan only**. It does not add provider evidence, local-model evidence, runtime provider calls, or new benchmark artifacts.

## Current foundation (Phase 1 complete)

Release-risk v4 Phase 1 is complete for deterministic no-key replay foundations:

- fixture replay scaffold
- direct script execution
- null generated-candidate handling
- test artifact isolation
- no-key deterministic path

## Architecture

The planned v4 flow remains split into two stages.

### Capture stage

`prompts/tasks -> optional generator -> generated-candidate JSONL`

- The generator may be fixture-based, provider-backed, or local-model backed in future phases.
- Capture remains optional and explicitly selected.

### Replay stage

`generated-candidate JSONL -> v4 replay script -> summary + replay artifacts`

- Replay remains the default deterministic path for benchmark evaluation.
- Replay logic should not care whether `candidate_source` is `fixture`, `openai`, `local_model`, or a future source.

## Candidate artifact shape

Planned required fields per generated-candidate record:

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

Planned optional provider/local metadata fields:

- `captured_at`
- `provider_request_id` (if safely available)
- `temperature` (if used)
- `max_output_tokens` (if used)
- `error_type` (if generation failed)
- `source_dataset` or `task_set`

Safety constraint for artifacts:

- Secrets, authorization headers, raw credentials, and sensitive provider logs must never be stored.

## CLI sketch (design only)

Intended future command surface (not implemented by this document):

```bash
python benchmarks/release_risk_v4_capture_candidates.py --mode fixture --output <path>
python benchmarks/release_risk_v4_capture_candidates.py --mode openai --model <model> --max-cases 10 --output <path>
python benchmarks/release_risk_v4_fixture_replay.py --input <generated-candidates.jsonl> --results-dir <path>
```

These are design sketches unless and until implementation lands.

## Safety and reproducibility constraints

- provider/local capture must be opt-in only
- fixture replay remains default
- no provider calls in CI by default
- tests must not require API keys
- no secrets committed
- failed/null candidates must remain replayable
- artifact output must not overwrite fixture evidence unless explicitly requested
- raw candidate artifacts must be inspectable and bounded

## Implementation phases

- **Phase 2A** — design doc only
- **Phase 2B** — capture CLI scaffold, no live provider by default
- **Phase 2C** — small opt-in provider sample run

## Non-claims

This plan does **not** claim:

- provider evidence yet
- local-model evidence yet
- production safety proof
- universal threshold transfer
- model improvement
- replacement for human review
- full #238 completion

## Suggested reading order

1. [`release_risk_v4_fixture_replay.md`](release_risk_v4_fixture_replay.md)
2. [`release_risk_benchmark_index.md`](release_risk_benchmark_index.md)
3. [`evidence_map.md`](evidence_map.md)
4. [`pilot_evaluation_template.md`](pilot_evaluation_template.md)
5. [`external_integration.md`](external_integration.md)
