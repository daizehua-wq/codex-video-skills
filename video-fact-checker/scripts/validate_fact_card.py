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
    schema_version = data.get("schema_version")
    claim_ids = [claim.get("id") for claim in claims]
    source_ids = [source.get("id") for source in sources]
    claim_id_set = set(claim_ids)
    source_id_set = set(source_ids)
    claims_by_id = {claim.get("id"): claim for claim in claims}
    sources_by_id = {source.get("id"): source for source in sources}

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
        for source_id in referenced_sources:
            source = sources_by_id.get(source_id)
            if source and claim_id not in source.get("supports_claim_ids", []):
                errors.append(f"{claim_id}: source {source_id} does not link back to this claim")
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
        if claim.get("verification_status") == "secondary_only" and script_use == "direct":
            errors.append(f"{claim_id}: secondary_only claim cannot be used directly")
        known_source_tiers = {
            sources_by_id[source_id].get("source_tier")
            for source_id in referenced_sources
            if source_id in sources_by_id
        }
        if known_source_tiers and known_source_tiers <= {"D_OTHER_SECONDARY", "E_USER_SUPPLIED"}:
            if claim.get("verification_status") in {"independently_verified", "primary_source_confirmed"}:
                errors.append(f"{claim_id}: D/E-only evidence cannot support {claim.get('verification_status')}")

    for source in sources:
        source_id = source.get("id", "<missing>")
        unknown_claims = sorted(set(source.get("supports_claim_ids", [])) - claim_id_set)
        if unknown_claims:
            errors.append(f"{source_id}: unknown supported claim IDs {unknown_claims}")
        for claim_id in source.get("supports_claim_ids", []):
            claim = claims_by_id.get(claim_id)
            if claim and source_id not in claim.get("source_ids", []):
                errors.append(f"{source_id}: claim {claim_id} does not link back to this source")

    for conflict in data.get("conflicts", []):
        unknown_claims = sorted(set(conflict.get("claim_ids", [])) - claim_id_set)
        if unknown_claims:
            errors.append(f"conflict references unknown claim IDs {unknown_claims}")

    if data.get("publication_status") in {"pass", "conditional"} and usable_claims == 0:
        errors.append("pass or conditional fact card requires at least one usable claim")

    if schema_version == "1.0":
        print("WARN: schema 1.0 is legacy; upgrade to 1.1 when revising this card", file=sys.stderr)

    if schema_version == "1.1":
        audit = data.get("verification_audit", {})
        temporal = audit.get("temporal_search", {})
        temporal_claim_types = {"number", "quote", "chronology", "causality", "forecast"}
        temporal_required = any(claim.get("claim_type") in temporal_claim_types for claim in claims)
        if temporal_required and temporal.get("applicable") is not True:
            errors.append("verification_audit.temporal_search must be applicable for source-sensitive claims")
        if temporal.get("applicable") is True:
            if temporal.get("completed") is not True:
                errors.append("applicable temporal search must be completed")
            if not temporal.get("official_domains"):
                errors.append("completed temporal search requires official_domains")
            if temporal.get("searched_through") != data.get("checked_at"):
                errors.append("temporal search must be current through checked_at")

        revision = audit.get("revision_audit", {})
        changed_claim_ids = revision.get("changed_claim_ids", [])
        unknown_changed_claims = sorted(set(changed_claim_ids) - claim_id_set)
        if unknown_changed_claims:
            errors.append(f"revision audit references unknown changed claim IDs {unknown_changed_claims}")
        if audit.get("mode") == "revision":
            if not str(revision.get("base_artifact") or "").strip():
                errors.append("revision audit requires base_artifact")
            if revision.get("all_material_claims_rechecked") is not True:
                errors.append("revision mode requires a full recheck of all material claims")

        negative_audits = audit.get("negative_claim_audits", [])
        negative_audit_ids = [item.get("claim_id") for item in negative_audits]
        if len(negative_audit_ids) != len(set(negative_audit_ids)):
            errors.append("negative claim audit IDs must be unique")
        required_negative_ids = {
            claim.get("id")
            for claim in claims
            if claim.get("verification_status") in {"secondary_only", "unverified", "false"}
        }
        missing_negative_audits = sorted(required_negative_ids - set(negative_audit_ids))
        if missing_negative_audits:
            errors.append(
                "secondary_only/unverified/false claims require negative audits: "
                f"{missing_negative_audits}"
            )
        for item in negative_audits:
            claim_id = item.get("claim_id")
            if claim_id not in claim_id_set:
                errors.append(f"negative audit references unknown claim ID {claim_id}")
            unknown_checked_sources = sorted(set(item.get("searched_source_ids", [])) - source_id_set)
            if unknown_checked_sources:
                errors.append(f"{claim_id}: negative audit references unknown source IDs {unknown_checked_sources}")
            if item.get("finding_scope") in {"official_sources_checked", "broad_search_completed"}:
                if not item.get("searched_domains"):
                    errors.append(f"{claim_id}: broad negative finding requires searched_domains")

        traces = audit.get("secondary_source_traces", [])
        trace_source_ids = [trace.get("source_id") for trace in traces]
        if len(trace_source_ids) != len(set(trace_source_ids)):
            errors.append("secondary source trace IDs must be unique")
        d_source_ids = {
            source.get("id")
            for source in sources
            if source.get("source_tier") == "D_OTHER_SECONDARY"
        }
        missing_traces = sorted(d_source_ids - set(trace_source_ids))
        if missing_traces:
            errors.append(f"D-tier sources require upstream traces: {missing_traces}")
        for trace in traces:
            source_id = trace.get("source_id")
            if source_id not in source_id_set:
                errors.append(f"secondary trace references unknown source ID {source_id}")
                continue
            status = trace.get("status")
            upstream_ids = trace.get("upstream_source_ids", [])
            unknown_upstreams = sorted(set(upstream_ids) - source_id_set)
            if unknown_upstreams:
                errors.append(f"{source_id}: trace references unknown upstream IDs {unknown_upstreams}")
            if source_id in d_source_ids and status == "not_applicable":
                errors.append(f"{source_id}: D-tier trace cannot be not_applicable")
            if status == "traced" and not upstream_ids:
                errors.append(f"{source_id}: traced source requires upstream_source_ids")
            source_group = sources_by_id[source_id].get("independence_group")
            for upstream_id in upstream_ids:
                upstream = sources_by_id.get(upstream_id)
                if upstream and upstream.get("independence_group") != source_group:
                    errors.append(f"{source_id}: traced upstream {upstream_id} must share independence_group")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        f"OK: schema={schema_version}, {len(claims)} claims, {len(sources)} sources, "
        f"{usable_claims} script-usable claims, status={data.get('publication_status')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
