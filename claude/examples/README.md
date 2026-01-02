# Examples

Runnable examples demonstrating silence-as-control patterns.

## Files

| Example | Description |
|---------|-------------|
| `basic_gate.py` | Minimal primitive demonstration |
| `agent_loop.py` | Complete agent loop with gating |
| `multi_model.py` | Multi-model consensus orchestration |

## Running Examples

```bash
python .claude/examples/basic_gate.py
python .claude/examples/agent_loop.py
python .claude/examples/multi_model.py
```

## Key Patterns

### Pattern 1: Basic Gate
```python
if should_silence(coherence, drift):
    return SILENCE
return response
```

### Pattern 2: Agent Step
```python
candidate = model(context, query)
coherence = measure_coherence(context, candidate)
drift = measure_drift(history)
if should_silence(coherence, drift):
    return SILENCE
return candidate
```

### Pattern 3: Multi-Model
```python
responses = [model(query) for model in models]
consensus = measure_consensus(responses)
if consensus < CONSENSUS_THRESHOLD:
    return SILENCE
return aggregate(responses)
```

---

*SemeAi Control Layer*
