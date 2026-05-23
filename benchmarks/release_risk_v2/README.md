# Release-Risk Benchmark v2 (Fixture Replay)

This benchmark measures **release behavior over candidate outputs**.

Core framing:

> generation capability != release authority

## What v2 adds

v1 uses deterministic handcrafted candidates.
v2 introduces generated-candidate replay evidence, starting with deterministic fixture mode.

## Comparison

- **Baseline**: `prompt -> candidate -> RELEASE` (release-by-default).
- **SaC-style route**: `prompt -> candidate -> gate -> PROCEED / NEEDS_REVIEW / SILENCE`.

## Fixture mode (first path)

- Deterministic and local replay of fixture candidates.
- No provider calls.
- No API keys required.
- Standard-library-only implementation.

## Limits and conservative framing

- Not a production safety guarantee.
- Not exploit prevention.
- Not an alignment solution.
- Not universal AI safety.
- Does not prove model correctness.

## Run

```bash
python benchmarks/release_risk_v2/run_release_risk_v2.py --mode fixture
```

## Artifacts

- `benchmarks/release_risk_v2/results/release_risk_v2_summary.json`
- `benchmarks/release_risk_v2/results/release_risk_v2_summary.csv`
- `benchmarks/release_risk_v2/results/release_risk_v2_replay.jsonl`

## Data

- Prompts: `benchmarks/release_risk_v2/data/release_risk_prompts_50.jsonl`
- Fixture candidates: `benchmarks/release_risk_v2/candidates/fixture_candidates_50.jsonl`
