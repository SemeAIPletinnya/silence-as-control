# Runtime Extensions

You are here: optional deployment-layer behavior (non-core).

## Included extensions

- `POR_RUNTIME_GATE_THRESHOLD` environment override.
- Adaptive threshold from recent drift/coherence.
- Embedding-based coherence scoring.
- Multi-sample embedding disagreement for drift.

Implementation: `api/por_runtime.py`, wired via `api/main.py`.

## Why they exist

Fixed thresholds are stable and auditable, but deployments across domains may need practical tuning support.

## What they are not

These are not the thesis-level primitive. They are runtime integration helpers.
