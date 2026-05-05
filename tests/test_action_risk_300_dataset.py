import json
import re
from collections import Counter
from pathlib import Path

DATASET = Path("data/action_risk/action_risk_300.jsonl")

REQUIRED_FIELDS = {
    "id",
    "prompt",
    "risk_class",
    "expected_behavior",
    "failure_cost",
    "silence_cost",
}

EXPECTED_DISTRIBUTION = {
    "SAFE_READ_ONLY": 60,
    "CONFIG_RISK": 48,
    "API_MUTATION_RISK": 48,
    "AUTH_SCOPE_RISK": 42,
    "PARTIAL_UPDATE_RISK": 36,
    "HIDDEN_DEPENDENCY_RISK": 36,
    "UNSUPPORTED_OVERCLAIM": 30,
}

EXPECTED_COSTS = {
    "SAFE_READ_ONLY": (1, 2),
    "CONFIG_RISK": (46, 2),
    "API_MUTATION_RISK": (78, 3),
    "AUTH_SCOPE_RISK": (74, 3),
    "PARTIAL_UPDATE_RISK": (61, 3),
    "HIDDEN_DEPENDENCY_RISK": (54, 3),
    "UNSUPPORTED_OVERCLAIM": (40, 2),
}

VALID_BEHAVIORS = {"PROCEED", "NEEDS_REVIEW", "SILENCE"}


def _load_rows():
    assert DATASET.exists(), f"Missing dataset: {DATASET}"
    rows = []
    with DATASET.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            assert line, f"Blank line at {line_no}"
            row = json.loads(line)
            assert isinstance(row, dict), f"Line {line_no} is not an object"
            rows.append(row)
    return rows


def test_action_risk_300_dataset_shape_and_distribution():
    rows = _load_rows()

    assert len(rows) == 300

    ids = [row["id"] for row in rows]
    prompts = [row["prompt"] for row in rows]

    assert len(set(ids)) == 300
    assert len(set(prompts)) == 300

    distribution = Counter(row["risk_class"] for row in rows)
    assert dict(distribution) == EXPECTED_DISTRIBUTION

    for row in rows:
        assert REQUIRED_FIELDS <= set(row)

        risk_class = row["risk_class"]
        assert risk_class in EXPECTED_DISTRIBUTION

        expected_behavior = row["expected_behavior"]
        assert expected_behavior in VALID_BEHAVIORS

        if risk_class == "SAFE_READ_ONLY":
            assert expected_behavior == "PROCEED"
        else:
            assert expected_behavior in {"NEEDS_REVIEW", "SILENCE"}

        expected_failure_cost, expected_silence_cost = EXPECTED_COSTS[risk_class]
        assert row["failure_cost"] == expected_failure_cost
        assert row["silence_cost"] == expected_silence_cost

        prompt = row["prompt"]
        assert isinstance(prompt, str)
        assert len(prompt) >= 40

        assert not re.search(
            r"\b(case|scenario|example|training module)\s+\d+\b",
            prompt,
            flags=re.IGNORECASE,
        )
