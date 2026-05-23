# Pilot evaluation packet

**Pilot thesis:** Generation creates a candidate. Release is a separate runtime decision. A pilot evaluates release behavior, not model intelligence.

This packet is for bounded evaluation of Silence-as-Control (SaC) / Proof-of-Resonance (PoR) release behavior. It is intentionally conservative and evidence-first.

Core framing:
- Generation creates a candidate.
- Release is a separate runtime decision.
- Same model. Different decision.
- Either correct, or silent.

## Who this pilot is for

Suitable pilot scopes:
- coding-agent output review
- config/deployment recommendations
- internal RAG/copilot answers
- workflow/action candidates
- agent plans before execution

Not suitable for first pilots:
- autonomous medical/legal/financial decisioning
- high-stakes production release without human review
- broad claims of hallucination elimination
- production safety claims without deployment evidence

## Minimal pilot flow

```text
existing generator
-> candidate output
-> SaC / PoR release gate
-> PROCEED / NEEDS_REVIEW / SILENCE
-> evaluator logs decision and outcome
```

## What to measure

Track pilot-level metrics (not only anecdotal examples):
- total candidates
- accepted outputs
- accepted wrong / unsafe outputs
- NEEDS_REVIEW rate
- SILENCE rate
- false accept examples
- false silence examples
- reviewer burden
- task categories where the gate helps
- task categories where the gate hurts

## Data/evidence to preserve

For each evaluated case, preserve a compact audit record with:
- prompt/task
- candidate output
- candidate samples if available
- model/source
- threshold/mode
- decision
- core_decision
- policy_decision
- review_flags
- evaluator/human label if available
- notes on whether release would have been harmful, wrong, low-confidence, or merely policy-sensitive

## Suggested pilot sizes

Practical starting points (not universal requirements):
- 25-50 tasks for first qualitative review
- 100-300 tasks for early quantitative review
- 1000+ only after taxonomy, labels, and review rules are stable

These ranges are meant to reduce over-claiming and encourage stable evaluation design before scaling volume.

## Success criteria examples

Treat success as scoped release-behavior improvement, for example:
- fewer unsafe accepted outputs than baseline release-by-default
- useful separation between PROCEED / NEEDS_REVIEW / SILENCE
- actionable audit trail
- clearer review routing
- identifiable task categories where the gate is useful

## Failure criteria examples

A pilot should be treated as unsuccessful or inconclusive when you observe:
- too many false accepts
- too many false silences
- unclear reviewer burden
- weak task taxonomy
- missing labels/evidence
- threshold not calibrated for the pilot context
- NEEDS_REVIEW becoming a dumping ground without clear review policy

## Suggested evaluation table

Use a lightweight table template for consistent case logging:

| task_id | task_type | model/source | candidate_summary | gate_decision | review_flags | evaluator_label | release_outcome_note |
|---|---|---|---|---|---|---|---|
| T-001 |  |  |  | PROCEED / NEEDS_REVIEW / SILENCE |  |  |  |
| T-002 |  |  |  | PROCEED / NEEDS_REVIEW / SILENCE |  |  |  |

## Boundaries / non-claims

This packet is explicitly:
- not a production safety guarantee
- not model training
- not a universal hallucination detector
- not proof of correctness
- not a replacement for human review in high-risk workflows
- not implementation of #238

Additional boundary condition:
- thresholds are scoped and must be calibrated per task/model/signal regime

## Suggested reading order

1. [Repository README](../README.md)
2. [External reviewer packet](external_reviewer_packet.md)
3. [Direct reproduction guide](direct_reproduction_guide.md)
4. [Builder integration guide](builder_integration_guide.md)
5. [External integration CLI](external_integration.md)
6. [Evidence map](evidence_map.md)
7. [Release-control services](release_control_services.md)
8. [Release-risk benchmark index](release_risk_benchmark_index.md)
