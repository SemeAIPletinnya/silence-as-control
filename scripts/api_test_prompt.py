from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI


THRESHOLD = 0.39
LOG_PATH = Path("api_prompt_log.jsonl")


def compute_drift(prompt: str, candidate: str) -> float:
    text = candidate.lower()

    uncertainty_markers = [
        "maybe", "probably", "possibly", "i think", "not sure",
        "unclear", "insufficient", "cannot determine", "guess"
    ]
    penalty = sum(1 for m in uncertainty_markers if m in text)

    base = 0.18

    if len(candidate.strip()) < 20:
        base += 0.08

    if "please provide" in text or "need more context" in text:
        base += 0.10

    if "division by zero" in prompt.lower() and "return none" in text:
        base -= 0.05

    if "factorial" in prompt.lower() and "n == 0" in text:
        base -= 0.05

    drift = min(1.0, max(0.0, base + penalty * 0.08))
    return round(drift, 3)


def compute_coherence(prompt: str, candidate: str) -> float:
    p = prompt.lower()
    c = candidate.lower()

    score = 0.5

    if "division" in p and ("division" in c or "return none" in c):
        score += 0.2
    if "factorial" in p and ("factorial" in c or "n == 0" in c):
        score += 0.2
    if "type conversion" in p and ("int(" in c or "str(" in c or "convert" in c):
        score += 0.15
    if "please provide" in c and "fix bug" in p:
        score -= 0.2

    return round(min(1.0, max(0.0, score)), 3)


def por_decision(drift: float, coherence: float, threshold: float = THRESHOLD) -> str:
    if drift > threshold or coherence < 0.5:
        return "SILENCE"
    return "PROCEED"


def call_model(prompt: str) -> str:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    response = client.responses.create(
        model="gpt-4.1",
        input=prompt,
    )
    return response.output_text.strip()


def log_result(record: dict) -> None:
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    prompt = input("Prompt: ").strip()
    if not prompt:
        print("Empty prompt.")
        return

    candidate = call_model(prompt)
    drift = compute_drift(prompt, candidate)
    coherence = compute_coherence(prompt, candidate)
    decision = por_decision(drift, coherence, THRESHOLD)

    released_output = candidate if decision == "PROCEED" else None

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt": prompt,
        "candidate_output": candidate,
        "drift": drift,
        "coherence": coherence,
        "threshold": THRESHOLD,
        "decision": decision,
        "released_output": released_output,
    }
    log_result(record)

    print("")
    print("=" * 70)
    print(f"DRIFT: {drift}")
    print(f"COHERENCE: {coherence}")
    print(f"DECISION: {decision}")

    print("")
    print("CANDIDATE OUTPUT:")
    print("")
    print(candidate)

    print("")
    print("FINAL OUTPUT:")
    print("")
    if released_output is None:
        print("SilenceToken")
    else:
        print(released_output)


if __name__ == "__main__":
    main()