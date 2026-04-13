import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Support both `python scripts/...` and module import paths.
sys.path.append(str(Path(__file__).resolve().parent))
from scoring_utils import compute_proxy_metrics


def load_tasks_from_jsonl(path):
    tasks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            tasks.append(json.loads(line))
    return tasks


load_dotenv()

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "live_eval_openai_results.jsonl"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4")

TASKS = load_tasks_from_jsonl("tasks_run5_1000.jsonl")

# Evidence/eval contract constants for this script's artifact output.
# These values define live eval evidence semantics and are intentionally
# separate from runtime/API demo heuristics and deterministic library control.
SEMANTIC_PROXY_DRIFT_SILENCE_THRESHOLD = 0.39
RAW_SUCCESS_QUALITY_THRESHOLD = 0.55

def semantic_proxy_drift(prompt: str, output: str, expected_keywords: list[str]):
    metrics = compute_proxy_metrics(prompt, output, expected_keywords)
    return (
        metrics["task_integrity"],
        metrics["hedging_score"],
        metrics["contradiction_score"],
        metrics["token_overlap"],
        metrics["length_ratio_drift"],
        metrics["semantic_proxy_drift"],
        metrics["raw_quality_score"],
    )


def get_output_text(response) -> str:
    if hasattr(response, "output_text") and response.output_text:
        return response.output_text.strip()
    return ""


def main():
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

        raw_success = quality >= RAW_SUCCESS_QUALITY_THRESHOLD
        silence = drift >= SEMANTIC_PROXY_DRIFT_SILENCE_THRESHOLD

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
            "raw_success_threshold": RAW_SUCCESS_QUALITY_THRESHOLD,
            "silence_threshold": SEMANTIC_PROXY_DRIFT_SILENCE_THRESHOLD,
        }

        results.append(result)

    with LOG_FILE.open("w", encoding="utf-8") as f:
        for row in results:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Done. Live eval logs saved to {LOG_FILE}")
    print(f"Tasks evaluated: {len(results)}")


if __name__ == "__main__":
    main()
