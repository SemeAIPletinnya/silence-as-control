# Release-Risk Benchmark (Deterministic, Local)

This benchmark measures **release behavior**, not model intelligence.

Core framing:

> generation capability != release authority

## What it compares

- **Baseline**: release every candidate by default (`candidate -> RELEASE`).
- **SaC-style routing**: route candidate outputs to `PROCEED`, `NEEDS_REVIEW`, or `SILENCE`.

## Scope and limits

- Deterministic and local: no external providers or API keys are required.
- Results are scoped to this dataset and this routing policy.
- This benchmark does **not** claim production safety guarantees.
- This benchmark does **not** claim exploit prevention or alignment completeness.

## Dataset

`data/release_risk_50.jsonl` contains 50 deterministic cases with risk classes:

- `safe`
- `medium_risk`
- `high_risk`
- `critical_risk`

Each row includes:

- `id`
- `risk`
- `category`
- `prompt`
- `candidate`
- `expected_behavior`

## Run

```bash
python benchmarks/release_risk/run_release_risk.py
```

## Outputs

Running the script prints a concise summary and writes:

- `benchmarks/release_risk/results/release_risk_summary.json`
- `benchmarks/release_risk/results/release_risk_summary.csv`

These artifacts provide a bounded comparison of baseline release-by-default behavior against deterministic SaC-style routing on the included dataset.
