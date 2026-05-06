import json
from collections import Counter
from pathlib import Path

DATASET = Path("data/action_risk/action_risk_1000.jsonl")

REQUIRED_FIELDS = {
    "id",
    "prompt",
    "risk_class",
    "expected_behavior",
    "failure_cost",
    "silence_cost",
}

EXPECTED_DISTRIBUTION = {
    "SAFE_READ_ONLY": 200,
    "CONFIG_RISK": 160,
    "API_MUTATION_RISK": 160,
    "AUTH_SCOPE_RISK": 140,
    "PARTIAL_UPDATE_RISK": 120,
    "HIDDEN_DEPENDENCY_RISK": 120,
    "UNSUPPORTED_OVERCLAIM": 100,
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

EXPECTED_PREFIXES = {
    "SAFE_READ_ONLY": "safe_ro",
    "CONFIG_RISK": "config_risk",
    "API_MUTATION_RISK": "api_mutation_risk",
    "AUTH_SCOPE_RISK": "auth_scope_risk",
    "PARTIAL_UPDATE_RISK": "partial_update_risk",
    "HIDDEN_DEPENDENCY_RISK": "hidden_dependency_risk",
    "UNSUPPORTED_OVERCLAIM": "unsupported_overclaim",
}

VALID_BEHAVIORS = {"PROCEED", "NEEDS_REVIEW"}


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


def test_action_risk_1000_dataset_shape_and_distribution():
    rows = _load_rows()

    assert len(rows) == 1000

    ids = [row["id"] for row in rows]
    assert len(set(ids)) == 1000

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
            assert expected_behavior == "NEEDS_REVIEW"

        expected_failure_cost, expected_silence_cost = EXPECTED_COSTS[risk_class]
        assert row["failure_cost"] == expected_failure_cost
        assert row["silence_cost"] == expected_silence_cost
        assert isinstance(row["failure_cost"], (int, float))
        assert isinstance(row["silence_cost"], (int, float))

        prompt = row["prompt"]
        assert isinstance(prompt, str)
        assert prompt


def test_action_risk_1000_dataset_stable_ids():
    rows = _load_rows()

    by_class = {risk_class: [] for risk_class in EXPECTED_DISTRIBUTION}
    for row in rows:
        by_class[row["risk_class"]].append(row["id"])

    for risk_class, count in EXPECTED_DISTRIBUTION.items():
        prefix = EXPECTED_PREFIXES[risk_class]
        assert by_class[risk_class] == [
            f"{prefix}_{index:03d}" for index in range(1, count + 1)
        ]
