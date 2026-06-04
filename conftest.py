"""Pytest configuration for repository-local test infrastructure."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parent
_PYTEST_TMP_RUNS = _REPO_ROOT / ".pytest_tmp_runs"


def _basetemp_was_requested(config) -> bool:  # noqa: ANN001
    """Return whether pytest already has an explicit basetemp configured."""

    return bool(config.option.basetemp)


def _repo_local_basetemp() -> Path:
    """Return a unique, repo-local pytest basetemp path for this run."""

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    _PYTEST_TMP_RUNS.mkdir(parents=True, exist_ok=True)
    return _PYTEST_TMP_RUNS / f"run-{timestamp}-{os.getpid()}"


def pytest_configure(config):  # noqa: ANN001
    """Use an isolated repo-local pytest basetemp unless one was requested."""

    if _basetemp_was_requested(config):
        return

    config.option.basetemp = str(_repo_local_basetemp())
