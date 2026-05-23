# Release-Risk Benchmark Report

## Scope

This report records the first deterministic local release-risk benchmark run.

- It measures release behavior, not model intelligence.
- The baseline path releases every candidate by default.
- SaC-style deterministic routing maps candidates to `PROCEED` / `NEEDS_REVIEW` / `SILENCE`.
- The run uses a deterministic local dataset with 50 cases.
- The run does not require provider credentials or API keys.
- This is not a production safety guarantee.

## Commands

The recorded local commands were:

```bash
python benchmarks/release_risk/run_release_risk.py
python -m pytest tests/test_release_risk_benchmark.py -q
python -m pytest tests/test_api.py -q
```

## Results

Recorded benchmark summary:

```text
total_cases: 50
baseline_released: 50
baseline_unsafe_released: 24
sac_proceed: 14
sac_needs_review: 14
sac_silence: 22
sac_unsafe_released: 0
unsafe_release_reduction_percent: 100.0
safe_proceed_rate: 100.0
```

| Metric | Value |
| --- | ---: |
| total_cases | 50 |
| baseline_released | 50 |
| baseline_unsafe_released | 24 |
| sac_proceed | 14 |
| sac_needs_review | 14 |
| sac_silence | 22 |
| sac_unsafe_released | 0 |
| unsafe_release_reduction_percent | 100.0 |
| safe_proceed_rate | 100.0 |

## Test validation

- `tests/test_release_risk_benchmark.py`: 1 passed
- `tests/test_api.py`: 15 passed

## Interpretation

This run demonstrates that, on the included deterministic dataset, release-by-default behavior releases all candidates, including 24 unsafe candidates, while the SaC-style deterministic route releases 0 unsafe candidates and routes the rest to `PROCEED` / `NEEDS_REVIEW` / `SILENCE`.

This should be interpreted as a local release-control behavior check, not as external model safety evidence.

## Artifacts

- [`../benchmarks/release_risk/README.md`](../benchmarks/release_risk/README.md)
- [`../benchmarks/release_risk/run_release_risk.py`](../benchmarks/release_risk/run_release_risk.py)
- [`../benchmarks/release_risk/data/release_risk_50.jsonl`](../benchmarks/release_risk/data/release_risk_50.jsonl)
- [`../benchmarks/release_risk/results/release_risk_summary.json`](../benchmarks/release_risk/results/release_risk_summary.json)
- [`../benchmarks/release_risk/results/release_risk_summary.csv`](../benchmarks/release_risk/results/release_risk_summary.csv)
- [`../tests/test_release_risk_benchmark.py`](../tests/test_release_risk_benchmark.py)
