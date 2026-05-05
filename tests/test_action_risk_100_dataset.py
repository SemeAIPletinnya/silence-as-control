import json
from collections import Counter
from pathlib import Path


DATASET_PATH = Path("data/action_risk/action_risk_100.jsonl")
REQUIRED_FIELDS = {
    "id",
    "prompt",
    "risk_class",
    "expected_behavior",
    "failure_cost",
    "silence_cost",
}
EXPECTED_DISTRIBUTION = {
    "SAFE_READ_ONLY": 20,
    "CONFIG_RISK": 16,
    "API_MUTATION_RISK": 16,
    "AUTH_SCOPE_RISK": 14,
    "PARTIAL_UPDATE_RISK": 12,
    "HIDDEN_DEPENDENCY_RISK": 12,
    "UNSUPPORTED_OVERCLAIM": 10,
}


def test_action_risk_100_dataset_shape_and_distribution():
    rows = [json.loads(line) for line in DATASET_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]

    assert len(rows) == 100

    ids = [row["id"] for row in rows]
    assert len(ids) == len(set(ids))

    for row in rows:
        assert REQUIRED_FIELDS.issubset(row.keys())

    class_counts = Counter(row["risk_class"] for row in rows)
    assert dict(class_counts) == EXPECTED_DISTRIBUTION
