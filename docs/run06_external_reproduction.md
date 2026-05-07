# Run 06 External Reproduction Guide

This guide describes how an external reader can reproduce the Run 06 LangChain/OpenAI action-risk benchmark path from the repository alone. It is intentionally documentation-only: it does not change PoR core behavior, detector logic, thresholds, model settings, datasets, benchmark runner logic, or tracked benchmark results.

## What Run 06 is

Run 06 is a 1000-case **synthetic action-risk integration/deployment validation benchmark** for the LangChain/OpenAI release-control lane.

- Dataset: `data/action_risk/action_risk_1000.jsonl`.
- Default model path: `gpt-4.1-mini` through the `OPENAI_MODEL` environment variable.
- Candidate generation: LangChain/OpenAI integration.
- Release control: `PoRLangChainReleaseGate` decisions over generated candidates.
- Execution mode: manual-only. Do not run this benchmark in CI.

The benchmark evaluates the release-control path: generation occurs first, and the release gate decides whether the generated candidate is released, routed to review, or silenced.

## What Run 06 is not

Run 06 should be read with narrow research-engineering scope.

- It is not a universal AI safety benchmark.
- It is not external validation.
- It is not proof of general model safety.
- It is not evidence that the model itself improved.
- It is not threshold retuning.
- It is not a PoR primitive-core change.

The tracked hardened v4 evidence supports an integration/deployment validation claim for this dataset, model path, and release-control interpretation. It does not establish broader safety or generalization claims.

## Prerequisites

Use a local Python environment with the repository dependencies installed:

```bash
python -m pip install -r requirements.txt
```

Set an OpenAI API key in your shell environment before running the benchmark:

```bash
export OPENAI_API_KEY=...
```

Optionally pin the model environment variable to the Run 06 default:

```bash
export OPENAI_MODEL=gpt-4.1-mini
```

Never commit API keys, `.env` files containing secrets, shell history with secrets, or generated artifacts that expose credentials.

## Reproduction commands

Run these commands from the repository root.

### Fresh run

```bash
python benchmarks/langchain_openai/run_langchain_openai_por.py --dataset data/action_risk/action_risk_1000.jsonl --run-id 06_1000case_repro
```

### Resume an interrupted run

If the run is interrupted after some rows have already been written, resume with the same run ID:

```bash
python benchmarks/langchain_openai/run_langchain_openai_por.py --dataset data/action_risk/action_risk_1000.jsonl --run-id 06_1000case_repro --resume
```

Resume mode reads the existing run JSONL for completed case IDs, validates duplicate IDs in that resume file, skips completed cases, and continues over the remaining dataset in deterministic order.

### Optional tracing

Tracing is disabled by default for local benchmark runs to avoid LangSmith/LangChain trace noise and upload/rate-limit warnings. Use tracing only when you need provider/tooling diagnostics:

```bash
python benchmarks/langchain_openai/run_langchain_openai_por.py --dataset data/action_risk/action_risk_1000.jsonl --run-id 06_1000case_repro --enable-tracing
```

## Expected outputs

For a run ID such as `06_1000case_repro`, the runner writes:

- `reports/langchain_openai_run_06_1000case_repro.jsonl`
- `reports/langchain_openai_summary_06_1000case_repro.md`

The general output paths are:

- `reports/langchain_openai_run_<run-id>.jsonl`
- `reports/langchain_openai_summary_<run-id>.md`

JSONL rows are written incrementally after each completed case. The summary file is generated only after the run completes successfully. If a provider/API failure occurs, completed JSONL rows are preserved and the runner exits non-zero instead of converting the provider failure into a benchmark decision.

Generated reproduction artifacts should be treated as local outputs unless there is an explicit reason to track them. Do not create or commit new benchmark results as part of documentation-only reproduction-guide work.

## Comparing with tracked Run 06 hardened v4 evidence

Use these tracked artifacts for comparison and interpretation:

- Hardened v4 summary: [`reports/langchain_openai_summary_06_1000case_hardened_v4.md`](../reports/langchain_openai_summary_06_1000case_hardened_v4.md)
- Benchmark framing and progression: [`docs/langchain_openai_action_risk_benchmark.md`](langchain_openai_action_risk_benchmark.md)
- Evidence navigation: [`docs/evidence_map.md`](evidence_map.md)

Exact reproduction numbers can vary if provider behavior, model serving, dependency behavior, or upstream model outputs change over time. The important reproducibility target is that the dataset, command path, output artifacts, and release-control interpretation remain auditable.

### Fixed hardened v4 reference numbers

The tracked hardened v4 Run 06 report records:

| Metric | Value |
| --- | ---: |
| Cases | 1000 |
| PROCEED | 422 |
| NEEDS_REVIEW | 578 |
| SILENCE | 0 |
| False accepts | 247 |
| Safe overblocks | 25 |
| Estimated cost saved | 33174 (~69.11%) |

These numbers are reference evidence for the tracked hardened v4 artifact, not a guarantee that a future provider-backed reproduction run will match exactly.

## How to read results

- `PROCEED` means the generated candidate was released.
- `NEEDS_REVIEW` is a release-control review outcome.
- `SILENCE` is a separate abstention outcome and should not be collapsed into `NEEDS_REVIEW`.
- A **false accept** is a risky case allowed to `PROCEED`.
- A **safe overblock** is a safe read-only case sent to `NEEDS_REVIEW`.
- Estimated cost saved is an asymmetric reporting heuristic, not a financial guarantee.

The benchmark is about the control path around release. It should not be interpreted as a direct measurement of general model quality or a claim that model generation became safer.

## Troubleshooting

### `OPENAI_API_KEY` is missing

Set `OPENAI_API_KEY` in the environment before running the benchmark. Do not paste the key into tracked files or commit it.

### Run interrupted

Use `--resume` with the same `--run-id` to continue from the existing incremental JSONL rows.

### LangSmith/LangChain trace noise

Tracing is disabled by default for local benchmark runs. Use `--enable-tracing` only if you need tracing diagnostics and are prepared for provider/tooling trace output.

### Windows pytest temporary-file permissions

If pytest encounters temporary directory permission issues on Windows, run tests with an explicit local base temp directory, for example:

```bash
python -m pytest tests/test_langchain_openai_benchmark_paths.py -q --basetemp=.pytest_tmp_runner
```
