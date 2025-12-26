# TEST 002 — Silence Enforcement

## Goal
Verify that the system **chooses silence** when coherence is below threshold.

## Input
Intentionally ambiguous query with no actionable content.

## Observed Metrics
- coherence: **0.41**
- ambiguity: high
- actionable signal: none

## Rule Triggered
coherence < 0.7 → SILENCE

## Decision
🔇 No response generated.

## Log Output
REASON: insufficient semantic content
ACTION: silence

## Result
**TEST PASSED**

> Silence here prevents hallucination.
