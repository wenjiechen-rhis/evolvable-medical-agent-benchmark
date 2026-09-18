from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: expected a JSON object")
            records.append(value)
    return records


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
    file_descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(file_descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def sum_usage(events: Iterable[dict[str, Any]]) -> dict[str, float | int]:
    totals: dict[str, float | int] = {
        "model_calls": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "elapsed_seconds": 0.0,
        "provider_failures": 0,
    }
    for event in events:
        usage = event.get("usage") or {}
        if not isinstance(usage, dict):
            continue
        for field in ("model_calls", "input_tokens", "output_tokens", "provider_failures"):
            value = usage.get(field, 0)
            if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                totals[field] = int(totals[field]) + value
        elapsed = usage.get("elapsed_seconds", 0)
        if isinstance(elapsed, (int, float)) and not isinstance(elapsed, bool) and elapsed >= 0:
            totals["elapsed_seconds"] = float(totals["elapsed_seconds"]) + float(elapsed)
    return totals
