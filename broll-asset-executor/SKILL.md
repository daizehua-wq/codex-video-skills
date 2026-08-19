---
name: broll-asset-executor
description: Execute explicit broll_requests.json into traceable, editable real assets with source, project-consistency and rights records. Use for B-roll search, verification, acquisition, screenshots, trimming, transcoding and manifests. Do not use to decide where B-roll belongs, interpret narration, or add shot requirements.
---

# B-roll Asset Executor

Convert explicit requests into reliable, traceable, edit-ready real assets.

## Fixed responsibility boundary

The director defines the need. This skill does not explain, reinterpret or expand it.

Input:

```text
broll_requests.json
```

Outputs:

```text
assets/
manifest.csv
manifest.json
sources.md
```

Do not inspect a script to decide where B-roll is needed. Do not create a request, split a request, extend a coverage window, change narration or substitute a different visual claim. If an input request is ambiguous or internally contradictory, mark it blocked and report the exact field conflict.

## Required pipeline

```text
broll_requests.json
        ↓
request validation
        ↓
asset search
        ↓
project-consistency verification
        ↓
source-tier verification
        ↓
rights-status marking
        ↓
download / screenshot / crop / transcode
        ↓
candidate selection
        ↓
assets/ + manifests + sources.md
```

Run `scripts/validate_broll_requests.py` before searching. The input contract is [references/broll_requests.schema.json](references/broll_requests.schema.json). Validation does not authorize repairing the director’s intent.

## Execution rules

For every request:

1. Preserve `id`, `block_id`, `sequence_position`, script anchor, coverage window, type, visual role and guardrails.
2. Search only for the stated `required_assets`, preferred sources and permitted fallback.
3. Verify that the asset depicts the correct company, product, person, period and workflow before considering source prestige.
4. Reject every `forbidden_assets` match and every adjacent-but-different product substitution.
5. Record the actual source page and direct acquisition URL when available.
6. Mark rights conservatively. Do not treat public accessibility as permission to publish.
7. Retain the requested source handles for video. Do not trim every candidate to the final editorial duration.
8. Preserve enough surrounding context for evidence crops to remain source-identifiable and non-misleading.
9. Deliver exactly one recommended candidate and two alternates unless the request contract explicitly changes this policy.
10. Keep alternates substitutable. Do not treat them as additional sequence shots.

Read [references/execution-policy.md](references/execution-policy.md) when ranking sources, validating asset types or assigning rights status. Read [references/asset-manifest-contract.md](references/asset-manifest-contract.md) before writing manifests.

## Type-specific invariants

### Evidence

- Prefer an original document, official release, legal filing or authoritative report.
- Keep the required readable region legible at delivery size.
- Do not use generic stock, AI-generated imagery or unattributed data cards as proof.
- Record whether the claim is the source’s own disclosure or independently verified.

### Product

- Use real official product UI, documentation or demonstration.
- Confirm the exact product surface; shared logos or company names are insufficient.
- Do not invent UI, hidden APIs, permissions, integrations or backend workflows.

### Scene

- Use official real scenes when required and available.
- Licensed generic scenes must be marked `GENERIC_SCENE_NOT_PROJECT_SPECIFIC`.
- Do not imply generic people, offices or workflows belong to the named project.

## Completion gate

Do not report completion until:

- every non-blocked request has one recommended and two alternate asset records;
- every file exists, opens and matches its manifest checksum;
- video dimensions, codec and duration are probed rather than guessed;
- source identity, source tier, project consistency and rights status are present;
- `manifest.csv` and `manifest.json` contain the same asset set;
- `sources.md` explains rights limitations and factual guardrails;
- no output asset originated from an unrequested shot requirement.

