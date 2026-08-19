#!/usr/bin/env python3
"""Validate a video fact-card handoff."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate fact_card.json")
    parser.add_argument("fact_card", type=Path)
    args = parser.parse_args()

    data = load_json(args.fact_card)
    schema_path = Path(__file__).resolve().parent.parent / "references" / "fact-card.schema.json"
    schema = load_json(schema_path)
    errors: list[str] = []

    try:
        import jsonschema

        validator = jsonschema.Draft202012Validator(schema)
        for error in sorted(validator.iter_errors(data), key=lambda item: list(item.path)):
            location = ".".join(str(part) for part in error.path) or "root"
            errors.append(f"schema {location}: {error.message}")
    except ImportError:
        print("WARN: jsonschema is unavailable; running relational checks only", file=sys.stderr)

    claims = data.get("claims", [])
    sources = data.get("sources", [])
    claim_ids = [claim.get("id") for claim in claims]
    source_ids = [source.get("id") for source in sources]
    claim_id_set = set(claim_ids)
    source_id_set = set(source_ids)

    if len(claim_ids) != len(claim_id_set):
        errors.append("claim IDs must be unique")
    if len(source_ids) != len(source_id_set):
        errors.append("source IDs must be unique")

    usable_claims = 0
    for claim in claims:
        claim_id = claim.get("id", "<missing>")
        script_use = claim.get("script_use")
        referenced_sources = claim.get("source_ids", [])
        unknown_sources = sorted(set(referenced_sources) - source_id_set)
        if unknown_sources:
            errors.append(f"{claim_id}: unknown source IDs {unknown_sources}")
        if script_use in {"direct", "attributed"}:
            usable_claims += 1
            if not referenced_sources:
                errors.append(f"{claim_id}: publishable claim requires at least one source")
            if not claim.get("allowed_wording"):
                errors.append(f"{claim_id}: publishable claim requires allowed_wording")
        if script_use == "attributed" and not (claim.get("attribution_text") or "").strip():
            errors.append(f"{claim_id}: attributed claim requires attribution_text")
        if claim.get("verification_status") in {"unverified", "disputed", "false"} and script_use != "prohibited":
            errors.append(f"{claim_id}: {claim.get('verification_status')} claim must be prohibited")

    for source in sources:
        source_id = source.get("id", "<missing>")
        unknown_claims = sorted(set(source.get("supports_claim_ids", [])) - claim_id_set)
        if unknown_claims:
            errors.append(f"{source_id}: unknown supported claim IDs {unknown_claims}")

    for conflict in data.get("conflicts", []):
        unknown_claims = sorted(set(conflict.get("claim_ids", [])) - claim_id_set)
        if unknown_claims:
            errors.append(f"conflict references unknown claim IDs {unknown_claims}")

    if data.get("publication_status") in {"pass", "conditional"} and usable_claims == 0:
        errors.append("pass or conditional fact card requires at least one usable claim")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {len(claims)} claims, {len(sources)} sources, {usable_claims} script-usable claims, status={data.get('publication_status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
