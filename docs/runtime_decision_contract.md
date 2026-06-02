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

Before comparison, runtime clamps the review-band edges into `[0.0, 1.0]`:

```text
lower_bound = max(threshold - margin, 0.0)
upper_bound = min(threshold + margin, 1.0)
```

Decision bands then use those bounded edges:

```text
instability < lower_bound
  => PROCEED

lower_bound <= instability < upper_bound
  => NEEDS_REVIEW

instability >= upper_bound
  => SILENCE
```

With the current margin, a threshold of `0.39` yields:

- `lower_bound = 0.36`
- `upper_bound = 0.42`
- `instability < 0.36` => `PROCEED`
- `0.36 <= instability < 0.42` => `NEEDS_REVIEW`
- `instability >= 0.42` => `SILENCE`

With the current margin, a threshold of `1.0` yields clipped review-band edges:

- `lower_bound = 0.97`
- `upper_bound = 1.0`
- `instability < 0.97` => `PROCEED`
- `0.97 <= instability < 1.0` => `NEEDS_REVIEW`
- `instability >= 1.0` => `SILENCE`

## Runtime policy overrides

Certain runtime/API policies may override the nominal instability-band result. These policies preserve runtime safety requirements that are stricter than pure instability-band routing.

For example, if the prompt expects JSON and runtime JSON validation fails, `/por/evaluate` forces `SILENCE` even if the instability score falls inside the nominal `PROCEED` or `NEEDS_REVIEW` band.

In that case:

- `release_output` is withheld
- `silence_token` is returned

This preserves structured-output safety above pure instability-band routing.

## Black-box compatibility

This contract is black-box compatible. It does not require model internals, logits, or logprobs. Integrations may supply generated text from any candidate source, then use the runtime gate to decide whether output is released, routed to review, or withheld as silence.
