import json
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
JSONL_FILE = LOG_DIR / "real_eval_v2_results.jsonl"
CSV_FILE = LOG_DIR / "real_eval_v2_results.csv"
SUMMARY_FILE = LOG_DIR / "real_eval_v2_summary.json"

TASKS = [
    {
        "task_id": "chain_001",
        "category": "reasoning_chain",
        "prompt": "Step 1: What is 14 + 9? Step 2: restate the answer in words.",
        "expected_keywords": ["23", "twenty-three"],
        "simulated_output": "14 + 9 = 23. In words: twenty-three.",
        "notes": "clean multi-step success",
    },
    {
        "task_id": "chain_002",
        "category": "reasoning_chain",
        "prompt": "Step 1: What is 14 + 9? Step 2: restate the answer in words.",
        "expected_keywords": ["23", "twenty-three"],
        "simulated_output": "14 + 9 = 23. In words: maybe twenty-four, not fully sure.",
        "notes": "local success, global instability",
    },
    {
        "task_id": "chain_003",
        "category": "reasoning_chain",
        "prompt": "Step 1: What is 7 * 6? Step 2: explain briefly.",
        "expected_keywords": ["42"],
        "simulated_output": "7 * 6 = 42. The multiplication result is 42.",
        "notes": "clean success",
    },
    {
        "task_id": "chain_004",
        "category": "reasoning_chain",
        "prompt": "Step 1: What is 7 * 6? Step 2: explain briefly.",
        "expected_keywords": ["42"],
        "simulated_output": "7 * 6 = 42, although it could also be 36 depending on interpretation.",
        "notes": "contradictory reasoning",
    },
    {
        "task_id": "fact_001",
        "category": "fact",
        "prompt": "What is the capital of Italy?",
        "expected_keywords": ["rome"],
        "simulated_output": "Rome is the capital of Italy.",
        "notes": "clean fact",
    },
    {
        "task_id": "fact_002",
        "category": "fact",
        "prompt": "What is the capital of Italy?",
        "expected_keywords": ["rome"],
        "simulated_output": "The capital of Italy is probably Rome, but Milan is also important.",
        "notes": "hedged fact with drift",
    },
    {
        "task_id": "summary_001",
        "category": "summary",
        "prompt": "Summarize: Backups reduce recovery risk after failures.",
        "expected_keywords": ["backups", "risk"],
        "simulated_output": "Backups reduce recovery risk after failures.",
        "notes": "clean summary",
    },
    {
        "task_id": "summary_002",
        "category": "summary",
        "prompt": "Summarize: Backups reduce recovery risk after failures.",
        "expected_keywords": ["backups", "risk"],
        "simulated_output": "Failures happen for many reasons, and systems are complex.",
        "notes": "topic drift summary",
    },
    {
        "task_id": "instr_001",
        "category": "instruction",
        "prompt": "Reply with exactly one word: approved",
        "expected_keywords": ["approved"],
        "simulated_output": "approved",
        "notes": "clean instruction following",
    },
    {
        "task_id": "instr_002",
        "category": "instruction",
        "prompt": "Reply with exactly one word: approved",
        "expected_keywords": ["approved"],
        "simulated_output": "approved, but there may be caveats worth noting.",
        "notes": "instruction drift",
    },
    {
        "task_id": "science_001",
        "category": "science",
        "prompt": "At sea level, at what temperature does water boil?",
        "expected_keywords": ["100"],
        "simulated_output": "Water boils at 100C at sea level.",
        "notes": "clean science",
    },
    {
        "task_id": "science_002",
        "category": "science",
        "prompt": "At sea level, at what temperature does water boil?",
        "expected_keywords": ["100"],
        "simulated_output": "It is around 100C, maybe 90C or 120C depending on conditions.",
        "notes": "gray-zone science answer",
    },
    {
        "task_id": "logic_001",
        "category": "logic",
        "prompt": "A > B and B > C. Which is largest?",
        "expected_keywords": ["a"],
        "simulated_output": "A is the largest.",
        "notes": "clean logic",
    },
    {
        "task_id": "logic_002",
        "category": "logic",
        "prompt": "A > B and B > C. Which is largest?",
        "expected_keywords": ["a"],
        "simulated_output": "A seems largest, although C might be if the ordering changes.",
        "notes": "logic instability",
    },
    {
        "task_id": "code_001",
        "category": "code_reasoning",
        "prompt": "What does len([1,2,3,4]) return?",
        "expected_keywords": ["4"],
        "simulated_output": "It returns 4.",
        "notes": "clean code reasoning",
    },
    {
        "task_id": "code_002",
        "category": "code_reasoning",
        "prompt": "What does len([1,2,3,4]) return?",
        "expected_keywords": ["4"],
        "simulated_output": "It returns 4, though indexing could make it 3 in some cases.",
        "notes": "partially correct but unstable",
    },
    {
        "task_id": "open_001",
        "category": "open_reasoning",
        "prompt": "Why do logs matter in production systems?",
        "expected_keywords": ["logs", "debug", "issues"],
        "simulated_output": "Logs matter because they help debug issues in production systems.",
        "notes": "clean open reasoning",
    },
    {
        "task_id": "open_002",
        "category": "open_reasoning",
        "prompt": "Why do logs matter in production systems?",
        "expected_keywords": ["logs", "debug", "issues"],
        "simulated_output": "Production systems are complicated, and many things can happen over time.",
        "notes": "low-integrity vague answer",
    },
]


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


def semantic_proxy_drift(prompt: str, output: str, expected_keywords: list[str]) -> tuple[float, float, float, float, float, float]:
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

    return integrity, hedge, contradiction, overlap, length_drift, drift, quality


def avg(values: list[float]) -> float:
    return round(sum(values) / len(values), 3) if values else 0.0


def pct(n: int, total: int) -> float:
    return round((n / total) * 100, 2) if total else 0.0


def main() -> None:
    # Розведені пороги:
    # raw_success — ширша зона прийняття
    # silence — контрольніший поріг
    raw_success_threshold = 0.55
    silence_threshold = 0.28

    results = []

    for task in TASKS:
        output = task["simulated_output"]
        integrity, hedge, contradiction, overlap, length_drift, drift, quality = semantic_proxy_drift(
            task["prompt"],
            output,
            task["expected_keywords"],
        )

        raw_success = quality >= raw_success_threshold
        silence = drift >= silence_threshold

        no_control_success = raw_success
        with_control_success = raw_success if not silence else False

        result = {
            "task_id": task["task_id"],
            "category": task["category"],
            "prompt": task["prompt"],
            "output": output,
            "expected_keywords": task["expected_keywords"],
            "notes": task["notes"],
            "task_integrity": integrity,
            "hedging_score": hedge,
            "contradiction_score": contradiction,
            "token_overlap": overlap,
            "length_ratio_drift": length_drift,
            "semantic_proxy_drift": drift,
            "raw_quality_score": quality,
            "raw_success": raw_success,
            "silence": silence,
            "no_control_success": no_control_success,
            "with_control_success": with_control_success,
            "raw_success_threshold": raw_success_threshold,
            "silence_threshold": silence_threshold,
        }
        results.append(result)

    with JSONL_FILE.open("w", encoding="utf-8") as f:
        for row in results:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    with CSV_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = None
        for row in results:
            if writer is None:
                writer = __import__("csv").DictWriter(f, fieldnames=row.keys())
                writer.writeheader()
            writer.writerow(row)

    total = len(results)
    silenced = [r for r in results if r["silence"]]
    accepted = [r for r in results if not r["silence"]]
    raw_successes = [r for r in results if r["raw_success"]]
    raw_fails = [r for r in results if not r["raw_success"]]

    accepted_raw_success = [r for r in accepted if r["raw_success"]]
    accepted_raw_fail = [r for r in accepted if not r["raw_success"]]
    silenced_raw_success = [r for r in silenced if r["raw_success"]]
    silenced_raw_fail = [r for r in silenced if not r["raw_success"]]

    summary = {
        "counts": {
            "total_tasks": total,
            "silenced": len(silenced),
            "accepted": len(accepted),
            "raw_successes": len(raw_successes),
            "raw_failures": len(raw_fails),
            "accepted_raw_success": len(accepted_raw_success),
            "accepted_raw_fail": len(accepted_raw_fail),
            "silenced_raw_success": len(silenced_raw_success),
            "silenced_raw_fail": len(silenced_raw_fail),
        },
        "rates": {
            "silence_rate_pct": pct(len(silenced), total),
            "coverage_pct": pct(len(accepted), total),
            "no_control_success_rate_pct": pct(len(raw_successes), total),
            "with_control_success_rate_pct": pct(sum(1 for r in results if r["with_control_success"]), total),
            "accepted_precision_pct": pct(len(accepted_raw_success), len(accepted)),
            "risk_capture_pct": pct(len(silenced_raw_fail), len(raw_fails)),
            "silence_precision_pct": pct(len(silenced_raw_fail), len(silenced)),
        },
        "drift": {
            "avg_all": avg([r["semantic_proxy_drift"] for r in results]),
            "avg_raw_success": avg([r["semantic_proxy_drift"] for r in raw_successes]),
            "avg_raw_fail": avg([r["semantic_proxy_drift"] for r in raw_fails]),
            "avg_accepted": avg([r["semantic_proxy_drift"] for r in accepted]),
            "avg_silenced": avg([r["semantic_proxy_drift"] for r in silenced]),
        },
        "quality": {
            "avg_all": avg([r["raw_quality_score"] for r in results]),
            "avg_accepted": avg([r["raw_quality_score"] for r in accepted]),
            "avg_silenced": avg([r["raw_quality_score"] for r in silenced]),
        },
    }

    with SUMMARY_FILE.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("=" * 72)
    print("PoR Eval #2 — Multi-step / Gray-zone Harness")
    print("=" * 72)
    print("COUNTS")
    print(f"  Total tasks            : {summary['counts']['total_tasks']}")
    print(f"  Silenced               : {summary['counts']['silenced']}")
    print(f"  Accepted               : {summary['counts']['accepted']}")
    print(f"  Raw successes          : {summary['counts']['raw_successes']}")
    print(f"  Raw failures           : {summary['counts']['raw_failures']}")
    print(f"  Accepted raw success   : {summary['counts']['accepted_raw_success']}")
    print(f"  Accepted raw fail      : {summary['counts']['accepted_raw_fail']}")
    print(f"  Silenced raw success   : {summary['counts']['silenced_raw_success']}")
    print(f"  Silenced raw fail      : {summary['counts']['silenced_raw_fail']}")
    print()
    print("RATES")
    print(f"  Silence rate           : {summary['rates']['silence_rate_pct']} %")
    print(f"  Coverage               : {summary['rates']['coverage_pct']} %")
    print(f"  No-control success     : {summary['rates']['no_control_success_rate_pct']} %")
    print(f"  With-control success   : {summary['rates']['with_control_success_rate_pct']} %")
    print(f"  Accepted precision     : {summary['rates']['accepted_precision_pct']} %")
    print(f"  Risk capture           : {summary['rates']['risk_capture_pct']} %")
    print(f"  Silence precision      : {summary['rates']['silence_precision_pct']} %")
    print()
    print("DRIFT")
    print(f"  Avg drift (all)        : {summary['drift']['avg_all']}")
    print(f"  Avg drift (raw success): {summary['drift']['avg_raw_success']}")
    print(f"  Avg drift (raw fail)   : {summary['drift']['avg_raw_fail']}")
    print(f"  Avg drift (accepted)   : {summary['drift']['avg_accepted']}")
    print(f"  Avg drift (silenced)   : {summary['drift']['avg_silenced']}")
    print()
    print("QUALITY")
    print(f"  Avg quality (all)      : {summary['quality']['avg_all']}")
    print(f"  Avg quality (accepted) : {summary['quality']['avg_accepted']}")
    print(f"  Avg quality (silenced) : {summary['quality']['avg_silenced']}")
    print()
    print("Artifacts:")
    print(f"  JSONL  : {JSONL_FILE}")
    print(f"  CSV    : {CSV_FILE}")
    print(f"  Summary: {SUMMARY_FILE}")
    print("=" * 72)


if __name__ == "__main__":
    main()