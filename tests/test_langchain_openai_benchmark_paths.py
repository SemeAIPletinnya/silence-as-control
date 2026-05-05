from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


MODULE_PATH = Path("benchmarks/langchain_openai/run_langchain_openai_por.py")


def _load_module():
    spec = spec_from_file_location("run_langchain_openai_por", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_parse_args_defaults_run_id_to_01():
    module = _load_module()
    args = module._parse_args([])
    assert args.run_id == "01"
    assert args.dataset is None


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
