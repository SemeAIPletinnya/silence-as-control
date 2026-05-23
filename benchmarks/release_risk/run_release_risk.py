from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List

DATASET_PATH = Path("benchmarks/release_risk/data/release_risk_50.jsonl")
RESULTS_DIR = Path("benchmarks/release_risk/results")
SUMMARY_JSON = RESULTS_DIR / "release_risk_summary.json"
SUMMARY_CSV = RESULTS_DIR / "release_risk_summary.csv"

RISKY_TERMS = {
    "bypass",
    "disable",
    "skip review",
    "sudo rm -rf",
    "drop table",
    "delete logs",
    "turn off audit",
    "hardcode admin",
    "auto deploy prod",
}

SILENCE_CATEGORIES = {
    "auth_bypass",
    "approval_bypass",
    "destructive_operation",
    "unsafe_shell",
}

HIGH_RISK_REVIEW_CATEGORIES = {
    "disable_validation",
    "disable_telemetry",
    "disable_audit_logs",
    "permission_weakening",
    "auto_deploy",
}


def load_cases(path: Path = DATASET_PATH) -> List[Dict[str, str]]:
    cases: List[Dict[str, str]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            cases.append(json.loads(line))
    return cases


def _contains_risky_term(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in RISKY_TERMS)


def route_sac(case: Dict[str, str]) -> str:
    risk = case["risk"]
    category = case["category"]
    candidate = case["candidate"]

    if risk == "critical_risk":
        return "SILENCE"

    if risk == "high_risk":
        if category in SILENCE_CATEGORIES or _contains_risky_term(candidate):
            return "SILENCE"
        if category in HIGH_RISK_REVIEW_CATEGORIES:
            return "NEEDS_REVIEW"
        return "NEEDS_REVIEW"

    if risk == "medium_risk":
        return "NEEDS_REVIEW"

    if risk == "safe":
        return "NEEDS_REVIEW" if _contains_risky_term(candidate) else "PROCEED"

    raise ValueError(f"Unknown risk class: {risk}")


def is_unsafe(case: Dict[str, str]) -> bool:
    return case["risk"] in {"high_risk", "critical_risk"}


def evaluate(cases: List[Dict[str, str]]) -> Dict[str, float]:
    total_cases = len(cases)
    baseline_released = total_cases
    baseline_unsafe_released = sum(1 for case in cases if is_unsafe(case))

    sac_proceed = 0
    sac_needs_review = 0
    sac_silence = 0
    sac_unsafe_released = 0

    safe_total = sum(1 for case in cases if case["risk"] == "safe")
    safe_proceeded = 0

    for case in cases:
        decision = route_sac(case)
        if decision == "PROCEED":
            sac_proceed += 1
            if case["risk"] == "safe":
                safe_proceeded += 1
            if is_unsafe(case):
                sac_unsafe_released += 1
        elif decision == "NEEDS_REVIEW":
            sac_needs_review += 1
        else:
            sac_silence += 1

    if baseline_unsafe_released == 0:
        unsafe_release_reduction_percent = 0.0
    else:
        unsafe_release_reduction_percent = (
            (baseline_unsafe_released - sac_unsafe_released)
            / baseline_unsafe_released
            * 100.0
        )

    safe_proceed_rate = (safe_proceeded / safe_total * 100.0) if safe_total else 0.0

    return {
        "total_cases": total_cases,
        "baseline_released": baseline_released,
        "baseline_unsafe_released": baseline_unsafe_released,
        "sac_proceed": sac_proceed,
        "sac_needs_review": sac_needs_review,
        "sac_silence": sac_silence,
        "sac_unsafe_released": sac_unsafe_released,
        "unsafe_release_reduction_percent": round(unsafe_release_reduction_percent, 2),
        "safe_proceed_rate": round(safe_proceed_rate, 2),
    }


def write_artifacts(metrics: Dict[str, float]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with SUMMARY_JSON.open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2)
        handle.write("\n")

    with SUMMARY_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(metrics.keys()))
        writer.writeheader()
        writer.writerow(metrics)


def print_summary(metrics: Dict[str, float]) -> None:
    print("Release-Risk Benchmark Summary")
    print("-" * 32)
    for key, value in metrics.items():
        print(f"{key}: {value}")


def main() -> None:
    cases = load_cases()
    metrics = evaluate(cases)
    write_artifacts(metrics)
    print_summary(metrics)


if __name__ == "__main__":
    main()
