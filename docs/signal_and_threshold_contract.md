# Signal and Threshold Contract

This page is the single source of truth for threshold and signal semantics in this repository.

## Why multiple layers exist

The repository contains three distinct layers with different purposes:

1. **Evidence/eval** for producing reported run artifacts.
2. **Runtime/API demo** for local gating behavior in the API path.
3. **Deterministic library control** for tested, stable control logic in `src/`.

These layers intentionally do **not** share one universal threshold primitive.

## Canonical layer contract table

| layer | file | signal names | threshold / condition | role | canonical status | notes |
|---|---|---|---|---|---|---|
| Evidence / eval | `scripts/live_eval_openai.py` (artifacts in `reports/*`, run summaries in `wiki/runs/*`) | `semantic_proxy_drift`, `raw_quality_score` | `semantic_proxy_drift >= 0.39` => silence, `raw_quality_score >= 0.55` => raw success | Produces evidence/workstream outputs used in reported runs | **Canonical for reported evidence** | This is the source contract for run-artifact interpretation. |
| Runtime / API demo | `api/main.py` | `estimate_drift`, `estimate_coherence` | `drift > 0.39 OR coherence < 0.39` => silence (default) | Local runtime/demo gate for API interaction | Canonical only for runtime/demo behavior | Heuristic runtime estimates are not identical to eval artifact semantics. |
| Deterministic library control | `src/silence_as_control/control.py` | `drift`, `coherence` (inputs to `por_control`) | `drift <= 0.3` and `coherence >= 0.7` required to proceed | Deterministic control primitive for library/tests | **Canonical deterministic control contract** | This is tested library logic and separate from eval/runtime heuristics. |

## Explicit canon language

- **Canonical for reported evidence**: eval pipeline + run artifacts (`scripts/live_eval_openai.py`, `reports/*`, `wiki/runs/*`).
- **Runtime/demo threshold**: API-local gate semantics in `api/main.py`.
- **Deterministic library control contract**: tested control interface in `src/silence_as_control/control.py`.

## What this does NOT mean

- `0.39` is **not** universal across all modules.
- Runtime/demo threshold naming does **not** imply semantic identity with `semantic_proxy_drift` from eval artifacts.
- Deterministic control thresholds (`drift <= 0.3`, `coherence >= 0.7`) are **not** the same primitive as the evidence/eval `0.39` anchor.
