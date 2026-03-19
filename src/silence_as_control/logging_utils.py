"""JSON-lines logging helpers for control decisions."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


LOG_PATH = Path("logs/decisions.jsonl")


def log_decision(
    *,
    coherence: float,
    drift: float,
    threshold: float,
    tolerance: float,
    decision: str,
) -> None:
    """Append one JSON-lines record for a control decision (best-effort)."""
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "coherence": coherence,
            "drift": drift,
            "threshold": threshold,
            "tolerance": tolerance,
            "decision": decision,
        }

        with LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")

    except Exception:
        # best-effort logging: never break control flow
        pass
