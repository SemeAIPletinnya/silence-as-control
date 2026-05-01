# Evaluation Summary

This page is a readable summary of recent results. Canonical evidence remains in `docs/` and committed artifacts.

## Recent local Ollama evidence (100 SimpleQA examples)

### Qwen3 4B / PoR v2

- Threshold: `0.43`
- Answer coverage: `84%`
- Silence: `16%`
- Accepted wrong: `0`
- Accepted precision: `100%`

### Qwen3 8B / PoR v2

- Threshold: `0.42/0.43`
- Answer coverage: `93%`
- Silence: `7%`
- Accepted wrong: `1`
- Accepted precision: `98.92%`

## Conservative interpretation

- Qwen3 4B is a practical zero-accepted-failure anchor for that run.
- Qwen3 8B is a high-coverage boundary, not a zero-failure anchor.
- A stronger model does not automatically imply safer release behavior at a fixed threshold.

## Scope note

These statements are run-scoped and repository-scoped. They should not be generalized as universal safety guarantees.
