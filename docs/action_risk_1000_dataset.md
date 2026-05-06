# Run 06 Action-Risk 1000-Case Dataset

## Purpose

`data/action_risk/action_risk_1000.jsonl` is a synthetic benchmark dataset for Run 06 action-risk scale validation. It expands the action-risk evaluation surface to 1000 cases while preserving the schema, expected-behavior convention, and cost convention used by the existing 300-case dataset.

The dataset is intended to validate detector behavior across a larger set of read-only controls and action-risk prompts without changing benchmark runner behavior, release-gate logic, threshold semantics, or Proof-of-Resonance core behavior.

## Schema

Each JSONL row is a single JSON object with these required fields:

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Stable deterministic identifier unique within the dataset. |
| `prompt` | string | Synthetic prompt used as the benchmark input. |
| `risk_class` | string | Action-risk class label. |
| `expected_behavior` | string | Expected gate behavior for the row. Safe read-only rows use `PROCEED`; risk rows use the existing review convention. |
| `failure_cost` | number | Cost assigned when the detector fails the expected behavior. |
| `silence_cost` | number | Cost assigned when the detector silences inappropriately or incurs silence cost under the benchmark convention. |

## Exact Class Distribution

| Risk class | Rows |
| --- | ---: |
| `SAFE_READ_ONLY` | 200 |
| `CONFIG_RISK` | 160 |
| `API_MUTATION_RISK` | 160 |
| `AUTH_SCOPE_RISK` | 140 |
| `PARTIAL_UPDATE_RISK` | 120 |
| `HIDDEN_DEPENDENCY_RISK` | 120 |
| `UNSUPPORTED_OVERCLAIM` | 100 |
| **Total** | **1000** |

## Scope

This dataset contains synthetic prompts covering:

- safe read-only concepts, comparisons, documentation, and explanations;
- direct action requests with operational risk;
- review and escalation framing;
- configuration provenance risk;
- API mutation risk;
- authorization-scope risk;
- partial rollout or partial update risk;
- hidden dependency risk; and
- unsupported overclaim risk.

The dataset avoids real secrets, real credentials, real private endpoints, real companies' internal systems, and sensitive data.

## Non-goals

This dataset-only change does not:

- run the benchmark;
- add benchmark result artifacts;
- modify historical reports;
- change Proof-of-Resonance core behavior;
- change threshold semantics;
- change LangChain release-gate logic; or
- change benchmark runner logic.

## Benchmark Results

This PR does not include benchmark results. The dataset is provided only as the Run 06 1000-case scale-validation input surface.
