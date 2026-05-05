# LangChain release-gate adapter (PoR integration layer)

This adapter is a minimal integration layer that makes PoR release control usable with a LangChain-style object exposing `.invoke(input)`.

## Core framing

- **Generation is not release.**
- The wrapped LangChain object produces a candidate.
- PoR evaluates instability and decides `PROCEED` or `SILENCE`.
- Optional config-risk detection can escalate a core `PROCEED` into `NEEDS_REVIEW`.

## Scope

This adapter does **not** modify:

- PoR core primitive behavior.
- Threshold regime logic.
- Benchmark logic, reports, or evidence outputs.

It is strictly an integration/deployment wrapper.

The config-risk detector is intentionally integration-layer logic: it catches actionable config/approval/policy removal advice, can escalate a core `PROCEED` into `NEEDS_REVIEW`, and does not change PoR core scoring.

## Integration-layer action-risk escalation

The adapter also supports integration-layer **action-risk escalation** for generated outputs that propose high-cost operational actions. When enabled, it can escalate a core `PROCEED` to `NEEDS_REVIEW` for patterns such as:

- destructive/bulk API mutation guidance,
- auth-scope widening or auth-bypass guidance,
- partial-update or consistency-skip rollout guidance,
- unsupported guarantees/overclaims.

This escalation is adapter-only behavior and does **not** modify PoR primitive scoring, threshold semantics, or core release decision logic.

If a safe read-only prompt is over-silenced, that is a threshold/gate calibration issue in core decision behavior, not an action-risk detector escalation issue.

## Behavior summary

`PoRLangChainReleaseGate.invoke(input_data)`:

1. calls `chain.invoke(input_data)` to get a candidate,
2. stringifies input and candidate for scoring,
3. computes drift/coherence and core instability decision,
4. returns:
   - `SILENCE` with `released=False` when unstable,
   - `NEEDS_REVIEW` with `released=False` when config-removal risk is detected,
   - `PROCEED` with `released=True` and output otherwise.
