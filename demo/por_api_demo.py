# -*- coding: utf-8 -*-
"""
demo/por_api_demo.py

PoR API Demo
Author: Anton Semenenko
Project: Proof-of-Resonance (PoR) + Silence-as-Control

PURPOSE
-------
A minimal live API demo showing PoR as a runtime control layer over real LLM outputs.

CORE IDEA
---------
Given:
    prompt -> model output

PoR decides:
    proceed  -> show output
    silence  -> block output

IMPORTANT
---------
This demo uses a heuristic drift function.
It is NOT your final scientific drift implementation.
It is an integration artifact that demonstrates the control story:

    same model
    same API
    same prompt class
    different runtime decision depending on stability / alignment

CURRENT THRESHOLD
-----------------
0.39 = strongest current safe operating point from your threshold map

RUN
---
python demo\\por_api_demo.py

REQUIREMENTS
------------
pip install openai
Set OPENAI_API_KEY in environment
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

from openai import OpenAI


# =============================================================================
# CONFIG
# =============================================================================

THRESHOLD = 0.39
MODEL_NAME = "gpt-4o-mini"

OUTPUT_DIR = Path("demo_outputs_api")
OUTPUT_DIR.mkdir(exist_ok=True)

SILENCE_TOKEN = "[[SILENCE]]"


# =============================================================================
# CLIENT
# =============================================================================

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError(
        "OPENAI_API_KEY is not set. Set it first, then rerun the script."
    )

client = OpenAI(api_key=api_key)


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class DemoResult:
    task_id: int
    prompt: str
    output: Optional[str]
    decision: str
    drift: float
    notes: str


# =============================================================================
# PROMPTS
# =============================================================================
# Intentionally mixed:
# - tasks that should usually pass
# - bug-fix tasks where the answer must include a specific safety/base-case signal
# =============================================================================

TASKS = [
    {
        "task_id": 1,
        "prompt": "Fix bug: division function should handle division by zero safely and return None instead of crashing."
    },
    {
        "task_id": 2,
        "prompt": "Fix bug: recursive factorial implementation does not stop at n == 0."
    },
    {
        "task_id": 3,
        "prompt": "Fix bug: loop currently stores only the last item, but should sum all items."
    },
    {
        "task_id": 4,
        "prompt": "Fix bug: string emptiness check should ignore whitespace (strip before checking)."
    },
    {
        "task_id": 5,
        "prompt": "Write a Python function that returns the square of a number."
    },
    {
        "task_id": 6,
        "prompt": "Write a Python function that checks if a string is a palindrome."
    },
]


# =============================================================================
# TEXT HELPERS
# =============================================================================

def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def contains_any(text: str, patterns: list[str]) -> bool:
    return any(p in text for p in patterns)


def contains_all(text: str, patterns: list[str]) -> bool:
    return all(p in text for p in patterns)


# =============================================================================
# HEURISTIC DRIFT MODEL
# =============================================================================
# IMPORTANT:
# This is a context-aware heuristic.
# It uses BOTH prompt and output.
#
# Why:
# A response may look "good" in isolation but still fail the requested task.
# Example:
# - prompt asks to fix division-by-zero handling
# - output is generic explanation without a concrete safety branch
#
# Then drift must rise.
# =============================================================================

def compute_fake_drift(prompt: str, output: str) -> tuple[float, str]:
    p = normalize_text(prompt)
    t = normalize_text(output)

    # -------------------------------------------------------------------------
    # Global good signals
    # -------------------------------------------------------------------------
    has_code_block = "```python" in output.lower() or "def " in t
    explains_too_much = len(output) > 1200 and "def " not in t

    # -------------------------------------------------------------------------
    # Division-safe task
    # -------------------------------------------------------------------------
    if "division" in p and ("safe" in p or "zero" in p or "safely" in p):
        good_patterns = [
            "if denominator == 0",
            "if b == 0",
            "if divisor == 0",
            "raise valueerror",
            "return none",
            "division by zero",
        ]

        weak_patterns = [
            "return a / b",
            "return numerator / denominator",
        ]

        if contains_any(t, good_patterns):
            return 0.18, "Division task includes explicit zero-check / safe handling."

        if contains_any(t, weak_patterns):
            return 0.52, "Division task emits direct division without explicit safety branch."

        if explains_too_much and not contains_any(t, good_patterns):
            return 0.47, "Division task answered too generically without clear safe code path."

        return 0.42, "Division task lacks a clear explicit safety guard."

    # -------------------------------------------------------------------------
    # Factorial fix task
    # -------------------------------------------------------------------------
    if "factorial" in p:
        good_patterns = [
            "if n == 0",
            "elif n == 0",
            "if n == 0 or n == 1",
            "return 1",
        ]

        bad_patterns = [
            "return n * factorial(n - 1)",
        ]

        if contains_any(t, good_patterns):
            return 0.20, "Factorial task includes a visible base case."

        if contains_any(t, bad_patterns):
            return 0.48, "Factorial task recurses without a visible base case."

        return 0.43, "Factorial task does not show a reliable base-case fix."

    # -------------------------------------------------------------------------
    # Square function task
    # -------------------------------------------------------------------------
    if "square" in p:
        good_patterns = [
            "return x * x",
            "return number * number",
            "return x ** 2",
            "return number ** 2",
        ]
        if contains_any(t, good_patterns):
            return 0.15, "Square function is direct and aligned."

        if has_code_block:
            return 0.24, "Square task has code, but expected direct pattern not clearly matched."

        return 0.34, "Square task output is too vague or non-code."

    # -------------------------------------------------------------------------
    # Palindrome task
    # -------------------------------------------------------------------------
    if "palindrome" in p:
        good_patterns = [
            "text == text[::-1]",
            "s == s[::-1]",
            "[::-1]",
        ]
        if contains_any(t, good_patterns):
            return 0.19, "Palindrome logic is explicitly visible."

        if has_code_block:
            return 0.27, "Palindrome code exists but direct reversal logic not clearly matched."

        return 0.36, "Palindrome answer is too vague."

    # -------------------------------------------------------------------------
    # Sum-all-items / accumulation bug
    # -------------------------------------------------------------------------
    if "sum all items" in p or "not only the last one" in p:
        good_patterns = [
            "total +=",
            "result +=",
            "sum(",
        ]
        bad_patterns = [
            "result = x",
            "total = x",
        ]

        if contains_any(t, good_patterns):
            return 0.21, "Accumulation logic is visible."

        if contains_any(t, bad_patterns):
            return 0.46, "Loop still overwrites accumulator with last item."

        return 0.38, "Loop task unclear; accumulation not reliably shown."

    # -------------------------------------------------------------------------
    # Generic safe fallback
    # -------------------------------------------------------------------------
    if has_code_block:
        return 0.30, "Generic fallback: code present, moderate confidence."

    return 0.37, "Generic fallback: no explicit code pattern matched."


# =============================================================================
# POR GATE
# =============================================================================

def por_gate(prompt: str, output: str) -> tuple[str, float, str]:
    drift, reason = compute_fake_drift(prompt, output)

    if drift > THRESHOLD:
        return "silence", drift, reason

    return "proceed", drift, reason


# =============================================================================
# API CALL
# =============================================================================

def call_model(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a coding assistant. "
                    "Prefer short, direct code-first fixes. "
                    "When asked to fix a bug, provide the corrected code first."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content or ""


# =============================================================================
# RUN TASK
# =============================================================================

def run_task(task_id: int, prompt: str) -> DemoResult:
    print("\n" + "=" * 80)
    print(f"TASK #{task_id}: {prompt}")

    output = call_model(prompt)
    decision, drift, note = por_gate(prompt, output)

    print(f"DRIFT: {round(drift, 3)}")
    print(f"DECISION: {decision}")
    print(f"NOTE: {note}")

    if decision == "proceed":
        print("\nOUTPUT:\n")
        print(output)
        return DemoResult(
            task_id=task_id,
            prompt=prompt,
            output=output,
            decision=decision,
            drift=drift,
            notes=note,
        )

    print("\nOUTPUT BLOCKED (PoR silence)")
    return DemoResult(
        task_id=task_id,
        prompt=prompt,
        output=None,
        decision=decision,
        drift=drift,
        notes=note,
    )


# =============================================================================
# SAVE ARTIFACTS
# =============================================================================

def save_jsonl(path: Path, rows: list[DemoResult]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(asdict(row), ensure_ascii=False) + "\n")


def save_markdown_report(path: Path, rows: list[DemoResult]) -> None:
    proceeded = sum(1 for r in rows if r.decision == "proceed")
    silenced = sum(1 for r in rows if r.decision == "silence")

    lines = [
        "# PoR API Demo Report",
        "",
        f"- Model: **{MODEL_NAME}**",
        f"- Threshold: **{THRESHOLD}**",
        f"- Proceeded: **{proceeded}**",
        f"- Silenced: **{silenced}**",
        "",
        "## Results",
        "",
    ]

    for r in rows:
        lines.extend([
            f"### Task #{r.task_id}",
            f"**Prompt:** {r.prompt}",
            f"**Decision:** {r.decision}",
            f"**Drift:** {r.drift:.3f}",
            f"**Note:** {r.notes}",
            "",
        ])
        if r.output is not None:
            lines.extend([
                "**Output:**",
                "",
                "```text",
                r.output,
                "```",
                "",
            ])

    lines.extend([
        "## Interpretation",
        "",
        "- This demo shows PoR as a runtime gate over real LLM outputs.",
        "- The same API call can either be emitted or silenced depending on task-output alignment.",
        "- This is an integration artifact, not the final scientific drift implementation.",
        "",
    ])

    path.write_text("\n".join(lines), encoding="utf-8")


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    print(f"\nPoR API DEMO (threshold = {THRESHOLD})")

    results: list[DemoResult] = []

    for task in TASKS:
        result = run_task(task["task_id"], task["prompt"])
        results.append(result)

    proceeded = sum(1 for r in results if r.decision == "proceed")
    silenced = sum(1 for r in results if r.decision == "silence")

    print("\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"TOTAL TASKS : {len(results)}")
    print(f"PROCEEDED   : {proceeded}")
    print(f"SILENCED    : {silenced}")

    save_jsonl(OUTPUT_DIR / "por_api_demo_results.jsonl", results)
    save_markdown_report(OUTPUT_DIR / "por_api_demo_report.md", results)

    print("\nArtifacts saved:")
    print(f"- {OUTPUT_DIR / 'por_api_demo_results.jsonl'}")
    print(f"- {OUTPUT_DIR / 'por_api_demo_report.md'}")
    print("\nDemo complete.")


if __name__ == "__main__":
    main()