#!/usr/bin/env python3
"""Validate a video-script semantic and factual handoff."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path


PACKAGE_HEADINGS = (
    "## A. 核心命题",
    "## B. 写稿逻辑",
    "## C. 完整口播稿",
    "## D. HKRR 自检",
)
HKRR_THRESHOLDS = {"H": 3, "K": 4, "R": 4, "Rhythm": 4}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def narration_body(narration: str) -> str:
    """Remove the first Markdown H1 title and return the spoken body."""
    lines = narration.splitlines()
    for index, line in enumerate(lines):
        if not line.strip():
            continue
        if line.lstrip().startswith("# "):
            del lines[index]
        break
    return "\n".join(lines).strip()


def normalize_text(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines()).strip()


def extract_package_sections(package: str, errors: list[str]) -> dict[str, str]:
    positions = [package.find(heading) for heading in PACKAGE_HEADINGS]
    for heading, position in zip(PACKAGE_HEADINGS, positions):
        if position < 0:
            errors.append(f"script package missing heading: {heading}")
    if any(position < 0 for position in positions):
        return {}
    if positions != sorted(positions):
        errors.append("script package sections must remain in A/B/C/D order")
        return {}

    sections: dict[str, str] = {}
    for index, heading in enumerate(PACKAGE_HEADINGS):
        start = positions[index] + len(heading)
        end = positions[index + 1] if index + 1 < len(positions) else len(package)
        content = package[start:end].strip()
        if not content:
            errors.append(f"script package section is empty: {heading}")
        sections[heading] = content
    return sections


def append_anchor_error(errors: list[str], body: str, label: str, anchor: str | None) -> int | None:
    if anchor is None:
        return None
    position = body.find(anchor)
    if position < 0:
        errors.append(f"{label}: anchor not found in narration body")
        return None
    return position


def validate_fact_ids(
    errors: list[str],
    facts: dict[str, dict],
    owner: str,
    fact_ids: list[str],
) -> None:
    for fact_id in fact_ids:
        fact = facts.get(fact_id)
        if fact is None:
            errors.append(f"{owner}: unknown fact ID {fact_id}")
            continue
        if fact.get("script_use") == "prohibited":
            errors.append(f"{owner}: prohibited fact used: {fact_id}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the four-part script package and machine handoff")
    parser.add_argument("fact_card", type=Path)
    parser.add_argument("narration", type=Path)
    parser.add_argument("script_package", type=Path)
    parser.add_argument("script_claims", type=Path)
    args = parser.parse_args()

    fact_card = load_json(args.fact_card)
    mapping = load_json(args.script_claims)
    narration = args.narration.read_text(encoding="utf-8")
    body = narration_body(narration)
    package = args.script_package.read_text(encoding="utf-8")
    schema_path = Path(__file__).resolve().parent.parent / "references" / "script-claims.schema.json"
    schema = load_json(schema_path)
    errors: list[str] = []

    try:
        import jsonschema

        validator = jsonschema.Draft202012Validator(schema)
        for error in sorted(validator.iter_errors(mapping), key=lambda item: list(item.path)):
            location = ".".join(str(part) for part in error.path) or "root"
            errors.append(f"schema {location}: {error.message}")
    except ImportError:
        print("WARN: jsonschema is unavailable; running relational checks only", file=sys.stderr)

    if fact_card.get("publication_status") == "blocked":
        errors.append("blocked fact card cannot produce a publishable script")
    if mapping.get("project_id") != fact_card.get("project_id"):
        errors.append("project_id does not match fact card")

    package_path = Path(str(mapping.get("script_package_path") or ""))
    if package_path and package_path.resolve() != args.script_package.resolve():
        errors.append("script_package_path does not match the validated package")

    package_sections = extract_package_sections(package, errors)
    editorial = mapping.get("editorial_design", {})
    section_a = package_sections.get(PACKAGE_HEADINGS[0], "")
    for field in ("core_thesis", "core_question", "audience_relevance", "final_judgment"):
        value = str(editorial.get(field) or "").strip()
        if value and value not in section_a:
            errors.append(f"script package A must contain editorial_design.{field}")
    section_b = package_sections.get(PACKAGE_HEADINGS[1], "")
    logic_chain = editorial.get("logic_chain", [])
    rendered_logic = " → ".join(str(item) for item in logic_chain)
    if rendered_logic and rendered_logic not in section_b:
        errors.append("script package B must contain the declared logic chain")
    section_c = package_sections.get(PACKAGE_HEADINGS[2], "")
    if section_c and normalize_text(section_c) != normalize_text(body):
        errors.append("script package C must exactly match narration.md spoken body")

    facts = {claim.get("id"): claim for claim in fact_card.get("claims", [])}
    mapping_ids: list[str] = []
    claim_anchors: list[str] = []

    for use in mapping.get("claim_uses", []):
        mapping_id = use.get("id", "<missing>")
        mapping_ids.append(mapping_id)
        anchor = use.get("exact_anchor", "")
        claim_anchors.append(anchor)
        if anchor and anchor not in body:
            errors.append(f"{mapping_id}: exact_anchor not found in narration body")

        fact_ids = use.get("fact_ids", [])
        validate_fact_ids(errors, facts, mapping_id, fact_ids)
        for fact_id in fact_ids:
            fact = facts.get(fact_id)
            if fact and fact.get("script_use") == "attributed" and not use.get("attribution_present"):
                errors.append(f"{mapping_id}: attributed fact lacks attribution flag: {fact_id}")

    if len(mapping_ids) != len(set(mapping_ids)):
        errors.append("script claim IDs must be unique")
    if len(claim_anchors) != len(set(claim_anchors)):
        errors.append("claim exact anchors must be unique")
    if mapping.get("unmapped_assertions"):
        errors.append("unmapped_assertions must be empty at completion")

    beats = mapping.get("narrative_beats", [])
    beat_ids = [beat.get("id") for beat in beats]
    if len(beat_ids) != len(set(beat_ids)):
        errors.append("narrative beat IDs must be unique")

    beat_positions: list[int] = []
    for index, beat in enumerate(beats):
        beat_id = beat.get("id", f"beat[{index}]")
        anchor = beat.get("exact_anchor", "")
        position = body.find(anchor) if anchor else -1
        if position < 0:
            errors.append(f"{beat_id}: exact_anchor not found in narration body")
        else:
            beat_positions.append(position)
        fact_ids = beat.get("fact_ids", [])
        validate_fact_ids(errors, facts, beat_id, fact_ids)
        if beat.get("statement_type") in {"fact", "attributed_fact"} and not fact_ids:
            errors.append(f"{beat_id}: factual beat requires fact_ids")
        if index < len(beats) - 1 and not str(beat.get("leads_to") or "").strip():
            errors.append(f"{beat_id}: non-final beat requires leads_to")
        if index == len(beats) - 1 and beat.get("leads_to") is not None:
            errors.append(f"{beat_id}: final beat must set leads_to to null")

    if beat_positions != sorted(beat_positions):
        errors.append("narrative beats must follow narration order")
    if beats:
        roles = [beat.get("role") for beat in beats]
        if roles[0] != "hook":
            errors.append("the first narrative beat must be the hook")
        for required_role in ("question", "promise", "takeaway"):
            if required_role not in roles:
                errors.append(f"narrative beats require a {required_role} role")
        if roles[-1] != "takeaway":
            errors.append("the final narrative beat must be the takeaway")

    structure = mapping.get("structure", {})
    opening = structure.get("opening", {})
    opening_positions: list[int] = []
    for field in ("tension_anchor", "source_anchor", "central_question_anchor", "viewing_promise_anchor"):
        position = append_anchor_error(errors, body, f"structure.opening.{field}", opening.get(field))
        if position is not None:
            opening_positions.append(position)
    opening_limit = max(180, int(len(body) * 0.35))
    if any(position > opening_limit for position in opening_positions):
        errors.append("opening tension, source, question and promise must appear near the opening")

    ending = structure.get("ending", {})
    ending_positions: list[int] = []
    for field in ("opening_callback_anchor", "transferable_takeaway_anchor"):
        position = append_anchor_error(errors, body, f"structure.ending.{field}", ending.get(field))
        if position is not None:
            ending_positions.append(position)
    ending_floor = int(len(body) * 0.65)
    if any(position < ending_floor for position in ending_positions):
        errors.append("ending callback and takeaway must appear in the final portion of narration")
    if ending.get("adds_new_factual_claims") is not False:
        errors.append("structure.ending.adds_new_factual_claims must be false")

    duration = mapping.get("duration_estimate", {})
    calculated_chars = sum(1 for character in body if not character.isspace())
    if duration.get("non_whitespace_chars") != calculated_chars:
        errors.append(
            "duration_estimate.non_whitespace_chars does not match narration body "
            f"({duration.get('non_whitespace_chars')!r} != {calculated_chars})"
        )
    rate = duration.get("assumed_chars_per_second")
    estimated = duration.get("estimated_duration_seconds")
    if isinstance(rate, (int, float)) and rate > 0 and isinstance(estimated, (int, float)):
        calculated_estimate = calculated_chars / rate
        if not math.isclose(estimated, calculated_estimate, abs_tol=0.6):
            errors.append(
                "duration_estimate.estimated_duration_seconds does not match character count and rate "
                f"({estimated!r} != {calculated_estimate:.2f})"
            )
    else:
        calculated_estimate = None
        errors.append("duration_estimate requires a positive rate and numeric estimated duration")

    target = mapping.get("target", {}).get("duration_seconds")
    target_delta = duration.get("target_delta_seconds")
    if target is None:
        if target_delta is not None:
            errors.append("duration_estimate.target_delta_seconds must be null when no target is set")
    elif calculated_estimate is not None:
        calculated_delta = calculated_estimate - target
        if not isinstance(target_delta, (int, float)) or not math.isclose(target_delta, calculated_delta, abs_tol=0.6):
            errors.append(
                "duration_estimate.target_delta_seconds does not match estimated minus target duration "
                f"({target_delta!r} != {calculated_delta:.2f})"
            )
        allowed_delta = max(15.0, target * 0.15)
        if abs(calculated_delta) > allowed_delta:
            errors.append(
                f"estimated duration misses target by {calculated_delta:.2f}s; allowed {allowed_delta:.2f}s"
            )

    hkrr = mapping.get("hkrr_review", {})
    dimensions = hkrr.get("dimensions", {})
    scores = {
        dimension: detail.get("score")
        for dimension, detail in dimensions.items()
        if isinstance(detail, dict)
    }
    thresholds_met = all(
        isinstance(scores.get(dimension), int) and scores[dimension] >= threshold
        for dimension, threshold in HKRR_THRESHOLDS.items()
    )
    if hkrr.get("thresholds_met") is not thresholds_met:
        errors.append("hkrr_review.thresholds_met does not match the dimension scores")
    if not thresholds_met:
        errors.append("final HKRR scores must reach H>=3, K>=4, R>=4 and Rhythm>=4")
        if hkrr.get("recommend_further_revision") is not True:
            errors.append("HKRR below threshold requires recommend_further_revision=true")

    numeric_scores = {key: value for key, value in scores.items() if isinstance(value, int)}
    if numeric_scores:
        minimum = min(numeric_scores.values())
        actual_weakest = {key for key, value in numeric_scores.items() if value == minimum}
        declared_weakest = set(hkrr.get("weakest_dimensions", []))
        if declared_weakest != actual_weakest:
            errors.append(
                f"hkrr_review.weakest_dimensions is {sorted(declared_weakest)}; "
                f"calculated {sorted(actual_weakest)}"
            )

    section_d = package_sections.get(PACKAGE_HEADINGS[3], "")
    for dimension in HKRR_THRESHOLDS:
        detail = dimensions.get(dimension, {})
        rationale = str(detail.get("rationale") or "").strip() if isinstance(detail, dict) else ""
        if rationale and rationale not in section_d:
            errors.append(f"script package D must contain the {dimension} rationale")
        if dimension not in section_d:
            errors.append(f"script package D must report {dimension}")
    for label in ("当前最弱项", "是否达到最低标准", "是否建议继续修改"):
        if label not in section_d:
            errors.append(f"script package D must contain {label}")

    checks = mapping.get("checks", {})
    required_true = [
        "all_factual_claims_mapped", "quotes_verified", "numbers_verified", "scope_reviewed",
        "repetition_reviewed", "read_aloud_completed", "opening_promise_reviewed",
        "fact_interpretation_separated", "beat_progression_reviewed",
        "ending_closure_reviewed", "duration_reviewed", "core_thesis_locked",
        "writing_logic_reviewed", "hkrr_review_completed", "human_package_matches_narration",
    ]
    for field in required_true:
        if checks.get(field) is not True:
            errors.append(f"checks.{field} must be true")
    if checks.get("prohibited_claims_used") is not False:
        errors.append("checks.prohibited_claims_used must be false")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        f"OK: {len(beats)} narrative beats, {len(mapping.get('claim_uses', []))} mapped factual assertions, "
        f"HKRR={scores}, estimated={calculated_estimate:.1f}s, project={mapping.get('project_id')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
