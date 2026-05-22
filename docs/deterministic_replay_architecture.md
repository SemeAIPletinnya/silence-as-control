# Deterministic Replay Architecture

## Purpose

The Deterministic Replay Architecture is a conceptual inspection layer for replaying normalized candidate evaluations inside the Reverse Integration Sandbox.

The purpose is not autonomous execution. The purpose is reproducible inspection and evaluation analysis.

Replay allows candidate intake and release decisions to be inspected more consistently across evaluation paths.

## Core idea

Normalized intake payloads may be replayed through the same conceptual evaluation flow to inspect:
- routing behavior
- release decisions
- evaluation traces
- normalization consistency
- transport-independent analysis paths

```text
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
Replay Trace
```

Replay is for inspection consistency, not autonomous authority.

Deterministic replay reduces ambiguity during evaluation analysis.

## Why this matters

Different intake paths may produce different evaluation contexts, even when they eventually map to similar candidate intent.

Replay allows repeated inspection of normalized candidate flows and may improve traceability and debugging across controlled evaluation conditions.

Transport-independent replay may improve comparison workflows between intake channels while keeping analysis focused on normalized payload and decision semantics.

Replay thinking also supports evidence-oriented evaluation architecture by making inspection paths easier to discuss and compare in documentation-first planning.

## Example conceptual replay record

```json
{
  "replay_id": "example-replay-001",
  "source_channel": "mattermost",
  "candidate_type": "message",
  "requested_action": "release_evaluation",
  "decision": "NEEDS_REVIEW",
  "trace_metadata": {
    "evaluation_mode": "sandbox_replay",
    "normalization_version": "concept-v1"
  }
}
```

This is only a conceptual replay example used for architectural discussion. It is not a committed runtime schema or API contract.

## What replay architecture is

The Deterministic Replay Architecture is:
- a conceptual replay layer
- an inspection-oriented architecture
- a traceability concept
- useful for sandbox experimentation
- useful for deterministic evaluation thinking
- useful for evidence-oriented workflows

## What replay architecture is not

It is not:
- autonomous execution
- a production replay engine
- guaranteed determinism
- a deployment platform
- a security boundary
- a runtime orchestration commitment
- a forensic guarantee system

## Relationship to the current repo

- `docs/reverse_integration_sandbox.md` explains the sandbox layer.
- `docs/sandbox_channel_adapters.md` explains intake adapters.
- `docs/intake_payload_schema.md` explains normalized intake payloads.
- `docs/agentic_release_control.md` explains release-control architecture.
- `docs/project_navigation.md` explains navigation flow.
- Issue #203 tracks roadmap/dependency evolution.

## Possible future directions

Possible future directions may include:
- replay-oriented evaluation traces
- deterministic inspection workflows
- replay comparison tooling
- normalization-version tracking
- intake replay telemetry
- evidence-linked replay reports

These are directional architecture notes only and do not represent committed runtime or product features.
