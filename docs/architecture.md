# Architecture: Core vs Runtime vs Experimental

You are here: architecture boundary map for external readers.

Silence-as-Control is intentionally split into three layers so readers can separate the **paper claim** from deployment extras.

## 1) Core Primitive (paper claim)

Core statement: **same model, different decision**.

- Generation and release are separate.
- PoR gate computes instability score `I = (drift + (1 - coherence)) / 2`.
- Fixed-threshold decision:
  - `I <= threshold` -> `PROCEED`
  - `I > threshold` -> `SILENCE`

Reference modules: `api/core_primitive.py`, `src/silence_as_control/control.py`.

## 2) Runtime Extensions (deployment helpers)

Useful, optional runtime helpers:
- environment-configurable runtime threshold,
- adaptive thresholding from recent history,
- embedding-based coherence,
- multi-sample drift estimation.

The bundled embedding fallback is deterministic and lightweight for reproducible runtime behavior; production deployments may provide stronger semantic embeddings.

Reference module: `api/por_runtime.py`.

## 3) Experimental Borderline Recovery

Optional post-silence lane:
- MAYBE_SHORT_REGEN only after initial `SILENCE`,
- only in narrow boundary pocket,
- explicitly experimental and non-core.

Reference module: `api/experimental_recovery.py`.

## Why this separation matters

This keeps the thesis-level primitive stable and auditable while still allowing practical extensions and experiments.
