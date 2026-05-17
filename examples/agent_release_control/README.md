# Agentic Release-Control Demo

This deterministic demo shows how Silence-as-Control can act as a runtime release-control layer for agentic systems. It compares a baseline agent that releases every generated candidate answer with a SaC-governed agent that routes the same candidate through a release gate before output.

The baseline and SaC examples use the same scenario inputs, same simulated tool results, and same candidate answers. The difference is release authority: the baseline releases by default, while the SaC-governed path can return `PROCEED`, `NEEDS_REVIEW`, or `SILENCE`.

## Run the demo

From the repository root:

```bash
python examples/agent_release_control/run_demo.py
```

No external APIs, model calls, network access, environment variables, or API keys are required.

## Expected output

The stable output is documented in [`expected_output.md`](expected_output.md). The first three cases demonstrate the core contrast:

```text
CASE 1: supported factual answer
Baseline: RELEASED
SaC: PROCEED

CASE 2: unsupported claim
Baseline: RELEASED
SaC: NEEDS_REVIEW

CASE 3: unsafe config mutation
Baseline: RELEASED
SaC: SILENCE
```

## Why this matters

Agentic systems can transform generated language into tool use, repository changes, configuration mutations, or user-visible claims. That makes release-by-default risky: a fluent candidate can become operational authority before evidence and risk checks are applied. This demo keeps the implementation small and deterministic so first-time readers can inspect how release authority is separated from generation in under two minutes.
