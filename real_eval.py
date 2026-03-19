#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PoR / Silence-as-Control
Real Eval Harness v0.1
Author-facing experimental script

PURPOSE
-------
This script is a more thorough next-step evaluation harness for your
"Silence-as-Control" / "PoR" experiments.

It is designed to move beyond:
    - pure random drift simulation
    - tiny 5-task toy evals
and toward:
    - a larger controlled eval suite
    - gray-zone cases
    - reproducible metrics
    - explicit coverage vs reliability trade-off analysis

CORE IDEA
---------
We want to test whether a control layer that can abstain ("silence")
helps filter unstable outputs.

Instead of pretending we already have a perfect semantic-drift model,
this harness uses a multi-signal proxy layer:

Signals:
    1. task_integrity         -> did the answer retain required content?
    2. contradiction_score    -> does the answer self-undermine?
    3. hedging_score          -> "maybe", "not sure", etc.
    4. token_overlap          -> cheap lexical alignment proxy
    5. length_ratio_drift     -> output length divergence
    6. semantic_proxy_drift   -> weighted drift proxy from several heuristics

Then it computes:
    - raw_success                : did the answer appear acceptable without control?
    - silence                    : should control abstain?
    - no_control_success         : baseline system outcome
    - with_control_success       : controlled system outcome
    - accepted_output_quality    : quality among only accepted outputs
    - coverage                   : fraction of outputs not silenced
    - risk_reduction             : bad outputs removed by silence

IMPORTANT
---------
This is still a proxy harness.
It is not claiming "scientific ground truth".
It is a structured bridge from:
    idea -> controlled evaluation -> measurable product signal.

USAGE
-----
1) Save as:
       real_eval_harness.py

2) Run:
       python real_eval_harness.py

3) Optional args:
       python real_eval_harness.py --silence-threshold 0.28 --raw-success-threshold 0.55

4) Outputs:
       logs/real_eval_results.jsonl
       logs/real_eval_summary.json
       logs/real_eval_results.csv

NEXT STEP AFTER THIS
--------------------
After this harness works, replace the "simulated_output" field with
real model outputs gathered from actual API/model runs.

Then the same evaluation skeleton can be reused.

"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


# ============================================================================
# PATHS / IO
# ============================================================================

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

JSONL_FILE = LOG_DIR / "real_eval_results.jsonl"
CSV_FILE = LOG_DIR / "real_eval_results.csv"
SUMMARY_FILE = LOG_DIR / "real_eval_summary.json"


# ============================================================================
# CONFIG / THRESHOLDS
# ============================================================================

DEFAULT_SILENCE_THRESHOLD = 0.28
DEFAULT_RAW_SUCCESS_THRESHOLD = 0.55

# The logic here is intentionally separate:
# - raw_success_threshold defines whether output is "acceptable" without control
# - silence_threshold defines when control abstains
#
# This lets you create an intermediate region where output could count as raw
# success but still be filtered by control, making the trade-off measurable.


# ============================================================================
# DATA MODEL
# ============================================================================

@dataclass
class EvalTask:
    task_id: str
    category: str
    prompt: str
    expected_keywords: List[str]
    simulated_output: str
    notes: str = ""


@dataclass
class EvalSignals:
    task_integrity: float
    contradiction_score: float
    hedging_score: float
    token_overlap: float
    length_ratio_drift: float
    semantic_proxy_drift: float
    raw_quality_score: float


@dataclass
class EvalResult:
    task_id: str
    category: str
    prompt: str
    output: str
    expected_keywords: List[str]
    notes: str

    # signals
    task_integrity: float
    contradiction_score: float
    hedging_score: float
    token_overlap: float
    length_ratio_drift: float
    semantic_proxy_drift: float
    raw_quality_score: float

    # control logic
    raw_success: bool
    silence: bool
    no_control_success: bool
    with_control_success: bool

    # thresholds
    silence_threshold: float
    raw_success_threshold: float


# ============================================================================
# TASK SUITE
# ============================================================================
# Mix:
# - good answers
# - obvious fails
# - gray-zone unstable answers
# - hedged/self-contradicting outputs
# - verbose drift-heavy outputs
#
# This is what will make the harness actually useful.

TASKS: List[EvalTask] = [
    EvalTask(
        task_id="math_001",
        category="math",
        prompt="What is 12 + 15? Give the answer and one short explanation.",
        expected_keywords=["27"],
        simulated_output="12 + 15 = 27. Adding the numbers gives a total of 27.",
        notes="clean success"
    ),
    EvalTask(
        task_id="math_002",
        category="math",
        prompt="What is 9 * 8? Then explain briefly.",
        expected_keywords=["72"],
        simulated_output="9 * 8 is maybe 65 or 72, not fully sure.",
        notes="gray-zone hedged wrong/uncertain math"
    ),
    EvalTask(
        task_id="geo_001",
        category="geography",
        prompt="What is the capital of France? Then give one short fact.",
        expected_keywords=["paris"],
        simulated_output="Paris is the capital of France. It is famous for the Eiffel Tower.",
        notes="clean success"
    ),
    EvalTask(
        task_id="geo_002",
        category="geography",
        prompt="Name the largest planet in the Solar System.",
        expected_keywords=["jupiter"],
        simulated_output="The largest planet is probably Saturn, though Jupiter is also very large.",
        notes="contradictory / gray-zone"
    ),
    EvalTask(
        task_id="science_001",
        category="science",
        prompt="Summarize: Water boils at 100C at sea level.",
        expected_keywords=["100", "boils"],
        simulated_output="At sea level, water boils at 100C.",
        notes="clean success"
    ),
    EvalTask(
        task_id="science_002",
        category="science",
        prompt="Summarize: Water boils at 100C at sea level.",
        expected_keywords=["100", "boils"],
        simulated_output="Water boils maybe at 90 or 120 depending on mood and environment.",
        notes="unstable / incorrect / hedged"
    ),
    EvalTask(
        task_id="reasoning_001",
        category="reasoning",
        prompt="A is larger than B. B is larger than C. Which is largest?",
        expected_keywords=["a"],
        simulated_output="A is the largest because A > B and B > C.",
        notes="clean reasoning"
    ),
    EvalTask(
        task_id="reasoning_002",
        category="reasoning",
        prompt="A is larger than B. B is larger than C. Which is largest?",
        expected_keywords=["a"],
        simulated_output="C might be largest if the ordering changes, but A was mentioned first.",
        notes="trajectory loss / contradiction"
    ),
    EvalTask(
        task_id="summary_001",
        category="summarization",
        prompt="Summarize this statement: The server failed because the disk was full.",
        expected_keywords=["disk", "full"],
        simulated_output="The server failed because the disk was full.",
        notes="clean summary"
    ),
    EvalTask(
        task_id="summary_002",
        category="summarization",
        prompt="Summarize this statement: The server failed because the disk was full.",
        expected_keywords=["disk", "full"],
        simulated_output="The server had an issue, maybe memory or networking, not completely sure.",
        notes="off-target summary"
    ),
    EvalTask(
        task_id="policy_001",
        category="instruction_following",
        prompt="Reply with exactly one word: approved",
        expected_keywords=["approved"],
        simulated_output="approved",
        notes="clean exact-follow"
    ),
    EvalTask(
        task_id="policy_002",
        category="instruction_following",
        prompt="Reply with exactly one word: approved",
        expected_keywords=["approved"],
        simulated_output="approved, although there could be some caveats worth discussing in more depth.",
        notes="instruction drift despite containing keyword"
    ),
    EvalTask(
        task_id="code_001",
        category="code_reasoning",
        prompt="What does `len([1,2,3])` return?",
        expected_keywords=["3"],
        simulated_output="It returns 3 because the list has three elements.",
        notes="clean code explanation"
    ),
    EvalTask(
        task_id="code_002",
        category="code_reasoning",
        prompt="What does `len([1,2,3])` return?",
        expected_keywords=["3"],
        simulated_output="It returns 2 or 3 depending on indexing, so probably 2.",
        notes="incorrect/confused"
    ),
    EvalTask(
        task_id="open_001",
        category="open_reasoning",
        prompt="Briefly explain why backups matter for production systems.",
        expected_keywords=["backup", "data"],
        simulated_output="Backups matter because they protect data and help recovery after failures.",
        notes="clean open reasoning"
    ),
    EvalTask(
        task_id="open_002",
        category="open_reasoning",
        prompt="Briefly explain why backups matter for production systems.",
        expected_keywords=["backup", "data"],
        simulated_output="Production systems need many things. Some are fast, some are slow. "
                         "Backups might matter, but maybe not if nothing important exists. "
                         "It depends and I am not fully sure what data means in this context.",
        notes="hedged / rambling / partially aligned"
    ),
    EvalTask(
        task_id="chain_001",
        category="multi_step_style",
        prompt="Step 1: say the answer to 5+5. Step 2: restate it in words.",
        expected_keywords=["10", "ten"],
        simulated_output="10. In words, ten.",
        notes="clean 2-step"
    ),
    EvalTask(
        task_id="chain_002",
        category="multi_step_style",
        prompt="Step 1: say the answer to 5+5. Step 2: restate it in words.",
        expected_keywords=["10", "ten"],
        simulated_output="10. In words, maybe eleven or ten depending on interpretation.",
        notes="local correctness masking global instability"
    ),
]


# ============================================================================
# TEXT UTILITIES
# ============================================================================

HEDGING_TERMS = {
    "maybe",
    "probably",
    "not sure",
    "unclear",
    "might",
    "could be",
    "possibly",
    "i think",
    "perhaps",
    "depending",
}

CONTRADICTION_PATTERNS = {
    "or",
    "not sure",
    "though",
    "however",
    "but",
    "depends",
    "maybe",
}


def normalize_text(text: str) -> str:
    return " ".join(text.strip().lower().split())


def tokenize(text: str) -> List[str]:
    # intentionally simple tokenization
    cleaned = (
        normalize_text(text)
        .replace(".", " ")
        .replace(",", " ")
        .replace(":", " ")
        .replace(";", " ")
        .replace("(", " ")
        .replace(")", " ")
        .replace("`", " ")
        .replace(">", " ")
        .replace("<", " ")
        .replace("=", " ")
        .replace("?", " ")
        .replace("!", " ")
        .replace("/", " ")
        .replace("\\", " ")
        .replace("-", " ")
        .replace("_", " ")
    )
    return [t for t in cleaned.split() if t]


def jaccard_overlap(a: Iterable[str], b: Iterable[str]) -> float:
    sa = set(a)
    sb = set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    inter = sa & sb
    union = sa | sb
    return round(len(inter) / len(union), 3)


def keyword_integrity(expected_keywords: List[str], output: str) -> float:
    """
    Fraction of expected keywords present.
    """
    out = normalize_text(output)
    hits = 0
    for kw in expected_keywords:
        if kw.lower() in out:
            hits += 1
    if not expected_keywords:
        return 1.0
    return round(hits / len(expected_keywords), 3)


def hedging_score(output: str) -> float:
    """
    Higher = more hedging / uncertainty.
    """
    out = normalize_text(output)
    hits = 0
    for phrase in HEDGING_TERMS:
        if phrase in out:
            hits += 1
    # cap around 1.0
    return round(min(hits / 3, 1.0), 3)


def contradiction_score(output: str) -> float:
    """
    Crude contradiction / self-undermining proxy.
    Higher = more likely unstable or self-contradictory.
    """
    out = normalize_text(output)
    hits = 0
    for pattern in CONTRADICTION_PATTERNS:
        if pattern in out:
            hits += 1

    # If there are multiple numeric alternatives ("2 or 3", "90 or 120") that is suspicious.
    numeric_tokens = [tok for tok in tokenize(out) if tok.isdigit()]
    if len(set(numeric_tokens)) >= 2:
        hits += 1

    return round(min(hits / 4, 1.0), 3)


def length_ratio_drift(prompt: str, output: str) -> float:
    """
    Cheap drift proxy:
    if output length diverges heavily from prompt length, score increases.
    """
    p = max(len(prompt), 1)
    o = len(output)
    ratio = abs(o - p) / p
    return round(min(ratio, 1.0), 3)


def task_integrity_penalty(task_integrity_value: float) -> float:
    """
    Penalty inverse of integrity.
    """
    return round(1.0 - task_integrity_value, 3)


def semantic_proxy_drift(
    prompt: str,
    output: str,
    expected_keywords: List[str],
) -> Tuple[float, float, float, float, float, float, float]:
    """
    Build a multi-signal proxy drift score.

    Components:
        - task_integrity
        - contradiction_score
        - hedging_score
        - token_overlap
        - length_ratio_drift

    Final idea:
        drift should rise when:
            - integrity falls
            - contradiction rises
            - hedging rises
            - token overlap falls too much
            - length divergence grows
    """
    prompt_tokens = tokenize(prompt)
    output_tokens = tokenize(output)

    integ = keyword_integrity(expected_keywords, output)              # higher better
    contra = contradiction_score(output)                             # higher worse
    hedge = hedging_score(output)                                    # higher worse
    overlap = jaccard_overlap(prompt_tokens, output_tokens)          # higher maybe better-ish
    len_drift = length_ratio_drift(prompt, output)                   # higher worse

    integ_penalty = task_integrity_penalty(integ)
    overlap_penalty = round(1.0 - overlap, 3)

    # weighted proxy drift
    drift = (
        0.32 * integ_penalty
        + 0.22 * contra
        + 0.16 * hedge
        + 0.15 * overlap_penalty
        + 0.15 * len_drift
    )
    drift = round(min(max(drift, 0.0), 1.0), 3)

    # quality score: high is better
    quality = (
        0.40 * integ
        + 0.20 * (1.0 - contra)
        + 0.15 * (1.0 - hedge)
        + 0.15 * overlap
        + 0.10 * (1.0 - len_drift)
    )
    quality = round(min(max(quality, 0.0), 1.0), 3)

    return integ, contra, hedge, overlap, len_drift, drift, quality


# ============================================================================
# CONTROL LOGIC
# ============================================================================

def evaluate_raw_success(raw_quality_score: float, threshold: float) -> bool:
    return raw_quality_score >= threshold


def evaluate_silence(drift: float, threshold: float) -> bool:
    return drift >= threshold


# ============================================================================
# HARNESS CORE
# ============================================================================

def evaluate_task(
    task: EvalTask,
    raw_success_threshold: float,
    silence_threshold: float,
) -> EvalResult:
    integ, contra, hedge, overlap, len_drift, drift, quality = semantic_proxy_drift(
        prompt=task.prompt,
        output=task.simulated_output,
        expected_keywords=task.expected_keywords,
    )

    raw_success = evaluate_raw_success(quality, raw_success_threshold)
    silence = evaluate_silence(drift, silence_threshold)

    no_control_success = raw_success
    with_control_success = raw_success if not silence else False

    return EvalResult(
        task_id=task.task_id,
        category=task.category,
        prompt=task.prompt,
        output=task.simulated_output,
        expected_keywords=task.expected_keywords,
        notes=task.notes,

        task_integrity=integ,
        contradiction_score=contra,
        hedging_score=hedge,
        token_overlap=overlap,
        length_ratio_drift=len_drift,
        semantic_proxy_drift=drift,
        raw_quality_score=quality,

        raw_success=raw_success,
        silence=silence,
        no_control_success=no_control_success,
        with_control_success=with_control_success,

        silence_threshold=silence_threshold,
        raw_success_threshold=raw_success_threshold,
    )


def run_harness(
    tasks: List[EvalTask],
    raw_success_threshold: float,
    silence_threshold: float,
) -> List[EvalResult]:
    return [
        evaluate_task(
            task=t,
            raw_success_threshold=raw_success_threshold,
            silence_threshold=silence_threshold,
        )
        for t in tasks
    ]


# ============================================================================
# ANALYTICS
# ============================================================================

def avg(values: List[float]) -> float:
    return round(sum(values) / len(values), 3) if values else 0.0


def pct(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


def median(values: List[float]) -> float:
    return round(statistics.median(values), 3) if values else 0.0


def stdev(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    return round(statistics.pstdev(values), 3)


def summarize_results(results: List[EvalResult]) -> Dict[str, Any]:
    total = len(results)

    silenced = [r for r in results if r.silence]
    accepted = [r for r in results if not r.silence]

    raw_successes = [r for r in results if r.raw_success]
    raw_failures = [r for r in results if not r.raw_success]

    with_control_successes = [r for r in results if r.with_control_success]
    with_control_failures = [r for r in results if not r.with_control_success]

    silenced_raw_success = [r for r in results if r.silence and r.raw_success]
    silenced_raw_fail = [r for r in results if r.silence and not r.raw_success]

    accepted_raw_success = [r for r in results if (not r.silence) and r.raw_success]
    accepted_raw_fail = [r for r in results if (not r.silence) and not r.raw_success]

    drift_all = [r.semantic_proxy_drift for r in results]
    drift_raw_success = [r.semantic_proxy_drift for r in raw_successes]
    drift_raw_fail = [r.semantic_proxy_drift for r in raw_failures]
    drift_accepted = [r.semantic_proxy_drift for r in accepted]
    drift_silenced = [r.semantic_proxy_drift for r in silenced]

    quality_all = [r.raw_quality_score for r in results]
    quality_accepted = [r.raw_quality_score for r in accepted]
    quality_silenced = [r.raw_quality_score for r in silenced]

    summary = {
        "counts": {
            "total_tasks": total,
            "silenced": len(silenced),
            "accepted": len(accepted),

            "raw_successes": len(raw_successes),
            "raw_failures": len(raw_failures),

            "with_control_successes": len(with_control_successes),
            "with_control_failures": len(with_control_failures),

            "silenced_raw_success": len(silenced_raw_success),
            "silenced_raw_fail": len(silenced_raw_fail),

            "accepted_raw_success": len(accepted_raw_success),
            "accepted_raw_fail": len(accepted_raw_fail),
        },
        "rates": {
            "silence_rate_pct": pct(len(silenced), total),
            "coverage_pct": pct(len(accepted), total),
            "no_control_success_rate_pct": pct(len(raw_successes), total),
            "with_control_success_rate_pct": pct(len(with_control_successes), total),

            # among accepted outputs only, how many are raw successes?
            "accepted_precision_pct": pct(len(accepted_raw_success), len(accepted)),

            # among all raw failures, how many got silenced?
            "risk_capture_pct": pct(len(silenced_raw_fail), len(raw_failures)),

            # among silenced outputs, how many were actually raw failures?
            "silence_precision_pct": pct(len(silenced_raw_fail), len(silenced)),
        },
        "drift": {
            "avg_all": avg(drift_all),
            "avg_raw_success": avg(drift_raw_success),
            "avg_raw_fail": avg(drift_raw_fail),
            "avg_accepted": avg(drift_accepted),
            "avg_silenced": avg(drift_silenced),

            "median_all": median(drift_all),
            "stdev_all": stdev(drift_all),
        },
        "quality": {
            "avg_all": avg(quality_all),
            "avg_accepted": avg(quality_accepted),
            "avg_silenced": avg(quality_silenced),
        }
    }

    return summary


# ============================================================================
# OUTPUT WRITERS
# ============================================================================

def write_jsonl(results: List[EvalResult], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in results:
            f.write(json.dumps(asdict(row), ensure_ascii=False) + "\n")


def write_csv(results: List[EvalResult], path: Path) -> None:
    if not results:
        return

    fieldnames = list(asdict(results[0]).keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(asdict(r))


def write_summary(summary: Dict[str, Any], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


# ============================================================================
# PRETTY PRINT
# ============================================================================

def print_header(title: str) -> None:
    print("=" * 78)
    print(title)
    print("=" * 78)


def print_summary(summary: Dict[str, Any]) -> None:
    print_header("PoR / Silence-as-Control — Real Eval Summary")

    counts = summary["counts"]
    rates = summary["rates"]
    drift = summary["drift"]
    quality = summary["quality"]

    print("COUNTS")
    print(f"  Total tasks              : {counts['total_tasks']}")
    print(f"  Silenced                 : {counts['silenced']}")
    print(f"  Accepted                 : {counts['accepted']}")
    print(f"  Raw successes            : {counts['raw_successes']}")
    print(f"  Raw failures             : {counts['raw_failures']}")
    print(f"  With-control successes   : {counts['with_control_successes']}")
    print(f"  With-control failures    : {counts['with_control_failures']}")
    print(f"  Silenced raw success     : {counts['silenced_raw_success']}")
    print(f"  Silenced raw fail        : {counts['silenced_raw_fail']}")
    print(f"  Accepted raw success     : {counts['accepted_raw_success']}")
    print(f"  Accepted raw fail        : {counts['accepted_raw_fail']}")
    print()

    print("RATES")
    print(f"  Silence rate             : {rates['silence_rate_pct']} %")
    print(f"  Coverage                 : {rates['coverage_pct']} %")
    print(f"  No-control success       : {rates['no_control_success_rate_pct']} %")
    print(f"  With-control success     : {rates['with_control_success_rate_pct']} %")
    print(f"  Accepted precision       : {rates['accepted_precision_pct']} %")
    print(f"  Risk capture             : {rates['risk_capture_pct']} %")
    print(f"  Silence precision        : {rates['silence_precision_pct']} %")
    print()

    print("DRIFT")
    print(f"  Avg drift (all)          : {drift['avg_all']}")
    print(f"  Avg drift (raw success)  : {drift['avg_raw_success']}")
    print(f"  Avg drift (raw fail)     : {drift['avg_raw_fail']}")
    print(f"  Avg drift (accepted)     : {drift['avg_accepted']}")
    print(f"  Avg drift (silenced)     : {drift['avg_silenced']}")
    print(f"  Median drift             : {drift['median_all']}")
    print(f"  Drift stdev              : {drift['stdev_all']}")
    print()

    print("QUALITY")
    print(f"  Avg quality (all)        : {quality['avg_all']}")
    print(f"  Avg quality (accepted)   : {quality['avg_accepted']}")
    print(f"  Avg quality (silenced)   : {quality['avg_silenced']}")
    print()

    print("INTERPRETATION")
    print(
        "  - 'No-control success' is baseline acceptance without abstention.\n"
        "  - 'With-control success' is outcome after applying silence.\n"
        "  - 'Accepted precision' shows how clean the accepted outputs are.\n"
        "  - 'Risk capture' shows how many baseline failures were intercepted.\n"
        "  - The goal is not maximum output volume, but better reliability trade-off."
    )
    print()


def print_task_table(results: List[EvalResult]) -> None:
    print_header("Per-task Breakdown")
    for r in results:
        print(f"[{r.task_id}] {r.category}")
        print(f"  Notes                : {r.notes}")
        print(f"  Drift                : {r.semantic_proxy_drift}")
        print(f"  Quality              : {r.raw_quality_score}")
        print(f"  Task integrity       : {r.task_integrity}")
        print(f"  Contradiction score  : {r.contradiction_score}")
        print(f"  Hedging score        : {r.hedging_score}")
        print(f"  Token overlap        : {r.token_overlap}")
        print(f"  Length ratio drift   : {r.length_ratio_drift}")
        print(f"  Raw success          : {r.raw_success}")
        print(f"  Silence              : {r.silence}")
        print(f"  No-control success   : {r.no_control_success}")
        print(f"  With-control success : {r.with_control_success}")
        print("-" * 78)


# ============================================================================
# CLI
# ============================================================================

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="PoR / Silence-as-Control real eval harness"
    )
    parser.add_argument(
        "--silence-threshold",
        type=float,
        default=DEFAULT_SILENCE_THRESHOLD,
        help="Threshold above which silence triggers",
    )
    parser.add_argument(
        "--raw-success-threshold",
        type=float,
        default=DEFAULT_RAW_SUCCESS_THRESHOLD,
        help="Threshold above which raw output counts as success",
    )
    parser.add_argument(
        "--print-tasks",
        action="store_true",
        help="Print per-task details",
    )
    return parser


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    results = run_harness(
        tasks=TASKS,
        raw_success_threshold=args.raw_success_threshold,
        silence_threshold=args.silence_threshold,
    )
    summary = summarize_results(results)

    write_jsonl(results, JSONL_FILE)
    write_csv(results, CSV_FILE)
    write_summary(summary, SUMMARY_FILE)

    print_summary(summary)

    if args.print_tasks:
        print_task_table(results)

    print_header("Artifacts")
    print(f"JSONL  : {JSONL_FILE}")
    print(f"CSV    : {CSV_FILE}")
    print(f"Summary: {SUMMARY_FILE}")
    print()
    print("Done.")


if __name__ == "__main__":
    main()