#!/usr/bin/env python3
"""Validate broll_requests/3.0 structure and acquisition invariants."""

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
    errors = sorted(
        jsonschema.Draft202012Validator(schema).iter_errors(data),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        fail(f"schema error at {location}: {error.message}")
    return "JSON Schema passed"


def readiness_validate(project: dict) -> None:
    if project.get("handoff_status") != "execution_ready":
        fail("project.handoff_status must be execution_ready")
    if project.get("timing_basis") != "measured":
        fail("project.timing_basis must be measured")
    if project.get("visual_policy") != "comprehension_led_no_quota":
        fail("project.visual_policy must be comprehension_led_no_quota")
    if "target_broll_coverage_ratio" in project:
        fail("target_broll_coverage_ratio is prohibited in v3")

    readiness = project.get("aroll_readiness", {})
    if readiness.get("human_finalized") is not True:
        fail("A-roll must be explicitly human-finalized")
    if readiness.get("duration_source") != "probed_media":
        fail("A-roll duration must come from probed media")
    checks = readiness.get("checks", {})
    required = (
        "media_readable",
        "video_stream_present",
        "audio_stream_present",
        "duration_measured",
        "transcript_timecoded",
        "transcript_within_runtime",
        "human_lock_confirmed",
    )
    failed = [name for name in required if checks.get(name) is not True]
    if failed:
        fail(f"A-roll readiness checks failed or missing: {failed}")


def relational_validate(data) -> None:
    readiness_validate(data.get("project", {}))
    requests = data.get("requests")
    if not isinstance(requests, list):
        fail("requests must be an array")

    ids = [item.get("id") for item in requests]
    if len(ids) != len(set(ids)):
        fail("request IDs must be unique")

    grouped = defaultdict(list)
    for item in requests:
        request_id = item.get("id", "<missing-id>")
        segment_id = item.get("segment_id")
        window = item.get("coverage_window", {})
        start = window.get("start_sec")
        end = window.get("end_sec")
        duration = item.get("coverage_duration_sec")
        position = item.get("sequence_position")

        if window.get("timing_basis") != "measured":
            fail(f"{request_id}: coverage_window.timing_basis must be measured")
        if not all(isinstance(value, (int, float)) for value in (start, end, duration)):
            fail(f"{request_id}: start_sec, end_sec and coverage_duration_sec must be numeric")
        if end <= start:
            fail(f"{request_id}: end_sec must be greater than start_sec")
        if abs((end - start) - duration) > 0.15:
            fail(f"{request_id}: coverage_duration_sec does not match its window")
        if not isinstance(position, int) or position < 1:
            fail(f"{request_id}: sequence_position must be a positive integer")
        if not isinstance(segment_id, str) or not segment_id:
            fail(f"{request_id}: segment_id is required")

        if item.get("visual_role") == "proof" or item.get("asset_class") in {
            "source_page_screenshot",
            "source_document",
            "source_video",
        }:
            if not item.get("source_identity_region"):
                fail(f"{request_id}: source evidence requires source_identity_region")
            if not item.get("evidence_region"):
                fail(f"{request_id}: source evidence requires evidence_region")
            forbidden = " ".join(item.get("forbidden_assets", [])).lower()
            if "re-typeset" not in forbidden and "重排" not in forbidden and "重制" not in forbidden:
                fail(f"{request_id}: source evidence must explicitly forbid re-typeset evidence cards")

        if item.get("requested_media") == "video":
            handles = item.get("source_handles_sec", {})
            if handles.get("before", 0) <= 0 and handles.get("after", 0) <= 0:
                fail(f"{request_id}: video acquisition requires a nonzero source handle")

        grouped[segment_id].append(item)

    for segment_id, items in grouped.items():
        items.sort(key=lambda item: item["sequence_position"])
        positions = [item["sequence_position"] for item in items]
        expected = list(range(1, len(items) + 1))
        if positions != expected:
            fail(f"{segment_id}: sequence positions must be continuous from 1; got {positions}")
        for left, right in zip(items, items[1:]):
            if right["coverage_window"]["start_sec"] < left["coverage_window"]["end_sec"]:
                fail(f"{segment_id}: {left['id']} overlaps {right['id']}")


def validate_file(input_path: Path) -> str:
    schema_path = Path(__file__).resolve().parents[1] / "references" / "broll_requests.schema.json"
    data = load_json(input_path)
    schema_status = schema_validate(data, schema_path)
    relational_validate(data)
    return schema_status


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_broll_requests.py /path/to/broll_requests.json", file=sys.stderr)
        return 2
    input_path = Path(sys.argv[1]).resolve()
    try:
        schema_status = validate_file(input_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"INVALID: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(f"VALID: {input_path}")
    print(schema_status)
    print("Acquisition checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
