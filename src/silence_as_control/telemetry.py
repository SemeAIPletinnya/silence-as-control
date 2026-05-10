"""Local JSONL telemetry helpers for runtime release-control events."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

LOGGER = logging.getLogger(__name__)

_ENABLED_VALUES = {"1", "true", "yes", "on"}
_DEFAULT_TELEMETRY_LOG_PATH = Path("runtime_logs/por_runtime_events.jsonl")


def _env_flag_enabled(value: str | None) -> bool:
    return (value or "").strip().lower() in _ENABLED_VALUES


def telemetry_enabled() -> bool:
    """Return whether local runtime telemetry is explicitly enabled."""
    return _env_flag_enabled(os.getenv("POR_TELEMETRY_ENABLED"))


def get_telemetry_log_path() -> Path:
    """Resolve the local JSONL telemetry path."""
    configured_path = os.getenv("POR_TELEMETRY_LOG_PATH")
    if configured_path and configured_path.strip():
        return Path(configured_path).expanduser()
    return _DEFAULT_TELEMETRY_LOG_PATH


def write_runtime_event(event: Mapping[str, Any]) -> bool:
    """Append one local JSONL runtime event when telemetry is enabled.

    Telemetry is best-effort only: disabled telemetry or write failures return
    False and never raise to callers.
    """
    if not telemetry_enabled():
        return False

    try:
        event_record = dict(event)
        event_record.setdefault(
            "timestamp_utc",
            datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        )
        event_record.setdefault("schema_version", "1")

        log_path = get_telemetry_log_path()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event_record, sort_keys=True, separators=(",", ":")))
            handle.write("\n")
        return True
    except Exception:
        LOGGER.warning("por_telemetry_write_failed", exc_info=True)
        return False
