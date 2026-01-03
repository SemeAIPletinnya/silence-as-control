# Debugger Agent

## Role
Monitors and logs silence decisions for observability.

## Function
- Tracks when silence is triggered
- Records coherence and drift values
- Provides visibility into control decisions
- Enables post-hoc analysis

## Logging Format

```python
def log_silence_decision(coherence, drift, query):
    print(f"[SILENCE] coherence={coherence:.2f}, drift={drift:.2f}, query='{query[:50]}...'")
```

## Metrics to Track

| Metric | Purpose |
|--------|---------|
| `coherence` | Internal alignment score |
| `drift` | Trajectory deviation |
| `query` | What triggered the decision |
| `timestamp` | When it occurred |
| `context_length` | Conversation depth |

## Use Cases
- Debugging unexpected silence
- Tuning thresholds
- Understanding failure modes
- Auditing control decisions

## Key Principle
> Silence is a control decision. It must be observable.

---

*SemeAi Control Layer*
