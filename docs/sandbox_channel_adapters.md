# Sandbox Channel Adapters

## Purpose

Sandbox Channel Adapters are lightweight intake connectors that allow external systems or communication channels to submit candidate outputs into the Reverse Integration Sandbox for evaluation.

The purpose is not direct execution. The purpose is controlled intake and release evaluation.

This concept is architectural and conservative: it describes intake boundaries for evaluation flows, not production orchestration.

## Core architecture

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
Sandbox Intake Layer
        ↓
Normalization
        ↓
PoR / Release Gate
        ↓
PROCEED / NEEDS_REVIEW / SILENCE
```

Different channels may produce different output formats, message shapes, or metadata. The intake layer normalizes those candidate submissions into a consistent evaluation envelope before release evaluation.

Transport channel is not release authority.

Generation transport is not release authority.

## Why this matters

Generated outputs may arrive from multiple surfaces, including:

- chat systems
- self-hosted team communication platforms
- coding assistants
- support tools
- workflow automation
- external agents
- repository bots
- operational dashboards

The architecture separates message transport from release authority so intake convenience does not bypass evaluation control.

## What channel adapters are

Channel adapters are:

- intake connectors
- normalization layers
- controlled routing surfaces
- evaluation entry points
- useful for demos, pilots, and controlled experiments

## What channel adapters are not

They are not:

- autonomous agents
- trusted execution systems
- deployment systems
- guaranteed-safe integrations
- production orchestration
- unrestricted automation

## Example flows

### Telegram example

```text
Telegram bot
→ candidate message
→ sandbox intake
→ release evaluation
→ decision returned
```

### Mattermost example

```text
Mattermost message
→ candidate operational output
→ sandbox intake
→ normalization
→ release evaluation
→ PROCEED / NEEDS_REVIEW / SILENCE
```

### GitHub example

```text
GitHub PR comment
→ candidate patch/action
→ sandbox intake
→ release evaluation
→ PROCEED / NEEDS_REVIEW / SILENCE
```

### Webhook example

```text
external webhook
→ candidate payload
→ normalization
→ release evaluation
→ decision response
```

## Relationship to the current repo

- `docs/reverse_integration_sandbox.md` explains the sandbox layer.
- `docs/agentic_release_control.md` explains release-control architecture.
- `docs/project_navigation.md` explains navigation flow.
- `docs/release_control_services.md` explains pilot/integration direction.
- Issue #203 tracks roadmap/dependency evolution.

## Possible future directions

Possible future directions may include:

- intake replay
- structured candidate payloads
- adapter-specific telemetry
- review queues
- deterministic replay/testing
- evaluation dashboards
- external comparison workflows

These are exploratory directions only and are not promised features.
