"""Pytest temp-directory hardening for Windows test runs.

This plugin keeps pytest's tmp_path basetemp out of shared, reusable temp
roots on Windows. It is test infrastructure only; it does not affect runtime
code, replay artifacts, or benchmark semantics.
"""

from __future__ import annotations

import os
import sys
import tempfile
import uuid
from pathlib import Path


def _has_basetemp(args: list[str]) -> bool:
    """Return True when the user already supplied a pytest basetemp option."""
    return any(arg == "--basetemp" or arg.startswith("--basetemp=") for arg in args)


def _run_basetemp(root: Path) -> Path:
    """Return a unique per-run basetemp path below *root*."""
    run_id = f"run-{os.getpid()}-{uuid.uuid4().hex[:8]}"
    return root / run_id


def _windows_tmp_root(repo_root: Path) -> Path:
    """Prefer a repo-local temp root, then fall back to a user temp subdir."""
    repo_tmp_root = repo_root / ".pytest_tmp_runs"
    try:
        repo_tmp_root.mkdir(exist_ok=True)
        return repo_tmp_root
    except OSError:
        fallback_root = Path(tempfile.gettempdir()) / "silence-as-control-pytest"
        fallback_root.mkdir(exist_ok=True)
        return fallback_root


def pytest_load_initial_conftests(early_config, parser, args: list[str]) -> None:
    """Set a unique Windows basetemp unless the caller chose one explicitly."""
    if sys.platform != "win32" or _has_basetemp(args):
        return

    repo_root = Path(str(getattr(early_config, "rootpath", Path.cwd())))
    basetemp = _run_basetemp(_windows_tmp_root(repo_root))
    args.append(f"--basetemp={basetemp}")
