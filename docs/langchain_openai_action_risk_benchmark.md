# LangChain + OpenAI Action-Risk Benchmark (PoR Release Control)

This benchmark is a **small integration/deployment validation artifact** for the LangChain adapter in this repository.

## Core framing

- **Generation is not release.**
- LangChain/OpenAI (`langchain_openai.ChatOpenAI`) generates candidate outputs.
- `PoRLangChainReleaseGate` controls whether those outputs are released (`PROCEED`) or blocked/deferred (`SILENCE` / `NEEDS_REVIEW`).

This preserves PoR's control-first architecture: model generation can occur, while release remains separately governed.

## What this benchmark is

- A manual benchmark runner with:
  - a backward-compatible built-in 14-case dataset (default), and
  - optional external JSONL dataset loading for larger runs (for example, 50 cases).
- Action-risk classes:
  - `SAFE_READ_ONLY`
  - `CONFIG_RISK`
  - `API_MUTATION_RISK`
  - `AUTH_SCOPE_RISK`
  - `PARTIAL_UPDATE_RISK`
  - `HIDDEN_DEPENDENCY_RISK`
  - `UNSUPPORTED_OVERCLAIM`
- A manual run script that writes local artifacts incrementally:
  - `reports/langchain_openai_run_01.jsonl`
  - `reports/langchain_openai_summary_01.md`
- A simple asymmetric cost summary:
  - baseline = release all generated outputs
  - PoR = penalize false accepts heavily; lower penalty for silence/review on safe content

## What this benchmark is **not**

- Not a universal model safety benchmark.
- Not a replacement for domain-specific validation.
- Not a claim that a single threshold or prompt-set generalizes globally.

## Running it manually

```bash
export OPENAI_API_KEY=... 
# optional override
export OPENAI_MODEL=gpt-4.1-mini
python benchmarks/langchain_openai/run_langchain_openai_por.py
```

Tracing is disabled by default for this benchmark runner to keep local runs quiet and avoid LangSmith/LangChain upload warnings or rate-limit noise. To opt out of that default disabling behavior, pass `--enable-tracing`; the flag leaves the caller's tracing environment settings unchanged rather than forcing tracing on.

The JSONL artifact is written after each completed case. If a provider/API call fails, the runner prints the failing case ID, exits non-zero, and preserves already written completed cases rather than converting the failure into a benchmark decision.

### Resume mode (`--resume`)

Use `--resume` after an interrupted run to continue from the same run ID without repeating completed cases. The runner reads the existing `reports/langchain_openai_run_<run-id>.jsonl`, loads completed case IDs, rejects duplicate IDs in that resume file, and skips completed IDs while preserving deterministic dataset order for the remaining cases.

```bash
python benchmarks/langchain_openai/run_langchain_openai_por.py \
  --dataset data/action_risk/action_risk_1000.jsonl \
  --run-id 06_1000case \
  --resume
```

Without `--resume`, the runner keeps the historical default behavior of starting a fresh output JSONL for the selected run ID.

### External dataset mode (`--dataset`)

Use `--dataset` to load cases from a JSONL file instead of the hardcoded default.

```bash
python benchmarks/langchain_openai/run_langchain_openai_por.py \
  --dataset data/action_risk/action_risk_50.jsonl \
  --run-id 03_50case
```

For larger/manual integration runs, prefer external JSONL datasets so the case set is auditable and easy to evolve without changing benchmark runner logic.

Run 04 (100-case expansion):

```bash
python benchmarks/langchain_openai/run_langchain_openai_por.py \
  --dataset data/action_risk/action_risk_100.jsonl \
  --run-id 04_100case
```

If `OPENAI_API_KEY` is missing, the script exits with a clear message and non-zero status.


## Run 06 1000-case action-risk progression

Run 06 is a **synthetic integration/deployment validation benchmark** for the LangChain/OpenAI release-control lane. It is not a universal AI safety claim, not external validation, and not evidence that the model itself improved.

Strongest supported claim: **same model, same dataset, same threshold, no PoR core change; release-layer hardening changed the review/release profile.** Across this progression, the dataset was `data/action_risk/action_risk_1000.jsonl`, the model was `gpt-4.1-mini`, and the improvements came from telemetry-driven integration/release-layer detector hardening rather than threshold tuning, model changes, dataset changes, benchmark-runner changes, or primitive PoR core changes.

| Run 06 stage | PROCEED | NEEDS_REVIEW | SILENCE | False accepts | Safe overblocks | Estimated cost saved | Report artifact |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Initial | 854 | 146 | 0 | 664 | n/a | 8,518 (~17.7%) | [`reports/langchain_openai_summary_06_1000case.md`](../reports/langchain_openai_summary_06_1000case.md) |
| Hardened v1 | 695 | 310 | 0 | 505 | n/a | 18,227 (~38.0%) | No separate v1 summary artifact currently tracked; values retained as recorded progression context. |
| Hardened v2 | 576 | 424 | 0 | 397 | n/a | 23,210 (~48.35%) | [`reports/langchain_openai_summary_06_1000case_hardened_v2.md`](../reports/langchain_openai_summary_06_1000case_hardened_v2.md) |
| Hardened v3 | 542 | 458 | 0 | 368 | n/a | 25,677 (~53.49%) | [`reports/langchain_openai_summary_06_1000case_hardened_v3.md`](../reports/langchain_openai_summary_06_1000case_hardened_v3.md) |
| Hardened v4 | 422 | 578 | 0 | 247 | 25 | 33,174 (~69.11%) | [`reports/langchain_openai_summary_06_1000case_hardened_v4.md`](../reports/langchain_openai_summary_06_1000case_hardened_v4.md) |

### Hardened v4 remaining false accepts by class

| Risk class | False accepts |
| --- | ---: |
| `HIDDEN_DEPENDENCY_RISK` | 65 |
| `UNSUPPORTED_OVERCLAIM` | 57 |
| `API_MUTATION_RISK` | 52 |
| `AUTH_SCOPE_RISK` | 39 |
| `PARTIAL_UPDATE_RISK` | 32 |
| `CONFIG_RISK` | 2 |

### How to read these results

- **False accept** = a risky case incorrectly allowed to `PROCEED`.
- **Safe overblock** = a safe read-only case sent to `NEEDS_REVIEW`.
- `NEEDS_REVIEW` is a release-control outcome, not a model failure.
- `SILENCE` remains separate from `NEEDS_REVIEW`; this progression moved cases between release and review lanes without collapsing the tri-state integration semantics.

## CI and test boundaries

- This run is manual-only and should not run in CI.
- Unit tests continue to validate adapter logic without requiring OpenAI credentials.

## Economic framing

The reporting uses a conservative asymmetric heuristic:

- Cost(false accept risky output) >> Cost(silence or review)

This is aligned with PoR's emphasis on release control over unconditional throughput.
