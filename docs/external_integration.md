# External integration CLI

## Purpose

Silence-as-Control can be called after an external system generates a candidate output.
The external generator remains unchanged.
The gate decides whether the candidate should be released.

## Command

```bash
python scripts/por_gate_cli.py --input examples/por_gate_input.json --output outputs/por_gate_decision.json
```

## Stdout mode

```bash
python scripts/por_gate_cli.py --input examples/por_gate_input.json
```

## Input fields

- `prompt`
- `candidate_answer`
- optional `candidate_samples`
- optional `threshold`
- optional `mode`
- optional `metadata`

## Output fields

- `decision`
- `released_output`
- `silence`
- `needs_review`
- `threshold`
- `mode`
- `signals.drift`
- `signals.coherence`
- `signals.instability`
- `signals.review_flags`
- `audit.reason`
- `audit.core_decision`
- `audit.policy_decision`
- `audit.model`
- `audit.source`

## Decision semantics

- `PROCEED`:
  Candidate is released.
- `NEEDS_REVIEW`:
  Candidate is stable enough at the PoR core layer, but release-policy flags require review.
- `SILENCE`:
  Candidate exceeded instability threshold and is not released.

## Architecture boundary

- PoR core primitive:
  `PROCEED` / `SILENCE`
- Release policy layer:
  `PROCEED` / `NEEDS_REVIEW` / `SILENCE`

## Claims boundary

- This is not a new model.
- This is not a training method.
- This is not a universal truth detector.
- This does not guarantee safety.
- It is a scoped post-generation release-control interface.

## Relation to por-copilot-bridge

`por-copilot-bridge` is an applied bridge for coding-agent outputs.
It is compatible by state/schema and architecture.
It is not a direct dependency of silence-as-control.
