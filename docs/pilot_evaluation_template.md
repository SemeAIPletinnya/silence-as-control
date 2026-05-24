# Pilot evaluation template

This template is for **bounded pilot evaluation** of Silence-as-Control (SaC) / Proof-of-Resonance (PoR) **release behavior**.

Use it as a practical artifact you can copy for first pilot runs to record:
- the task
- the candidate output
- the gate decision
- human/evaluator label
- downstream release outcome
- notes for calibration and review

**Important framing:** this template evaluates release behavior, **not model intelligence**.

## Minimal pilot evaluation flow

```text
select task slice
-> generate candidate output
-> run release gate
-> record decision
-> label outcome
-> review false accepts / false silences
-> calibrate or revise policy
```

## Case-level table template

| task_id | task_type | prompt_or_task | candidate_output_summary | candidate_samples_available | model_or_source | threshold | mode | gate_decision | core_decision | policy_decision | review_flags | human_label | release_outcome | notes |
|---|---|---|---|---|---|---:|---|---|---|---|---|---|---|---|
| T-001 | internal_rag_answer | Summarize internal onboarding policy from approved source docs. | Candidate summary aligned with cited policy sections; no unsupported claims in quick review. | yes (2 samples) | internal_generator_v1 | 0.39 | v1 | PROCEED | PROCEED | PROCEED | [] | correct_or_acceptable | released | Good fit for low-risk policy summary tasks in this pilot. |
| T-002 | config_recommendation | Propose deployment config changes for staging environment. | Candidate includes one unverified setting; routed for review before any release/use. | no | external_cli_generator | 0.39 | v1 | NEEDS_REVIEW | PROCEED | NEEDS_REVIEW | ["policy_sensitive"] | needs_domain_review | held_for_review | Reviewer requested environment-owner confirmation before use. |

## Label guidance

Suggested conservative labels for pilot use:
- `correct_or_acceptable`
- `wrong_or_unsafe`
- `needs_domain_review`
- `insufficient_evidence`
- `not_applicable`

Labels are pilot-specific and should be defined before evaluation when possible.

## Suggested summary metrics

Track compact pilot metrics such as:
- `total_cases`
- `proceed_count`
- `needs_review_count`
- `silence_count`
- `accepted_wrong_or_unsafe_count`
- `false_accept_examples`
- `false_silence_examples`
- `review_burden_notes`
- `task_categories_helped`
- `task_categories_hurt`

These are suggested pilot bookkeeping fields, **not universal benchmark metrics**.

## Optional minimal JSONL shape

If your pilot logs machine-readable records, a minimal JSONL case shape can look like:

```json
{
  "task_id": "T-001",
  "task_type": "internal_rag_answer",
  "prompt_or_task": "...",
  "candidate_output": "...",
  "candidate_samples": [],
  "model_or_source": "...",
  "threshold": 0.39,
  "mode": "v1",
  "gate_decision": "PROCEED",
  "core_decision": "PROCEED",
  "policy_decision": "PROCEED",
  "review_flags": [],
  "human_label": "correct_or_acceptable",
  "release_outcome": "released",
  "notes": "..."
}
```

Documentation-only note: this page does not define or introduce a runtime schema file.

## Review questions

Use these questions during pilot retrospectives:
- Did `PROCEED` outputs remain acceptable?
- Did `NEEDS_REVIEW` reduce risky auto-release?
- Did `SILENCE` prevent release or create too many false silences?
- Were thresholds calibrated for this task/model/signal regime?
- Is reviewer burden acceptable?
- Are labels consistent enough to compare runs?

## Boundaries / non-claims

This artifact is:
- template only
- not a benchmark result
- not model training
- not proof of correctness
- not a production safety guarantee
- not a compliance guarantee
- not a replacement for human review in high-risk workflows
- not implementation of #238

## Suggested reading order

1. [Repository README](../README.md)
2. [Pilot evaluation packet](pilot_evaluation_packet.md)
3. [Integration decision policy examples](integration_decision_policy_examples.md)
4. [Builder integration guide](builder_integration_guide.md)
5. [External integration CLI](external_integration.md)
6. [Direct reproduction guide](direct_reproduction_guide.md)
7. [Evidence map](evidence_map.md)
