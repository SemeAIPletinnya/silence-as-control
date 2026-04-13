from __future__ import annotations

"""Shared proxy scoring helpers for eval and sandbox extension workflows.

These heuristics support evidence-style measurement surfaces.
They do not define primitive gating behavior.
"""

from typing import Any

HEDGING_TERMS = [
    "maybe",
    "probably",
    "not sure",
    "could",
    "might",
    "depending",
    "seems",
    "around",
]

CONTRADICTION_TERMS = [
    "but",
    "although",
    "however",
    "or",
    "not sure",
    "might",
    "could",
]


def normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def tokenize(text: str) -> list[str]:
    cleaned = (
        normalize(text)
        .replace(".", " ")
        .replace(",", " ")
        .replace(":", " ")
        .replace(";", " ")
        .replace("(", " ")
        .replace(")", " ")
        .replace("?", " ")
        .replace("!", " ")
        .replace("-", " ")
        .replace("_", " ")
        .replace("/", " ")
    )
    return [t for t in cleaned.split() if t]


def keyword_integrity(expected_keywords: list[str], output: str) -> float:
    out = normalize(output)
    hits = 0
    for kw in expected_keywords:
        if kw.lower() in out:
            hits += 1
    return round(hits / len(expected_keywords), 3) if expected_keywords else 1.0


def hedging_score(output: str) -> float:
    out = normalize(output)
    hits = sum(1 for term in HEDGING_TERMS if term in out)
    return round(min(hits / 3, 1.0), 3)


def contradiction_score(output: str) -> float:
    out = normalize(output)
    hits = sum(1 for term in CONTRADICTION_TERMS if term in out)
    nums = [tok for tok in tokenize(out) if tok.isdigit()]
    if len(set(nums)) >= 2:
        hits += 1
    return round(min(hits / 4, 1.0), 3)


def token_overlap(prompt: str, output: str) -> float:
    p = set(tokenize(prompt))
    o = set(tokenize(output))
    if not p or not o:
        return 0.0
    return round(len(p & o) / len(p | o), 3)


def length_ratio_drift(prompt: str, output: str) -> float:
    p = max(len(prompt), 1)
    o = len(output)
    ratio = abs(o - p) / p
    return round(min(ratio, 1.0), 3)


def compute_proxy_metrics(prompt: str, output: str, expected_keywords: list[str]) -> dict[str, Any]:
    integrity = keyword_integrity(expected_keywords, output)
    hedge = hedging_score(output)
    contradiction = contradiction_score(output)
    overlap = token_overlap(prompt, output)
    length_drift = length_ratio_drift(prompt, output)

    integrity_penalty = 1.0 - integrity
    overlap_penalty = 1.0 - overlap

    drift = (
        0.35 * integrity_penalty
        + 0.20 * hedge
        + 0.20 * contradiction
        + 0.15 * overlap_penalty
        + 0.10 * length_drift
    )
    drift = round(min(max(drift, 0.0), 1.0), 3)

    quality = (
        0.45 * integrity
        + 0.15 * (1.0 - hedge)
        + 0.15 * (1.0 - contradiction)
        + 0.15 * overlap
        + 0.10 * (1.0 - length_drift)
    )
    quality = round(min(max(quality, 0.0), 1.0), 3)

    return {
        "task_integrity": integrity,
        "hedging_score": hedge,
        "contradiction_score": contradiction,
        "token_overlap": overlap,
        "length_ratio_drift": length_drift,
        "semantic_proxy_drift": drift,
        "raw_quality_score": quality,
    }
