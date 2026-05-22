# Runtime Governance Stack

## Purpose

Runtime Governance Stack is a canonical map of the conceptual governance layers used in Silence-as-Control / PoR sandbox and release-control architecture.

The purpose is not to introduce a new runtime feature.
The purpose is to show how existing conceptual documents fit together.

This document should act as an orientation layer for reviewers, contributors, and future Codex/ChatGPT sessions.

## Core stack

```text
External Transport / Connector
        ↓
Connector Sandbox Boundary
        ↓
Sandbox Channel Adapter
        ↓
Normalized Intake Payload
        ↓
Replay / Inspection Layer
        ↓
PoR / Release Gate
        ↓
Decision Provenance
        ↓
Evaluation Trace
        ↓
Review Lane Routing
        ↓
Sandbox Evaluation Telemetry
        ↓
Policy Surface
        ↓
Evidence Retention
        ↓
Reviewer / Evidence Surface
```

The stack separates transport, generation, evaluation, release authority, review visibility, and evidence continuity.

This is a conceptual governance map, not a production runtime contract.

## Layer responsibilities

| Layer | Responsibility | Related doc |
| --- | --- | --- |
| Connector Sandbox Boundary | Separates external transport access from release authority. | `connector_sandbox_boundary.md` |
| Sandbox Channel Adapter | Describes conceptual channel intake connectors. | `sandbox_channel_adapters.md` |
| Normalized Intake Payload | Describes a shared evaluation envelope for candidate inputs. | `intake_payload_schema.md` |
| Replay / Inspection Layer | Describes replay-oriented inspection of normalized candidates. | `deterministic_replay_architecture.md` |
| PoR / Release Gate | Produces `PROCEED`, `NEEDS_REVIEW`, or `SILENCE`. | `agentic_release_control.md` |
| Decision Provenance | Connects release decisions to inspectable context. | `decision_provenance_architecture.md` |
| Evaluation Trace | Describes candidate movement through evaluation layers. | `evaluation_trace_architecture.md` |
| Review Lane Routing | Separates proceed/review/silence routing visibility. | `review_lane_architecture.md` |
| Sandbox Evaluation Telemetry | Summarizes sandbox activity for bounded inspection. | `sandbox_evaluation_telemetry.md` |
| Policy Surface | Provides bounded policy-aware interpretation. | `policy_surface_architecture.md` |
| Evidence Retention | Preserves references for bounded evidence continuity. | `evidence_retention_architecture.md` |
| Reviewer / Evidence Surface | Final human-facing inspection and evidence layer. | `evidence_map.md` |

## What the stack is

The Runtime Governance Stack is:
- a canonical architecture map
- a navigation layer across existing docs
- a way to understand conceptual dependencies
- useful for reviewers and contributors
- useful for future roadmap sessions
- documentation-first and conservative

## What the stack is not

It is not:
- a production runtime contract
- a deployed system
- a compliance framework
- a security guarantee
- a monitoring platform
- an autonomous enforcement system
- an API specification
- a runtime implementation commitment

## Relationship to roadmap and issues

- `docs/roadmap_2026.md` is the strategic roadmap.
- Issue #202 is the project memory capsule.
- Issue #203 is the live roadmap/progress/dependency capsule.
- This document is the canonical governance-stack map.
- Individual architecture docs remain the source for each layer’s detailed explanation.

## Suggested reading order

1. `plain_english_pitch.md`
2. `project_navigation.md`
3. `agentic_release_control.md`
4. `reverse_integration_sandbox.md`
5. `runtime_governance_stack.md`
6. Layer-specific docs as needed.
7. `evidence_map.md`
8. Issue #203 for live roadmap/dependency state.

## Possible future directions

Possible future directions may include:
- a visual diagram version of the governance stack
- reviewer-facing architecture summaries
- evidence-linked stack walkthroughs
- sandbox-stack onboarding examples
- trace-to-policy-to-evidence navigation guides

These are directional ideas and do not represent implementation commitments.
