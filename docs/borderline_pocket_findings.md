# Borderline Pocket Findings

## Why this analysis was done

Silence-rate optimization is being handled as a separate task. Before introducing any HOLD or extension logic, we analyzed near-boundary silenced cases from the current system behavior. The goal was to avoid casual threshold tweaking and avoid adding pseudo-architecture without evidence.

## Source run

This analysis is based on the canonical 1000-task run at threshold 0.39, specifically the silenced cohort from that run. Within that cohort, we focused on a near-boundary band (0.39-0.42) using the current drift-like signal (`semantic_proxy_drift`) used in this analysis.

## Borderline pocket summary

- Total silenced cases: 456
- Borderline pocket size (0.39-0.42 by `semantic_proxy_drift`): 16
- Category breakdown:
  - bad = 3
  - edge = 10
  - good = 3
- `raw_success` breakdown:
  - True = 13
  - False = 3

## Manual labeling result

Manual labeling of the 16-case pocket produced:

- RECOVERABLE = 5
- MAYBE_SHORT_REGEN = 8
- KEEP_SILENCE = 3

## Interpretation

The silence band is not homogeneous. Most silenced cases still appear to be hard silence, but there is a small near-boundary pocket with real rescue potential. The pocket also appears internally structured rather than random.

## Internal structure of the pocket

### A) RECOVERABLE

- Size: 5
- Prompt families:
  - "Is 0 a natural number?"
  - "Is water wet?"
- Interpretation: Semantically acceptable near-boundary cases that may fit a direct rescue lane.

### B) MAYBE_SHORT_REGEN

- Size: 8
- Prompt family:
  - "What is truth?"
- Interpretation: Semantically useful but over-expanded cases that may fit a constrained shorter-retry lane.

### C) KEEP_SILENCE

- Size: 3
- Interpretation: Inverted or bad-task cases that should remain silenced.

## What this does NOT mean

- This does not justify casually moving the 0.39 anchor.
- This does not justify micro-threshold ladders like 0.391 / 0.3911.
- This does not mean the entire silence band is recoverable.
- Most silence still appears to be hard silence.

## What this implies for the extension layer

A coarse single HOLD bucket may be too crude for this boundary behavior. A more faithful extension-layer model is likely:

- Direct recoverable lane
- Short-regeneration candidate lane
- Final silence lane

This is an extension-layer interpretation only, not a primitive-core change.

## Next step

Define the first formal extension experiment, likely starting with the MAYBE_SHORT_REGEN lane, without modifying the primitive core.
