---
name: video-director
description: Turn a narration script or timestamped transcript into an A-roll edit plan and explicit broll_requests.json for evidence-led talking-head videos. Use when deciding where visuals belong, how long they cover, and what real assets a downstream B-roll execution skill must obtain. Do not use to search, download, license, or process the assets.
---

# Video Director

Design the edit; do not execute asset acquisition.

## Responsibility boundary

The director owns:

- where A-roll remains full screen;
- where B-roll begins and ends;
- the visual purpose of every B-roll shot;
- the required source class, factual guardrails and forbidden substitutions;
- sequence grouping, shot order, coverage duration and layout;
- the final `director_plan.json` and `broll_requests.json` handoff.

The downstream B-roll skill owns searching, project-consistency checks, source ranking, rights marking, downloading, cropping, transcoding and manifests. It must not decide that an additional shot is needed or reinterpret the narration.

## Required inputs

Use a final narration script or timestamped transcript. Preserve the supplied wording and claims. If timing is unavailable, estimate timings explicitly and mark them as estimated; do not fabricate timecodes presented as measured.

Before directing, identify the finished runtime, delivery aspect ratio and any explicit editorial constraints. Apply the default style only where the user has not supplied a more specific project rule.

## Directing workflow

1. Divide the narration into argument beats, not arbitrary equal intervals.
2. Mark full-screen A-roll moments for thesis statements, transitions, emotional emphasis and visual resets.
3. Mark B-roll blocks only where a real visual can prove, demonstrate, explain or concretize the current beat.
4. Target 60–70% B-roll coverage across the finished content. Calculate coverage from the union of B-roll time windows; never add overlapping durations twice.
5. Build each 8–40 second B-roll block from multiple explicit 2–10 second shot requests when the beat needs internal variation. Never hide several different shot needs inside one ambiguous request.
6. Group those requests with `block_id` and `sequence_position`. Each request still receives one recommended candidate and two alternates downstream.
7. Return to full-screen A-roll between major evidence blocks so the speaker remains the narrative anchor.
8. Validate factual fit, mobile readability, coverage math and downstream executability before handoff.

Do not insert decorative footage solely to reach the coverage target. When truthful, relevant visuals cannot support 60%, report the shortfall and the affected beats instead of inventing requests.

## Default visual language

Use the style in [references/style-profile.md](references/style-profile.md). Read it whenever the user has not supplied an overriding project style or when evaluating coverage, layout, shot duration or readability.

The default is evidence-led rather than atmospheric:

- official talks, first-party product UI, primary documents and source-backed diagrams before generic stock;
- B-roll as the dominant layer with A-roll retained as a small picture-in-picture when continuity matters;
- full-screen A-roll as a deliberate reset, not the unexamined default;
- hard cuts or restrained transitions;
- no generic “AI”, robot or office imagery when a specific product, person, document or workflow is being discussed.

## Output contract

Produce both files when the task requires a machine handoff:

1. `director_plan.json`: complete A-roll/B-roll timeline, B-roll block grouping, layouts and coverage calculation.
2. `broll_requests.json`: only explicit asset requests for downstream execution.

Read [references/handoff-schema.md](references/handoff-schema.md) before producing or validating either file. Use [references/broll_requests.schema.json](references/broll_requests.schema.json) when strict JSON validation is needed.

After producing `broll_requests.json`, run:

```bash
python3 scripts/validate_broll_requests.py /path/to/broll_requests.json
```

The validator checks the JSON Schema when `jsonschema` is available and always checks cross-field timing, IDs, block order and overlap rules.

`broll_requests.json` must remain asset-oriented. Do not place editing commentary, alternative narration, speculative product capabilities or hidden implementation assumptions in it.

## Quality gates

Reject the handoff until all of these are true:

- every B-roll request points to an exact script anchor and one timeline window;
- every request has one visual purpose and can be sourced independently;
- every B-roll block lists its ordered request IDs;
- total coverage is computed and compared with the project target;
- Evidence requests identify the fact being supported and the acceptable source identity;
- Product requests prohibit fabricated interfaces and adjacent-but-different products;
- Scene requests state whether the scene is official or generic licensed illustration;
- pages, documents and UI specify the region that must remain readable;
- video requests specify desired usable duration plus source handles;
- no B-roll request silently changes the spoken claim;
- the downstream candidate policy remains one recommended asset plus two alternates per request.
