from __future__ import annotations

import re
import unicodedata
from itertools import combinations

_TOKEN_RE = re.compile(r"\b[\w']+\b", flags=re.UNICODE)
_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "was",
    "were",
    "with",
}
_LEMMA_MAP = {
    "wrote": "write",
    "written": "write",
    "writes": "write",
}


def _normalize_token(token: str) -> str:
    token = unicodedata.normalize("NFKC", token.lower().strip())
    if not token:
        return ""
    if token in _LEMMA_MAP:
        return _LEMMA_MAP[token]
    return token


def _content_token_set(text: str) -> set[str]:
    tokens = {_normalize_token(t) for t in _TOKEN_RE.findall(text)}
    return {t for t in tokens if t and t not in _STOPWORDS}


def pairwise_semantic_similarity(a: str, b: str) -> float:
    """Lightweight lexical-factual similarity in [0, 1]."""
    set_a = _content_token_set(a)
    set_b = _content_token_set(b)

    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0

    intersection = set_a.intersection(set_b)
    union = set_a.union(set_b)
    return len(intersection) / len(union)


def semantic_agreement_score(candidates: list[str]) -> float:
    """Mean pairwise similarity across candidate answers in [0, 1]."""
    if not candidates:
        return 0.0
    if len(candidates) == 1:
        return 1.0

    similarities = [pairwise_semantic_similarity(a, b) for a, b in combinations(candidates, 2)]
    return sum(similarities) / len(similarities)
