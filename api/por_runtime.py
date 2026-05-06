"""Runtime extensions for PoR API scoring (non-core).

These helpers are deployment-oriented additions around the core primitive:
- environment-configurable runtime threshold,
- adaptive threshold computation,
- embedding-based coherence estimation,
- multi-sample drift estimation.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass

from silence_as_control.config import (
    ADAPTIVE_THRESHOLD_ALPHA_DEFAULT,
    ADAPTIVE_THRESHOLD_MAXIMUM_DEFAULT,
    ADAPTIVE_THRESHOLD_MINIMUM_DEFAULT,
    MAX_EMBEDDING_CHARS_DEFAULT,
    RUNTIME_EXTENSION_THRESHOLD_DEFAULT,
    get_max_embedding_chars as resolve_max_embedding_chars,
    get_runtime_gate_threshold,
)
from silence_as_control.signals import (
    cosine_similarity,
    is_nonnegative_vector,
    local_bow_embedding,
    map_similarity_to_coherence,
    stable_token_index,
)

# Runtime extension default. Kept aligned to the core default by default.
RUNTIME_EXTENSION_DEFAULT_THRESHOLD = RUNTIME_EXTENSION_THRESHOLD_DEFAULT
# Backward-compatible alias.
RUNTIME_GATE_THRESHOLD_DEFAULT = RUNTIME_EXTENSION_DEFAULT_THRESHOLD

THRESHOLD_ENV_VAR = "POR_RUNTIME_GATE_THRESHOLD"
MAX_EMBEDDING_CHARS_ENV_VAR = "MAX_EMBEDDING_CHARS"
DEFAULT_MAX_EMBEDDING_CHARS = MAX_EMBEDDING_CHARS_DEFAULT
EmbeddingFn = Callable[[str], list[float]]
CUSTOM_EMBEDDING_FN: EmbeddingFn | None = None


@dataclass(frozen=True)
class AdaptiveThresholdConfig:
    """[RUNTIME] Adaptive-threshold policy parameters."""

    alpha: float = ADAPTIVE_THRESHOLD_ALPHA_DEFAULT
    minimum: float = ADAPTIVE_THRESHOLD_MINIMUM_DEFAULT
    maximum: float = ADAPTIVE_THRESHOLD_MAXIMUM_DEFAULT


def _clip(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(value, high))


def _stable_token_index(token: str, dim: int) -> int:
    """Backward-compatible wrapper around the shared stable token index."""
    return stable_token_index(token, dim)


def _is_nonnegative_vector(vec: Sequence[float]) -> bool:
    return is_nonnegative_vector(vec)


def get_runtime_threshold(default: float = RUNTIME_EXTENSION_DEFAULT_THRESHOLD) -> float:
    """[RUNTIME] Resolve runtime threshold from env with safe fallback.

    Uses `POR_RUNTIME_GATE_THRESHOLD` if set; otherwise returns `default`.
    """
    return get_runtime_gate_threshold(default)


def get_max_embedding_chars(default: int = DEFAULT_MAX_EMBEDDING_CHARS) -> int:
    """[RUNTIME] Resolve max chars for local embedding with safe fallback."""
    return resolve_max_embedding_chars(default)


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
    return local_bow_embedding(text)


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
    notes.append(
        "embedding_cosine_nonnegative" if nonnegative_space else "embedding_cosine"
    )
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
    instabilities = [
        _clip((drifts[i] + (1.0 - coherences[i])) / 2.0) for i in range(n)
    ]
    mean_instability = sum(instabilities) / len(instabilities)

    adapted = base_threshold + config.alpha * (mean_instability - base_threshold)
    return _clip(adapted, config.minimum, config.maximum)
