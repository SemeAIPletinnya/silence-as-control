# Adapters

Integration layer for silence-as-control with external frameworks.

## Available Adapters

| Adapter | Framework | Status |
|---------|-----------|--------|
| `langchain_adapter.py` | LangChain | Ready |
| `openai_adapter.py` | OpenAI API | Ready |
| `poe_adapter.py` | Poe Python | Ready |

## Usage Pattern

All adapters follow the same pattern:

```python
from adapters.openai_adapter import gated_completion

result = gated_completion(
    client,
    messages=[...],
    coherence_fn=my_coherence_fn,
    drift_fn=my_drift_fn,
)

if result is None:
    # Silence was triggered
    pass
```

## Adding New Adapters

1. Import constants: `SILENCE`, `COHERENCE_THRESHOLD`, `DRIFT_THRESHOLD`
2. Implement `should_silence(coherence, drift)`
3. Wrap the framework's call with gate logic
4. Return `SILENCE` (None) when gate triggers

---

*SemeAi Control Layer*
