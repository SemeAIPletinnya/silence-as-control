# Runtime Governance Visual Map

## Purpose

This document provides a visual-oriented overview of the Runtime Governance Stack used in Silence-as-Control / PoR governance architecture.

The goal is:
- onboarding clarity
- governance readability
- conceptual stack visualization
- architecture orientation

This document is conceptual and documentation-oriented.

## Canonical governance map

```text
┌─────────────────────────────────────┐
│ External Transport / Connector      │
└─────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────┐
│ Connector Sandbox Boundary          │
└─────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────┐
│ Sandbox Channel Adapter             │
└─────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────┐
│ Normalized Intake Payload           │
└─────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────┐
│ Replay / Inspection Layer           │
└─────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────┐
│ PoR / Release Gate                  │
│ PROCEED / NEEDS_REVIEW / SILENCE    │
└─────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────┐
│ Decision Provenance                 │
└─────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────┐
│ Evaluation Trace                    │
└─────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────┐
│ Review Lane Routing                 │
└─────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────┐
│ Sandbox Evaluation Telemetry        │
└─────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────┐
│ Policy Surface                      │
└─────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────┐
│ Evidence Retention                  │
└─────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────┐
│ Reviewer / Evidence Surface         │
└─────────────────────────────────────┘
```

The governance stack separates:
- transport
- candidate intake
- evaluation
- release authority
- review visibility
- evidence continuity

This visual map is conceptual and does not represent a production runtime contract.

## Layer groups

### Intake and transport layers

Includes:
- connector boundary
- adapters
- normalized payloads

References:
- `connector_sandbox_boundary.md`
- `sandbox_channel_adapters.md`
- `intake_payload_schema.md`

### Evaluation and release-control layers

Includes:
- replay
- PoR gate
- release decisions

References:
- `deterministic_replay_architecture.md`
- `agentic_release_control.md`

### Traceability and review layers

Includes:
- provenance
- traces
- review routing
- telemetry

References:
- `decision_provenance_architecture.md`
- `evaluation_trace_architecture.md`
- `review_lane_architecture.md`
- `sandbox_evaluation_telemetry.md`

### Governance continuity layers

Includes:
- policy interpretation
- evidence retention
- reviewer/evidence surfaces

References:
- `policy_surface_architecture.md`
- `evidence_retention_architecture.md`
- `evidence_map.md`

## Suggested onboarding flow

1. `plain_english_pitch.md`
2. `project_navigation.md`
3. `runtime_governance_stack.md`
4. `governance_stack_walkthrough.md`
5. `runtime_governance_visual_map.md`
6. Layer-specific docs as needed.
7. Issue #203 for roadmap/dependency state.

## What this visual map is

This visual map is:
- a governance visualization layer
- a runtime-governance orientation surface
- a conceptual architecture map
- an onboarding-oriented reference

## What this visual map is not

It is not:
- a runtime specification
- a deployment contract
- a compliance framework
- a monitoring system
- a production architecture guarantee
- an autonomous governance engine

## Possible future directions

Possible future directions may include:
- SVG/PNG governance diagrams
- interactive architecture navigation
- reviewer-facing architecture summaries
- evidence-linked flow diagrams
- onboarding-oriented visual maps

These are directional possibilities and are not commitments.
