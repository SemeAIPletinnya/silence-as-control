#!/usr/bin/env python
"""Summarize local JSONL runtime telemetry events."""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

DEFAULT_TELEMETRY_LOG_PATH = Path("runtime_logs/por_runtime_events.jsonl")


def get_default_report_path() -> Path:
    configured_path = os.getenv("POR_TELEMETRY_LOG_PATH")
    if configured_path and configured_path.strip():
        return Path(configured_path).expanduser()
    return DEFAULT_TELEMETRY_LOG_PATH


def load_events(path: Path) -> tuple[list[dict[str, Any]], int]:
    events: list[dict[str, Any]] = []
    malformed_lines = 0

    if not path.exists():
        return events, malformed_lines

    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if not stripped:
                    continue
                try:
                    event = json.loads(stripped)
                except json.JSONDecodeError:
                    malformed_lines += 1
                    continue
                if isinstance(event, dict):
                    events.append(event)
                else:
                    malformed_lines += 1
    except OSError:
        return events, malformed_lines + 1

    return events, malformed_lines


def _average(events: Iterable[dict[str, Any]], field: str) -> float | None:
    values: list[float] = []
    for event in events:
        value = event.get(field)
        if isinstance(value, (int, float)):
            values.append(float(value))
    if not values:
        return None
    return sum(values) / len(values)


def summarize_events(events: list[dict[str, Any]], malformed_lines: int = 0) -> dict[str, Any]:
    events_by_type = Counter(str(event.get("event_type", "unknown")) for event in events)
    decisions_by_type: dict[str, Counter[str]] = defaultdict(Counter)

    for event in events:
        event_type = str(event.get("event_type", "unknown"))
        decision = event.get("decision")
        if decision is not None:
            decisions_by_type[event_type][str(decision)] += 1

    return {
        "total_events": len(events),
        "malformed_lines": malformed_lines,
        "events_by_type": dict(sorted(events_by_type.items())),
        "decisions_by_type": {
            key: dict(sorted(value.items())) for key, value in sorted(decisions_by_type.items())
        },
        "release_count": sum(1 for event in events if event.get("released") is True),
        "silence_count": sum(1 for event in events if event.get("silenced") is True),
        "average_drift": _average(events, "drift"),
        "average_coherence": _average(events, "coherence"),
        "average_instability_score": _average(events, "instability_score"),
    }


def _format_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return json.dumps(value, sort_keys=True)


def print_summary(summary: dict[str, Any], path: Path) -> None:
    print(f"path: {path}")
    for key in (
        "total_events",
        "malformed_lines",
        "events_by_type",
        "decisions_by_type",
        "release_count",
        "silence_count",
        "average_drift",
        "average_coherence",
        "average_instability_score",
    ):
        print(f"{key}: {_format_value(summary[key])}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize PoR runtime JSONL telemetry.")
    parser.add_argument("--path", type=Path, default=None, help="Path to JSONL telemetry log.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = args.path if args.path is not None else get_default_report_path()
    events, malformed_lines = load_events(path)
    summary = summarize_events(events, malformed_lines=malformed_lines)
    print_summary(summary, path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
