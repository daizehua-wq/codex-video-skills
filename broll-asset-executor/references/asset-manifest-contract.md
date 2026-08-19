# Asset and Manifest Contract v1.0

## Asset record

Each delivered candidate has one manifest record with these fields:

- `asset_id`: stable ID derived from request and candidate rank.
- `request_id`: unchanged director request ID.
- `block_id`: unchanged sequence block ID.
- `sequence_position`: unchanged order within the block.
- `rank`: `recommended`, `alternate_1` or `alternate_2`.
- `filename` and `relative_path`.
- `asset_type`: still, screenshot, PDF page render, video or explicitly labeled derivative evidence card.
- `source_tier`, `source_name`, `source_url` and optional `download_url`.
- `source_published_at` when known.
- `project_consistency`.
- `rights_status`, `license` and `license_url` when applicable.
- `transformations`.
- `selected_reason` and `limitations`.
- `width`, `height`, `codec`, `duration_sec` and `bytes`.
- `sha256` calculated from the delivered file.

Unknown values must be empty or `null`; do not fabricate metadata. A rights status may not be empty.

## `manifest.json`

Use this envelope:

```json
{
  "schema": "broll_manifest/1.0",
  "generated_at": "ISO-8601 timestamp with timezone",
  "project": {
    "name": "Project name",
    "input_file": "broll_requests.json",
    "input_sha256": "SHA-256 of the exact input"
  },
  "candidate_policy": {
    "recommended_per_request": 1,
    "alternates_per_request": 2
  },
  "request_summary": [],
  "assets": []
}
```

`request_summary` records candidate counts and blocked status for every input request. `assets` contains the full asset records.

## `manifest.csv`

Use one row per asset and the same field values as `manifest.json`. Encode as UTF-8 with BOM when Chinese text is present so common spreadsheet applications open it correctly.

The asset ID set in CSV must exactly equal the asset ID set in JSON.

## `sources.md`

Group sources by `request_id` and list:

- recommended and alternate filenames;
- clickable source pages;
- direct download URLs when appropriate;
- the verification that connects the asset to the request;
- rights/license status and publication limitations;
- project-specific factual guardrails;
- whether a scene is official or generic licensed stock.

Do not hide blocked requests. Explain them in a dedicated section without adding substitute demands.

