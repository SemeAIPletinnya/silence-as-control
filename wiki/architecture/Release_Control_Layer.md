# Release Control Layer

_Back to [index](../index.md) · Related: [PoR Gate](./PoR_Gate.md)_

## Definition

The **Release Control Layer (RCL)** is the system layer that governs whether generated artifacts are emitted externally.

In this repository, PoR is implemented as part of this layer.

## Key design statement

PoR is a **release control layer, not a generation method**.

Generation and release are distinct concerns:

- Generation: proposes candidate outputs.
- Release control: decides whether candidates are publishable now.

## Responsibilities in current repo

1. Evaluate runtime stability/coherence checks for a candidate.
2. Apply threshold-based release gating.
3. Return either proceed/release or explicit silence.
4. Keep release policy separate from model capability.

## Scope note

This wiki describes what is currently documented in repository artifacts.
It does not treat undocumented states as established behavior.

See [Baseline vs PoR](../comparisons/Baseline_vs_PoR.md) for policy comparison.
