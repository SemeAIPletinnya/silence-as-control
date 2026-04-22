from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class SimpleQAExample:
    """Single SimpleQA benchmark example."""

    example_id: str
    question: str
    reference_answers: list[str]
    raw: dict[str, Any]


class DatasetFormatError(ValueError):
    """Raised when dataset schema cannot be mapped to required fields."""


def _as_list_of_strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(v) for v in value if str(v).strip()]
    return [str(value)]


def _validate_example(
    item: dict[str, Any],
    idx: int,
    *,
    question_field: str,
    answer_field: str | None,
    answers_field: str | None,
    id_field: str | None,
) -> SimpleQAExample:
    question = str(item.get(question_field, "")).strip()
    if not question:
        raise DatasetFormatError(
            f"Example {idx} missing non-empty question field '{question_field}'."
        )

    refs: list[str] = []
    if answers_field:
        refs.extend(_as_list_of_strings(item.get(answers_field)))
    if answer_field:
        refs.extend(_as_list_of_strings(item.get(answer_field)))

    refs = [r.strip() for r in refs if r and r.strip()]
    if not refs:
        raise DatasetFormatError(
            f"Example {idx} missing reference answers in '{answer_field}'/'{answers_field}'."
        )

    if id_field:
        example_id = str(item.get(id_field, f"ex_{idx:06d}"))
    else:
        example_id = f"ex_{idx:06d}"

    return SimpleQAExample(
        example_id=example_id,
        question=question,
        reference_answers=refs,
        raw=item,
    )


def _read_json(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [dict(x) for x in payload]
    if isinstance(payload, dict):
        for key in ("data", "examples", "rows", "items"):
            if key in payload and isinstance(payload[key], list):
                return [dict(x) for x in payload[key]]
    raise DatasetFormatError(
        "JSON file must be either a list of examples or an object containing one of: data/examples/rows/items."
    )


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            obj = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise DatasetFormatError(f"Invalid JSONL on line {line_no}: {exc}") from exc
        if not isinstance(obj, dict):
            raise DatasetFormatError(f"JSONL line {line_no} is not an object.")
        items.append(obj)
    return items


def _read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [dict(row) for row in csv.DictReader(f)]


def load_simpleqa_dataset(
    dataset_path: str | Path,
    *,
    question_field: str = "question",
    answer_field: str | None = "answer",
    answers_field: str | None = "answers",
    id_field: str | None = "id",
    max_examples: int | None = None,
) -> list[SimpleQAExample]:
    """Load a SimpleQA-style local dataset from JSON/JSONL/CSV.

    Required mapped fields:
    - `question_field`: question string.
    - one of `answer_field` or `answers_field` must provide references.

    This loader is deterministic and does not fetch remote datasets.
    """
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset file not found: {path}. Provide a local SimpleQA export file."
        )

    suffix = path.suffix.lower()
    if suffix == ".json":
        raw_items = _read_json(path)
    elif suffix == ".jsonl":
        raw_items = _read_jsonl(path)
    elif suffix == ".csv":
        raw_items = _read_csv(path)
    else:
        raise DatasetFormatError(
            f"Unsupported dataset extension '{suffix}'. Use .json, .jsonl, or .csv."
        )

    examples: list[SimpleQAExample] = []
    for idx, item in enumerate(raw_items):
        if max_examples is not None and len(examples) >= max_examples:
            break
        examples.append(
            _validate_example(
                item,
                idx,
                question_field=question_field,
                answer_field=answer_field,
                answers_field=answers_field,
                id_field=id_field,
            )
        )

    if not examples:
        raise DatasetFormatError("No valid examples were loaded from dataset.")

    return examples
