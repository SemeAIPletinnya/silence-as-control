# Release-Risk v4 Fixture Replay (Phase 1 Scaffold)

This document describes **Phase 1** of issue #238 for release-risk v4.

## What this phase includes

- A deterministic fixture replay path using synthetic generated-candidate-like records.
- A no-key script that replays fixture candidates through existing release-control policy handling.
- Stable summary/replay artifacts for auditability.

## What this phase does **not** include

- No provider calls.
- No local model live generation.
- No API-key usage.
- No CI provider generation.
- No production-path rollout claims.
- No universal threshold-transfer claims.
- No model-improvement claims.

## Scope clarification

This is **fixture replay scaffold evidence only** for v4 candidate shape and replay mechanics. It is not provider/local generated-candidate evidence yet.

Results are strictly scoped to fixture candidates and should not be interpreted as production safety proof.

## Artifacts

- Fixture input: `data/release_risk_v4/release_risk_v4_fixture_candidates.jsonl`
- Replay script: `benchmarks/release_risk_v4_fixture_replay.py`
- Summary output: `benchmarks/release_risk_v4/results/release_risk_v4_summary.json`
- Replay output: `benchmarks/release_risk_v4/results/release_risk_v4_replay.jsonl`

## Repro command

```bash
python benchmarks/release_risk_v4_fixture_replay.py
```

No secrets are required.

## Relation to #238

Issue #238 targets optional provider/local generated-candidate capture and replay for v4.
This PR is **Phase 1 only** and does not implement full #238.
