"""Shared runtime/demo signal-estimation utilities.

This module intentionally does not define a universal PoR signal contract.
Benchmark/eval signal semantics, action-risk telemetry, SimpleQA scoring, and
LangChain-specific benchmark signals can use distinct contracts and thresholds.
"""

from __future__ import annotations

import math
from hashlib import sha256
from collections.abc import Callable, Sequence

from silence_as_control.config import get_max_embedding_chars

EmbeddingFn = Callable[[str], list[float]]


def _clip(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(value, high))


def stable_token_index(token: str, dim: int) -> int:
    """Map token to a deterministic embedding slot."""
    digest = sha256(token.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big") % dim


def local_bow_embedding(text: str, *, dim: int = 64) -> list[float]:
    """Return the deterministic local bag-of-words embedding used by runtime demos."""
    vec = [0.0] * dim
    truncated = text[: get_max_embedding_chars()]
    for token in truncated.lower().split():
        vec[stable_token_index(token, len(vec))] += 1.0

    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0.0:
        return vec
    return [v / norm for v in vec]


def cosine_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
    """Compute cosine similarity with zero-vector safeguards."""
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    denom = norm_a * norm_b
    if denom == 0.0:
        return 0.0
    return dot / denom


def is_nonnegative_vector(vec: Sequence[float]) -> bool:
    """Return whether all vector dimensions are nonnegative."""
    return all(v >= 0.0 for v in vec)


def map_similarity_to_coherence(similarity: float, *, nonnegative_space: bool) -> float:
    """Map cosine similarity into runtime/demo coherence in [0, 1]."""
    if nonnegative_space:
        return _clip(similarity)
    return _clip((similarity + 1.0) / 2.0)


def compute_signals(candidate: str, reference: str) -> tuple[float, float]:
    """Return `(coherence, drift)` for shared runtime/demo signal estimation.

    WARNING: this helper is for shared runtime/demo signal estimation only. It
    is not a universal PoR signal contract, and must not replace benchmark,
    evaluation, action-risk telemetry, SimpleQA, or LangChain signal semantics
    unless those call sites are proven pure duplicates with identical behavior.
    """
    if not candidate.strip():
        return 0.0, 1.0

    candidate_vec = local_bow_embedding(candidate)
    reference_vec = local_bow_embedding(reference)
    nonnegative_space = is_nonnegative_vector(candidate_vec) and is_nonnegative_vector(
        reference_vec
    )
    similarity = cosine_similarity(candidate_vec, reference_vec)
    coherence = map_similarity_to_coherence(
        similarity,
        nonnegative_space=nonnegative_space,
    )
    return coherence, _clip(1.0 - coherence)
