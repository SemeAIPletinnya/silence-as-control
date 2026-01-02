# Orchestrator Agent

## Role
Coordinates multi-model responses with consensus gating.

## Function
- Collects responses from multiple models
- Measures consensus across responses
- Applies consensus gate before output
- Returns SILENCE if models disagree

## Behavior

```python
def orchestrate(models, query):
    responses = [model(query) for model in models]
    consensus = measure_consensus(responses)
    
    if consensus < CONSENSUS_THRESHOLD:
        return SILENCE  # Models disagree
    
    return aggregate(responses)
```

## When to Use
- Multi-model verification required
- High-stakes decisions
- Conflicting information sources

## Threshold
`CONSENSUS_THRESHOLD = 0.5`

## Key Principle
> No synthetic agreement. If models disagree, silence is preferable to forced consensus.

---

*SemeAi Control Layer*
