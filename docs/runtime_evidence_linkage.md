# Runtime Evidence Linkage

This document links runtime and replay artifacts to the project evidence layer.

The goal is to keep runtime evidence separate from broad claims.

## Evidence chain

```text
runtime claim
→ runtime artifact
→ replay or benchmark output
→ evidence map entry
→ chronology entry
```

## Current linkage targets

### Release-control behavior

```text
PoR gate
→ PROCEED / NEEDS_REVIEW / SILENCE
→ replay outputs
→ docs/evidence_map.md
```

### Deterministic replay

```text
candidate capture
→ fixture replay
→ stable decision trace
→ evidence map
```

### Release-risk examples

```text
unsafe or ambiguous candidate
→ gate decision
→ replayable result
→ release-risk evidence
```

Linked surfaces:

- `docs/release_risk_benchmark_index.md`
- `docs/release_risk_v4_capture_to_replay.md`
- `benchmarks/release_risk_v4_fixture_replay.py`
- `benchmarks/release_risk_v4/results/release_risk_v4_summary.json`
- `benchmarks/release_risk_v4/results/release_risk_v4_replay.jsonl`

### Local runtime

```text
candidate generation
→ local gate
→ runtime log
→ replay log
→ evidence map
```

Linked surfaces:

- `docs/runtime_observability.md`
- `scripts/runtime_observability_report.py`
- `tests/test_runtime_observability_report.py`

## Evidence rules

- Prefer replayable artifacts.
- Prefer small curated outputs over raw logs.
- Do not store private archives here.
- Do not claim complete validation from partial evidence.
- Keep runtime behavior separate from model quality claims.

## Pending links

- hosted deployment traces
- optional provider-backed replay artifacts
- future memory-admission prototype evidence
