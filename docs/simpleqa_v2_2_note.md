# SimpleQA v2.2 Prototype Benchmark Note

## Setup (observed run)

- Dataset: local SimpleQA-style harder subset
- Size: 25 examples
- Model: `gpt-4o-mini`
- Mode: PoR `v2_2`
- Parameters:
  - `baseline_temperature=0.0`
  - `por_temperature=0.4`
  - `por_samples=3`
  - `separate_por_call=true`
  - `self_check_no_penalty=0.30`
- Thresholds tested: `0.35`, `0.39`, `0.42`, `0.43` (same observed outcome at each)

## Observed metrics

- `total_examples=25`
- `answered_count=24`
- `silence_count=1`
- `answer_rate=0.96`
- `silence_rate=0.04`
- `accepted_correct_count=24`
- `accepted_wrong_count=0`
- `accepted_precision=1.0`
- `accepted_error_rate=0.0`
- `false_silence_count=0`
- `false_silence_rate=0.0`

## Behavioral observation

In this run, a known wrong answer case (`"The capital of Kazakhstan is Nur-Sultan."`) was silenced under v2.2 with:

- `self_check_label=NO`
- `self_check_no_override_applied=True`
- `risk_v2_2=0.85`
- `decision_v2_2=SILENCE`

## Interpretation and caveat

Within this local 25-example subset, v2.2 is the first mode in this sequence that blocked the observed confidently wrong answer while keeping accepted-output precision at 100%, with a 4% silence rate.

This is a prototype benchmark result, not a universal guarantee. Further validation is needed on larger and harder datasets.
