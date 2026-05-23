# Release-Risk v3 Benchmark Report

## Scope

This report records the first local fixture-generation/replay run for Release-risk Benchmark v3 after PR #232.

Release-risk v3 validates the generated-candidate schema and replay-routing surface for candidate-based release control.

Fixture generation mode is deterministic and local.

Provider/local generation remains placeholder-only in this benchmark scaffold.

No provider or API keys are required for this fixture generation/replay path.

This is not live provider/model generation evidence.

This is not a production safety guarantee.

## Commands

```bash
python benchmarks/release_risk_v3/generate_candidates_v3.py --mode fixture
python benchmarks/release_risk_v3/run_release_risk_v3.py --mode fixture

python -m pytest tests/test_release_risk_v3_benchmark.py -q
python -m pytest tests/test_release_risk_v2_benchmark.py -q
python -m pytest tests/test_release_risk_benchmark.py -q
python -m pytest tests/test_api.py -q
```

## Candidate generation output

```text
Wrote fixture-generated candidates to:
benchmarks/release_risk_v3/candidates/generated_candidates_fixture.jsonl
```

## Results

```text
total_cases: 50
baseline_released: 50
baseline_unsafe_released: 25
sac_proceed: 9
sac_needs_review: 18
sac_silence: 23
sac_unsafe_released: 0
unsafe_release_reduction_percent: 100.0
safe_proceed_rate: 90.0
candidate_source: fixture
generation_mode: fixture
provider: null
model: fixture-generated-candidates-v1
num_generation_failures: 0
num_empty_candidates: 0
num_replayed_candidates: 50
```

| Metric | Value |
| --- | ---: |
| total_cases | 50 |
| baseline_released | 50 |
| baseline_unsafe_released | 25 |
| sac_proceed | 9 |
| sac_needs_review | 18 |
| sac_silence | 23 |
| sac_unsafe_released | 0 |
| unsafe_release_reduction_percent | 100.0 |
| safe_proceed_rate | 90.0 |
| candidate_source | fixture |
| generation_mode | fixture |
| provider | null |
| model | fixture-generated-candidates-v1 |
| num_generation_failures | 0 |
| num_empty_candidates | 0 |
| num_replayed_candidates | 50 |

## Test validation

- `tests/test_release_risk_v3_benchmark.py`: 1 passed
- `tests/test_release_risk_v2_benchmark.py`: 1 passed
- `tests/test_release_risk_benchmark.py`: 1 passed
- `tests/test_api.py`: 15 passed

## Interpretation

This run demonstrates fixture-generation/replay release-routing behavior over locally generated fixture candidates. Baseline release-by-default releases all replayed candidates, including 25 unsafe candidates, while SaC-style routing releases 0 unsafe candidates and routes the rest to PROCEED / NEEDS_REVIEW / SILENCE.

This should be interpreted as deterministic fixture generation/replay evidence, not as live provider/model generation evidence.

## Artifacts

- [`../benchmarks/release_risk_v3/README.md`](../benchmarks/release_risk_v3/README.md)
- [`../benchmarks/release_risk_v3/generate_candidates_v3.py`](../benchmarks/release_risk_v3/generate_candidates_v3.py)
- [`../benchmarks/release_risk_v3/run_release_risk_v3.py`](../benchmarks/release_risk_v3/run_release_risk_v3.py)
- [`../benchmarks/release_risk_v3/data/release_risk_prompts_50.jsonl`](../benchmarks/release_risk_v3/data/release_risk_prompts_50.jsonl)
- [`../benchmarks/release_risk_v3/candidates/fixture_generated_candidates_50.jsonl`](../benchmarks/release_risk_v3/candidates/fixture_generated_candidates_50.jsonl)
- [`../benchmarks/release_risk_v3/candidates/generated_candidates_fixture.jsonl`](../benchmarks/release_risk_v3/candidates/generated_candidates_fixture.jsonl)
- [`../benchmarks/release_risk_v3/results/release_risk_v3_summary.json`](../benchmarks/release_risk_v3/results/release_risk_v3_summary.json)
- [`../benchmarks/release_risk_v3/results/release_risk_v3_summary.csv`](../benchmarks/release_risk_v3/results/release_risk_v3_summary.csv)
- [`../benchmarks/release_risk_v3/results/release_risk_v3_replay.jsonl`](../benchmarks/release_risk_v3/results/release_risk_v3_replay.jsonl)
- [`../tests/test_release_risk_v3_benchmark.py`](../tests/test_release_risk_v3_benchmark.py)
