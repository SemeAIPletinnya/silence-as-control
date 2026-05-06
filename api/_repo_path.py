"""Repository-local import path helpers for direct script execution.

The package is installable via `pip install -e .`, but several benchmark and CLI
scripts are intentionally runnable directly from a checkout. This helper keeps
that compatibility for the `src/` package layout without changing benchmark
semantics.
"""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_src_on_path() -> None:
    """Make the repository `src/` directory importable for direct scripts."""
    src_path = Path(__file__).resolve().parents[1] / "src"
    src_path_str = str(src_path)
    if src_path.is_dir() and src_path_str not in sys.path:
        sys.path.insert(0, src_path_str)
