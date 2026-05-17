"""Print a deterministic comparison of baseline and SaC release control."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from examples.agent_release_control.baseline_agent import run_baseline
from examples.agent_release_control.sac_agent import run_sac
from examples.agent_release_control.scenarios import SCENARIOS


def _reason(sac_result: dict) -> str:
    return "; ".join(sac_result["reasons"])


def main() -> None:
    """Run all deterministic scenarios and print a stable comparison table."""

    print("CASE | TITLE | BASELINE | SaC | REASON")
    print("--- | --- | --- | --- | ---")
    for index, scenario in enumerate(SCENARIOS, start=1):
        baseline = run_baseline(scenario)
        sac = run_sac(scenario)
        print(
            f"CASE {index} | {scenario['title']} | {baseline['decision']} | "
            f"{sac['decision']} | {_reason(sac)}"
        )


if __name__ == "__main__":
    main()
