# Release-Risk Benchmark Index

## Purpose

This page is the recommended entry point for the release-risk benchmark evidence chain across v1, v2, and v3.

Core thesis:

**generation capability != release authority**

These benchmarks measure release-control behavior, not model intelligence.

- Baseline route: `candidate -> RELEASE`
- SaC-style route: `candidate -> release gate -> PROCEED / NEEDS_REVIEW / SILENCE`

For project identity and framing, see project memory/tracking surfaces in `docs/evidence_map.md`, `docs/roadmap_2026.md`, and issue tracking referenced there.

## Benchmark progression

- **v1** -> deterministic handcrafted release-risk routing
- **v2** -> fixture candidate-output replay
- **v3** -> fixture generation/replay scaffold
- **v4** -> future provider/local generated-candidate capture + replay (**not yet implemented**)

## v1: deterministic release-risk benchmark

**Scope**

- Deterministic local evidence over handcrafted release-risk cases.
- Baseline release-by-default versus SaC-style routing behavior.

**Main artifacts**

- `benchmarks/release_risk/README.md`
- `benchmarks/release_risk/run_release_risk.py`
- `benchmarks/release_risk/data/release_risk_50.jsonl`
- `benchmarks/release_risk/results/release_risk_summary.json`
- `benchmarks/release_risk/results/release_risk_summary.csv`
- `tests/test_release_risk_benchmark.py`

**Report**

- `docs/release_risk_benchmark_report.md`

**Commands**

```bash
python benchmarks/release_risk/run_release_risk.py
python -m pytest tests/test_release_risk_benchmark.py -q
```

**Interpretation boundary**

- Deterministic local benchmark evidence only.
- Not live model-output generation evidence.
- Not production safety evidence.

## v2: fixture candidate-output replay benchmark

**Scope**

- Release-routing behavior over fixture candidate outputs.
- Baseline release-by-default versus SaC-style routing behavior.

**Main artifacts**

- `benchmarks/release_risk_v2/README.md`
- `benchmarks/release_risk_v2/run_release_risk_v2.py`
- `benchmarks/release_risk_v2/data/release_risk_prompts_50.jsonl`
- `benchmarks/release_risk_v2/candidates/fixture_candidates_50.jsonl`
- `benchmarks/release_risk_v2/results/release_risk_v2_summary.json`
- `benchmarks/release_risk_v2/results/release_risk_v2_summary.csv`
- `benchmarks/release_risk_v2/results/release_risk_v2_replay.jsonl`
- `tests/test_release_risk_v2_benchmark.py`

**Report**

- `docs/release_risk_v2_benchmark_report.md`

**Commands**

```bash
python benchmarks/release_risk_v2/run_release_risk_v2.py --mode fixture
python -m pytest tests/test_release_risk_v2_benchmark.py -q
```

**Interpretation boundary**

- Deterministic fixture replay evidence only.
- Not live provider/model generation evidence.
- Not production safety evidence.

## v3: fixture generation/replay scaffold

**Scope**

- Validates generated-candidate schema.
- Validates fixture generation path.
- Validates replay routing surface.
- Validates provider/local mode separation in benchmark interfaces.

**Main artifacts**

- `benchmarks/release_risk_v3/README.md`
- `benchmarks/release_risk_v3/generate_candidates_v3.py`
- `benchmarks/release_risk_v3/run_release_risk_v3.py`
- `benchmarks/release_risk_v3/data/release_risk_prompts_50.jsonl`
- `benchmarks/release_risk_v3/candidates/fixture_generated_candidates_50.jsonl`
- `benchmarks/release_risk_v3/candidates/generated_candidates_fixture.jsonl`
- `benchmarks/release_risk_v3/results/release_risk_v3_summary.json`
- `benchmarks/release_risk_v3/results/release_risk_v3_summary.csv`
- `benchmarks/release_risk_v3/results/release_risk_v3_replay.jsonl`
- `tests/test_release_risk_v3_benchmark.py`

**Report**

- `docs/release_risk_v3_benchmark_report.md`

**Current recorded summary (from committed artifact)**

- total_cases: 50
- baseline_released: 50
- baseline_unsafe_released: 25
- sac_proceed: 9
- sac_needs_review: 22
- sac_silence: 19
- sac_unsafe_released: 0
- unsafe_release_reduction_percent: 100.0
- safe_proceed_rate: 90.0
- candidate_source: fixture
- generation_mode: fixture
- provider: null
- model: fixture-generated-candidates-v1
- num_generation_failures: 0
- num_empty_candidates: 0
- num_replayed_candidates: 50

**Commands**

```bash
python benchmarks/release_risk_v3/generate_candidates_v3.py --mode fixture
python benchmarks/release_risk_v3/run_release_risk_v3.py --mode fixture
python -m pytest tests/test_release_risk_v3_benchmark.py -q
```

**Interpretation boundary**

- Deterministic fixture generation/replay evidence only.
- This is not live provider/model generation evidence.
- Provider/local generation capture remains future work.
- No API keys are required for fixture mode.
- Not production safety evidence.

## Artifact lineage

- `#224 -> #225 -> #226`: v1 deterministic benchmark
- `#227 -> #228 -> #229 -> #230`: v2 fixture replay benchmark
- `#231 -> #232 -> #233 -> #234 -> #235`: v3 fixture generation/replay benchmark

## Common interpretation boundaries

These benchmarks do **not** claim:

- production safety;
- exploit prevention;
- universal AI safety;
- alignment solution;
- model correctness;
- model improvement;
- hallucination elimination;
- live provider/model generation evidence for v1/v2/v3;
- threshold generalization across all models/tasks.

Supported interpretation:

- baseline releases candidates by default;
- SaC-style routing changes release behavior;
- unsafe candidate releases are reduced in these scoped deterministic/fixture benchmark settings;
- generation remains separate from release authority.

## Reproduction commands

**v1**

```bash
python benchmarks/release_risk/run_release_risk.py
python -m pytest tests/test_release_risk_benchmark.py -q
```

**v2**

```bash
python benchmarks/release_risk_v2/run_release_risk_v2.py --mode fixture
python -m pytest tests/test_release_risk_v2_benchmark.py -q
```

**v3**

```bash
python benchmarks/release_risk_v3/generate_candidates_v3.py --mode fixture
python benchmarks/release_risk_v3/run_release_risk_v3.py --mode fixture
python -m pytest tests/test_release_risk_v3_benchmark.py -q
```

**Shared**

```bash
python -m pytest tests/test_api.py -q
```

## Next step

The next benchmark step is **v4 provider/local generated-candidate capture + replay**.

Do not start v4 until v1/v2/v3 benchmark navigation and evidence architecture are coherent.

v4 should remain optional-provider, fixture-fallback, secret-safe, and conservative in claims.
