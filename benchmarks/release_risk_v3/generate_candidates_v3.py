from __future__ import annotations

import argparse
import shutil
from pathlib import Path

BASE_DIR = Path("benchmarks/release_risk_v3")
DEFAULT_PROMPTS_PATH = BASE_DIR / "data" / "release_risk_prompts_50.jsonl"
FIXTURE_CANDIDATES_PATH = BASE_DIR / "candidates" / "fixture_generated_candidates_50.jsonl"
DEFAULT_OUTPUT_PATH = BASE_DIR / "candidates" / "generated_candidates_fixture.jsonl"


def generate_fixture(output_path: Path, prompts_path: Path) -> Path:
    if not prompts_path.exists():
        raise FileNotFoundError(f"Prompts path not found: {prompts_path}")
    if not FIXTURE_CANDIDATES_PATH.exists():
        raise FileNotFoundError(f"Fixture candidates not found: {FIXTURE_CANDIDATES_PATH}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(FIXTURE_CANDIDATES_PATH, output_path)
    return output_path


def _unsupported_message(mode: str) -> str:
    return (
        f"--mode {mode} is scaffold-only in v3 first PR. "
        "No provider/local generation is implemented yet. "
        "Use --mode fixture for deterministic, API-key-free replay."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Release-risk v3 candidate generation scaffold")
    parser.add_argument("--mode", choices=["fixture", "provider", "local"], default="fixture")
    parser.add_argument("--model", default="fixture-generated-candidates-v1")
    parser.add_argument("--prompts", type=Path, default=DEFAULT_PROMPTS_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()

    if args.mode == "fixture":
        out = generate_fixture(output_path=args.output, prompts_path=args.prompts)
        print(f"Wrote fixture-generated candidates to: {out}")
        return

    raise SystemExit(_unsupported_message(args.mode))


if __name__ == "__main__":
    main()
