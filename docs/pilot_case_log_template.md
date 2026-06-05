# Pilot case log template

## 1. Purpose

This template is for bounded pilot logging during a first Silence-as-Control (SaC) evaluation. It helps reviewers compare release-by-default behavior against SaC-style release mediation, where a generated candidate is evaluated before it is allowed to proceed.

The log is not benchmark evidence by itself. It is not production deployment evidence. It is a practical traceability surface for manual review: each candidate, baseline release assumption, SaC decision, review reason, and reviewer interpretation should remain inspectable together.

## 2. When to use this template

Use this template:

- during a first 25–100 case pilot
- for one narrow workflow or task family
- before production enforcement
- when comparing candidate outputs against release-gate decisions

Do not use a first pilot log to make broad production, provider-backed, or universal safety claims.

## 3. Case log table

| case_id | workflow | prompt_or_task | candidate_summary | baseline_release | sac_decision | review_reason | human_label | release_outcome_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |  |

Column meanings:

- `case_id`: stable pilot identifier.
- `workflow`: narrow pilot workflow or task family.
- `prompt_or_task`: short task description.
- `candidate_summary`: compact summary, not necessarily the full raw output.
- `baseline_release`: whether the candidate would have been released by default.
- `sac_decision`: `PROCEED` / `NEEDS_REVIEW` / `SILENCE`.
- `review_reason`: short explanation, trace, or policy note.
- `human_label`: optional reviewer label such as `acceptable`, `risky`, `wrong`, `unsafe`, or `unclear`.
- `release_outcome_note`: final reviewer interpretation.

## 4. Decision values

- `PROCEED`: release the candidate.
- `NEEDS_REVIEW`: do not auto-release; route the candidate for bounded review.
- `SILENCE`: withhold the candidate.

## 5. Suggested labels

Optional human labels include:

- `acceptable`
- `review-worthy`
- `wrong`
- `unsafe`
- `unclear`
- `policy-sensitive`
- `insufficient-evidence`

## 6. Minimal pilot summary

```text
Total cases:
Baseline released:
SaC PROCEED:
SaC NEEDS_REVIEW:
SaC SILENCE:
False-negative releases found:
False-positive reviews found:
Notes:
```

## 7. Evidence boundary

This log is pilot evidence only for the scoped workflow, candidate set, thresholds, and policy settings. It does not prove model correctness, guarantee safety, or prove universal threshold transfer.

Interpret the log together with the [Pilot evaluation packet](pilot_evaluation_packet.md) and [Evidence map](evidence_map.md), especially when deciding which claims are supported by repository-visible evidence and which claims remain outside the current evidence boundary.

## 8. Relationship to existing docs

Use this template alongside:

- [Pilot evaluation packet](pilot_evaluation_packet.md)
- [Reviewer console guide](reviewer_console_guide.md)
- [Evidence map](evidence_map.md)
- [Runtime evidence linkage](runtime_evidence_linkage.md)
- [Release-risk benchmark index](release_risk_benchmark_index.md)
