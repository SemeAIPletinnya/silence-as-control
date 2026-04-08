import json
import os
from pathlib import Path
def load_tasks_from_jsonl(path):
    tasks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            tasks.append(json.loads(line))
    return tasks

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "live_eval_openai_results.jsonl"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4")

TASKS = load_tasks_from_jsonl("tasks_run5_1000.jsonl")

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

def semantic_proxy_drift(prompt: str, output: str, expected_keywords: list[str]):
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

def get_output_text(response) -> str:
    if hasattr(response, "output_text") and response.output_text:
        return response.output_text.strip()
    return ""

def main():
    raw_success_threshold = 0.55
    silence_threshold = 0.39

    results = []

    for task in TASKS:
        request_id = f"por-live-{task['task_id']}"

        response = client.responses.create(
            model=MODEL,
            input=task["prompt"],
            extra_headers={"X-Client-Request-Id": request_id},
        )

        output = get_output_text(response)

        integrity, hedge, contradiction, overlap, length_drift, drift, quality = semantic_proxy_drift(
            task["prompt"],
            output,
            task["expected_keywords"],
        )

        raw_success = quality >= raw_success_threshold
        silence = drift >= silence_threshold

        result = {
            "task_id": task["task_id"],
            "category": task["category"],
            "prompt": task["prompt"],
            "output": output,
            "expected_keywords": task["expected_keywords"],
            "notes": task.get("notes", ""),
            "request_id": request_id,
            "model": MODEL,
            "task_integrity": integrity,
            "hedging_score": hedge,
            "contradiction_score": contradiction,
            "token_overlap": overlap,
            "length_ratio_drift": length_drift,
            "semantic_proxy_drift": drift,
            "raw_quality_score": quality,
            "raw_success": raw_success,
            "silence": silence,
            "no_control_success": raw_success,
            "with_control_success": raw_success if not silence else False,
            "raw_success_threshold": raw_success_threshold,
            "silence_threshold": silence_threshold,
        }

        results.append(result)

    with LOG_FILE.open("w", encoding="utf-8") as f:
        for row in results:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Done. Live eval logs saved to {LOG_FILE}")
    print(f"Tasks evaluated: {len(results)}")

if __name__ == "__main__":
    main()