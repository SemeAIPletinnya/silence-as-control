# Release-Risk Benchmark v3 (Generated-Candidate Scaffold)

This benchmark track is intended for **generated candidate replay**.

Core framing:

> generation capability != release authority

## Scope of this first v3 PR

This first v3 change only adds a conservative scaffold:

- fixture fallback mode
- generated-candidate schema
- generator CLI with provider/local placeholders
- deterministic replay runner and artifacts

No real provider calls are implemented in this PR.

## Modes

- `fixture`: deterministic local replay over fixture-generated candidates (default).
- `provider`: placeholder path, exits with a clear "not implemented" message.
- `local`: placeholder path, exits with a clear "not implemented" message.

Fixture mode is deterministic, local, and API-key-free.

## Conservative limitations

- Not production safety evidence.
- Not exploit prevention.
- Not an alignment solution.
- Does not prove model correctness.
- Generation is separate from release authority.

## Run

```bash
python benchmarks/release_risk_v3/generate_candidates_v3.py --mode fixture
python benchmarks/release_risk_v3/run_release_risk_v3.py --mode fixture
```

## Artifacts

- `benchmarks/release_risk_v3/results/release_risk_v3_summary.json`
- `benchmarks/release_risk_v3/results/release_risk_v3_summary.csv`
- `benchmarks/release_risk_v3/results/release_risk_v3_replay.jsonl`
