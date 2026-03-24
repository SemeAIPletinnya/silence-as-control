# -*- coding: utf-8 -*-
"""
por_agent_demo.py

PoR-gated integration demo
Author: Anton Semenenko
Project: Proof-of-Resonance (PoR) + Silence-as-Control

PURPOSE
-------
A minimal integration demo that shows the difference between:
1. Baseline mode  -> always emits a suggestion
2. PoR mode       -> emits only if runtime state appears stable

This is NOT meant to be a full production system.
It is a clean demonstration artifact for the transition:
proof -> system behavior -> integration story

CORE IDEA
---------
Baseline:
    model always returns a suggestion

PoR:
    model returns a suggestion only if:
        drift <= threshold
    otherwise:
        return SILENCE

DEMO MESSAGE
------------
Baseline may confidently emit bad outputs.
PoR either emits a safe/accepted output or abstains.

CURRENT THRESHOLD
-----------------
0.39 = strongest current safe operating point (based on current project state)

USAGE
-----
python por_agent_demo.py

OPTIONAL
--------
You can later replace the toy model backend with:
- OpenAI API
- local LLM
- your real drift function
- your current eval logic
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import json
import math
import statistics
from pathlib import Path


# =============================================================================
# CONFIG
# =============================================================================

POR_THRESHOLD = 0.39
OUTPUT_DIR = Path("demo_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

SILENCE_TOKEN = "[[SILENCE]]"


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class DemoTask:
    task_id: int
    prompt: str
    expected_keywords: List[str]
    simulated_baseline_output: str
    simulated_drift: float
    simulated_quality: float


@dataclass
class EngineResult:
    mode: str
    task_id: int
    prompt: str
    output: Optional[str]
    decision: str
    drift: float
    quality: float
    accepted: bool
    matched_keywords: int
    expected_keywords_total: int
    notes: str


# =============================================================================
# DEMO TASKS
# =============================================================================
# IMPORTANT:
# These are controlled demo tasks.
# We intentionally include:
# - stable / good examples
# - borderline examples
# - clearly unstable examples
#
# The point is to show system behavior, not benchmark leaderboard behavior.
# =============================================================================

DEMO_TASKS: List[DemoTask] = [
    DemoTask(
        task_id=1,
        prompt="Write a Python function that returns the square of a number x.",
        expected_keywords=["def", "return", "x", "x * x"],
        simulated_baseline_output=(
            "def square(x):\n"
            "    return x * x\n"
        ),
        simulated_drift=0.18,
        simulated_quality=0.95,
    ),
    DemoTask(
        task_id=2,
        prompt="Fix this Python bug: function should return True if n is even.",
        expected_keywords=["def", "%", "==", "0", "return"],
        simulated_baseline_output=(
            "def is_even(n):\n"
            "    return n % 2 == 0\n"
        ),
        simulated_drift=0.24,
        simulated_quality=0.94,
    ),
    DemoTask(
        task_id=3,
        prompt="Write a Python function that sums all numbers in a list.",
        expected_keywords=["def", "return", "sum", "numbers"],
        simulated_baseline_output=(
            "def sum_list(numbers):\n"
            "    return sum(numbers)\n"
        ),
        simulated_drift=0.22,
        simulated_quality=0.93,
    ),
    DemoTask(
        task_id=4,
        prompt="Fix the bug: division function should handle division by zero safely.",
        expected_keywords=["def", "if", "0", "raise", "return"],
        simulated_baseline_output=(
            "def divide(a, b):\n"
            "    return a / b\n"
        ),
        simulated_drift=0.46,
        simulated_quality=0.41,
    ),
    DemoTask(
        task_id=5,
        prompt="Write a Python function that reverses a string.",
        expected_keywords=["def", "return", "[::-1]", "text"],
        simulated_baseline_output=(
            "def reverse_string(text):\n"
            "    return text[::-1]\n"
        ),
        simulated_drift=0.19,
        simulated_quality=0.96,
    ),
    DemoTask(
        task_id=6,
        prompt="Fix the bug: recursive factorial should stop at n == 0.",
        expected_keywords=["def", "if", "n == 0", "return 1", "return n *"],
        simulated_baseline_output=(
            "def factorial(n):\n"
            "    return n * factorial(n - 1)\n"
        ),
        simulated_drift=0.44,
        simulated_quality=0.38,
    ),
    DemoTask(
        task_id=7,
        prompt="Write a Python function that checks whether a string is a palindrome.",
        expected_keywords=["def", "return", "text", "[::-1]", "=="],
        simulated_baseline_output=(
            "def is_palindrome(text):\n"
            "    return text == text[::-1]\n"
        ),
        simulated_drift=0.26,
        simulated_quality=0.91,
    ),
    DemoTask(
        task_id=8,
        prompt="Fix the bug: loop should sum all items, not only the last one.",
        expected_keywords=["def", "total", "+=", "for", "return"],
        simulated_baseline_output=(
            "def total(items):\n"
            "    result = 0\n"
            "    for x in items:\n"
            "        result = x\n"
            "    return result\n"
        ),
        simulated_drift=0.43,
        simulated_quality=0.35,
    ),
    DemoTask(
        task_id=9,
        prompt="Write a Python function that returns the maximum value in a list.",
        expected_keywords=["def", "return", "max", "values"],
        simulated_baseline_output=(
            "def max_value(values):\n"
            "    return max(values)\n"
        ),
        simulated_drift=0.21,
        simulated_quality=0.95,
    ),
    DemoTask(
        task_id=10,
        prompt="Fix this bug: function should strip whitespace before checking emptiness.",
        expected_keywords=["def", "strip", "return", "==", '""'],
        simulated_baseline_output=(
            "def is_empty(text):\n"
            "    return text == ''\n"
        ),
        simulated_drift=0.41,
        simulated_quality=0.48,
    ),
    DemoTask(
        task_id=11,
        prompt="Write a Python function that counts words in a sentence.",
        expected_keywords=["def", "split", "return", "len", "sentence"],
        simulated_baseline_output=(
            "def count_words(sentence):\n"
            "    return len(sentence.split())\n"
        ),
        simulated_drift=0.27,
        simulated_quality=0.90,
    ),
    DemoTask(
        task_id=12,
        prompt="Fix bug: function should append items to a list, not overwrite it.",
        expected_keywords=["def", "append", "for", "return", "result"],
        simulated_baseline_output=(
            "def collect(items):\n"
            "    result = []\n"
            "    for x in items:\n"
            "        result = x\n"
            "    return result\n"
        ),
        simulated_drift=0.45,
        simulated_quality=0.34,
    ),
]


# =============================================================================
# HELPERS
# =============================================================================

def normalize_text(text: str) -> str:
    return " ".join(text.lower().strip().split())


def count_keyword_matches(output: str, expected_keywords: List[str]) -> int:
    normalized_output = normalize_text(output)
    matches = 0
    for kw in expected_keywords:
        if normalize_text(kw) in normalized_output:
            matches += 1
    return matches


def evaluate_acceptance(output: str, expected_keywords: List[str]) -> Dict[str, int | bool]:
    matched = count_keyword_matches(output, expected_keywords)
    total = len(expected_keywords)

    # Simple demo rule:
    # accepted if at least 60% of expected keywords are present
    accepted = matched >= math.ceil(total * 0.60)

    return {
        "matched_keywords": matched,
        "expected_keywords_total": total,
        "accepted": accepted,
    }


def pretty_float(value: float) -> str:
    return f"{value:.3f}"


# =============================================================================
# BACKENDS
# =============================================================================

class BaselineEngine:
    """
    Baseline engine:
    always emits the model draft
    """

    def run(self, task: DemoTask) -> EngineResult:
        output = task.simulated_baseline_output
        eval_result = evaluate_acceptance(output, task.expected_keywords)

        return EngineResult(
            mode="baseline",
            task_id=task.task_id,
            prompt=task.prompt,
            output=output,
            decision="proceed",
            drift=task.simulated_drift,
            quality=task.simulated_quality,
            accepted=bool(eval_result["accepted"]),
            matched_keywords=int(eval_result["matched_keywords"]),
            expected_keywords_total=int(eval_result["expected_keywords_total"]),
            notes="Baseline always emits suggestion.",
        )


class PoREngine:
    """
    PoR-gated engine:
    emits output only if drift <= threshold
    otherwise emits SILENCE
    """

    def __init__(self, threshold: float):
        self.threshold = threshold

    def run(self, task: DemoTask) -> EngineResult:
        output = task.simulated_baseline_output
        drift = task.simulated_drift
        quality = task.simulated_quality

        if drift > self.threshold:
            return EngineResult(
                mode="por",
                task_id=task.task_id,
                prompt=task.prompt,
                output=None,
                decision="silence",
                drift=drift,
                quality=quality,
                accepted=False,
                matched_keywords=0,
                expected_keywords_total=len(task.expected_keywords),
                notes=(
                    f"Silenced because drift={pretty_float(drift)} "
                    f"> threshold={pretty_float(self.threshold)}"
                ),
            )

        eval_result = evaluate_acceptance(output, task.expected_keywords)

        return EngineResult(
            mode="por",
            task_id=task.task_id,
            prompt=task.prompt,
            output=output,
            decision="proceed",
            drift=drift,
            quality=quality,
            accepted=bool(eval_result["accepted"]),
            matched_keywords=int(eval_result["matched_keywords"]),
            expected_keywords_total=int(eval_result["expected_keywords_total"]),
            notes=(
                f"Allowed because drift={pretty_float(drift)} "
                f"<= threshold={pretty_float(self.threshold)}"
            ),
        )


# =============================================================================
# ANALYSIS
# =============================================================================

def summarize_results(results: List[EngineResult]) -> Dict[str, float | int]:
    total = len(results)
    proceeded = sum(1 for r in results if r.decision == "proceed")
    silenced = sum(1 for r in results if r.decision == "silence")
    accepted = sum(1 for r in results if r.accepted)
    rejected_after_emit = sum(
        1 for r in results
        if r.decision == "proceed" and not r.accepted
    )

    drift_values = [r.drift for r in results]
    quality_values = [r.quality for r in results]
    accepted_drifts = [r.drift for r in results if r.accepted]
    silenced_drifts = [r.drift for r in results if r.decision == "silence"]

    summary = {
        "total_tasks": total,
        "proceeded": proceeded,
        "silenced": silenced,
        "accepted": accepted,
        "rejected_after_emit": rejected_after_emit,
        "coverage_pct": round((proceeded / total) * 100, 2),
        "silence_rate_pct": round((silenced / total) * 100, 2),
        "accepted_rate_pct": round((accepted / total) * 100, 2),
        "avg_drift_all": round(statistics.mean(drift_values), 3),
        "avg_quality_all": round(statistics.mean(quality_values), 3),
        "avg_drift_accepted": round(statistics.mean(accepted_drifts), 3) if accepted_drifts else None,
        "avg_drift_silenced": round(statistics.mean(silenced_drifts), 3) if silenced_drifts else None,
    }
    return summary


def print_results_table(baseline_results: List[EngineResult], por_results: List[EngineResult]) -> None:
    print("=" * 120)
    print("PoR-GATED CODE SUGGESTION DEMO")
    print("=" * 120)
    print(f"PoR threshold: {POR_THRESHOLD}")
    print()

    header = (
        f"{'ID':<4}"
        f"{'BASE_DEC':<12}"
        f"{'BASE_ACC':<10}"
        f"{'BASE_DRIFT':<12}"
        f"{'POR_DEC':<12}"
        f"{'POR_ACC':<10}"
        f"{'POR_DRIFT':<12}"
        f"{'TASK':<48}"
    )
    print(header)
    print("-" * 120)

    for b, p in zip(baseline_results, por_results):
        task_preview = b.prompt[:45] + "..." if len(b.prompt) > 45 else b.prompt
        row = (
            f"{b.task_id:<4}"
            f"{b.decision:<12}"
            f"{str(b.accepted):<10}"
            f"{pretty_float(b.drift):<12}"
            f"{p.decision:<12}"
            f"{str(p.accepted):<10}"
            f"{pretty_float(p.drift):<12}"
            f"{task_preview:<48}"
        )
        print(row)

    print("-" * 120)
    print()


def print_summary(name: str, summary: Dict[str, float | int]) -> None:
    print(f"{name.upper()} SUMMARY")
    print("-" * 60)
    for k, v in summary.items():
        print(f"{k:<24}: {v}")
    print()


def print_key_examples(baseline_results: List[EngineResult], por_results: List[EngineResult]) -> None:
    print("KEY EXAMPLES")
    print("-" * 60)

    for b, p in zip(baseline_results, por_results):
        # baseline emitted bad output, PoR silenced it
        if b.decision == "proceed" and not b.accepted and p.decision == "silence":
            print(f"[TASK {b.task_id}] BASELINE FAIL -> POR SILENCE")
            print(f"Prompt: {b.prompt}")
            print(f"Baseline drift: {pretty_float(b.drift)}")
            print("Baseline output:")
            print(b.output)
            print(f"PoR decision: {p.decision}")
            print(f"PoR note: {p.notes}")
            print("-" * 60)

    print()


# =============================================================================
# SAVE ARTIFACTS
# =============================================================================

def save_jsonl(path: Path, rows: List[EngineResult]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(asdict(row), ensure_ascii=False) + "\n")


def save_markdown_report(
    path: Path,
    baseline_summary: Dict[str, float | int],
    por_summary: Dict[str, float | int],
) -> None:
    content = f"""# PoR-Gated Code Suggestion Demo

## Threshold
- PoR threshold: **{POR_THRESHOLD}**

## Demo message
Baseline may confidently emit bad suggestions.
PoR either emits an accepted suggestion or abstains.

## Baseline summary
- Total tasks: {baseline_summary['total_tasks']}
- Proceeded: {baseline_summary['proceeded']}
- Silenced: {baseline_summary['silenced']}
- Accepted: {baseline_summary['accepted']}
- Rejected after emit: {baseline_summary['rejected_after_emit']}
- Coverage: {baseline_summary['coverage_pct']}%
- Silence rate: {baseline_summary['silence_rate_pct']}%
- Accepted rate: {baseline_summary['accepted_rate_pct']}%
- Avg drift (all): {baseline_summary['avg_drift_all']}
- Avg quality (all): {baseline_summary['avg_quality_all']}

## PoR summary
- Total tasks: {por_summary['total_tasks']}
- Proceeded: {por_summary['proceeded']}
- Silenced: {por_summary['silenced']}
- Accepted: {por_summary['accepted']}
- Rejected after emit: {por_summary['rejected_after_emit']}
- Coverage: {por_summary['coverage_pct']}%
- Silence rate: {por_summary['silence_rate_pct']}%
- Accepted rate: {por_summary['accepted_rate_pct']}%
- Avg drift (all): {por_summary['avg_drift_all']}
- Avg quality (all): {por_summary['avg_quality_all']}
- Avg drift (accepted): {por_summary['avg_drift_accepted']}
- Avg drift (silenced): {por_summary['avg_drift_silenced']}

## Interpretation
- Baseline always emits a suggestion.
- PoR suppresses outputs when drift exceeds the threshold.
- This demonstrates Silence-as-Control as a runtime gate.
- Threshold {POR_THRESHOLD} is used as the current strongest safe operating point.

## Product framing
- Baseline = uncontrolled emission
- PoR = controlled emission
- Either correct, or silent
"""
    path.write_text(content, encoding="utf-8")


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    baseline = BaselineEngine()
    por = PoREngine(threshold=POR_THRESHOLD)

    baseline_results = [baseline.run(task) for task in DEMO_TASKS]
    por_results = [por.run(task) for task in DEMO_TASKS]

    baseline_summary = summarize_results(baseline_results)
    por_summary = summarize_results(por_results)

    print_results_table(baseline_results, por_results)
    print_summary("baseline", baseline_summary)
    print_summary("por", por_summary)
    print_key_examples(baseline_results, por_results)

    save_jsonl(OUTPUT_DIR / "baseline_demo_results.jsonl", baseline_results)
    save_jsonl(OUTPUT_DIR / "por_demo_results.jsonl", por_results)
    save_markdown_report(
        OUTPUT_DIR / "por_agent_demo_report.md",
        baseline_summary,
        por_summary,
    )

    print("Artifacts saved:")
    print(f"- {OUTPUT_DIR / 'baseline_demo_results.jsonl'}")
    print(f"- {OUTPUT_DIR / 'por_demo_results.jsonl'}")
    print(f"- {OUTPUT_DIR / 'por_agent_demo_report.md'}")
    print()
    print("Demo complete.")


if __name__ == "__main__":
    main()