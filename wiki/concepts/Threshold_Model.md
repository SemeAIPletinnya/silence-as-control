# Threshold Model

_Back to [index](../index.md) · Previous: [Silence as Control](./Silence_as_Control.md) · Next: [Drift vs Coherence](./Drift_vs_Coherence.md)_

## Purpose

A threshold model converts continuous runtime signals into release decisions.

## Current repository framing

The current implementation uses threshold-gated decisions that resolve to either proceed/release or silence.

A simplified decision form is:

- if signal is within allowed bounds -> proceed
- otherwise -> silence

In run artifacts, `silence_threshold` is recorded per row (for example 0.30, 0.35, 0.39 depending on run file).

## Practical notes

- Threshold values are operating-point parameters, not truth guarantees.
- Lower thresholds and higher thresholds change release/silence behavior; impact must be read from committed run artifacts.
- Threshold interpretation should stay tied to documented runs, not generalized beyond available evidence.

See [Run 4 (300 tasks)](../runs/Run_4_300_tasks.md) and [Run 6 (1000 tasks)](../runs/Run_6_1000_tasks.md).
