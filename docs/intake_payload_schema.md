# Intake Payload Schema

## Purpose

The Intake Payload Schema is a conceptual normalization format for candidate outputs entering the Reverse Integration Sandbox.

The purpose is not execution. The purpose is consistent evaluation and release-control routing.

Different transport channels may produce different message formats, metadata structures, or candidate types. The schema provides a common evaluation envelope before release decisions are made.

## Core idea

Sandbox Channel Adapters may normalize incoming candidate outputs into a shared structure before release evaluation.

Normalization reduces transport-specific ambiguity before evaluation.

```text
Telegram
Slack
Discord
Mattermost
Webhook
GitHub Comment
CLI
Email
        ↓
Channel Adapter
        ↓
Normalized Intake Payload
        ↓
PoR / Release Gate
        ↓
PROCEED / NEEDS_REVIEW / SILENCE
```

## Example conceptual payload

```json
{
  "source_channel": "telegram",
  "candidate_type": "message",
  "candidate_payload": "example candidate output",
  "requested_action": "release_evaluation",
  "metadata": {
    "origin": "sandbox_adapter",
    "transport_mode": "chat"
  }
}
```

This is only a conceptual example used to describe architectural normalization ideas. It is not a committed runtime contract.

## Why this matters

- Different channels produce inconsistent formats.
- Release evaluation should not depend on transport-specific layouts.
- Normalization allows more consistent replay, inspection, and evaluation.
- A shared intake envelope may improve deterministic analysis paths.

## What the schema is

The Intake Payload Schema is:

- a conceptual normalization layer
- a shared intake structure
- a routing/evaluation envelope
- useful for replay and inspection thinking
- useful for sandbox experimentation

## What the schema is not

It is not:

- a production API contract
- a deployment protocol
- a security boundary
- a guarantee of correctness
- a stable interoperability standard
- a runtime implementation commitment

## Relationship to the current repo

- `docs/reverse_integration_sandbox.md` explains the sandbox layer.
- `docs/sandbox_channel_adapters.md` explains intake adapters.
- `docs/agentic_release_control.md` explains release-control architecture.
- `docs/project_navigation.md` explains navigation flow.
- Issue #203 tracks roadmap/dependency evolution.

## Possible future directions

Possible future directions may include:

- replay-friendly payload structures
- adapter-specific metadata envelopes
- structured evaluation traces
- deterministic replay workflows
- evaluation comparison tooling
- intake telemetry surfaces

These are exploratory directions only and are not commitments to runtime implementation.
