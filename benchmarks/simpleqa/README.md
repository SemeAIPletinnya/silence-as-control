# SimpleQA PoR Benchmark Harness

This benchmark evaluates **baseline answering** vs **PoR-gated release control** on a local SimpleQA-style dataset.

It is designed to test the Silence-as-Control hypothesis:

- baseline: always answers,
- PoR-gated: generates multiple candidates, computes drift across that candidate set, then answers only when instability is below threshold (otherwise silences).

It supports four PoR gate modes:

- **PoR v1 (default)**: drift + coherence -> instability -> threshold decision.
- **PoR v2 (experimental)**: keeps v1 signals and adds semantic agreement + self-check risk before thresholding.
- **PoR v2.1 (experimental)**: keeps v2 signals and adds contradiction challenge risk before thresholding.
- **PoR v2.2 (experimental)**: keeps v2.1 and adds a strong additive risk penalty when `self_check = NO`.

## Why SimpleQA

SimpleQA gives short factual QA examples with canonical answers, making it suitable for measuring:

- accepted wrong answers,
- controlled silence,
- threshold tradeoffs.

## Architecture alignment

This harness preserves repository layer boundaries:

- **core primitive**: `api/core_primitive.py`
- **runtime scoring extensions**: `api/por_runtime.py`
- **experimental recovery**: **disabled by default** (not used in this benchmark)

This benchmark evaluates **release-control tradeoffs**, not model-generation improvement.

## Files

- `benchmarks/simpleqa/run_simpleqa_por.py` — end-to-end runner
- `benchmarks/simpleqa/dataset_loader.py` — deterministic local dataset loader
- `benchmarks/simpleqa/model_adapter.py` — model-provider adapter interface
- `benchmarks/simpleqa/por_adapter.py` — bridge to repo PoR runtime + core gate
- `benchmarks/simpleqa/metrics.py` — scoring + aggregate metrics
- `benchmarks/simpleqa/plot_results.py` — matplotlib tradeoff plot

## Dataset format

Use a local `.json`, `.jsonl`, or `.csv` file with mapped fields:

- question: text prompt (`--question-field`)
- answer(s): canonical answer(s) (`--answer-field` and/or `--answers-field`)
- id: optional unique id (`--id-field`)

Defaults:

- `question`
- `answer`
- `answers`
- `id`

## Run

```bash
python benchmarks/simpleqa/run_simpleqa_por.py \
  --dataset-path /path/to/simpleqa.jsonl \
  --provider openai \
  --model gpt-4o-mini \
  --por-mode v1 \
  --max-examples 200 \
  --thresholds 0.35 0.39 0.42 0.43 \
  --por-samples 3 \
  --baseline-temperature 0.0 \
  --por-temperature 0.4 \
  --output-dir results/simpleqa
```

Environment variables for OpenAI-compatible adapter:

- `OPENAI_API_KEY` (required)
- `OPENAI_BASE_URL` (optional)

Temperature controls:

- `--baseline-temperature` defaults to `0.0` (deterministic baseline behavior).
- `--por-temperature` defaults to `0.4`, allowing PoR candidate samples to vary and expose instability/drift.

PoR mode:

- `--por-mode v1` (default): existing benchmark behavior.
- `--por-mode v2`: experimental prototype combining:
  - v1 instability,
  - semantic agreement risk from multi-sample candidate overlap,
  - compact self-check label (`YES` / `NO` / `UNSURE`) mapped to risk.
- `--por-mode v2_1`: experimental prototype extending v2 with a short contradiction challenge check:
  - model is asked to challenge the primary candidate,
  - response is mapped to `NO_CONTRADICTION` / `WEAK_CHALLENGE` / `STRONG_CHALLENGE`,
  - contradiction risk is combined with v2 signals.
- `--por-mode v2_2`: experimental prototype extending v2.1 with stronger handling of `self_check = NO`:
  - computes `risk_v2_2 = risk_v2_1 + self_check_no_penalty` when `self_check_label == "NO"`,
  - otherwise `risk_v2_2 = risk_v2_1`,
  - then thresholds `risk_v2_2` for release-control decision.
- `--self-check-no-penalty` (default `0.30`): additive penalty used only in `v2_2`.

v2.1/v2.2 are designed to probe confidently wrong but internally consistent answers. v2.2 specifically tests whether internal model rejection should act as a stronger release-control signal. Both remain experimental and do **not** replace the core PoR primitive.

## Output artifacts

The run writes:

1. Per-example CSV:
   - `results/simpleqa/simpleqa_por_results.csv`
2. Aggregate metrics JSON:
   - `results/simpleqa/simpleqa_por_metrics.json`
3. Threshold summary CSV:
   - `results/simpleqa/simpleqa_threshold_summary.csv`
4. Plot:
   - `results/simpleqa/simpleqa_threshold_tradeoff.png`

Per-example rows include:

- `por_candidates_json` (all PoR candidates used for drift),
- `por_primary_candidate` (candidate[0], used for coherence and release output),
- `por_sample_count`,
- `por_mode`,
- `semantic_agreement_score`,
- `semantic_agreement_risk`,
- `self_check_label`,
- `self_check_risk`,
- `risk_v2`,
- `decision_v2`,
- `contradiction_label`,
- `contradiction_risk`,
- `risk_v2_1`,
- `decision_v2_1`,
- `self_check_no_penalty`,
- `self_check_no_override_applied`,
- `risk_v2_2`,
- `decision_v2_2`,
- `effective_decision` (the decision used for final output; equals v1 in v1 mode, v2 in v2 mode, v2.1 in v2_1 mode, and v2.2 in v2_2 mode).

For `v2_1`, `effective_decision` equals `decision_v2_1`. For `v2_2`, `effective_decision` equals `decision_v2_2`.

## Metric definitions

### Baseline

- `total_examples`
- `answered_count`
- `correctness_rate`
- `error_rate`

### Per-threshold PoR

- PoR drift uses multi-sample candidates per prompt (`--por-samples`, minimum 2, default 3)
- `total_examples`
- `answered_count` = non-silenced outputs
- `silence_count`
- `answer_rate` = answered_count / total_examples
- `silence_rate` = silence_count / total_examples
- `accepted_correct_count`
- `accepted_wrong_count`
- `accepted_precision` = accepted_correct_count / answered_count
- `accepted_error_rate` = accepted_wrong_count / answered_count
- `false_silence_count`
- `false_silence_rate` = false_silence_count / total_examples

`false_silence` is defined as: PoR silences a candidate that would have been judged correct under deterministic matching.

## Correctness evaluation

Default correctness is deterministic normalized exact-match:

- lowercase
- punctuation removed
- whitespace squashed

No hidden judge heuristics are used by default.

## Threshold precision

Thresholds preserve full precision internally for grouping/aggregation (no 2-decimal bucket collapsing). Display formatting is separate from grouping keys.

## Interpretation

PoR is beneficial when:

- `accepted_error_rate` decreases materially relative to baseline,
- while `silence_rate` stays within an interpretable operational range.
