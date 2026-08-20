# Director Handoff Contract v3.1

## Version boundary

- `director_plan.json` uses `director_plan/3.1`.
- `broll_requests.json` remains `broll_requests/3.0` because acquisition responsibilities did not change.
- Both files use `style_profile: comprehension-led-talking-head/3.0`.

Version 3.1 adds reusable visual anchors, stateful animation beats, presenter-continuity fields, evidence choreography and metaphor safety. It does not authorize the director to acquire assets or edit video.

## `director_plan.json`

The director plan records why each intervention exists, what changes on screen and what the viewer learns.

### Top-level structure

```json
{
  "schema": "director_plan/3.1",
  "project": {},
  "visual_anchors": [],
  "segments": [],
  "visual_summary": {}
}
```

### Project

```json
{
  "name": "Example",
  "runtime_sec": 60,
  "timing_basis": "measured",
  "handoff_status": "execution_ready",
  "aroll_readiness": {
    "human_finalized": true,
    "media_file": "aroll_master.mov",
    "transcript_file": "transcript.srt",
    "duration_source": "probed_media",
    "checks": {
      "media_readable": true,
      "video_stream_present": true,
      "audio_stream_present": true,
      "duration_measured": true,
      "transcript_timecoded": true,
      "transcript_within_runtime": true,
      "human_lock_confirmed": true
    },
    "notes": []
  },
  "aspect_ratio": "9:16",
  "style_profile": "comprehension-led-talking-head/3.0",
  "visual_policy": "comprehension_led_no_quota"
}
```

### Visual anchors

Register a reusable explanation canvas only when multiple segments revisit the same system, chronology, process or comparison.

```json
{
  "id": "VA001",
  "type": "map",
  "purpose": "Keep recurring companies and investment directions spatially stable",
  "initial_state": "Four company nodes are visible; no investment arrows have been introduced",
  "consistency_rules": [
    "Company positions and colors remain fixed",
    "Previously established arrows remain visible unless explicitly revised",
    "Unrelated nodes dim instead of moving"
  ],
  "reuse_segment_ids": ["SEG002", "SEG004"]
}
```

Allowed anchor types:

- `map`
- `timeline`
- `process`
- `comparison`
- `system_diagram`
- `spatial_canvas`

Every ID in `reuse_segment_ids` must exist and reference the same `visual_anchor_id`. Every segment anchor reference must exist in the registry.

### Segments

Allowed modes:

- `AROLL_FULL`
- `SOURCE_EVIDENCE`
- `PRODUCT_DEMO`
- `MOTION_GRAPHICS`
- `ILLUSTRATIVE_METAPHOR`
- `TEXT_EMPHASIS`

All segments require:

- exact measured `start_sec` and `end_sec`;
- `script_anchor`, purpose and visual-necessity metadata;
- nullable `visual_anchor_id`;
- `human_presence`: `full_frame`, `split_screen`, `pip` or `absent`;
- `return_to_aroll_reason` for `AROLL_FULL`, otherwise `null`;
- a `representation` safety object;
- a `visual_treatment` with stateful beats.

### A-roll segment

```json
{
  "segment_id": "SEG001",
  "start_sec": 0,
  "end_sec": 5,
  "mode": "AROLL_FULL",
  "script_anchor": "为什么这些公司既竞争又互相投资？",
  "purpose": "Pose the opening conflict through the presenter",
  "visual_function": null,
  "why_visual_needed": null,
  "failure_if_absent": null,
  "information_revealed": [],
  "visual_anchor_id": null,
  "human_presence": "full_frame",
  "return_to_aroll_reason": "opening_question",
  "representation": {
    "literal_status": "aroll",
    "ai_generated": false,
    "disclosure_required": false,
    "misinterpretation_risk": null
  },
  "layout": "full_frame_aroll",
  "visual_treatment": {
    "kind": "none",
    "asset_request_ids": [],
    "focus_regions": [],
    "beats": [],
    "motion_rule": "",
    "evidence_sequence": null
  }
}
```

Allowed `return_to_aroll_reason` values:

- `opening_question`
- `new_question`
- `interpretation`
- `reset`
- `conclusion`
- `continuation`

### Motion-graphics segment using an anchor

```json
{
  "segment_id": "SEG002",
  "start_sec": 5,
  "end_sec": 12,
  "mode": "MOTION_GRAPHICS",
  "script_anchor": "公司 A 投资公司 B，同时向它采购算力",
  "purpose": "Explain two different relationships without conflating them",
  "visual_function": "explain",
  "why_visual_needed": "The audience must hold two directed relationships between the same entities",
  "failure_if_absent": "Investment and procurement could be mistaken for the same transaction",
  "information_revealed": ["equity direction", "procurement direction"],
  "visual_anchor_id": "VA001",
  "human_presence": "pip",
  "return_to_aroll_reason": null,
  "representation": {
    "literal_status": "explanatory_diagram",
    "ai_generated": false,
    "disclosure_required": false,
    "misinterpretation_risk": null
  },
  "layout": "full_screen_map_with_safe_pip",
  "visual_treatment": {
    "kind": "semantic_animation",
    "asset_request_ids": [],
    "focus_regions": ["company A", "company B", "relationship legend"],
    "beats": [
      {
        "at_sec": 5.4,
        "state_before": "Both nodes are visible with no connection",
        "action": "Draw a green equity arrow from A to B",
        "state_after": "The equity relationship is visible and labeled",
        "information_gained": "A is an investor in B"
      },
      {
        "at_sec": 8.2,
        "state_before": "The green equity arrow remains visible",
        "action": "Draw a blue procurement arrow from B to A",
        "state_after": "Both relationships are visible with distinct labels",
        "information_gained": "B also pays A for compute, a separate commercial relationship"
      }
    ],
    "motion_rule": "Keep nodes fixed; only reveal one labeled relationship per beat",
    "evidence_sequence": null
  }
}
```

Every treatment beat requires:

- `state_before`
- `action`
- `state_after`
- `information_gained`

Motion whose information gain is only “more dynamic” or “keeps the frame active” is invalid.

### Source-evidence segment

```json
{
  "segment_id": "SEG003",
  "start_sec": 12,
  "end_sec": 20,
  "mode": "SOURCE_EVIDENCE",
  "script_anchor": "官方公告披露了投资金额",
  "purpose": "Prove the attributed amount from the original announcement",
  "visual_function": "prove",
  "why_visual_needed": "The amount and attribution must be directly inspectable",
  "failure_if_absent": "The audience cannot distinguish the official figure from commentary",
  "information_revealed": ["publisher", "announcement title", "exact amount"],
  "visual_anchor_id": null,
  "human_presence": "absent",
  "return_to_aroll_reason": null,
  "representation": {
    "literal_status": "literal_evidence",
    "ai_generated": false,
    "disclosure_required": false,
    "misinterpretation_risk": null
  },
  "layout": "full_screen_readable_source",
  "visual_treatment": {
    "kind": "source_identity_to_detail",
    "asset_request_ids": ["BR001"],
    "focus_regions": ["publisher and title", "amount sentence"],
    "beats": [
      {
        "at_sec": 12,
        "state_before": "No source is visible",
        "action": "Show the complete identifiable announcement",
        "state_after": "Publisher, title and date are readable",
        "information_gained": "The source identity is established"
      },
      {
        "at_sec": 15,
        "state_before": "The complete page remains visible",
        "action": "Crop to and highlight the amount sentence",
        "state_after": "The exact supporting words are readable",
        "information_gained": "The official document states the attributed amount"
      }
    ],
    "motion_rule": "Movement terminates on a readable evidence region",
    "evidence_sequence": {
      "source_identity_frame": "Publisher, title and date in the complete announcement",
      "evidence_region": "Paragraph containing the investment amount",
      "highlight_text": "The exact amount phrase supporting the narration",
      "translation_overlay": "Chinese translation below the original paragraph",
      "editorial_interpretation": "The amount is a disclosed commitment, not proof of cash already paid",
      "minimum_read_time_sec": 4
    }
  }
}
```

Source evidence requires at least two beats: identity and detail. Translation and interpretation may be `null`; when present they must remain visually distinct from the source.

### Illustrative metaphor

Use `ILLUSTRATIVE_METAPHOR` only for visibly non-literal explanation. It must use:

```json
{
  "representation": {
    "literal_status": "metaphor",
    "ai_generated": true,
    "disclosure_required": true,
    "misinterpretation_risk": "Viewers could mistake the staged boardroom for a real meeting"
  }
}
```

Metaphor segments cannot reference B-roll acquisition requests, cannot use `visual_function: prove`, and cannot replace original evidence.

### Visual summary

```json
{
  "aroll_full_sec": 20,
  "source_evidence_sec": 10,
  "product_demo_sec": 0,
  "motion_graphics_sec": 20,
  "illustrative_metaphor_sec": 5,
  "text_emphasis_sec": 5,
  "visual_intervention_union_sec": 40,
  "observed_ratio": 0.6667,
  "coverage_target": null
}
```

The summary is descriptive. `coverage_target` must remain `null`.

## `broll_requests.json`

This file contains only external real-asset acquisition needs and retains `broll_requests/3.0`. The following block is structural shorthand, not a copyable validation fixture; `aroll_readiness` and `execution_rules` must still be fully populated according to the schema.

```json
{
  "schema": "broll_requests/3.0",
  "project": {
    "name": "Example",
    "runtime_sec": 60,
    "timing_basis": "measured",
    "handoff_status": "execution_ready",
    "aroll_readiness": {},
    "aspect_ratio": "9:16",
    "style_profile": "comprehension-led-talking-head/3.0",
    "visual_policy": "comprehension_led_no_quota",
    "director_plan": "director_plan.json"
  },
  "requests": [],
  "execution_rules": {}
}
```

Required request fields and asset classes remain defined by [broll_requests.schema.json](broll_requests.schema.json). One request represents one independently sourceable real asset. A wide page, detail crop and highlight derived from the same source remain one acquisition request with several director-treatment beats.

Do not create a request for:

- kinetic typography;
- a diagram constructible from verified narration without source imagery;
- an illustrative metaphor or generated scene;
- generic transitions or visual resets;
- a static image whose only planned treatment is decorative motion.

## Validation rules

- final handoffs require successful A-roll readiness and measured timing;
- segment times are continuous and end at measured runtime;
- each non-A-roll segment passes the visual-necessity gate;
- every treatment beat states a real information gain;
- every visual-anchor reference and declared reuse matches;
- source evidence includes source identity, exact evidence region and positive read time;
- AI-generated representations require disclosure;
- metaphors cannot act as proof or request acquired assets;
- every B-roll request ID is referenced exactly once by a compatible director segment;
- each request window falls inside its director segment;
- observed coverage is reported but never validated against a target.
