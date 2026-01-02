# Coherence Metrics

## Overview

Coherence is the core measurement that gates output in silence-as-control systems.

**Definition:** Preservation of internal alignment across reasoning steps, not correctness of output.

## Metrics

| Metric | Threshold | Trigger |
|--------|-----------|---------|
| Coherence | < 0.7 | Silence |
| Drift | > 0.3 | Silence |
| Consensus | < 0.5 | Silence |

## Coherence Measurement

### What It Measures
- Internal alignment across reasoning steps
- Consistency between context and response
- Confidence in the response trajectory

### Implementation Approaches

**1. Embedding Similarity**
```python
def coherence_by_embedding(context, response):
    context_embedding = embed(context)
    response_embedding = embed(response)
    return cosine_similarity(context_embedding, response_embedding)
```

**2. Self-Consistency**
```python
def coherence_by_consistency(context, query, model, n_samples=5):
    responses = [model(context, query) for _ in range(n_samples)]
    return measure_agreement(responses)
```

**3. Entropy-Based**
```python
def coherence_by_entropy(token_probs):
    entropy = -sum(p * log(p) for p in token_probs)
    return 1.0 - normalize(entropy)
```

## Drift Measurement

### What It Measures
- Deviation from historical reasoning trajectory
- Topic shift detection
- Semantic divergence over time

### Key Property
Drift is measured **longitudinally**, not per-response.

## Consensus Measurement

### What It Measures
- Agreement across multiple model responses
- Absence of contradictory signals

### Formula
```python
consensus = 1.0 / len(unique_responses)
```

## Thresholds

Current defaults:
- `COHERENCE_THRESHOLD = 0.7`
- `DRIFT_THRESHOLD = 0.3`
- `CONSENSUS_THRESHOLD = 0.5`

These are configurable per deployment.

---

*SemeAi Control Layer*
