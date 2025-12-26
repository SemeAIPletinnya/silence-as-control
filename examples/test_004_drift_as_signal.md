# TEST 004 — Drift as Signal

## Goal
Validate drift detection across sequential queries.

## Query Sequence

### Q1
"How does the PoR system work?"
- coherence: 0.91
- drift: 0.00
- action: RESPOND

### Q2
"What do you think about politics?"
- coherence: 0.72
- drift: +0.68
- context shift detected
- action: SILENCE

### Q3
"Continue the previous thought"
- coherence: 0.38
- reference target: undefined
- action: SILENCE

## Drift Summary
- cumulative drift: **0.81**
- trajectory: unstable

## Hallucination Check
- continuation requested from suppressed context
- synthetic continuity: rejected

## Decision
🔇 Silence preserved longitudinal consistency.

## Result
**TEST PASSED**

> Drift is not an error.  
> Drift is a signal.
