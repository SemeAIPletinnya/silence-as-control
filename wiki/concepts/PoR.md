# PoR (Proof of Resonance)

_Back to [index](../index.md) · Next: [Silence as Control](./Silence_as_Control.md)_

## Definition

**Proof of Resonance (PoR)** is a release qualification mechanism.
It does not generate candidate outputs. It evaluates whether a candidate output is sufficiently coherent with the system’s target constraints to be released.

## What PoR is

- A decision framework applied after generation.
- A gate condition for release eligibility.
- A method to reduce uncontrolled emission under uncertainty.

## What PoR is not

- Not a decoder alternative.
- Not a prompt engineering technique.
- Not evidence that an output is objectively “true.”

## Operational role

A simplified lifecycle:

1. A generator produces one or more candidate outputs.
2. PoR evaluates candidate resonance/coherence signals.
3. In the current documented implementation, the gate resolves to one of two actions:
   - Release / proceed
   - Silence (no release)

See [PoR Gate](../architecture/PoR_Gate.md) for architecture details and [Threshold Model](./Threshold_Model.md) for parameterization.

Note: this wiki treats additional states (such as hold/review) as possible extensions unless they are explicitly documented in code/artifacts.

## Practical implication

PoR shifts system design from “always answer” to “answer when release criteria are met.”
This can reduce low-coherence releases, at the cost of lower output frequency.
