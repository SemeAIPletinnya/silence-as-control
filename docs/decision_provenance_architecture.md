# Decision Provenance Architecture

## Purpose

Decision Provenance Architecture is a conceptual traceability layer for explaining how a sandbox release decision was reached.

The purpose is not autonomous authority. The purpose is inspectable decision context.

A release decision should not be treated as a black box when it can be connected to candidate input, normalization context, replay traces, evaluation signals, and routing outcomes.

## Core idea

After a normalized candidate is evaluated, the result may be associated with a provenance record that helps reviewers understand the decision path.

```text
Normalized Intake Payload
        ↓
Replay / Inspection Layer
        ↓
PoR / Release Gate
        ↓
PROCEED / NEEDS_REVIEW / SILENCE
        ↓
Decision Provenance Record
        ↓
Reviewer / Evidence Surface
```

Decision provenance is for inspection, not automatic justification.

A decision record should describe the path to a release outcome without pretending to prove universal correctness.

## Why this matters

Release decisions need traceability so reviewers can inspect the reasoning path behind routing outcomes.

Reviewers need to understand why a candidate was released, reviewed, or silenced in a sandbox evaluation flow.

Provenance records may help compare decisions across replay runs, especially when the same candidate family is evaluated under different contexts.

Provenance thinking supports evidence-oriented evaluation workflows by keeping decision context explicit and reviewable.

Traceable decisions reduce ambiguity during review and debugging by preserving a consistent inspection surface.

## Example conceptual provenance record

```json
{
  "provenance_id": "example-prov-001",
  "replay_id": "example-replay-001",
  "source_channel": "mattermost",
  "candidate_type": "message",
  "decision": "NEEDS_REVIEW",
  "decision_context": {
    "reason_category": "borderline_or_ambiguous_candidate",
    "evaluation_mode": "sandbox_replay",
    "normalization_version": "concept-v1"
  },
  "review_hint": "Route to human or policy review before release."
}
```

This is only a conceptual provenance example used for architectural discussion. It is not a committed runtime schema, API contract, or explanation guarantee.

## What decision provenance is

Decision provenance is:
- a conceptual traceability layer
- an inspection-oriented record
- a way to connect release decisions to normalized inputs
- useful for replay comparison thinking
- useful for review workflows
- useful for evidence-oriented documentation

## What decision provenance is not

It is not:
- proof of correctness
- full model explainability
- a legal audit guarantee
- a security boundary
- a production compliance system
- autonomous justification
- a runtime implementation commitment

## Relationship to the current repo

- `docs/reverse_integration_sandbox.md` explains the sandbox layer.
- `docs/sandbox_channel_adapters.md` explains intake adapters.
- `docs/intake_payload_schema.md` explains normalized intake payloads.
- `docs/deterministic_replay_architecture.md` explains replay and inspection.
- `docs/agentic_release_control.md` explains release-control architecture.
- `docs/project_navigation.md` explains navigation flow.
- Issue #203 tracks roadmap/dependency evolution.

## Possible future directions

Possible future directions may include:
- provenance-oriented evaluation traces
- decision reason categories
- review hints
- replay-to-provenance comparison
- evidence-linked decision records
- reviewer-facing trace summaries

These directions are exploratory architectural considerations and are not promised features or implementation commitments.
