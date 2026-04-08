# PoR Gate

_Back to [index](../index.md) · Related: [Release Control Layer](./Release_Control_Layer.md)_

## Purpose

The **PoR Gate** is the architectural checkpoint that determines whether generated content can cross into release.

## Position in pipeline

`Input -> Generation -> PoR Gate -> {Proceed | Silence}`

PoR is downstream of generation and upstream of release.

## Decision inputs

The current repository implementation evaluates release using runtime signals including drift/coherence checks and format validity checks.

(See implementation in `api/main.py`, especially `por_decision(...)` and `evaluate_candidate(...)`.)

## Decision outputs

- **Proceed**: candidate is eligible for output.
- **Silence**: candidate is not released.

Note: a separate “hold” state is not documented as an active mode in the current code path.

See [Threshold Model](../concepts/Threshold_Model.md) and run pages for artifact-backed behavior.
