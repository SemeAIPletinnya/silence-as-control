# Runtime Decision Contract for `/por/evaluate`

This page documents the applied runtime/API decision contract for reviewers and integrators using `POST /por/evaluate`.

It describes release mediation at the runtime boundary. It does not redefine the PoR primitive core and does not change runtime behavior.

## Layer boundary

- **Generation is not release authority.** A generated candidate is only a candidate. The runtime gate decides whether that candidate may be released, held for review, or withheld as silence.
- **The core primitive remains binary.** The primitive core computes instability from drift/coherence signals and compares that score to a threshold as a release-control primitive.
- **The runtime/API layer uses tri-state mediation.** The API wraps the binary primitive with a bounded review band around the threshold so borderline candidates are routed to review instead of being auto-released or hard-silenced.

## Runtime outcomes

`POST /por/evaluate` returns one of three runtime decisions:

| Decision | Runtime contract |
| --- | --- |
| `PROCEED` | `release_output` is returned. The candidate passed the runtime release gate. |
| `NEEDS_REVIEW` | `release_output` is withheld for review. The candidate is inside the bounded review band. |
| `SILENCE` | `release_output` is withheld and `silence_token` is returned. The candidate is outside the allowed release/review region. |

For integrators, the operational rule is: only `PROCEED` carries releasable output. Both `NEEDS_REVIEW` and `SILENCE` withhold `release_output`, but they mean different downstream actions: review lane vs. silence/blocked output.

## Review band formula

The runtime computes an `instability` score and compares it with a resolved `threshold` using the current bounded review margin.

Current margin: `0.03`.

Decision bands:

```text
instability < threshold - margin
  => PROCEED

threshold - margin <= instability < threshold + margin
  => NEEDS_REVIEW

instability >= threshold + margin
  => SILENCE
```

With the current margin, a threshold of `0.39` yields:

- `instability < 0.36` => `PROCEED`
- `0.36 <= instability < 0.42` => `NEEDS_REVIEW`
- `instability >= 0.42` => `SILENCE`

## Runtime policy overrides

Certain runtime policies may override the nominal instability-band result. These overrides are runtime/API-layer controls, not changes to the primitive core.

For example, if the prompt expects JSON output and runtime JSON validation fails, the runtime may force `SILENCE` even when the instability score falls inside the nominal `PROCEED` band. In that case, `release_output` remains withheld and `silence_token` is returned.

This preserves runtime safety and structured-output guarantees above pure instability-band semantics. Integrators should therefore treat the review-band formula as the default routing rule, subject to explicit runtime policy overrides.

## Black-box compatibility

This contract is black-box compatible. It does not require model internals, logits, or logprobs. Integrations may supply generated text from any candidate source, then use the runtime gate to decide whether output is released, routed to review, or withheld as silence.
