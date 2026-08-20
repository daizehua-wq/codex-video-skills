#!/usr/bin/env python3
"""Validate a comprehension-led director_plan/3.1 and broll_requests/3.0 handoff."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import validate_broll_requests as broll_validator


TOLERANCE = 0.15
MODE_SUMMARY_KEYS = {
    "AROLL_FULL": "aroll_full_sec",
    "SOURCE_EVIDENCE": "source_evidence_sec",
    "PRODUCT_DEMO": "product_demo_sec",
    "MOTION_GRAPHICS": "motion_graphics_sec",
    "ILLUSTRATIVE_METAPHOR": "illustrative_metaphor_sec",
    "TEXT_EMPHASIS": "text_emphasis_sec",
}
PROHIBITED_JUSTIFICATIONS = (
    "覆盖率",
    "丰富画面",
    "避免单调",
    "增加节奏",
    "为了放",
    "hide the a-roll",
    "visual variety",
    "coverage target",
)
NON_INFORMATION_REVEALS = {
    "增加动感",
    "让画面动起来",
    "保持画面活跃",
    "add motion",
    "make it dynamic",
    "keep the frame active",
}


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


def close(left: float, right: float, tolerance: float = TOLERANCE) -> bool:
    return abs(left - right) <= tolerance


def validate_timeline(plan: dict) -> tuple[dict[str, dict], list[str]]:
    project = plan.get("project", {})
    broll_validator.readiness_validate(project)
    runtime = project.get("runtime_sec")
    segments = plan.get("segments")
    if not isinstance(segments, list) or not segments:
        fail("segments must be a non-empty array")

    ids = [segment.get("segment_id") for segment in segments]
    if len(ids) != len(set(ids)):
        fail("segment IDs must be unique")
    if not close(segments[0].get("start_sec", -1), 0):
        fail("timeline must start at zero")

    segment_map = {}
    asset_refs = []
    durations = {key: 0.0 for key in MODE_SUMMARY_KEYS.values()}
    previous_end = 0.0

    for index, segment in enumerate(segments):
        segment_id = segment.get("segment_id", f"segment[{index}]")
        start = segment.get("start_sec")
        end = segment.get("end_sec")
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            fail(f"{segment_id}: start_sec and end_sec must be numeric")
        if end <= start:
            fail(f"{segment_id}: end_sec must be greater than start_sec")
        if not close(start, previous_end):
            fail(f"{segment_id}: timeline gap or overlap after {previous_end}")
        previous_end = end
        segment_map[segment_id] = segment

        mode = segment.get("mode")
        if mode not in MODE_SUMMARY_KEYS:
            fail(f"{segment_id}: unsupported mode {mode!r}")
        durations[MODE_SUMMARY_KEYS[mode]] += end - start
        treatment = segment.get("visual_treatment", {})
        request_ids = treatment.get("asset_request_ids", [])
        asset_refs.extend(request_ids)

        human_presence = segment.get("human_presence")
        return_reason = segment.get("return_to_aroll_reason")
        if mode == "AROLL_FULL":
            if human_presence != "full_frame":
                fail(f"{segment_id}: AROLL_FULL requires full_frame human presence")
            if not return_reason:
                fail(f"{segment_id}: AROLL_FULL requires return_to_aroll_reason")
        elif return_reason is not None:
            fail(f"{segment_id}: non-A-roll segment must set return_to_aroll_reason to null")

        representation = segment.get("representation", {})
        if representation.get("ai_generated") is True and representation.get("disclosure_required") is not True:
            fail(f"{segment_id}: AI-generated representation requires disclosure")
        if mode in {"SOURCE_EVIDENCE", "PRODUCT_DEMO"} and representation.get("ai_generated") is True:
            fail(f"{segment_id}: generated visuals cannot be evidence or product observation")
        if mode == "ILLUSTRATIVE_METAPHOR":
            if representation.get("literal_status") != "metaphor":
                fail(f"{segment_id}: illustrative metaphor must be marked non-literal")
            if not str(representation.get("misinterpretation_risk") or "").strip():
                fail(f"{segment_id}: illustrative metaphor requires misinterpretation_risk")
            if segment.get("visual_function") == "prove":
                fail(f"{segment_id}: illustrative metaphor cannot prove a claim")
            if request_ids:
                fail(f"{segment_id}: illustrative metaphor cannot create acquisition requests")

        justification = " ".join(
            str(segment.get(field) or "")
            for field in ("purpose", "why_visual_needed", "failure_if_absent")
        ).lower()
        prohibited = [phrase for phrase in PROHIBITED_JUSTIFICATIONS if phrase in justification]
        if prohibited:
            fail(f"{segment_id}: prohibited visual justification {prohibited}")

        for beat in treatment.get("beats", []):
            at_sec = beat.get("at_sec")
            if not isinstance(at_sec, (int, float)) or at_sec < start - TOLERANCE or at_sec > end + TOLERANCE:
                fail(f"{segment_id}: treatment beat {at_sec!r} lies outside the segment")
            for field in ("state_before", "action", "state_after", "information_gained"):
                if not str(beat.get(field, "")).strip():
                    fail(f"{segment_id}: treatment beat requires {field}")
            if str(beat.get("information_gained", "")).strip().lower() in NON_INFORMATION_REVEALS:
                fail(f"{segment_id}: treatment beat describes motion without information")

        if mode == "SOURCE_EVIDENCE":
            if not treatment.get("focus_regions"):
                fail(f"{segment_id}: source evidence requires focus_regions")
            if len(treatment.get("beats", [])) < 2:
                fail(f"{segment_id}: source evidence requires identity and detail beats")
            sequence = treatment.get("evidence_sequence")
            if not isinstance(sequence, dict):
                fail(f"{segment_id}: source evidence requires evidence_sequence")
            for field in ("source_identity_frame", "evidence_region", "highlight_text"):
                if not str(sequence.get(field, "")).strip():
                    fail(f"{segment_id}: evidence_sequence requires {field}")
            read_time = sequence.get("minimum_read_time_sec")
            if not isinstance(read_time, (int, float)) or read_time <= 0:
                fail(f"{segment_id}: evidence_sequence requires positive minimum_read_time_sec")
        if mode in {"MOTION_GRAPHICS", "ILLUSTRATIVE_METAPHOR"}:
            gained = {beat.get("information_gained", "").strip() for beat in treatment.get("beats", [])}
            if not gained or "" in gained:
                fail(f"{segment_id}: every semantic beat must reveal information")

    if not close(previous_end, runtime):
        fail(f"timeline ends at {previous_end}, not measured runtime {runtime}")

    summary = plan.get("visual_summary", {})
    for key, calculated in durations.items():
        if not close(summary.get(key, -1), calculated):
            fail(f"visual_summary.{key} is {summary.get(key)!r}; calculated {calculated:.3f}")
    intervention = sum(value for key, value in durations.items() if key != "aroll_full_sec")
    if not close(summary.get("visual_intervention_union_sec", -1), intervention):
        fail("visual_summary.visual_intervention_union_sec does not match the timeline")
    expected_ratio = intervention / runtime
    if abs(summary.get("observed_ratio", -1) - expected_ratio) > 0.002:
        fail("visual_summary.observed_ratio does not match the timeline")
    if summary.get("coverage_target", "missing") is not None:
        fail("visual_summary.coverage_target must be null")

    duplicate_refs = [request_id for request_id, count in Counter(asset_refs).items() if count != 1]
    if duplicate_refs:
        fail(f"asset request IDs must be referenced once: {duplicate_refs}")
    return segment_map, asset_refs


def validate_visual_anchors(plan: dict, segment_map: dict[str, dict]) -> None:
    anchors = plan.get("visual_anchors")
    if not isinstance(anchors, list):
        fail("visual_anchors must be an array")
    anchor_ids = [anchor.get("id") for anchor in anchors]
    if len(anchor_ids) != len(set(anchor_ids)):
        fail("visual anchor IDs must be unique")
    anchor_map = {anchor.get("id"): anchor for anchor in anchors}

    for anchor_id, anchor in anchor_map.items():
        declared = anchor.get("reuse_segment_ids", [])
        for segment_id in declared:
            segment = segment_map.get(segment_id)
            if not segment:
                fail(f"{anchor_id}: unknown reuse segment {segment_id}")
            if segment.get("visual_anchor_id") != anchor_id:
                fail(f"{anchor_id}: {segment_id} does not reference the declared anchor")

    for segment_id, segment in segment_map.items():
        anchor_id = segment.get("visual_anchor_id")
        if anchor_id is None:
            continue
        anchor = anchor_map.get(anchor_id)
        if not anchor:
            fail(f"{segment_id}: unknown visual_anchor_id {anchor_id}")
        if segment_id not in anchor.get("reuse_segment_ids", []):
            fail(f"{segment_id}: anchor {anchor_id} does not declare this reuse")


def validate_mapping(plan: dict, requests_doc: dict, segment_map: dict, asset_refs: list[str]) -> None:
    plan_project = plan.get("project", {})
    request_project = requests_doc.get("project", {})
    for key in ("name", "runtime_sec", "timing_basis", "handoff_status", "aspect_ratio", "style_profile", "visual_policy"):
        if plan_project.get(key) != request_project.get(key):
            fail(f"project.{key} differs between director plan and B-roll requests")

    requests = requests_doc.get("requests", [])
    request_ids = [request.get("id") for request in requests]
    if set(request_ids) != set(asset_refs):
        missing = sorted(set(asset_refs) - set(request_ids))
        unrequested = sorted(set(request_ids) - set(asset_refs))
        fail(f"director/request mapping differs; missing={missing}, unreferenced={unrequested}")

    for request in requests:
        request_id = request["id"]
        segment_id = request["segment_id"]
        segment = segment_map.get(segment_id)
        if not segment:
            fail(f"{request_id}: unknown segment_id {segment_id}")
        if request_id not in segment["visual_treatment"]["asset_request_ids"]:
            fail(f"{request_id}: not referenced by its declared segment {segment_id}")
        window = request["coverage_window"]
        if window["start_sec"] < segment["start_sec"] - TOLERANCE or window["end_sec"] > segment["end_sec"] + TOLERANCE:
            fail(f"{request_id}: request window lies outside {segment_id}")

        mode = segment["mode"]
        if mode == "SOURCE_EVIDENCE" and request["asset_class"] not in {
            "source_page_screenshot", "source_document", "source_video", "source_backed_diagram"
        }:
            fail(f"{request_id}: asset_class does not match SOURCE_EVIDENCE")
        if mode == "PRODUCT_DEMO" and request["asset_class"] not in {
            "product_ui_still", "product_demo_video"
        }:
            fail(f"{request_id}: asset_class does not match PRODUCT_DEMO")


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "usage: validate_director_handoff.py /path/to/director_plan.json /path/to/broll_requests.json",
            file=sys.stderr,
        )
        return 2

    plan_path = Path(sys.argv[1]).resolve()
    request_path = Path(sys.argv[2]).resolve()
    skill_root = Path(__file__).resolve().parents[1]
    try:
        plan = load_json(plan_path)
        requests_doc = load_json(request_path)
        plan_schema_status = schema_validate(plan, skill_root / "references" / "director_plan.schema.json")
        request_schema_status = broll_validator.schema_validate(
            requests_doc,
            skill_root / "references" / "broll_requests.schema.json",
        )
        broll_validator.relational_validate(requests_doc)
        segment_map, asset_refs = validate_timeline(plan)
        validate_visual_anchors(plan, segment_map)
        validate_mapping(plan, requests_doc, segment_map, asset_refs)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"INVALID: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    print(f"VALID: {plan_path}")
    print(f"VALID: {request_path}")
    print(f"Director plan: {plan_schema_status}")
    print(f"B-roll requests: {request_schema_status}")
    print("Timeline, necessity metadata, visual anchors, semantic beats, metaphor safety, coverage summary and request mapping passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
