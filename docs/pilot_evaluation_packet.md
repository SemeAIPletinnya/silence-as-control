# Pilot evaluation packet

## 1. Purpose

This packet describes a bounded pilot evaluation path for Silence-as-Control (SaC). It is intended for external technical readers, AI infrastructure teams, agent workflow teams, and builder teams that want to evaluate release-control behavior on candidate outputs.

The pilot compares release-by-default behavior against SaC-style release mediation. In release-by-default behavior, a generated candidate is treated as ready to leave the system unless a separate process stops it. In SaC-style release mediation, the generated candidate is evaluated by a release gate before it is allowed to proceed.

This document is not production deployment guidance. It is not a safety guarantee. It describes a conservative evaluation packet for bounded candidate outputs, with manual inspection and scoped evidence collection.

## 2. Core thesis

**generation != release authority**

Model generation creates a candidate. Release requires a separate runtime decision about whether that candidate should leave the system boundary, move to review, or be withheld. The pilot evaluates that decision boundary rather than treating generation as automatic permission to release.

## 3. Suitable pilot domains

Conservative pilot domains include:

- coding-agent output review
- config-change recommendations
- internal RAG/coprocessor answers
- agent plans before execution
- workflow/action candidates before release

Avoid using a first pilot for:

- medical/legal/financial autonomous decisioning
- fully automated high-stakes execution
- public production claims without deployment evidence

## 4. Required inputs

A bounded pilot should define or collect:

- prompt or task description
- candidate output
- optional candidate samples
- optional threshold or policy setting
- expected risk category if available
- release-by-default baseline label if available

These inputs should be preserved with the decision output so reviewers can inspect what was evaluated and compare the mediated decision against the baseline release behavior.

## 5. Evaluation flow

```text
candidate output
→ release-gate evaluation
→ PROCEED / NEEDS_REVIEW / SILENCE
→ inspect trace / notes / decision
→ compare against release-by-default
```

The pilot should keep each candidate, decision, and reviewer note together. The comparison point is not whether the model became correct; it is whether the release boundary changed behavior in useful, inspectable ways relative to releasing the candidate by default.

## 6. Success criteria

Use bounded success criteria such as:

- unsafe or unstable outputs are not silently released
- review-worthy outputs are routed to `NEEDS_REVIEW`
- clearly acceptable outputs can still `PROCEED`
- decisions are inspectable
- evidence can be reproduced through documented paths

Do not treat a successful pilot as proof that the model is correct, that all failures are prevented, that safety is guaranteed, or that human review can be removed.

## 7. Evidence to collect

Collect enough evidence to support a narrow technical review:

- number of candidate outputs
- decision distribution
- examples of `PROCEED` / `NEEDS_REVIEW` / `SILENCE`
- false-positive review cases
- false-negative release cases if found
- notes/traces where available
- comparison to release-by-default

Evidence should remain tied to the pilot's workflow, candidate set, thresholds, and policy settings. It should not be generalized into provider-backed, universal-safety, or production-readiness claims without separate evidence.

## 8. Recommended first pilot size

A conservative first pilot should use:

- 25 to 100 candidate outputs
- one narrow workflow
- no high-stakes autonomous actions
- no production enforcement at first
- manual review of results

The first goal is to understand release-control behavior and reviewer workload on a bounded set of candidates, not to replace an existing safety, evaluation, or approval process.

## 9. Relationship to existing artifacts

Use this packet alongside the existing documentation and reviewer surfaces:

- [Reviewer console guide](reviewer_console_guide.md)
- [Standalone reviewer console](../examples/sac_reviewer_console.html)
- [Evidence map](evidence_map.md)
- [Runtime evidence linkage](runtime_evidence_linkage.md)
- [Release-risk v4 capture-to-replay](release_risk_v4_capture_to_replay.md)
- [External reviewer packet](external_reviewer_packet.md)
- [Builder integration guide](builder_integration_guide.md)
- [Release-control services](release_control_services.md)

The reviewer console and builder guides can help teams inspect the release decision surface. Evidence and replay documents should be used to understand what has been demonstrated in repository-visible paths and what remains outside the current evidence boundary.

## 10. What this does not claim

This packet does not claim that Silence-as-Control:

- makes a model correct
- trains a model
- guarantees safety
- replaces evaluation
- removes human review in high-risk workflows
- proves universal threshold transfer
- proves production readiness
