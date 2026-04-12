# Home

## Silence-as-Control in one paragraph

Silence-as-Control (Proof of Resonance, PoR) is a **runtime release-control layer**.
It does not change generation weights or decoding. It evaluates a candidate output and decides whether to release it (`PROCEED`) or withhold it (`SILENCE`).

Canonical gate logic:

```text
if drift > threshold OR coherence < threshold -> SILENCE
else -> PROCEED
```

Silence is an intentional control outcome, not an error, timeout, or crash.

## Core framing

Generation != Authority.
Release must be earned by stability.
Either correct, or silent.

## Current project stage

Current stage is:

- post-proof
- post-threshold-map
- structured API/runtime path exists
- pre-external integration proof

## Quick navigation

- [Current Status](Current-Status)
- [API Walkthrough](API-Walkthrough)
- [Threshold Regimes](Threshold-Regimes)
- [Evaluation Summary](Evaluation-Summary)
- [Evidence Map](Evidence-Map)
- [Reading Order](Reading-Order)
- [Milestones](Milestones)

## Repository references

- Runtime/API path: `docs/api_walkthrough.md`, `api/main.py`
- Evaluation artifacts and plots: `reports/`
- Existing concept and architecture material: `wiki/concepts/`, `wiki/architecture/`

## Notes on evidence surface

The repository now includes tracked JSONL run artifacts, run summaries, and visual evidence snapshots in `reports/`.
These strengthen proof readability, but they do not replace raw artifacts or external audited integration evidence.
