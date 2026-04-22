from __future__ import annotations

import re
import string
from dataclasses import dataclass
from typing import Any


def normalize_text(text: str) -> str:
    """Deterministic normalization used for default SimpleQA exact matching."""
    lowered = text.lower().strip()
    no_punct = lowered.translate(str.maketrans("", "", string.punctuation))
    squashed = re.sub(r"\s+", " ", no_punct)
    return squashed


def is_correct(answer: str, references: list[str]) -> bool:
    norm_answer = normalize_text(answer)
    if not norm_answer:
        return False
    for ref in references:
        if norm_answer == normalize_text(ref):
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
    key = f"{threshold:.2f}"
    subset = [r for r in rows if r.get("threshold_label") == key]
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
