#!/usr/bin/env python3
"""Validate a video-script semantic and factual handoff."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path


PACKAGE_HEADINGS = (
    "## A. 核心命题",
    "## B. 写稿逻辑",
    "## C. 完整口播稿",
    "## D. HKRR 自检",
)
HKRR_THRESHOLDS = {"H": 3, "K": 4, "R": 4, "Rhythm": 4}
BOUNDARY_MAX_DISTANCE_CHARS = 500
CHINESE_SENTENCE_WARNING_CHARS = 52
CHINESE_SENTENCE_HARD_LIMIT_CHARS = 72
CHINESE_CLAUSE_PUNCTUATION_LIMIT = 5
AUDIT_LANGUAGE_LIMIT = 4
AUDIT_LANGUAGE_MARKERS = (
    "注意",
    "口径",
    "边界要说清楚",
    "这里要说清楚",
    "复核",
    "审核",
    "独立验证",
    "建议路径",
    "实施记录",
)
FACT_CARD_1_5_CHECKS = (
    "fact_card_1_5_controls_reviewed",
    "handoff_roles_reviewed",
    "title_controls_reviewed",
    "metric_scope_preserved",
    "causality_status_preserved",
    "forbidden_transformations_reviewed",
    "required_spoken_boundaries_reviewed",
    "implementation_parameterization_reviewed",
)


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


def markdown_h1_titles(markdown: str) -> list[str]:
    """Return level-one headings outside fenced code blocks."""
    titles: list[str] = []
    in_fence = False
    for line in markdown.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if not in_fence and stripped.startswith("# "):
            titles.append(stripped[2:].strip())
    return titles


def normalize_text(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines()).strip()


def extract_package_sections(package: str, errors: list[str]) -> dict[str, str]:
    positions = [package.find(heading) for heading in PACKAGE_HEADINGS]
    for heading, position in zip(PACKAGE_HEADINGS, positions):
        count = package.count(heading)
        if count != 1:
            errors.append(f"script package must contain heading exactly once: {heading} (found {count})")
        if position < 0:
            continue
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
        if fact.get("handoff_role") == "fact_card_only":
            errors.append(f"{owner}: fact-card-only claim used in script: {fact_id}")


def required_fact_controls(fact: dict) -> set[str]:
    """Return schema 1.5 controls a script use must explicitly preserve."""
    controls = {
        "event_stage",
        "temporal_scope",
        "causality_status",
        "forbidden_transformations",
    }
    if fact.get("claim_type") == "number" or fact.get("metric_scope") is not None:
        controls.add("metric_scope")
    if fact.get("spoken_attribution_required") is True:
        controls.add("spoken_attribution")
    return controls


def anchor_distance(body: str, first: str, second: str) -> int | None:
    """Return the distance between two narration anchors, or None if either is absent."""
    first_position = body.find(first)
    second_position = body.find(second)
    if first_position < 0 or second_position < 0:
        return None
    first_end = first_position + len(first)
    second_end = second_position + len(second)
    if first_position <= second_position:
        return max(0, second_position - first_end)
    return max(0, first_position - second_end)


def spoken_sentences(body: str) -> list[str]:
    """Split narration into sentence-like units while preserving semicolon breath load."""
    pattern = r"[。！？!?]+|(?<!\d)\.(?=\s|$)"
    return [item.strip() for item in re.split(pattern, body) if item.strip()]


def spoken_char_count(text: str) -> int:
    """Approximate Mandarin breath load: CJK characters plus non-CJK word tokens."""
    cjk_count = len(re.findall(r"[\u3400-\u9fff]", text))
    non_cjk = re.sub(r"[\u3400-\u9fff]", " ", text)
    word_count = len(re.findall(r"[A-Za-z0-9]+(?:[._/-][A-Za-z0-9]+)*", non_cjk))
    return cjk_count + word_count


def exception_covers(text: str, exceptions: list[dict]) -> bool:
    return any(
        str(item.get("anchor") or "").strip().rstrip("。！？!?.") in text
        for item in exceptions
    )


def validate_oral_exceptions(
    errors: list[str],
    body: str,
    label: str,
    exceptions: list[dict],
) -> None:
    seen_anchors: set[str] = set()
    for index, item in enumerate(exceptions):
        anchor = str(item.get("anchor") or "").strip()
        reason = str(item.get("reason") or "").strip()
        if not anchor:
            errors.append(f"{label}[{index}].anchor must be non-empty")
        elif anchor not in body:
            errors.append(f"{label}[{index}]: anchor not found in narration body")
        elif anchor in seen_anchors:
            errors.append(f"{label}: duplicate exception anchor")
        else:
            seen_anchors.add(anchor)
        if not reason:
            errors.append(f"{label}[{index}].reason must be non-empty")


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
    warnings: list[str] = []
    schema_validation_available = False

    try:
        import jsonschema

        schema_validation_available = True
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

    for field_name, actual_path in (
        ("fact_card_path", args.fact_card),
        ("narration_path", args.narration),
        ("script_package_path", args.script_package),
    ):
        mapped_path = str(mapping.get(field_name) or "").strip()
        if not mapped_path:
            errors.append(f"{field_name} must be a non-empty path")
        elif Path(mapped_path).expanduser().resolve() != actual_path.resolve():
            errors.append(f"{field_name} does not match the validated file")

    package_sections = extract_package_sections(package, errors)
    package_titles = markdown_h1_titles(package)
    narration_titles = markdown_h1_titles(narration)
    if len(package_titles) != 1:
        errors.append(f"script package must contain exactly one H1; found {len(package_titles)}")
    if len(narration_titles) != 1:
        errors.append(f"narration must contain exactly one H1; found {len(narration_titles)}")
    if len(package_titles) == 1 and len(narration_titles) == 1 and package_titles[0] != narration_titles[0]:
        errors.append("script package and narration H1 titles must match exactly")
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
    transferability = fact_card.get("transferability", {})
    lessons = {lesson.get("id"): lesson for lesson in transferability.get("lessons", [])}
    implementation_path = transferability.get("implementation_path", {})
    implementation_stages = {
        stage.get("id"): stage for stage in implementation_path.get("stages", [])
    }
    fact_card_version = str(fact_card.get("schema_version") or "")
    mapping_version = mapping.get("schema_version")
    if fact_card_version == "1.5" and mapping_version != "1.4":
        errors.append("fact-card schema 1.5 requires script_claims schema 1.4")
    elif transferability.get("applicable") is True and mapping_version not in {"1.3", "1.4"}:
        errors.append("case-based fact card with transferability requires script_claims schema 1.3 or 1.4")
    if mapping_version == "1.4" and not schema_validation_available:
        for field in (
            "title_fact_ids",
            "title_limitations_preserved",
            "title_scope_note",
            "primary_lesson_override_reason",
        ):
            if field not in editorial:
                errors.append(f"editorial_design.{field} is required by script_claims schema 1.4")
        if "boundary_uses" not in mapping:
            errors.append("boundary_uses is required by script_claims schema 1.4")
        if "oral_delivery_review" not in mapping:
            errors.append("oral_delivery_review is required by script_claims schema 1.4")
        else:
            oral_review_fields = (
                "language",
                "status",
                "logic_order_reviewed",
                "actor_action_reviewed",
                "qualification_placement_reviewed",
                "abstraction_reviewed",
                "audit_language_reviewed",
                "read_aloud_revision_completed",
                "long_sentence_exceptions",
                "audit_language_exceptions",
                "unresolved_flags",
            )
            oral_review = mapping.get("oral_delivery_review", {})
            for field in oral_review_fields:
                if field not in oral_review:
                    errors.append(f"oral_delivery_review.{field} is required by schema 1.4")
        for index, use in enumerate(mapping.get("claim_uses", [])):
            for field in ("preserved_controls", "forbidden_transformations_absent"):
                if field not in use:
                    errors.append(f"claim_uses[{index}].{field} is required by schema 1.4")
        for index, use in enumerate(mapping.get("lesson_uses", [])):
            for field in (
                "required_boundary_anchor",
                "forbidden_generalizations_absent",
                "implementation_stage_ids",
                "implementation_guidance_disclosed",
                "implementation_parameters_preserved",
            ):
                if field not in use:
                    errors.append(f"lesson_uses[{index}].{field} is required by schema 1.4")

    selected_lesson_ids = editorial.get("selected_lesson_ids", [])
    for lesson_id in selected_lesson_ids:
        if lesson_id not in lessons:
            errors.append(f"editorial_design: unknown selected lesson ID {lesson_id}")
    if transferability.get("applicable") is True and not selected_lesson_ids:
        errors.append("case-based script requires at least one selected_lesson_id")
    if mapping_version in {"1.3", "1.4"}:
        audience_decision = str(editorial.get("audience_decision") or "").strip()
        if audience_decision and audience_decision not in section_a:
            errors.append("script package A must contain editorial_design.audience_decision")

    title_fact_ids = editorial.get("title_fact_ids", [])
    if mapping_version == "1.4":
        validate_fact_ids(errors, facts, "editorial_design.title_fact_ids", title_fact_ids)
        title = narration_titles[0] if len(narration_titles) == 1 else ""
        if any(character.isdigit() for character in title) and not title_fact_ids:
            errors.append("numeric title requires at least one editorial_design.title_fact_id")
        if title_fact_ids and not str(editorial.get("title_scope_note") or "").strip():
            errors.append("title_fact_ids require a non-empty editorial_design.title_scope_note")
        for fact_id in title_fact_ids:
            fact = facts.get(fact_id)
            if fact is None:
                continue
            title_use = fact.get("title_use")
            if title_use == "prohibited":
                errors.append(f"title uses claim prohibited from titles: {fact_id}")
            if title_use == "conditional" and editorial.get("title_limitations_preserved") is not True:
                errors.append(f"conditional title claim must preserve title limitations: {fact_id}")

        primary_lesson_ids = {
            lesson_id for lesson_id, lesson in lessons.items() if lesson.get("priority") == "primary"
        }
        if transferability.get("applicable") is True and len(primary_lesson_ids) != 1:
            errors.append("fact-card schema 1.5 must expose exactly one primary lesson")
        primary_missing = primary_lesson_ids - set(selected_lesson_ids)
        override_reason = str(editorial.get("primary_lesson_override_reason") or "").strip()
        if primary_missing and not override_reason:
            errors.append("excluding the primary lesson requires primary_lesson_override_reason")
        if not primary_missing and override_reason:
            errors.append("primary_lesson_override_reason must be null when the primary lesson is selected")

    mapping_ids: list[str] = []
    claim_anchors: list[str] = []
    used_fact_ids: set[str] = set()

    for use in mapping.get("claim_uses", []):
        mapping_id = use.get("id", "<missing>")
        mapping_ids.append(mapping_id)
        anchor = use.get("exact_anchor", "")
        claim_anchors.append(anchor)
        if anchor and anchor not in body:
            errors.append(f"{mapping_id}: exact_anchor not found in narration body")

        fact_ids = use.get("fact_ids", [])
        used_fact_ids.update(fact_ids)
        validate_fact_ids(errors, facts, mapping_id, fact_ids)
        for fact_id in fact_ids:
            fact = facts.get(fact_id)
            if fact and fact.get("script_use") == "attributed" and not use.get("attribution_present"):
                errors.append(f"{mapping_id}: attributed fact lacks attribution flag: {fact_id}")
            if fact_card_version == "1.5" and fact:
                if fact.get("spoken_attribution_required") is True and not use.get("attribution_present"):
                    errors.append(f"{mapping_id}: spoken attribution required for {fact_id}")
                declared_controls = set(use.get("preserved_controls", []))
                missing_controls = sorted(required_fact_controls(fact) - declared_controls)
                if missing_controls:
                    errors.append(
                        f"{mapping_id}: missing preserved controls for {fact_id}: {missing_controls}"
                    )
                if use.get("forbidden_transformations_absent") is not True:
                    errors.append(
                        f"{mapping_id}: forbidden_transformations_absent must be true for {fact_id}"
                    )

    if len(mapping_ids) != len(set(mapping_ids)):
        errors.append("script claim IDs must be unique")
    if len(claim_anchors) != len(set(claim_anchors)):
        errors.append("claim exact anchors must be unique")
    if mapping.get("unmapped_assertions"):
        errors.append("unmapped_assertions must be empty at completion")

    if fact_card_version == "1.5":
        core_proof_ids = {
            fact_id for fact_id, fact in facts.items() if fact.get("handoff_role") == "core_proof"
        }
        missing_core_proof = sorted(core_proof_ids - used_fact_ids)
        if missing_core_proof:
            errors.append(f"core_proof claims are not mapped in narration: {missing_core_proof}")

        boundary_use_ids: list[str] = []
        mapped_boundary_ids: set[str] = set()
        for boundary_use in mapping.get("boundary_uses", []):
            boundary_use_id = boundary_use.get("id", "<missing>")
            boundary_use_ids.append(boundary_use_id)
            boundary_fact_ids = boundary_use.get("boundary_fact_ids", [])
            bounded_fact_ids = boundary_use.get("bounded_fact_ids", [])
            validate_fact_ids(errors, facts, boundary_use_id, boundary_fact_ids + bounded_fact_ids)
            for fact_id in boundary_fact_ids:
                fact = facts.get(fact_id)
                if fact and fact.get("handoff_role") != "required_boundary":
                    errors.append(f"{boundary_use_id}: {fact_id} is not a required_boundary claim")
                mapped_boundary_ids.add(fact_id)
            unmapped_bounded = sorted(set(bounded_fact_ids) - used_fact_ids)
            if unmapped_bounded:
                errors.append(
                    f"{boundary_use_id}: bounded facts are not mapped in narration: {unmapped_bounded}"
                )
            unmapped_boundaries = sorted(set(boundary_fact_ids) - used_fact_ids)
            if unmapped_boundaries:
                errors.append(
                    f"{boundary_use_id}: boundary facts are not mapped in narration: {unmapped_boundaries}"
                )
            boundary_anchor = str(boundary_use.get("boundary_anchor") or "")
            bounded_anchor = str(boundary_use.get("bounded_anchor") or "")
            distance = anchor_distance(body, boundary_anchor, bounded_anchor)
            if distance is None:
                if boundary_anchor not in body:
                    errors.append(f"{boundary_use_id}: boundary_anchor not found in narration body")
                if bounded_anchor not in body:
                    errors.append(f"{boundary_use_id}: bounded_anchor not found in narration body")
            elif distance > BOUNDARY_MAX_DISTANCE_CHARS:
                errors.append(
                    f"{boundary_use_id}: required boundary is {distance} characters from its claim; "
                    f"maximum is {BOUNDARY_MAX_DISTANCE_CHARS}"
                )
        if len(boundary_use_ids) != len(set(boundary_use_ids)):
            errors.append("boundary-use IDs must be unique")
        required_boundary_ids = {
            fact_id for fact_id, fact in facts.items()
            if fact.get("handoff_role") == "required_boundary"
        }
        missing_boundaries = sorted(required_boundary_ids - mapped_boundary_ids)
        if missing_boundaries:
            errors.append(f"required_boundary claims lack a proximity mapping: {missing_boundaries}")

    lesson_use_ids: list[str] = []
    lesson_anchors: list[str] = []
    used_lesson_ids: set[str] = set()
    bounded_lesson_ids: set[str] = set()
    for use in mapping.get("lesson_uses", []):
        use_id = use.get("id", "<missing>")
        lesson_use_ids.append(use_id)
        anchor = use.get("exact_anchor", "")
        lesson_anchors.append(anchor)
        if anchor and anchor not in body:
            errors.append(f"{use_id}: exact_anchor not found in narration body")
        for lesson_id in use.get("lesson_ids", []):
            used_lesson_ids.add(lesson_id)
            lesson = lessons.get(lesson_id)
            if lesson is None:
                errors.append(f"{use_id}: unknown lesson ID {lesson_id}")
                continue
            handoff_use = lesson.get("handoff_use")
            evidence_layer = lesson.get("evidence_layer")
            if evidence_layer == "implementation_hypothesis":
                errors.append(f"{use_id}: implementation hypothesis {lesson_id} cannot be used in script")
            if handoff_use not in {"script_ready", "conditional"}:
                errors.append(f"{use_id}: lesson {lesson_id} is not permitted for script use")
            if handoff_use == "conditional" and use.get("conditions_preserved") is not True:
                errors.append(f"{use_id}: conditional lesson {lesson_id} must preserve conditions")
            if use.get("implementation_difficulty_preserved") is not True:
                errors.append(f"{use_id}: lesson {lesson_id} must preserve implementation difficulty")
            if fact_card_version == "1.5":
                if use.get("forbidden_generalizations_absent") is not True:
                    errors.append(
                        f"{use_id}: forbidden_generalizations_absent must be true for {lesson_id}"
                    )
                required_spoken_boundary = str(lesson.get("required_spoken_boundary") or "").strip()
                boundary_anchor = str(use.get("required_boundary_anchor") or "").strip()
                if required_spoken_boundary and boundary_anchor:
                    distance = anchor_distance(body, anchor, boundary_anchor)
                    if distance is None:
                        errors.append(f"{use_id}: required_boundary_anchor not found in narration body")
                    elif distance > BOUNDARY_MAX_DISTANCE_CHARS:
                        errors.append(
                            f"{use_id}: lesson boundary is {distance} characters from its use; "
                            f"maximum is {BOUNDARY_MAX_DISTANCE_CHARS}"
                        )
                    else:
                        bounded_lesson_ids.add(lesson_id)
        if fact_card_version == "1.5" and use.get("use") == "implementation_path":
            stage_ids = use.get("implementation_stage_ids", [])
            if not stage_ids:
                errors.append(f"{use_id}: implementation_path use requires implementation_stage_ids")
            for stage_id in stage_ids:
                if stage_id not in implementation_stages:
                    errors.append(f"{use_id}: unknown implementation stage ID {stage_id}")
            if use.get("implementation_guidance_disclosed") is not True:
                errors.append(f"{use_id}: implementation guidance must be disclosed as editorial guidance")
            if use.get("implementation_parameters_preserved") is not True:
                errors.append(f"{use_id}: implementation parameterization must be preserved")
    if len(lesson_use_ids) != len(set(lesson_use_ids)):
        errors.append("script lesson-use IDs must be unique")
    if len(lesson_anchors) != len(set(lesson_anchors)):
        errors.append("lesson-use exact anchors must be unique")
    if transferability.get("applicable") is True and not used_lesson_ids:
        errors.append("case-based script requires at least one mapped lesson use")
    missing_selected_uses = sorted(set(selected_lesson_ids) - used_lesson_ids)
    if missing_selected_uses:
        errors.append(f"selected lessons are not mapped in narration: {missing_selected_uses}")
    if fact_card_version == "1.5":
        lessons_requiring_boundary = {
            lesson_id for lesson_id in used_lesson_ids
            if str(lessons.get(lesson_id, {}).get("required_spoken_boundary") or "").strip()
        }
        missing_lesson_boundaries = sorted(lessons_requiring_boundary - bounded_lesson_ids)
        if missing_lesson_boundaries:
            errors.append(
                f"used lessons lack a nearby required spoken boundary: {missing_lesson_boundaries}"
            )

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
        for lesson_id in beat.get("lesson_ids", []):
            if lesson_id not in lessons:
                errors.append(f"{beat_id}: unknown lesson ID {lesson_id}")
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

    oral_review = mapping.get("oral_delivery_review", {})
    if mapping_version == "1.4":
        language = oral_review.get("language")
        status = oral_review.get("status")
        long_exceptions = oral_review.get("long_sentence_exceptions", [])
        audit_exceptions = oral_review.get("audit_language_exceptions", [])
        if not isinstance(long_exceptions, list):
            long_exceptions = []
            errors.append("oral_delivery_review.long_sentence_exceptions must be an array")
        if not isinstance(audit_exceptions, list):
            audit_exceptions = []
            errors.append("oral_delivery_review.audit_language_exceptions must be an array")
        long_exceptions = [item for item in long_exceptions if isinstance(item, dict)]
        audit_exceptions = [item for item in audit_exceptions if isinstance(item, dict)]
        validate_oral_exceptions(
            errors,
            body,
            "oral_delivery_review.long_sentence_exceptions",
            long_exceptions,
        )
        validate_oral_exceptions(
            errors,
            body,
            "oral_delivery_review.audit_language_exceptions",
            audit_exceptions,
        )
        if oral_review.get("unresolved_flags"):
            errors.append("oral_delivery_review.unresolved_flags must be empty at completion")

        if language == "zh-CN":
            if status != "passed":
                errors.append("Chinese narration requires oral_delivery_review.status=passed")
            for field in (
                "logic_order_reviewed",
                "actor_action_reviewed",
                "qualification_placement_reviewed",
                "abstraction_reviewed",
                "audit_language_reviewed",
                "read_aloud_revision_completed",
            ):
                if oral_review.get(field) is not True:
                    errors.append(f"oral_delivery_review.{field} must be true for Chinese narration")
            if not re.search(r"[\u3400-\u9fff]", body):
                errors.append("oral_delivery_review.language is zh-CN but narration contains no Chinese text")

            for sentence in spoken_sentences(body):
                character_count = spoken_char_count(sentence)
                covered = exception_covers(sentence, long_exceptions)
                clause_punctuation = sum(sentence.count(mark) for mark in ("，", ",", "；", ";"))
                if character_count > CHINESE_SENTENCE_HARD_LIMIT_CHARS and not covered:
                    errors.append(
                        "Chinese sentence exceeds the hard spoken-length gate "
                        f"({character_count}>{CHINESE_SENTENCE_HARD_LIMIT_CHARS} spoken units): "
                        f"{sentence[:42]!r}"
                    )
                elif character_count > CHINESE_SENTENCE_WARNING_CHARS and not covered:
                    warnings.append(
                        "Chinese sentence needs a read-aloud review "
                        f"({character_count} spoken units): {sentence[:42]!r}"
                    )
                if clause_punctuation >= CHINESE_CLAUSE_PUNCTUATION_LIMIT and not covered:
                    errors.append(
                        "Chinese sentence carries too many comma/semicolon clauses "
                        f"({clause_punctuation}>={CHINESE_CLAUSE_PUNCTUATION_LIMIT}): {sentence[:42]!r}"
                    )

            audit_scan_body = body
            for item in audit_exceptions:
                audit_scan_body = audit_scan_body.replace(str(item.get("anchor") or ""), "")
            audit_marker_count = sum(audit_scan_body.count(marker) for marker in AUDIT_LANGUAGE_MARKERS)
            if audit_marker_count > AUDIT_LANGUAGE_LIMIT:
                errors.append(
                    "Chinese narration contains too much unexcepted audit-process language "
                    f"({audit_marker_count}>{AUDIT_LANGUAGE_LIMIT})"
                )
        elif language == "other":
            if status != "not_applicable":
                errors.append("non-Chinese narration requires oral_delivery_review.status=not_applicable")
        else:
            errors.append("oral_delivery_review.language must be zh-CN or other")

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
    revision_actions = hkrr.get("revision_actions")
    if hkrr.get("recommend_further_revision") is True and not revision_actions:
        errors.append("recommend_further_revision=true requires non-empty revision_actions")
    if hkrr.get("recommend_further_revision") is False and revision_actions:
        errors.append("recommend_further_revision=false requires empty revision_actions")

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
    if mapping_version in {"1.3", "1.4"}:
        for field in (
            "transferability_reviewed",
            "lesson_conditions_preserved",
            "implementation_difficulty_reviewed",
        ):
            if checks.get(field) is not True:
                errors.append(f"checks.{field} must be true")
    if fact_card_version == "1.5":
        for field in FACT_CARD_1_5_CHECKS:
            if checks.get(field) is not True:
                errors.append(f"checks.{field} must be true")
    if checks.get("prohibited_claims_used") is not False:
        errors.append("checks.prohibited_claims_used must be false")

    for warning in warnings:
        print(f"WARN: {warning}", file=sys.stderr)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        f"OK: {len(beats)} narrative beats, {len(mapping.get('claim_uses', []))} mapped factual assertions, "
        f"{len(mapping.get('lesson_uses', []))} mapped transferable lessons, "
        f"HKRR={scores}, estimated={calculated_estimate:.1f}s, project={mapping.get('project_id')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
