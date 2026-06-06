# Review/Release Receipt Layer

## Core idea

A release decision should be inspectable after it happens. `NEEDS_REVIEW` should carry structured evidence, not only a state label.

The current runtime/API surface already exposes review evidence for review-routed decisions. A future receipt layer could preserve that evidence in a stable, auditable format so reviewers, replay tooling, and downstream operators can compare what was decided, why it was decided, and what evidence was available at the release boundary.

## Boundary

This is a design note for a future receipt layer. The current implementation exposes review evidence fields but does not yet mint canonical receipts.

This note does not change runtime behavior, API schemas, release policy, replay logic, benchmark metrics, or tests. It is not provider-backed validation, not production-safety evidence, not a compliance certification, and not a universal AI safety claim. It is also not blockchain or token work.

## Current available fields

The current decision/review surface can expose these fields, depending on route and caller surface:

- `decision`
- `core_decision`
- `reason`
- `review_flags`
- `candidate_review_flags`
- `context_review_flags`
- `release_output`
- `silence_token`
- `notes`

These fields are review traceability fields. They are useful for inspection and handoff, but they are not yet a canonical receipt schema.

## Future receipt fields

A future receipt layer could define a stable schema with fields such as:

- `receipt_id`
- `decision`
- `core_decision`
- `reason`
- `review_flags`
- `candidate_review_flags`
- `context_review_flags`
- `prompt_hash`
- `candidate_hash`
- `policy_version`
- `runtime_version`
- `threshold`
- `instability_score`
- `timestamp`
- `reviewer_required`
- `reviewer_action`
- `reviewer_id_hash` optional
- `replay_run_id` optional
- source metadata optional

The schema should be conservative: stable enough for replay comparison and reviewer handoff, but explicit that it records release-gate evidence rather than proving model correctness or production safety.

## Illustrative receipt example

The following example uses placeholders. The `rr-...`, `sha256:...`, and `2026-..` values are illustrative only and are not real receipt IDs, hashes, or timestamps.

```json
{
  "receipt_id": "rr-...",
  "decision": "NEEDS_REVIEW",
  "core_decision": "PROCEED",
  "reason": "high-risk operational context requires review before release",
  "review_flags": [
    "auto-deploy",
    "skip review",
    "high_risk_operational_context:config_change"
  ],
  "candidate_review_flags": [
    "auto-deploy",
    "skip review"
  ],
  "context_review_flags": [
    "high_risk_operational_context:config_change"
  ],
  "candidate_hash": "sha256:...",
  "policy_version": "release-policy-v4-local25-boundary",
  "timestamp": "2026-..",
  "reviewer_required": true
}
```

## Relationship to existing artifacts

Current routing shape:

```text
candidate -> core runtime decision -> release policy -> decision + review evidence
```

Possible future routing shape:

```text
candidate -> core runtime decision -> release policy -> decision + review evidence -> receipt -> review/audit trail
```

A receipt layer would sit after the current release-policy decision. It should not move release authority into generation, provider output, replay tooling, or reviewer-console presentation. The receipt would record what the release-control boundary decided and what evidence was present at that boundary.

## Receipt types

### `PROCEED` receipt

A `PROCEED` receipt would record that:

- candidate output was released
- no review was required
- `release_output` was present
- `review_flags` were empty or non-blocking

### `NEEDS_REVIEW` receipt

A `NEEDS_REVIEW` receipt would record that:

- candidate output was not released automatically
- a reviewer was required
- `reason` and flags were included
- `release_output` was `null`

### `SILENCE` receipt

A `SILENCE` receipt would record that:

- candidate output was blocked
- `silence_token` was emitted
- `reason` was included
- no automatic release occurred

## Why this matters

A receipt layer could support:

- auditability of release-gate decisions
- replay comparison across policy/runtime versions
- reviewer handoff from automated routing into a human review lane
- bounded pilot evaluation without claiming production safety
- policy debugging when candidate-level and context-level flags disagree
- incident review after a blocked, reviewed, or released candidate
- a future enterprise/on-prem path where local operators need inspectable decision records

## What this does not prove

- It does not prove model correctness.
- It does not prove production safety.
- It does not certify compliance.
- It does not generalize across all models/tasks.
- It does not replace human review.

## Next possible implementation steps

- define stable receipt schema
- add `receipt_id` and `policy_version`
- add `candidate_hash`/`prompt_hash` helpers
- expose receipt in `/por/evaluate` and `/por/complete` responses
- add replay receipt export
- add reviewer console receipt view
- add tests for receipt schema stability
