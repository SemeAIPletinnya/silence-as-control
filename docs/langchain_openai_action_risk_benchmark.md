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
- A manual run script that writes:
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

## CI and test boundaries

- This run is manual-only and should not run in CI.
- Unit tests continue to validate adapter logic without requiring OpenAI credentials.

## Economic framing

The reporting uses a conservative asymmetric heuristic:

- Cost(false accept risky output) >> Cost(silence or review)

This is aligned with PoR's emphasis on release control over unconditional throughput.
