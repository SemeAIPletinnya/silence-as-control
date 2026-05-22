# Connector Sandbox Boundary

## Purpose

Connector Sandbox Boundary is a conceptual governance boundary for external communication surfaces interacting with sandbox evaluation flows.

The purpose is not autonomous execution.
The purpose is bounded intake, inspection, and routing visibility.

External connectors may conceptually provide candidate inputs into sandbox evaluation layers without automatically receiving execution authority.

## Core idea

External communication surfaces should remain separated from release authority.

Connectors may conceptually:
- submit candidate inputs
- receive bounded review outcomes
- participate in replay-oriented inspection flows

without bypassing release-control evaluation.

```text
External Connector
(Telegram / Discord / Slack / Mattermost / Webhook)
        ↓
Connector Sandbox Boundary
        ↓
Channel Adapter
        ↓
Normalized Intake Payload
        ↓
Replay / Inspection Layer
        ↓
PoR / Release Gate
        ↓
PROCEED / NEEDS_REVIEW / SILENCE
        ↓
Review / Evidence Surface
```

Connector boundaries are governance-oriented, not execution-oriented.

Transport access is not equivalent to release authority.

## Why this matters

- External communication surfaces may require bounded evaluation visibility.
- Transport layers should remain separated from release authority.
- Connectors may benefit from replay-oriented inspection thinking.
- Bounded connector routing may reduce ambiguity during sandbox evaluation.
- Connector boundaries support evidence-oriented governance workflows.

## Example conceptual connector-boundary record

```json
{
  "connector_boundary_id": "example-boundary-001",
  "source_connector": "mattermost",
  "candidate_type": "message",
  "boundary_mode": "sandbox_only",
  "routing_policy": {
    "allow_release": false,
    "allow_review_visibility": true
  },
  "review_hint": "Route candidate into sandbox evaluation before any release decision."
}
```

This is only a conceptual connector-boundary example used for architectural discussion.
It is not a runtime API contract, deployment configuration, or security guarantee.

## What connector sandbox boundaries are

Connector sandbox boundaries are:
- a conceptual governance boundary
- a bounded intake surface
- a separation layer between transport and release authority
- useful for sandbox experimentation
- useful for replay-oriented inspection workflows
- useful for evidence-oriented governance thinking

## What connector sandbox boundaries are not

They are not:
- unrestricted connector execution
- autonomous orchestration
- production deployment guarantees
- a security perimeter
- a compliance boundary
- unrestricted agent autonomy
- a runtime implementation commitment

## Relationship to the current repo

- `docs/reverse_integration_sandbox.md` explains the sandbox layer.
- `docs/sandbox_channel_adapters.md` explains intake adapters.
- `docs/intake_payload_schema.md` explains normalized intake payloads.
- `docs/deterministic_replay_architecture.md` explains replay and inspection.
- `docs/decision_provenance_architecture.md` explains provenance and review context.
- `docs/evaluation_trace_architecture.md` explains evaluation trace visibility.
- `docs/review_lane_architecture.md` explains governance routing.
- `docs/agentic_release_control.md` explains release-control architecture.
- `docs/project_navigation.md` explains navigation flow.
- Issue #203 tracks roadmap/dependency evolution.

## Possible future directions

Possible future directions may include:
- bounded connector routing
- replay-linked connector traces
- review-visible connector summaries
- evidence-linked transport records
- connector-specific review lanes
- transport-aware sandbox telemetry

These directions are exploratory and do not represent implementation commitments.
