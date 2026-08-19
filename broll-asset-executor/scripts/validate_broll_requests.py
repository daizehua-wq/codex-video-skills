#!/usr/bin/env python3
"""Validate broll_requests/2.0 structure and relational invariants."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path


def fail(message: str) -> None:
    raise ValueError(message)


def load_json(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def schema_validate(data, schema_path: Path) -> str:
    try:
        import jsonschema
    except ImportError:
        return "JSON Schema skipped (optional 'jsonschema' package unavailable)"
    schema = load_json(schema_path)
    jsonschema.Draft202012Validator(schema).validate(data)
    return "JSON Schema passed"


def relational_validate(data) -> None:
    requests = data.get("requests")
    if not isinstance(requests, list) or not requests:
        fail("requests must be a non-empty array")

    ids = [item.get("id") for item in requests]
    if len(ids) != len(set(ids)):
        fail("request IDs must be unique")

    grouped = defaultdict(list)
    for item in requests:
        request_id = item.get("id", "<missing-id>")
        block_id = item.get("block_id")
        window = item.get("coverage_window", {})
        start = window.get("start_sec")
        end = window.get("end_sec")
        duration = item.get("coverage_duration_sec")
        position = item.get("sequence_position")

        if not all(isinstance(value, (int, float)) for value in (start, end, duration)):
            fail(f"{request_id}: start_sec, end_sec and coverage_duration_sec must be numeric")
        if end <= start:
            fail(f"{request_id}: end_sec must be greater than start_sec")
        if abs((end - start) - duration) > 0.15:
            fail(f"{request_id}: coverage_duration_sec does not match its window")
        if not isinstance(position, int) or position < 1:
            fail(f"{request_id}: sequence_position must be a positive integer")
        if not isinstance(block_id, str) or not block_id:
            fail(f"{request_id}: block_id is required")

        if item.get("type") == "Evidence" and item.get("visual_role") == "proof":
            readable = item.get("readable_region")
            guardrails = " ".join(item.get("fact_guardrails", [])).lower()
            if not readable and not any(token in guardrails for token in ("source", "来源", "identity")):
                fail(f"{request_id}: proof requires a readable region or explicit source-identity guardrail")

        grouped[block_id].append(item)

    for block_id, items in grouped.items():
        items.sort(key=lambda item: item["sequence_position"])
        positions = [item["sequence_position"] for item in items]
        expected = list(range(1, len(items) + 1))
        if positions != expected:
            fail(f"{block_id}: sequence positions must be continuous from 1; got {positions}")

        for left, right in zip(items, items[1:]):
            left_end = left["coverage_window"]["end_sec"]
            right_start = right["coverage_window"]["start_sec"]
            layouts = {left.get("layout"), right.get("layout")}
            if right_start < left_end and "split_screen" not in layouts:
                fail(f"{block_id}: {left['id']} overlaps {right['id']} without split_screen")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_broll_requests.py /path/to/broll_requests.json", file=sys.stderr)
        return 2
    input_path = Path(sys.argv[1]).resolve()
    schema_path = Path(__file__).resolve().parents[1] / "references" / "broll_requests.schema.json"
    try:
        data = load_json(input_path)
        schema_status = schema_validate(data, schema_path)
        relational_validate(data)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"INVALID: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"VALID: {input_path}")
    print(schema_status)
    print("Relational checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
