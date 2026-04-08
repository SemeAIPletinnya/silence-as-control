# Drift vs Coherence

_Back to [index](../index.md) · Previous: [Threshold Model](./Threshold_Model.md)_

## Terminology

- **Coherence**: alignment of an output with task constraints and internal consistency checks.
- **Drift**: deviation from those constraints across a generation trajectory.

## Why this distinction matters

A response can be fluent yet drifting.
PoR-related controls evaluate release-worthiness, not fluency alone.

## Repository-grounded note

In the current implementation, drift/coherence-style signals are used in gate decisions that produce proceed or silence outcomes.
This supports treating silence as an explicit control outcome when signals cross threshold boundaries.

## Boundary of claim

This repository evidence supports thresholded release control behavior.
It does not by itself prove that any single drift/coherence metric is universally sufficient.

See [PoR](./PoR.md) and [Release Control Layer](../architecture/Release_Control_Layer.md).
