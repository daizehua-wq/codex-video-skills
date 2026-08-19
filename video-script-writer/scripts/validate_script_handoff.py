#!/usr/bin/env python3
"""Validate a narration-to-fact-card handoff."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate narration and script_claims.json")
    parser.add_argument("fact_card", type=Path)
    parser.add_argument("narration", type=Path)
    parser.add_argument("script_claims", type=Path)
    args = parser.parse_args()

    fact_card = load_json(args.fact_card)
    mapping = load_json(args.script_claims)
    narration = args.narration.read_text(encoding="utf-8")
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

    facts = {claim.get("id"): claim for claim in fact_card.get("claims", [])}
    mapping_ids: list[str] = []
    anchors: list[str] = []

    for use in mapping.get("claim_uses", []):
        mapping_id = use.get("id", "<missing>")
        mapping_ids.append(mapping_id)
        anchor = use.get("exact_anchor", "")
        anchors.append(anchor)
        if anchor and anchor not in narration:
            errors.append(f"{mapping_id}: exact_anchor not found in narration")

        for fact_id in use.get("fact_ids", []):
            fact = facts.get(fact_id)
            if fact is None:
                errors.append(f"{mapping_id}: unknown fact ID {fact_id}")
                continue
            if fact.get("script_use") == "prohibited":
                errors.append(f"{mapping_id}: prohibited fact used: {fact_id}")
            if fact.get("script_use") == "attributed" and not use.get("attribution_present"):
                errors.append(f"{mapping_id}: attributed fact lacks attribution flag: {fact_id}")

    if len(mapping_ids) != len(set(mapping_ids)):
        errors.append("script claim IDs must be unique")
    if len(anchors) != len(set(anchors)):
        errors.append("exact anchors must be unique")
    if mapping.get("unmapped_assertions"):
        errors.append("unmapped_assertions must be empty at completion")

    checks = mapping.get("checks", {})
    required_true = ["all_factual_claims_mapped", "quotes_verified", "numbers_verified", "scope_reviewed", "repetition_reviewed", "read_aloud_completed"]
    for field in required_true:
        if checks.get(field) is not True:
            errors.append(f"checks.{field} must be true")
    if checks.get("prohibited_claims_used") is not False:
        errors.append("checks.prohibited_claims_used must be false")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {len(mapping.get('claim_uses', []))} mapped script assertions, project={mapping.get('project_id')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
