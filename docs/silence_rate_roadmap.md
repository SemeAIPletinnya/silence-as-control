# Silence Rate Optimization Roadmap

## Why this is a separate task
This roadmap is a separate engineering task focused on silence-rate optimization outside the primitive core.

- It is **not** a primitive rewrite.
- It is **not** a threshold-retuning task.
- It is about handling the silence band **in an extension layer around the primitive**, not by changing primitive internals.

## Core constraints
The following constraints are fixed for this workstream:

- The PoR primitive core remains unchanged.
- The **0.39** anchor remains the safe reference point.
- No optimization should weaken the current safety framing.

Any proposal that violates these constraints is out of scope for this roadmap.

## Operating regimes
Use a conservative conceptual split to reason about behavior, without introducing new hard-coded threshold policy:

- **Safe zone**: clear PROCEED cases under the current primitive behavior.
- **Borderline zone**: near-boundary cases that may be candidates for extension-layer handling.
- **Hard silence zone**: clearly SILENCE cases where recovery attempts are unlikely to be safe or useful.

This split is an analysis and orchestration aid only; it does not change the primitive decision rule.

## State design
Keep state boundaries explicit:

- **Core primitive states**: `PROCEED` / `SILENCE`.
- **Extension-layer state (optional)**: `HOLD`.

If introduced, `HOLD` exists only outside the primitive core, in an extension layer around the primitive. It must not become a hidden third primitive state.

## Primitive-preserving extension options
Potential extension-layer patterns (all outside the primitive core):

1. **Borderline HOLD queue** for bounded delayed handling of near-boundary silences.
2. **Post-silence recheck lane** with strict guardrails and limited triggers.
3. **One constrained regeneration attempt** under explicit safety constraints.
4. **Safe fallback output** when recovery is not justified.

These are orchestration options around the primitive, not modifications to primitive logic.

## Silence cohort analysis plan
The first concrete engineering step is to analyze the silenced cohort from the 1000-task runs.

Suggested drift bands for analysis:

- **0.39–0.42**
- **0.42–0.45**
- **0.45–0.50**
- **0.50+**

Analysis goals:

- Identify whether a meaningful borderline band exists.
- Estimate how many silence cases may be recoverable under strict constraints.
- Separate potentially recoverable cases from hard silence cases.

No extension-layer policy should be introduced before this cohort analysis is complete.

## Cost of control
Evaluate every extension-layer option against operational cost and safety impact:

- Latency increase
- Extra compute
- Extra checks / orchestration complexity
- Coverage gain versus safety risk

Improvements in silence rate are acceptable only when safety guarantees remain intact.

## First candidate experiment
After cohort analysis, the first candidate experiment should be conservative:

- **Borderline HOLD queue** with strict bounds and explicit exit criteria.

This is a sequencing rule: analysis first, then a minimal extension experiment.

## What not to do
Avoid these anti-patterns:

- Moving the **0.39** anchor casually.
- Introducing `HOLD` before cohort analysis.
- Optimizing silence rate by eroding the primitive guarantee.
- Using micro-threshold ladders (e.g., 0.391 / 0.3911) as pseudo-architecture.

## Short next-step summary
Immediate next engineering step: **analyze the silenced cohort from the 1000-task runs** to establish a disciplined basis for any extension-layer experiment.
