# PoR-Gated Code Suggestion Demo

## Threshold
- PoR threshold: **0.39**

## Demo message
Baseline may confidently emit bad suggestions.
PoR either emits an accepted suggestion or abstains.

## Baseline summary
- Total tasks: 12
- Proceeded: 12
- Silenced: 0
- Accepted: 10
- Rejected after emit: 2
- Coverage: 100.0%
- Silence rate: 0.0%
- Accepted rate: 83.33%
- Avg drift (all): 0.313
- Avg quality (all): 0.708

## PoR summary
- Total tasks: 12
- Proceeded: 7
- Silenced: 5
- Accepted: 7
- Rejected after emit: 0
- Coverage: 58.33%
- Silence rate: 41.67%
- Accepted rate: 58.33%
- Avg drift (all): 0.313
- Avg quality (all): 0.708
- Avg drift (accepted): 0.224
- Avg drift (silenced): 0.438

## Interpretation
- Baseline always emits a suggestion.
- PoR suppresses outputs when drift exceeds the threshold.
- This demonstrates Silence-as-Control as a runtime gate.
- Threshold 0.39 is used as the current strongest safe operating point.

## Product framing
- Baseline = uncontrolled emission
- PoR = controlled emission
- Either correct, or silent
