import random
import json

RESULTS_FILE = "logs/results.jsonl"

def simulate_run():
    # симулюємо drift (0.0 – 0.5)
    drift = random.uniform(0.0, 0.5)

    # --- LOGIC ---
    raw_success = drift < 0.4          
    silence = drift > 0.35             

    no_control_success = raw_success
    with_control_success = raw_success if not silence else False

    return {
        "drift": drift,
        "raw_success": raw_success,
        "silence": silence,
        "no_control_success": no_control_success,
        "with_control_success": with_control_success,
    }


def main():
    runs = 30

    with open(RESULTS_FILE, "w") as f:
        for _ in range(runs):
            result = simulate_run()
            f.write(json.dumps(result) + "\n")

    print("Done. Logs saved to", RESULTS_FILE)


if __name__ == "__main__":
    main()