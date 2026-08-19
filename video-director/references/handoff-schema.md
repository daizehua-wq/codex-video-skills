# Director Handoff Contract v2.0

## Outputs

### `director_plan.json`

The complete editorial decision record.

```json
{
  "schema": "director_plan/2.0",
  "project": {
    "name": "Example",
    "runtime_sec": 240,
    "timing_basis": "measured",
    "aspect_ratio": "9:16",
    "style_profile": "evidence-led-talking-head/1.0",
    "target_broll_coverage_ratio": {"min": 0.60, "max": 0.70}
  },
  "segments": [
    {
      "segment_id": "SEG001",
      "start_sec": 0,
      "end_sec": 12,
      "mode": "AROLL_FULL",
      "script_anchor": "Exact opening words",
      "purpose": "Thesis and presenter connection",
      "layout": "full_screen_aroll",
      "broll_block_id": null
    }
  ],
  "broll_blocks": [
    {
      "block_id": "BB001",
      "start_sec": 12,
      "end_sec": 36,
      "purpose": "Prove the case, then explain the mechanism",
      "layout": "broll_dominant_with_aroll_pip",
      "request_ids": ["BR001", "BR002", "BR003"]
    }
  ],
  "coverage": {
    "broll_union_duration_sec": 156,
    "editorial_content_duration_sec": 240,
    "ratio": 0.65,
    "target_met": true,
    "exceptions": []
  }
}
```

Allowed `mode` values:

- `AROLL_FULL`
- `BROLL_WITH_AROLL_PIP`
- `BROLL_FULL`
- `SPLIT_SCREEN`

Segments must form a non-overlapping timeline. Calculate B-roll coverage from segments whose mode is not `AROLL_FULL`. If the source includes leader, loading screens, slate or trailing dead air, exclude them from `editorial_content_duration_sec` and document the exclusion.

### `broll_requests.json`

The acquisition handoff. A request represents one independently sourceable shot need, not an entire vague topic.

Required request fields:

- `id`: stable ID such as `BR001`.
- `block_id`: parent B-roll block in `director_plan.json`.
- `sequence_position`: 1-based order within the block.
- `script_anchor`: exact narration words the asset covers.
- `coverage_window`: start/end time and timing basis.
- `type`: `Evidence`, `Product` or `Scene`.
- `visual_role`: `proof`, `demonstration`, `explanation`, `context` or `reset`.
- `purpose`: why this specific shot is required.
- `required_assets`: observable content the executor must find.
- `preferred_sources`: ordered source classes or named sources.
- `forbidden_assets`: substitutions that would create mismatch or misleading evidence.
- `coverage_duration_sec`: intended duration of this shot in the edit.
- `source_handles_sec`: extra usable video before and after the intended selection.
- `layout`: intended editorial treatment.
- `readable_region`: exact source text/UI that must remain readable, or `null`.
- `priority`: `critical`, `high`, `medium` or `low`.
- `fact_guardrails`: claims the visual may and may not support.
- `fallback`: a narrower acceptable fallback, never permission to invent a visual.

Project-level `execution_rules` must keep:

```json
{
  "candidate_count_per_request": {
    "recommended": 1,
    "alternates": 2
  },
  "default_reject": [
    "AI_GENERATED used as factual proof",
    "UNKNOWN source",
    "project-inconsistent asset",
    "adjacent product substituted for the requested product",
    "unattributed news, data or person footage"
  ]
}
```

## Sequence construction

An 8–40 second B-roll block should normally contain multiple explicit requests:

```text
BB003 (24 seconds)
├── BR008 · source-identifiable event shot · 6 seconds
├── BR009 · readable product UI · 7 seconds
├── BR010 · mechanism diagram · 6 seconds
└── BR011 · outcome evidence · 5 seconds
```

The B-roll executor returns one recommended candidate and two alternates for each of BR008–BR011. Alternates remain substitutes; they are not additional sequence shots unless the director creates separate requests for them.

## Validation rules

- `end_sec` must be greater than `start_sec`.
- `coverage_duration_sec` should equal the request window within normal rounding tolerance.
- Every request ID must appear exactly once in a `broll_blocks[].request_ids` list.
- `sequence_position` must be unique and continuous within a block.
- Request windows within one block must not overlap unless the layout is explicitly `SPLIT_SCREEN`.
- `Evidence/proof` requires a non-null `readable_region` or an explicit source-identity requirement.
- `Scene` using generic stock must say `GENERIC_SCENE_NOT_PROJECT_SPECIFIC` in its guardrails.
- Video requests must retain source handles. Stills may set handles to zero.
- The sum of request durations is not the project coverage metric; use the union of directed B-roll windows.

