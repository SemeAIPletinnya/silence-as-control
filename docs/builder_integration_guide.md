# Builder integration guide

This guide is for builders who already have a generator: a model, an agent, a RAG system, a coding assistant, or a workflow engine.

In Silence-as-Control, the release gate is placed **after** candidate generation and **before** release. Your generator stays as-is. You do not need to change how it produces candidates.

The gate then decides whether the candidate should be released, routed for review, or withheld. This is a release-control decision layer, not a generation-improvement layer.

Generation and release are separate responsibilities. This guide focuses on where and how to insert the release decision boundary.

## 1. Integration thesis

Generation creates a candidate. Release is a separate runtime decision.

Do not treat generation as automatic release authority. Add a gate between candidate creation and user-visible/action-visible release. The gate output should become part of the system's audit trail.

## 2. Where the gate sits

```text
user/task request
  -> existing generator/model/agent/RAG/coding tool
  -> candidate output
  -> SaC / PoR release gate
       -> PROCEED
       -> NEEDS_REVIEW
       -> SILENCE
  -> downstream release policy
```

- **PROCEED:** release the candidate.
- **NEEDS_REVIEW:** route to human/reviewer/workflow review.
- **SILENCE:** withhold output or trigger a bounded fallback.

Do not auto-convert `SILENCE` into another ungoverned generation step.

## 3. Minimal CLI integration

See [`docs/external_integration.md`](external_integration.md) for the external CLI integration surface.

```bash
python scripts/por_gate_cli.py --input examples/por_gate_input.json --output outputs/por_gate_decision.json
```

Minimal input shape:

```json
{
  "prompt": "User task or system request",
  "candidate_answer": "Candidate output from your generator",
  "candidate_samples": [
    "Candidate output from your generator"
  ],
  "threshold": 0.39,
  "mode": "v1",
  "metadata": {
    "model": "external-generator-name",
    "source": "external_pipeline"
  }
}
```

Minimal output fields:

```json
{
  "decision": "PROCEED | NEEDS_REVIEW | SILENCE",
  "released_output": "...",
  "silence": false,
  "needs_review": false,
  "signals": {},
  "audit": {}
}
```

## 4. App / API integration pattern

Conceptual pattern:

1. Call your model or agent first.
2. Capture the candidate answer.
3. Submit `prompt` + `candidate_answer` + optional `candidate_samples` to the release gate.
4. Read `decision`.
5. Apply your own downstream release policy.

Pseudocode example (illustrative only, **not** a new API implementation):

```python
candidate = generator.run(task)

gate_result = por_gate.evaluate(
    prompt=task,
    candidate_answer=candidate,
    candidate_samples=[candidate],
    metadata={"model": "my-generator", "source": "my_app"},
)

if gate_result["decision"] == "PROCEED":
    return gate_result["released_output"]

if gate_result["decision"] == "NEEDS_REVIEW":
    return route_to_review(gate_result)

if gate_result["decision"] == "SILENCE":
    return withhold_or_safe_fallback(gate_result)
```

## 5. RAG / coprocessor integration pattern

RAG retrieval can stay unchanged. The generated answer becomes a candidate. Silence-as-Control then gates that candidate before it is shown to a user or used downstream.

Audit metadata should preserve source, retrieval context ID (if available), model, threshold, and decision.

```text
query
  -> retrieval
  -> answer generation
  -> candidate answer
  -> release gate
  -> user-visible answer / review / silence
```

## 6. Agent / workflow integration pattern

Agent plans and tool-use recommendations can be treated as release candidates. Gate those candidates before executing or exposing high-impact actions.

`NEEDS_REVIEW` is useful for stable-looking but operationally risky action suggestions. `SILENCE` should not automatically execute a hidden retry loop without policy.

Examples:

- config mutation suggestions
- deployment recommendations
- file/system modification plans
- tool-call plans
- workflow action candidates

## 7. Coding-agent bridge pattern

[`por-copilot-bridge`](https://github.com/SemeAIPletinnya/por-copilot-bridge) is an applied bridge for coding-agent outputs.

It is not a direct dependency of `silence-as-control`. It demonstrates the same state/schema idea: `PROCEED / NEEDS_REVIEW / SILENCE`.

Use it as an applied example for coding assistant output review, alongside [`docs/applied_bridges.md`](applied_bridges.md).

## 8. What metadata builders should preserve

Recommended audit metadata:

- source
- model
- threshold
- mode
- task type
- candidate id
- timestamp (if available)
- retrieval/context id (if applicable)
- decision
- review_flags
- core_decision
- policy_decision

Metadata makes the gate auditable and helps compare release behavior across tasks.

## 9. Decision policy checklist

For each integration, define:

- What happens on `PROCEED`?
- What happens on `NEEDS_REVIEW`?
- What happens on `SILENCE`?
- Who reviews `NEEDS_REVIEW`?
- Is `SILENCE` a final abstention, retry, safe fallback, or no-output path?
- What counts as an unsafe release?
- Which thresholds are used and why?
- Which evidence supports this task/model/signal regime?

## 10. Boundaries and non-claims

This guide does not define a production safety guarantee.

It does not prove model correctness.

It does not make thresholds universal.

It does not replace task-specific evaluation.

It does not remove the need for human review in high-risk workflows.

It does not implement #238.

## 11. Suggested builder reading order

1. [`README.md`](../README.md)
2. [`docs/direct_reproduction_guide.md`](direct_reproduction_guide.md)
3. [`docs/external_integration.md`](external_integration.md)
4. [`docs/builder_integration_guide.md`](builder_integration_guide.md)
5. [`docs/external_reviewer_packet.md`](external_reviewer_packet.md)
6. [`docs/evidence_map.md`](evidence_map.md)
7. [`docs/applied_bridges.md`](applied_bridges.md)
