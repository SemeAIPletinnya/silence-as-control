# Home

## Silence-as-Control in one paragraph

Silence-as-Control (Proof of Resonance, PoR) is a **runtime release-control layer**.
It does not change generation weights or decoding. It evaluates a candidate output and decides whether to release it (`PROCEED`) or withhold it (`SILENCE`).

Canonical gate logic:

```text
if drift > threshold OR coherence < threshold -> SILENCE
else -> PROCEED
```

Silence is an intentional control outcome (not an error and not a timeout).

## Core framing

- Generation != Authority.
- Release must be earned by stability.
- Either correct, or silent.

## Current project stage

Current stage is:
- post-proof
- post-threshold-map
- applied API/runtime surface emerging
- pre-clear external integration demo

## Quick navigation

- [Current Status](./Current-Status.md)
- [API Walkthrough](./API-Walkthrough.md)
- [Threshold Regimes](./Threshold-Regimes.md)
- [Evaluation Summary](./Evaluation-Summary.md)
- [Evidence Map](./Evidence-Map.md)
- [Reading Order](./Reading-Order.md)
- [Milestones](./Milestones.md)

## Repository references

- Runtime/API path: `docs/api_walkthrough.md`, `api/main.py`
- Evaluation artifacts: `reports/`
- Existing concept + architecture material: `wiki/concepts/`, `wiki/architecture/`
