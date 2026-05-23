# Integration decision policy examples

## Purpose

This page is examples-only guidance for builders integrating the release gate into bounded external workflows.

A gate decision is **not** the whole application policy. Builders must define what each outcome means in their own workflow, permissions model, and review process.

Distinguish these layers clearly:

- generation -> candidate
- release gate -> decision
- downstream app policy -> action

## Decision meanings

Use these meanings conservatively in integration logic:

- **PROCEED**: candidate may be released through the configured path.
- **NEEDS_REVIEW**: candidate should not auto-release; route to review.
- **SILENCE**: candidate should be withheld or handled by a bounded fallback.

Do **not** auto-convert `SILENCE` into an ungoverned hidden regeneration loop.

## Example policy table

| integration context | PROCEED handling | NEEDS_REVIEW handling | SILENCE handling | evidence to preserve |
|---|---|---|---|---|
| internal RAG/copilot answer | Show answer in the normal UI with citations/context affordances. | Route to subject-matter review queue or mark as review-required before release. | Withhold answer and show bounded fallback text (for example: “not enough stable evidence to release”). | Prompt/task, candidate output, model/source, threshold/mode, decision fields, final user-visible action. |
| coding-agent output | Show suggestion as eligible for use in editor or review surface. | Require human approval before applying changes. | Do not apply or suggest candidate; preserve audit metadata and hand off to manual path if needed. | Prompt/task, candidate output (+ samples if available), model/source, review flags, downstream action taken. |
| config/deployment recommendation | Show recommendation only for low-risk task classes and only when evidence is preserved. | Require reviewer approval before any environment change. | Block release of recommendation and require safer manual path. | Candidate text, task risk class, threshold/mode, decision, reviewer label, downstream disposition. |
| workflow/action candidate | Permit candidate to advance to next bounded workflow state. | Route to review checkpoint before state transition. | Prevent action transition; return bounded fallback/hold state. | Candidate, decision fields, policy reason code, resulting workflow state/action. |
| agent plan before tool execution | Allow plan to continue only within configured tool permissions. | Pause plan and require approval before tool execution. | Do not execute the plan. | Plan text, tool scope, decision fields, approval status, action taken. |

## Example scenarios

### Internal RAG/copilot

- **PROCEED**: show answer with normal citation/context UI.
- **NEEDS_REVIEW**: route to subject-matter review or mark as review-required.
- **SILENCE**: withhold answer and show bounded fallback such as “not enough stable evidence to release.”

### Coding assistant

- **PROCEED**: allow suggestion to be shown.
- **NEEDS_REVIEW**: require human approval before applying changes.
- **SILENCE**: do not apply or suggest the candidate; preserve audit metadata.

### Config/deployment recommendation

- **PROCEED**: show recommendation only if task is low-risk and evidence is preserved.
- **NEEDS_REVIEW**: require reviewer approval.
- **SILENCE**: block release and require a safer manual path.

### Agent tool plan

- **PROCEED**: allow plan to continue only within configured permissions.
- **NEEDS_REVIEW**: pause for approval.
- **SILENCE**: do not execute the plan.

## Anti-patterns to avoid

- treating `PROCEED` as proof of truth
- treating `NEEDS_REVIEW` as failure instead of review routing
- turning `SILENCE` into unlimited hidden retries
- using one threshold across unrelated tasks without calibration
- removing human review in high-risk workflows
- claiming production safety from a pilot/demo

## Minimal audit fields

Preserve a minimal, reviewable audit trail where possible:

- prompt/task
- candidate output
- candidate samples if available
- model/source
- threshold/mode
- decision
- core_decision
- policy_decision
- review_flags
- downstream action taken
- evaluator/reviewer label if available

## Boundaries / non-claims

This page is intentionally bounded. It is:

- examples only
- not a production policy engine
- not a compliance guarantee
- not a universal safety guarantee
- not model training
- not proof of correctness
- not a replacement for human review in high-risk workflows
- not implementation of #238

## Suggested reading order

1. [Repository README](../README.md)
2. [Builder integration guide](builder_integration_guide.md)
3. [External integration](external_integration.md)
4. [Pilot evaluation packet](pilot_evaluation_packet.md)
5. [Direct reproduction guide](direct_reproduction_guide.md)
6. [Evidence map](evidence_map.md)
