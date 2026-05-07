import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


MODULE_PATH = Path("benchmarks/langchain_openai/run_langchain_openai_por.py")


def _load_module():
    spec = spec_from_file_location("run_langchain_openai_por", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _minimal_completed_row(case_id: str) -> dict:
    return {
        "id": case_id,
        "decision": "PROCEED",
        "released": True,
        "risk_class": "SAFE_READ_ONLY",
        "expected_behavior": "PROCEED",
        "failure_cost": 1,
        "silence_cost": 2,
    }


def test_parse_args_defaults_run_id_to_01():
    module = _load_module()
    args = module._parse_args([])
    assert args.run_id == "01"
    assert args.dataset is None
    assert args.resume is False
    assert args.enable_tracing is False


def test_parse_args_accepts_resume_and_tracing_flags():
    module = _load_module()
    args = module._parse_args(["--resume", "--enable-tracing"])
    assert args.resume is True
    assert args.enable_tracing is True


def test_artifact_paths_include_run_id(tmp_path, monkeypatch):
    module = _load_module()
    monkeypatch.chdir(tmp_path)

    jsonl_path, summary_path = module._artifact_paths("02_hardened")

    assert jsonl_path == Path("reports/langchain_openai_run_02_hardened.jsonl")
    assert summary_path == Path("reports/langchain_openai_summary_02_hardened.md")
    assert Path("reports").is_dir()


def test_load_dataset_from_fixture():
    module = _load_module()
    dataset, source = module._load_dataset("tests/fixtures/action_risk_small.jsonl")
    assert len(dataset) == 2
    assert source == "tests/fixtures/action_risk_small.jsonl"
    assert dataset[0]["id"] == "safe_1"


def test_load_dataset_missing_field_fails_clearly(tmp_path):
    module = _load_module()
    bad_path = tmp_path / "bad.jsonl"
    bad_path.write_text('{"id":"x","prompt":"p"}\n', encoding="utf-8")
    try:
        module._load_dataset(str(bad_path))
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "missing required fields" in str(exc)


def test_load_dataset_default_uses_hardcoded_dataset():
    module = _load_module()
    dataset, source = module._load_dataset(None)
    assert source == "hardcoded default"
    assert dataset == module.DATASET


def test_resume_skips_already_completed_ids_in_dataset_order(tmp_path):
    module = _load_module()
    output_path = tmp_path / "run.jsonl"
    output_path.write_text(json.dumps(_minimal_completed_row("safe_1")) + "\n", encoding="utf-8")
    dataset, _ = module._load_dataset("tests/fixtures/action_risk_small.jsonl")

    rows, completed_ids = module._load_resume_rows(output_path)
    remaining = module._remaining_cases(dataset, completed_ids)

    assert [row["id"] for row in rows] == ["safe_1"]
    assert completed_ids == {"safe_1"}
    assert [case["id"] for case in remaining] == ["cfg_1"]


def test_resume_append_does_not_write_duplicate_ids(tmp_path):
    module = _load_module()
    output_path = tmp_path / "run.jsonl"
    output_path.write_text(json.dumps(_minimal_completed_row("safe_1")) + "\n", encoding="utf-8")
    dataset, _ = module._load_dataset("tests/fixtures/action_risk_small.jsonl")

    _, completed_ids = module._load_resume_rows(output_path)
    with output_path.open("a", encoding="utf-8") as f:
        for case in module._remaining_cases(dataset, completed_ids):
            row = _minimal_completed_row(case["id"])
            module._write_jsonl_row(f, row)
            completed_ids.add(case["id"])

    ids = [json.loads(line)["id"] for line in output_path.read_text(encoding="utf-8").splitlines()]
    assert ids == ["safe_1", "cfg_1"]
    assert len(ids) == len(set(ids))


def test_resume_rejects_existing_duplicate_ids(tmp_path):
    module = _load_module()
    output_path = tmp_path / "run.jsonl"
    output_path.write_text(
        json.dumps(_minimal_completed_row("safe_1"))
        + "\n"
        + json.dumps(_minimal_completed_row("safe_1"))
        + "\n",
        encoding="utf-8",
    )

    try:
        module._load_resume_rows(output_path)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "duplicate id" in str(exc)


def test_tracing_is_disabled_by_default(monkeypatch):
    module = _load_module()
    for name in module.TRACING_ENV_VARS:
        monkeypatch.setenv(name, "true")

    module._configure_tracing(enable_tracing=False)

    for name in module.TRACING_ENV_VARS:
        assert name in {"LANGCHAIN_TRACING", "LANGCHAIN_TRACING_V2", "LANGSMITH_TRACING"}
        assert module.os.environ[name] == "false"


def test_enable_tracing_does_not_override_user_environment(monkeypatch):
    module = _load_module()
    for name in module.TRACING_ENV_VARS:
        monkeypatch.setenv(name, "true")

    module._configure_tracing(enable_tracing=True)

    for name in module.TRACING_ENV_VARS:
        assert module.os.environ[name] == "true"


def test_enable_tracing_does_not_force_tracing_on(monkeypatch):
    module = _load_module()
    for name in module.TRACING_ENV_VARS:
        monkeypatch.delenv(name, raising=False)

    module._configure_tracing(enable_tracing=True)

    for name in module.TRACING_ENV_VARS:
        assert name not in module.os.environ
