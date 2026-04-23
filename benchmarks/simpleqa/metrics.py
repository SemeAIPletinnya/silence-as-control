from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any

_SUBSUPER_TRANSLATION = str.maketrans(
    {
        "₀": "0",
        "₁": "1",
        "₂": "2",
        "₃": "3",
        "₄": "4",
        "₅": "5",
        "₆": "6",
        "₇": "7",
        "₈": "8",
        "₉": "9",
        "⁰": "0",
        "¹": "1",
        "²": "2",
        "³": "3",
        "⁴": "4",
        "⁵": "5",
        "⁶": "6",
        "⁷": "7",
        "⁸": "8",
        "⁹": "9",
        "⁺": "+",
        "⁻": "-",
        "₊": "+",
        "₋": "-",
    }
)

_DEGREE_CELSIUS_PATTERN = re.compile(
    r"(-?\d+(?:\.\d+)?)\s*(?:°\s*c|degrees?\s*celsius|degree\s*celsius|celsius)\b",
    flags=re.IGNORECASE,
)
_NON_ALNUM_PATTERN = re.compile(r"[^a-z0-9]+")
_MULTISPACE_PATTERN = re.compile(r"\s+")
_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def normalize_text(text: str) -> str:
    """Deterministic normalization used for default SimpleQA exact matching."""
    normalized = unicodedata.normalize("NFKC", text).translate(_SUBSUPER_TRANSLATION).lower()
    normalized = _DEGREE_CELSIUS_PATTERN.sub(r"\1 celsius", normalized)
    normalized = _NON_ALNUM_PATTERN.sub(" ", normalized)
    return _MULTISPACE_PATTERN.sub(" ", normalized).strip()


def _token_set(text: str) -> set[str]:
    return set(_TOKEN_PATTERN.findall(text))


def _is_short_token_reference(norm_ref: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9]{1,3}", norm_ref))


def is_correct(answer: str, references: list[str]) -> bool:
    norm_answer = normalize_text(answer)
    if not norm_answer:
        return False
    answer_tokens = _token_set(norm_answer)

    for ref in references:
        norm_ref = normalize_text(ref)
        if not norm_ref:
            continue
        if ("celsius" in norm_ref) != ("celsius" in norm_answer):
            continue

        if norm_answer == norm_ref:
            return True
        if _is_short_token_reference(norm_ref):
            if norm_ref in answer_tokens:
                return True
            continue
        if norm_ref in norm_answer:
            return True
        if norm_answer in norm_ref:
            return True

    return False


@dataclass(frozen=True)
class BaselineMetrics:
    total_examples: int
    answered_count: int
    correctness_rate: float
    error_rate: float


@dataclass(frozen=True)
class ThresholdMetrics:
    threshold: float
    total_examples: int
    answered_count: int
    silence_count: int
    answer_rate: float
    silence_rate: float
    accepted_correct_count: int
    accepted_wrong_count: int
    accepted_precision: float
    accepted_error_rate: float
    false_silence_count: int
    false_silence_rate: float


def _safe_div(num: int, denom: int) -> float:
    if denom == 0:
        return 0.0
    return num / denom


def compute_baseline_metrics(rows: list[dict[str, Any]]) -> BaselineMetrics:
    baseline_rows = [r for r in rows if r["threshold_label"] == "baseline"]
    total = len(baseline_rows)
    answered = sum(1 for r in baseline_rows if not r.get("silence_flag", False))
    correct = sum(1 for r in baseline_rows if r.get("correctness_label") == "correct")

    correctness_rate = _safe_div(correct, total)
    error_rate = 1.0 - correctness_rate if total > 0 else 0.0
    return BaselineMetrics(
        total_examples=total,
        answered_count=answered,
        correctness_rate=correctness_rate,
        error_rate=error_rate,
    )


def compute_threshold_metrics(rows: list[dict[str, Any]], threshold: float) -> ThresholdMetrics:
    subset = [r for r in rows if r.get("threshold_value") == threshold]
    total = len(subset)
    answered = sum(1 for r in subset if not r.get("silence_flag", False))
    silence = total - answered
    accepted_correct = sum(
        1
        for r in subset
        if (not r.get("silence_flag", False)) and r.get("correctness_label") == "correct"
    )
    accepted_wrong = sum(
        1
        for r in subset
        if (not r.get("silence_flag", False)) and r.get("correctness_label") == "wrong"
    )
    false_silence = sum(1 for r in subset if r.get("false_silence_flag", False))

    return ThresholdMetrics(
        threshold=threshold,
        total_examples=total,
        answered_count=answered,
        silence_count=silence,
        answer_rate=_safe_div(answered, total),
        silence_rate=_safe_div(silence, total),
        accepted_correct_count=accepted_correct,
        accepted_wrong_count=accepted_wrong,
        accepted_precision=_safe_div(accepted_correct, answered),
        accepted_error_rate=_safe_div(accepted_wrong, answered),
        false_silence_count=false_silence,
        false_silence_rate=_safe_div(false_silence, total),
    )
