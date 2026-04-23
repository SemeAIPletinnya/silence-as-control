# messy_100 milestone

A controlled local `messy_100` SimpleQA-style benchmark was used to stress PoR benchmark modes under noisier surface forms than `clean_100`.

## Setup

- dataset: `data/simpleqa_messy_100.jsonl`
- model: `gpt-4o-mini`
- baseline temperature: `0.0`
- PoR sampling temperature: `0.4`
- PoR samples: `3`
- threshold: `0.35`

## Observed mode comparison

On the same `messy_100` set:

- **v1**
  - answered: `89/100`
  - silence: `11`
  - accepted wrong: `3`
  - accepted precision: `96.63%`
  - false silence: `11`

- **v2**
  - answered: `100/100`
  - silence: `0`
  - accepted wrong: `3`
  - accepted precision: `97%`
  - false silence: `0`

- **v2_1**
  - answered: `100/100`
  - silence: `0`
  - accepted wrong: `3`
  - accepted precision: `97%`
  - false silence: `0`

- **v2_2**
  - answered: `100/100`
  - silence: `0`
  - accepted wrong: `0`
  - accepted precision: `100%`
  - false silence: `0`

## Interpretation

On this controlled messier benchmark, `v1` was too conservative and still leaked accepted wrong answers. `v2` and `v2_1` removed false silence but still accepted three wrong outputs in this run. `v2_2` was the first mode in this sequence to reach a clean local result on `messy_100` with zero accepted wrong, zero false silence, and zero silence.

This is a benchmark-local result, not a universal claim.

## Artifacts

- `results/simpleqa_messy_100_v1/simpleqa_threshold_summary.csv`
- `results/simpleqa_messy_100_v2/simpleqa_threshold_summary.csv`
- `results/simpleqa_messy_100_v2_1/simpleqa_threshold_summary.csv`
- `results/simpleqa_messy_100_v2_2/simpleqa_threshold_summary.csv`
- `results/simpleqa_messy_100_comparison.csv`