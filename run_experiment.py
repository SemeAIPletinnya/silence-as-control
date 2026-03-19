import json
import random
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "results.jsonl"


def simulate_run(run_id: int) -> dict:
    drift = round(random.uniform(0.0, 0.5), 3)
    coherence = round(random.uniform(0.5, 1.0), 3)
    cosine = round(random.uniform(0.6, 1.0), 3)

    raw_success = drift < 0.27
    silence = drift > 0.35

    no_control_success = raw_success
    with_control_success = raw_success if not silence else False

    return {
        "run_id": run_id,
        "drift": drift,
        "coherence": coherence,
        "cosine": cosine,
        "raw_success": raw_success,
        "silence": silence,
        "no_control_success": no_control_success,
        "with_control_success": with_control_success,
    }


def main() -> None:
    with LOG_FILE.open("w", encoding="utf-8") as f:
        for i in range(30):
            result = simulate_run(i)
            f.write(json.dumps(result) + "\n")

    print(f"Done. Logs saved to {LOG_FILE}")


if __name__ == "__main__":
    main()