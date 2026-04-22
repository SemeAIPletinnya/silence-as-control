from benchmarks.simpleqa.run_simpleqa_por import _parse_args
from benchmarks.simpleqa.metrics import compute_threshold_metrics
from benchmarks.simpleqa.por_adapter import evaluate_por_gate
from benchmarks.simpleqa.run_simpleqa_por import validate_por_samples


def test_validate_por_samples_rejects_lt_2() -> None:
    try:
        validate_por_samples(1)
    except ValueError as exc:
        assert ">= 2" in str(exc)
    else:
        raise AssertionError("Expected ValueError for por_samples < 2")


def test_threshold_metrics_preserve_precision_buckets() -> None:
    rows = [
        {
            "threshold_label": "0.341",
            "threshold_value": 0.341,
            "silence_flag": False,
            "correctness_label": "correct",
            "false_silence_flag": False,
        },
        {
            "threshold_label": "0.344",
            "threshold_value": 0.344,
            "silence_flag": True,
            "correctness_label": "wrong",
            "false_silence_flag": True,
        },
    ]

    m_341 = compute_threshold_metrics(rows, 0.341)
    m_344 = compute_threshold_metrics(rows, 0.344)

    assert m_341.total_examples == 1
    assert m_341.answered_count == 1
    assert m_344.total_examples == 1
    assert m_344.silence_count == 1


def test_por_gate_uses_multi_sample_drift() -> None:
    result = evaluate_por_gate(
        prompt="What is the capital of France?",
        primary_candidate="Paris",
        candidate_samples=["Paris", "Lyon", "Marseille"],
        threshold=0.39,
    )
    assert result.drift > 0.0


def test_por_mode_default_and_choices(monkeypatch) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_simpleqa_por.py",
            "--dataset-path",
            "dummy.jsonl",
            "--model",
            "gpt-4o-mini",
        ],
    )
    args = _parse_args()
    assert args.por_mode == "v1"
    assert args.self_check_no_penalty == 0.30

    monkeypatch.setattr(
        "sys.argv",
        [
            "run_simpleqa_por.py",
            "--dataset-path",
            "dummy.jsonl",
            "--model",
            "gpt-4o-mini",
            "--por-mode",
            "v2",
        ],
    )
    args_v2 = _parse_args()
    assert args_v2.por_mode == "v2"

    monkeypatch.setattr(
        "sys.argv",
        [
            "run_simpleqa_por.py",
            "--dataset-path",
            "dummy.jsonl",
            "--model",
            "gpt-4o-mini",
            "--por-mode",
            "v2_1",
        ],
    )
    args_v2_1 = _parse_args()
    assert args_v2_1.por_mode == "v2_1"

    monkeypatch.setattr(
        "sys.argv",
        [
            "run_simpleqa_por.py",
            "--dataset-path",
            "dummy.jsonl",
            "--model",
            "gpt-4o-mini",
            "--por-mode",
            "v2_2",
            "--self-check-no-penalty",
            "0.35",
        ],
    )
    args_v2_2 = _parse_args()
    assert args_v2_2.por_mode == "v2_2"
    assert args_v2_2.self_check_no_penalty == 0.35
