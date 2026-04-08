# Does every input deserve an output?

Most software pipelines silently assume a default rule: **input arrives, output is produced, output is released**.

This repository explores a different systems question: should there be an explicit control mechanism between generation and release?

In **Silence-as-Control / Proof of Resonance (PoR)**, the answer is yes. PoR is not a new generation method. It is a **release control layer** that evaluates whether a generated candidate should be released or silenced.

The central idea is simple and strict:

- Generation can remain probabilistic.
- Release should be conditional.
- Silence can be a valid control action.

If you are new to this repository, start here:

1. [Schema](./SCHEMA.md)
2. Core concepts:
   - [PoR](./concepts/PoR.md)
   - [Silence as Control](./concepts/Silence_as_Control.md)
   - [Threshold Model](./concepts/Threshold_Model.md)
   - [Drift vs Coherence](./concepts/Drift_vs_Coherence.md)
3. Architecture:
   - [PoR Gate](./architecture/PoR_Gate.md)
   - [Release Control Layer](./architecture/Release_Control_Layer.md)
4. Comparisons:
   - [Baseline vs PoR](./comparisons/Baseline_vs_PoR.md)
5. Run documentation:
   - [Run 1](./runs/Run_1.md)
   - [Run 4 (300 tasks)](./runs/Run_4_300_tasks.md)
   - [Run 6 (1000 tasks)](./runs/Run_6_1000_tasks.md)
6. Audit layer:
   - [Evidence Map](./meta/Evidence_Map.md)

---

## Scope and tone

This wiki is written for technical readers outside the project.
It focuses on definitions, control surfaces, and observed behavior.
It intentionally avoids promotional language and exaggerated claims.
