# Signal Contract

PoR release control consumes signal values; it does not make every signal source
identical.

## Runtime/demo signal helper

`silence_as_control.signals.compute_signals(candidate, reference)` returns:

- `coherence`: runtime/demo embedding overlap estimate in `[0, 1]`
- `drift`: `1 - coherence` for that same local runtime/demo estimate

This helper is intentionally scoped. It is not a universal PoR signal contract.

## Contracts that remain separate

- Core primitive: consumes `drift` and `coherence` and computes instability.
- API runtime: may estimate coherence/drift with local or injected embeddings.
- Benchmarks/evals: may use benchmark-specific signal definitions.
- Action-risk detector telemetry: remains its own telemetry contract.
- SimpleQA and LangChain benchmark signals: remain benchmark-specific unless a
  call site is proven to be a pure duplicate with identical behavior.

## Non-goal

Do not reinterpret 0.39, 0.35, 0.42, or 0.43 as universal thresholds just
because a signal helper exists. Threshold meaning depends on the signal regime,
model, task, and acceptance-risk target.
