"""Runtime extensions for PoR API scoring (non-core).

These helpers are deployment-oriented additions around the core primitive:
- environment-configurable runtime threshold,
- adaptive threshold computation,
- embedding-based coherence estimation,
- multi-sample drift estimation.
"""

from __future__ import annotations

import math
import os
from hashlib import sha256
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

# Runtime extension default. Kept aligned to the core default by default.
RUNTIME_EXTENSION_DEFAULT_THRESHOLD = 0.39
# Backward-compatible alias.
RUNTIME_GATE_THRESHOLD_DEFAULT = RUNTIME_EXTENSION_DEFAULT_THRESHOLD

THRESHOLD_ENV_VAR = "POR_RUNTIME_GATE_THRESHOLD"
MAX_EMBEDDING_CHARS_ENV_VAR = "MAX_EMBEDDING_CHARS"
DEFAULT_MAX_EMBEDDING_CHARS = 4000
EmbeddingFn = Callable[[str], list[float]]
CUSTOM_EMBEDDING_FN: EmbeddingFn | None = None


@dataclass(frozen=True)
class AdaptiveThresholdConfig:
    """[RUNTIME] Adaptive-threshold policy parameters."""

    alpha: float = 0.4
    minimum: float = 0.20
    maximum: float = 0.80


def _clip(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(value, high))


def _stable_token_index(token: str, dim: int) -> int:
    """Map token to embedding slot with deterministic hashing.

    Python's built-in `hash()` is process-randomized, so we use SHA-256 and
    take the first 8 bytes for a stable integer across runs and machines.
    """
    digest = sha256(token.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big") % dim


def map_similarity_to_coherence(similarity: float, *, nonnegative_space: bool) -> float:
    """Convert cosine similarity to coherence in [0, 1] for runtime gating.

    - For nonnegative bag-of-words fallback embeddings, cosine is already in
      [0, 1], so we only clamp.
    - For signed embedding spaces, cosine is in [-1, 1], so we map with
      `(cos + 1) / 2`.
    """
    if nonnegative_space:
        return _clip(similarity)
    return _clip((similarity + 1.0) / 2.0)


def _is_nonnegative_vector(vec: Sequence[float]) -> bool:
    return all(v >= 0.0 for v in vec)


def get_runtime_threshold(default: float = RUNTIME_EXTENSION_DEFAULT_THRESHOLD) -> float:
    """[RUNTIME] Resolve runtime threshold from env with safe fallback.

    Uses `POR_RUNTIME_GATE_THRESHOLD` if set; otherwise returns `default`.
    """
    raw = os.getenv(THRESHOLD_ENV_VAR)
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return _clip(value)


def get_max_embedding_chars(default: int = DEFAULT_MAX_EMBEDDING_CHARS) -> int:
    """[RUNTIME] Resolve max chars for local embedding with safe fallback."""
    raw = os.getenv(MAX_EMBEDDING_CHARS_ENV_VAR)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return max(1, value)


def _truncate_for_local_embedding(text: str) -> str:
    max_chars = get_max_embedding_chars()
    return text[:max_chars]


def _resolve_embedding_fn(embedding_fn: EmbeddingFn | None) -> EmbeddingFn:
    if embedding_fn is not None:
        return embedding_fn
    if CUSTOM_EMBEDDING_FN is not None:
        return CUSTOM_EMBEDDING_FN
    return get_embedding


def get_embedding(text: str) -> list[float]:
    """[RUNTIME] Deterministic fallback embedding function.

    This lightweight fallback keeps offline usage and tests stable.
    Production integrations can inject a stronger embedding function.
    """
    vec = [0.0] * 64
    truncated = _truncate_for_local_embedding(text)
    for token in truncated.lower().split():
        vec[_stable_token_index(token, len(vec))] += 1.0

    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0.0:
        return vec
    return [v / norm for v in vec]


def cosine_similarity(vec_a: Sequence[float], vec_b: Sequence[float]) -> float:
    """[RUNTIME] Compute cosine similarity with zero-vector safeguards."""
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    denom = norm_a * norm_b
    if denom == 0.0:
        return 0.0
    return dot / denom


def estimate_coherence(
    prompt: str,
    candidate: str,
    embedding_fn: EmbeddingFn | None = None,
) -> tuple[float, list[str]]:
    """[RUNTIME] Estimate coherence from prompt/candidate embedding similarity."""
    notes: list[str] = []
    if not candidate.strip():
        return 0.0, ["no_candidate_tokens"]

    embed = _resolve_embedding_fn(embedding_fn)
    prompt_vec = embed(prompt)
    candidate_vec = embed(candidate)
    cos = cosine_similarity(prompt_vec, candidate_vec)

    nonnegative_space = _is_nonnegative_vector(prompt_vec) and _is_nonnegative_vector(
        candidate_vec
    )
    coherence = map_similarity_to_coherence(cos, nonnegative_space=nonnegative_space)
    notes.append("embedding_cosine_nonnegative" if nonnegative_space else "embedding_cosine")
    return coherence, notes


def estimate_drift(
    candidate_texts: Sequence[str],
    embedding_fn: EmbeddingFn | None = None,
) -> tuple[float, list[str]]:
    """[RUNTIME] Estimate drift from multi-sample embedding disagreement."""
    notes: list[str] = []
    cleaned = [text.strip() for text in candidate_texts if text.strip()]
    if len(cleaned) <= 1:
        notes.append("single_sample_drift")
        return 0.0, notes

    embed = _resolve_embedding_fn(embedding_fn)
    vectors = [embed(text) for text in cleaned]
    pairwise: list[float] = []
    for i in range(len(vectors)):
        for j in range(i + 1, len(vectors)):
            pairwise.append(cosine_similarity(vectors[i], vectors[j]))

    avg_similarity = (sum(pairwise) / len(pairwise)) if pairwise else 1.0
    nonnegative_space = all(_is_nonnegative_vector(vec) for vec in vectors)
    coherence_between_samples = map_similarity_to_coherence(
        avg_similarity,
        nonnegative_space=nonnegative_space,
    )
    drift = _clip(1.0 - coherence_between_samples)
    notes.append(f"pairwise_samples:{len(cleaned)}")
    return drift, notes


def compute_adaptive_threshold(
    base_threshold: float,
    recent_drifts: Iterable[float],
    recent_coherences: Iterable[float],
    config: AdaptiveThresholdConfig = AdaptiveThresholdConfig(),
) -> float:
    """[RUNTIME] Adapt threshold toward recent mean instability.

    This is optional runtime behavior and not part of the thesis-level primitive.
    """
    drifts = [float(x) for x in recent_drifts]
    coherences = [float(x) for x in recent_coherences]

    if not drifts or not coherences:
        return _clip(base_threshold, config.minimum, config.maximum)

    n = min(len(drifts), len(coherences))
    instabilities = [_clip((drifts[i] + (1.0 - coherences[i])) / 2.0) for i in range(n)]
    mean_instability = sum(instabilities) / len(instabilities)

    adapted = base_threshold + config.alpha * (mean_instability - base_threshold)
    return _clip(adapted, config.minimum, config.maximum)
