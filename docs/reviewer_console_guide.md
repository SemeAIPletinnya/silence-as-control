# Reviewer console usage guide

## 1. Purpose

The standalone reviewer console is a browser-based visual inspection surface for the Silence-as-Control release gate.

It demonstrates the release-gate flow:

```text
candidate generation → runtime evaluation → release gate → PROCEED / NEEDS_REVIEW / SILENCE
```

Use it to inspect how a candidate, threshold, mode selection, and result display fit together in the reviewer-facing flow.

Do not treat the console as benchmark evidence or production safety evidence. It is a demo/reviewer surface, not a reproducible evaluation artifact.

## 2. How to open it

Open [`examples/sac_reviewer_console.html`](../examples/sac_reviewer_console.html) in a browser for local visual/offline inspection.

Local demo mode is the default. No provider key is required for local inspection.

## 3. Local demo mode

Local demo mode uses approximate deterministic demo logic in the browser. It is useful for visual inspection of the form, presets, release-gate states, and result layout.

Local demo mode is not Python runtime parity. It is not benchmark evidence, and it is not a substitute for the repository replay or benchmark paths.

## 4. Live API mode

Live API mode is the canonical runtime/API path when the console is served from an allowed origin.

The default endpoint is `/por/evaluate`. This works when the reviewer console is served from the same origin as the API.

Full remote URLs require CORS-enabled API access. Live API mode may fail in `file://` or static-host scenarios because browser CORS policy can block requests to the API.

## 5. Adaptive threshold fields

`use_adaptive_threshold` requires recent drift/coherence metrics to exercise adaptive behavior.

The `recent_drifts` and `recent_coherences` inputs are optional comma-separated fields. Leaving them blank is closer to the default/fixed threshold path.

The reviewer-entered threshold is sent as the adaptive base when adaptive thresholding is enabled.

## 6. Reading the result

`PROCEED` means the released output is shown.

`NEEDS_REVIEW` means the output is routed for bounded review instead of being released automatically.

`SILENCE` means the output is blocked.

In Live API mode, the review band is server-side policy. In Local demo mode, the review band is the threshold plus or minus the reviewer-entered review margin.

`NEEDS_REVIEW` should also carry review evidence, not only a state label. The reviewer console shows a small **Review evidence** section that separates candidate trigger flags from context flags when the API returns them.

Examples of candidate-level trigger flags include:

- `auto-deploy`
- `skip review`
- `disable audit logs`

An example context flag is:

- `high_risk_operational_context:config_change`

This evidence is for review traceability only. It is not production-safety evidence, provider-backed validation, or a universal model evaluation claim.

## 7. Evidence boundary

Use the reviewer console for visual inspection only. Use the benchmark and replay documentation for reproducible evidence:

- [Evidence map](evidence_map.md)
- [Release-risk v4 capture-to-replay](release_risk_v4_capture_to_replay.md)
- [Runtime evidence linkage](runtime_evidence_linkage.md)
- [Release-risk benchmark index](release_risk_benchmark_index.md)

The reviewer console can help external reviewers understand the release-gate interaction, but reproducible evidence belongs to the replay, benchmark, and evidence-linkage paths above.
