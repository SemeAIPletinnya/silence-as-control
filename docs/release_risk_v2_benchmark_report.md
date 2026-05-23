# Release-Risk v2 Benchmark Report

## Scope

This report records the first local fixture-replay run for Release-risk Benchmark v2.

Release-risk v2 evaluates release behavior over candidate outputs. In fixture mode, candidate outputs are deterministic and local, and no provider/API keys are required.

This report is not live model-output generation evidence and not a production safety guarantee.

## Commands

```bash
python benchmarks/release_risk_v2/run_release_risk_v2.py --mode fixture
python -m pytest tests/test_release_risk_v2_benchmark.py -q
python -m pytest tests/test_release_risk_benchmark.py -q
python -m pytest tests/test_api.py -q
```

## Results

- total_cases: 50
- baseline_released: 50
- baseline_unsafe_released: 20
- sac_proceed: 9
- sac_needs_review: 25
- sac_silence: 16
- sac_unsafe_released: 0
- unsafe_release_reduction_percent: 100.0
- safe_proceed_rate: 90.0
- candidate_source: fixture
- generation_mode: fixture
- num_generation_failures: 0
- num_empty_candidates: 0
- num_replayed_candidates: 50

| Metric | Value |
| --- | ---: |
| total_cases | 50 |
| baseline_released | 50 |
| baseline_unsafe_released | 20 |
| sac_proceed | 9 |
| sac_needs_review | 25 |
| sac_silence | 16 |
| sac_unsafe_released | 0 |
| unsafe_release_reduction_percent | 100.0 |
| safe_proceed_rate | 90.0 |
| candidate_source | fixture |
| generation_mode | fixture |
| num_generation_failures | 0 |
| num_empty_candidates | 0 |
| num_replayed_candidates | 50 |

## Test validation

- `tests/test_release_risk_v2_benchmark.py`: 1 passed
- `tests/test_release_risk_benchmark.py`: 1 passed
- `tests/test_api.py`: 15 passed

## Interpretation

This run demonstrates that, on the included deterministic fixture candidate-output dataset, baseline release-by-default releases all 50 candidates, including 20 unsafe candidates, while SaC-style routing releases 0 unsafe candidates and routes the rest to PROCEED / NEEDS_REVIEW / SILENCE.

This should be interpreted as fixture replay release-control behavior evidence, not as live provider/model generation safety evidence.

## Artifacts

- [`../benchmarks/release_risk_v2/README.md`](../benchmarks/release_risk_v2/README.md)
- [`../benchmarks/release_risk_v2/run_release_risk_v2.py`](../benchmarks/release_risk_v2/run_release_risk_v2.py)
- [`../benchmarks/release_risk_v2/data/release_risk_prompts_50.jsonl`](../benchmarks/release_risk_v2/data/release_risk_prompts_50.jsonl)
- [`../benchmarks/release_risk_v2/candidates/fixture_candidates_50.jsonl`](../benchmarks/release_risk_v2/candidates/fixture_candidates_50.jsonl)
- [`../benchmarks/release_risk_v2/results/release_risk_v2_summary.json`](../benchmarks/release_risk_v2/results/release_risk_v2_summary.json)
- [`../benchmarks/release_risk_v2/results/release_risk_v2_summary.csv`](../benchmarks/release_risk_v2/results/release_risk_v2_summary.csv)
- [`../benchmarks/release_risk_v2/results/release_risk_v2_replay.jsonl`](../benchmarks/release_risk_v2/results/release_risk_v2_replay.jsonl)
- [`../tests/test_release_risk_v2_benchmark.py`](../tests/test_release_risk_v2_benchmark.py)
