# API Walkthrough

This page mirrors the applied runtime path documented in `docs/api_walkthrough.md`.

## Runtime flow

```text
Request -> Candidate Output -> PoR Gate -> PROCEED / SILENCE
```

- `Request`: caller sends prompt/context.
- `Candidate Output`: model (or provided candidate) produces text.
- `PoR Gate`: runtime evaluates drift/coherence against threshold policy.
- `Decision`:
  - `PROCEED` -> release output
  - `SILENCE` -> withhold output intentionally

## Why the gate matters

Without a gate, generation is typically release-by-default.
PoR inserts an explicit control decision before release, so unstable candidates can be withheld.

## Why silence is valid

In this project, silence is a control action:
- not transport failure
- not timeout
- not crash behavior

Silence indicates the runtime decided the candidate did not meet release stability criteria.

## How this differs from baseline always-output systems

- Baseline path: output is emitted by default.
- PoR path: output release is conditional on stability checks.

This is a policy difference, not a claim of model-weight improvement.

## Current API endpoints (from docs + code)

Current documented endpoints in this repository:
- `GET /health`
- `POST /por/evaluate`
- `POST /generate` (legacy compatibility)
- `POST /por/complete`

See:
- `docs/api_walkthrough.md`
- `api/main.py`

## Release-control flow

The API keeps candidate generation and release separate:

1. `/por/complete` asks the configured generator for one or more candidates.
2. Runtime estimators compute drift/coherence for the candidate set.
3. The core PoR gate applies the threshold rule.
4. The response releases output only on `PROCEED`; otherwise it returns a silence
   token and notes.

`/por/evaluate` skips generation and evaluates a caller-provided candidate.
This is the safest entry point for wrapping an existing generation stack.
