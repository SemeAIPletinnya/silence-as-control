"""Pytest configuration for repository-local test infrastructure."""

from __future__ import annotations

import os
import tempfile
import uuid
from pathlib import Path


def _unique_basetemp(temp_root: Path) -> Path:
    """Return a unique per-run pytest basetemp path below ``temp_root``."""

    return temp_root / f"run-{os.getpid()}-{uuid.uuid4().hex}"


def _windows_basetemp() -> Path:
    """Choose the Windows pytest basetemp path, falling back outside the repo."""

    repo_temp_root = Path(__file__).resolve().parent / ".pytest_tmp_runs"

    try:
        repo_temp_root.mkdir(parents=True, exist_ok=True)
        return _unique_basetemp(repo_temp_root)
    except OSError:
        fallback_root = Path(tempfile.gettempdir()) / "silence-as-control-pytest"
        fallback_root.mkdir(parents=True, exist_ok=True)
        return _unique_basetemp(fallback_root)


def pytest_configure(config):  # noqa: ANN001
    """Use an isolated Windows pytest temp directory unless one was requested."""

    if os.name != "nt" or config.option.basetemp:
        return

    config.option.basetemp = str(_windows_basetemp())
