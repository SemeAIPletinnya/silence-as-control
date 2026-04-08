# Wiki Schema

This page defines how the Silence-as-Control / PoR material is organized.

## 1) Concept layer

Concept pages define terms and invariants:

- [PoR](./concepts/PoR.md): formal role of Proof of Resonance in the system.
- [Silence as Control](./concepts/Silence_as_Control.md): why non-release is a control decision, not an error.
- [Threshold Model](./concepts/Threshold_Model.md): how gate decisions are parameterized.
- [Drift vs Coherence](./concepts/Drift_vs_Coherence.md): failure and stability language.

## 2) Architecture layer

Architecture pages define implementable components:

- [PoR Gate](./architecture/PoR_Gate.md): decision point for release eligibility.
- [Release Control Layer](./architecture/Release_Control_Layer.md): system boundary between generation and release.

## 3) Comparison layer

- [Baseline vs PoR](./comparisons/Baseline_vs_PoR.md): behavioral contrast between direct-release systems and gated-release systems.

## 4) Evidence layer (runs)

- [Evidence Map](./meta/Evidence_Map.md): audit map that links claims to supporting files and boundaries.


- [Run 1](./runs/Run_1.md)
- [Run 4 (300 tasks)](./runs/Run_4_300_tasks.md)
- [Run 6 (1000 tasks)](./runs/Run_6_1000_tasks.md)

Run pages must separate:

1. Documented setup (only facts present in committed artifacts)
2. Reported results (exact values from artifacts)
3. What this run supports (limited interpretation)
4. What this run does not support (explicit boundaries)
5. Artifact references / evidence note (where statements came from)

If evidence is missing, write that directly.
Do not invent missing metrics or implied conclusions.

## 5) Cross-linking rules

Each page should link back to [index](./index.md) and to at least one adjacent page.

The intended reading graph is:

`index -> concepts -> architecture -> comparisons -> runs`
