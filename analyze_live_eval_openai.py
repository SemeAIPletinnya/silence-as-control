import json
from pathlib import Path

LOG_FILE = Path("logs/live_eval_openai_results.jsonl")


def avg(values):
    return round(sum(values) / len(values), 3) if values else 0.0


def pct(n, total):
    return round((n / total) * 100, 2) if total else 0.0


def main():
    with LOG_FILE.open("r", encoding="utf-8") as f:
        rows = [json.loads(line) for line in f]

    total = len(rows)

    silenced = [r for r in rows if r["silence"]]
    accepted = [r for r in rows if not r["silence"]]

    raw_successes = [r for r in rows if r["raw_success"]]
    raw_fails = [r for r in rows if not r["raw_success"]]

    accepted_raw_success = [r for r in accepted if r["raw_success"]]
    accepted_raw_fail = [r for r in accepted if not r["raw_success"]]
    silenced_raw_success = [r for r in silenced if r["raw_success"]]
    silenced_raw_fail = [r for r in silenced if not r["raw_success"]]

    baseline_successes = [r for r in rows if r["no_control_success"]]
    baseline_fails = [r for r in rows if not r["no_control_success"]]

    por_successes = [r for r in rows if r["with_control_success"]]
    por_fails = [r for r in rows if not r["with_control_success"]]

    print("=" * 72)
    print("Live Eval — OpenAI Responses API")
    print("=" * 72)

    print("COUNTS")
    print(f"  Total tasks            : {total}")
    print(f"  Silenced               : {len(silenced)}")
    print(f"  Accepted               : {len(accepted)}")
    print(f"  Raw successes          : {len(raw_successes)}")
    print(f"  Raw failures           : {len(raw_fails)}")
    print(f"  Accepted raw success   : {len(accepted_raw_success)}")
    print(f"  Accepted raw fail      : {len(accepted_raw_fail)}")
    print(f"  Silenced raw success   : {len(silenced_raw_success)}")
    print(f"  Silenced raw fail      : {len(silenced_raw_fail)}")
    print()

    print("BASELINE VS PoR")
    print(f"  Baseline success       : {len(baseline_successes)}")
    print(f"  Baseline fail          : {len(baseline_fails)}")
    print(f"  PoR success            : {len(por_successes)}")
    print(f"  PoR fail               : {len(por_fails)}")
    print()

    print("RATES")
    print(f"  Silence rate           : {pct(len(silenced), total)} %")
    print(f"  Coverage               : {pct(len(accepted), total)} %")
    print(f"  Baseline success rate  : {pct(len(baseline_successes), total)} %")
    print(f"  PoR success rate       : {pct(len(por_successes), total)} %")
    print(f"  Accepted precision     : {pct(len(accepted_raw_success), len(accepted))} %")
    print(f"  Risk capture           : {pct(len(silenced_raw_fail), len(raw_fails))} %")
    print(f"  Silence precision      : {pct(len(silenced_raw_fail), len(silenced))} %")
    print()

    print("DELTA")
    print(
        f"  Success rate gain      : "
        f"{round(pct(len(por_successes), total) - pct(len(baseline_successes), total), 2)} pp"
    )
    print(
        f"  Fail reduction         : "
        f"{round(pct(len(baseline_fails), total) - pct(len(por_fails), total), 2)} pp"
    )
    print()

    print("DRIFT")
    print(f"  Avg drift (all)        : {avg([r['semantic_proxy_drift'] for r in rows])}")
    print(f"  Avg drift (raw success): {avg([r['semantic_proxy_drift'] for r in raw_successes])}")
    print(f"  Avg drift (raw fail)   : {avg([r['semantic_proxy_drift'] for r in raw_fails])}")
    print(f"  Avg drift (accepted)   : {avg([r['semantic_proxy_drift'] for r in accepted])}")
    print(f"  Avg drift (silenced)   : {avg([r['semantic_proxy_drift'] for r in silenced])}")
    print()

    print("QUALITY")
    print(f"  Avg quality (all)      : {avg([r['raw_quality_score'] for r in rows])}")
    print(f"  Avg quality (accepted) : {avg([r['raw_quality_score'] for r in accepted])}")
    print(f"  Avg quality (silenced) : {avg([r['raw_quality_score'] for r in silenced])}")
    print("=" * 72)


if __name__ == "__main__":
    main()