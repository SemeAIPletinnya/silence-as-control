# Pilot outreach examples

This page is for lightweight, bounded pilot/audit conversations.

- It is not a mass outreach script.
- It is not a pricing page.
- It is not a production-readiness claim.
- It should help a reader understand what to send first and what evidence links to include.

## Core offer

First offer: **AI workflow release-control audit**.

This audit stays narrow and conservative:

- It looks for places where generated output becomes release/action.
- The goal is to identify where a release gate could be inserted.
- The deliverable is a bounded review and a recommended pilot design.
- The audit evaluates release behavior, not model intelligence.

## What to send first

Recommended link order:

1. [README](../README.md)
2. [docs/release_control_services.md](release_control_services.md)
3. [docs/pilot_evaluation_packet.md](pilot_evaluation_packet.md)
4. [docs/builder_integration_guide.md](builder_integration_guide.md)
5. [docs/direct_reproduction_guide.md](direct_reproduction_guide.md)
6. [docs/evidence_map.md](evidence_map.md)

Show the no-key reproduction path before any provider-backed claims.

## Outreach example: technical builder

Hi — I am working on Silence-as-Control, a release-control layer for LLM/agent outputs.

It separates candidate generation from release authority.

I am looking for 1-2 bounded pilot conversations with teams building agents, RAG systems, or coding assistants.

The first step is a small workflow audit: where does generated output become user-visible output or action?

No production-safety claims; the goal is scoped release-behavior evaluation.

## Outreach example: founder/operator

Many LLM workflows still release generated output by default.

This can create accepted-wrong-output and review-routing risk.

Silence-as-Control adds a small release decision layer: PROCEED / NEEDS_REVIEW / SILENCE.

I can review one workflow and propose a bounded pilot.

## Outreach example: researcher/reviewer

v0.7 has a deterministic no-key capture-to-replay evidence path.

The project is not claiming universal safety.

The focus is release behavior under a runtime gate.

Feedback on evidence boundaries and pilot design is welcome.

## What not to say

Avoid phrases like:

- “solves hallucinations”
- “guarantees correctness”
- “production-safe AI”
- “AGI runtime”
- “fully autonomous safety layer”
- “universal threshold”
- “model improvement”
- “replacement for human review”

## Better phrases

Prefer phrases like:

- “release-control audit”
- “bounded pilot”
- “runtime release gate”
- “candidate/release separation”
- “accepted-output risk review”
- “review-routing layer”
- “deterministic no-key reviewer path”
- “scoped release-behavior evaluation”

## Minimal pilot ask

Suggested ask:

“Can we review one workflow where an LLM or agent produces output that becomes user-visible, code-visible, or action-visible?”

Minimal pilot shape:

- 25-50 examples for qualitative review.
- 100-300 examples for early quantitative review.
- Measure PROCEED / NEEDS_REVIEW / SILENCE.
- Preserve candidate, decision, review flag, and outcome note.

## Boundaries

- Not a production safety guarantee.
- Not model training.
- Not model improvement.
- Not hallucination elimination.
- Not a replacement for human review.
- Provider/local generated-candidate capture remains optional future work.
- Thresholds must be calibrated per task/model/signal regime.

## Suggested follow-up reading

- [release_control_services.md](release_control_services.md)
- [pilot_evaluation_packet.md](pilot_evaluation_packet.md)
- [pilot_evaluation_template.md](pilot_evaluation_template.md)
- [builder_integration_guide.md](builder_integration_guide.md)
- [direct_reproduction_guide.md](direct_reproduction_guide.md)
- [evidence_map.md](evidence_map.md)
