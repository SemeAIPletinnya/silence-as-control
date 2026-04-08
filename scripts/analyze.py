import json
from pathlib import Path

LOG_FILE = Path("logs/results.jsonl")


def avg(values):
    return round(sum(values) / len(values), 3) if values else 0.0


def rate(values):
    return round((sum(values) / len(values)) * 100, 2) if values else 0.0


def main() -> None:
    drift_success = []
    drift_fail = []
    silence_count = 0
    total = 0

    no_control = []
    with_control = []

    with LOG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            total += 1

            if data["silence"]:
                silence_count += 1

            if data["raw_success"]:
                drift_success.append(data["drift"])
            else:
                drift_fail.append(data["drift"])

            no_control.append(1 if data["no_control_success"] else 0)
            with_control.append(1 if data["with_control_success"] else 0)

    avg_success = avg(drift_success)
    avg_fail = avg(drift_fail)
    effective_quality = avg_success

    print(f"Total runs: {total}")
    print(f"Silence rate: {round((silence_count / total) * 100, 2)} %")
    print(f"Avg drift (success): {avg_success:.3f}")
    print(f"Avg drift (fail): {avg_fail:.3f}")
    print(f"No control success rate: {rate(no_control):.2f} %")
    print(f"With control success rate: {rate(with_control):.2f} %")
    print(f"Effective quality (lower drift better): {effective_quality:.3f}")


if __name__ == "__main__":
    main()