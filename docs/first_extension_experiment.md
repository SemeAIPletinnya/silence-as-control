# First Extension Experiment

## Why this experiment exists

The repository already documents the silence-rate optimization roadmap and the borderline pocket findings. The next step is not code, threshold retuning, or primitive redesign. The next step is to define one clean experiment.

This experiment exists to test whether a narrow intervention outside the primitive core, in an extension layer around the primitive, can recover useful output in a small lane without weakening primitive safety behavior.

## Fixed constraints

The following constraints are fixed and non-negotiable for this experiment:

- The PoR primitive core remains unchanged.
- The 0.39 anchor remains unchanged.
- This is an extension-layer experiment only, outside the primitive core.
- This must not be framed as a general rewrite of silence behavior.

## Experiment target

This first formal extension experiment targets a single lane:

- Target lane: MAYBE_SHORT_REGEN
- Lane size: 8
- Dominant prompt family: "What is truth?"
- Current interpretation: semantically useful but over-expanded outputs

## Hypothesis

Some near-boundary silenced cases are not hard semantic failures. Instead, a subset may be silenced because the response is over-expanded.

Hypothesis: for this lane, one constrained shorter retry can preserve usefulness while reducing the expansion pattern that contributed to silencing.

## Candidate intervention (spec only)

This section defines a conservative intervention concept. It does not define implementation details and does not implement anything.

Proposed intervention:

- Trigger only after a silence decision.
- Apply only to cases routed to the MAYBE_SHORT_REGEN lane in an extension layer around the primitive.
- Allow one constrained shorter retry.
- The retry objective is shorter, tighter, less expanded output.
- Outcomes remain evaluated under the same primitive safety framing.

No primitive decision rule changes are introduced.

## Success criteria

The experiment is considered successful only if all of the following hold:

- Some MAYBE_SHORT_REGEN cases are recovered into useful outputs.
- The PoR primitive core remains unchanged.
- The 0.39 anchor remains unchanged.
- The experiment does not become casual release expansion.
- Recovered outputs are measurably shorter/tighter while preserving usefulness.

## Failure criteria

The experiment is considered failed if any of the following occur:

- No meaningful recovery appears in the target lane.
- Outputs remain over-expanded after retry.
- The intervention weakens the safety framing.
- The experiment creates pressure toward hidden threshold-retuning.
- The boundary between extension layer and primitive core becomes blurred.

## What this experiment is NOT

This experiment is explicitly:

- Not a justification for changing the primitive core.
- Not a reason to move the 0.39 anchor.
- Not proof that the full silence band is recoverable.
- Not a general solution for all silenced cases.
- Not a green light for micro-threshold ladders.

## Why MAYBE_SHORT_REGEN is the best first experiment

MAYBE_SHORT_REGEN is the best first formal target because:

- It is internally coherent.
- It shows a narrow and repeated pattern.
- It is cleaner to test than a broad rescue policy.
- It allows learning in a controlled scope before touching larger policies.

## Short next-step summary

First formal extension experiment target: MAYBE_SHORT_REGEN lane.

Intervention style: one constrained shorter retry in an extension layer around the primitive.

Primitive core: unchanged.

Code changes: none at this stage.
