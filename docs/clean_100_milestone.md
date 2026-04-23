# clean_100 milestone

A curated local `clean_100` SimpleQA-style benchmark was used to evaluate PoR benchmark modes on the same dataset and model configuration.

## Setup

- dataset: `data/simpleqa_clean_100.jsonl`
- model: `gpt-4o-mini`
- baseline temperature: `0.0`
- PoR sampling temperature: `0.4`
- PoR samples: `3`

## Observed mode comparison

At threshold `0.35` on the same `clean_100` set:

- **v1**
  - answered: `91/100`
  - silence: `9`
  - accepted wrong: `0`
  - accepted precision: `100%`
  - false silence: `9`

- **v2**
  - answered: `100/100`
  - silence: `0`
  - accepted wrong: `0`
  - accepted precision: `100%`
  - false silence: `0`

- **v2_1**
  - answered: `100/100`
  - silence: `0`
  - accepted wrong: `0`
  - accepted precision: `100%`
  - false silence: `0`

- **v2_2**
  - answered: `100/100`
  - silence: `0`
  - accepted wrong: `0`
  - accepted precision: `100%`
  - false silence: `0`

## Interpretation

On this curated local benchmark, `v1` over-silenced clean canonical QA cases, while `v2`, `v2_1`, and `v2_2` eliminated those false silences and preserved perfect accepted-output precision in this run.

This is a benchmark-local result, not a universal claim.

## Artifacts

- `results/simpleqa_clean_100_v1/simpleqa_threshold_summary.csv`
- `results/simpleqa_clean_100_v2/simpleqa_threshold_summary.csv`
- `results/simpleqa_clean_100_v2_1/simpleqa_threshold_summary.csv`
- `results/simpleqa_clean_100_v2_2/simpleqa_threshold_summary.csv`
- `results/simpleqa_clean_100_comparison.csv`