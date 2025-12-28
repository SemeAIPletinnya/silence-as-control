from pathlib import Path

def test_control_specs_exist():
    specs = Path("examples").glob("test_*.md")
    assert any(specs), "No control specification tests found"
