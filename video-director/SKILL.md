---
name: video-director
description: Turn a human-finalized A-roll and aligned transcript into a comprehension-led visual plan, using reusable explanation anchors, original-source evidence, product demonstrations, semantic animation, safe metaphor or text emphasis. Produce real-asset requests only when acquisition is necessary. Do not research, acquire assets or edit the final video.
---

# Video Director

Design visual interventions that make narration easier to understand, verify or observe. A-roll is the default. Visual coverage is an outcome, never a quota.

## Responsibility boundary

The director owns:

- where the final A-roll remains uninterrupted;
- whether a beat needs proof, explanation, demonstration, metaphor or emphasis;
- reusable visual anchors for recurring entities, relationships, states or processes;
- the exact information progression, presenter presence and exit point of each visual segment;
- requests for external real assets when those assets are genuinely required;
- the measured `director_plan.json` and acquisition-only `broll_requests.json` handoff.

The director does not:

- rewrite locked narration, repair unclear claims with visuals or add new shot requirements not implied by the approved script;
- search, download, license, screenshot, crop or transcode source assets;
- execute motion graphics, generative illustration, subtitles, effects or final editing;
- add a visual to create rhythm, hide A-roll or reach a coverage percentage.

The B-roll executor receives only real-asset acquisition requests. Motion graphics, text emphasis and illustrative metaphors remain in `director_plan.json` for a downstream editor or generation workflow.

## Required inputs

For an execution-ready handoff, require:

- the human-finalized A-roll master;
- explicit confirmation that recording, take selection, mistake removal, pacing and approval are complete;
- a timecoded transcript aligned to that exact cut;
- runtime measured from the media file;
- delivery aspect ratio and explicit editorial constraints.

Preserve the spoken wording and claims. Record material deviations from the approved narration; do not silently rewrite the speaker.

## A-roll readiness gate

Read [references/aroll-readiness.md](references/aroll-readiness.md) and run `scripts/check_aroll_readiness.py` when local media and subtitles are available.

- `execution_ready`: all final media, timing, transcript and human-lock checks pass. Final time fields must be measured.
- `draft_only`: any required input is missing or changing. Produce only a draft plan and readiness report; do not refresh executable asset requests.

## Default directing grammar

Use this sequence when it fits the argument:

1. A-roll poses the question, conflict or judgment.
2. A visual proves, explains or demonstrates the point.
3. A-roll returns to interpret the evidence, reset attention or conclude.

Do not force the sequence on every sentence. Use it at argument and chapter boundaries.

## Visual-necessity gate

Start every argument beat as `AROLL_FULL`. Change it only when at least one concrete gap exists:

- **proof gap**: the audience needs an identifiable original source to trust a factual statement;
- **explanation gap**: a mechanism, relationship, sequence or comparison is difficult to hold in spoken language alone;
- **demonstration gap**: the audience needs to observe a real product, interface, process or behavior;
- **metaphor need**: a verified but abstract relationship benefits from a clearly non-literal analogy;
- **emphasis need**: a number, contrast or conclusion benefits from brief typography without replacing the presenter.

For every non-A-roll segment, record `why_visual_needed`, `failure_if_absent`, `information_revealed` and time-aligned treatment beats. Each beat must state the visual state before it, the change, the state after it and the information gained.

If removing the proposed visual would not reduce comprehension, verifiability or observability, keep A-roll. A visual reset, decorative motion or empty variety is not sufficient justification.

## Reusable visual anchors

Create a visual anchor only when several later beats refer to the same system, entities, chronology or comparison and a stable canvas will reduce reorientation. Examples include a relationship map, layered system, timeline, process or comparison board.

Register each anchor once in `visual_anchors` and preserve:

- stable entity positions, colors and labels;
- a clear initial state;
- incremental state changes tied to narration;
- previously established relationships unless the script explicitly changes them;
- readable crops for the delivery aspect ratio.

Do not build a master diagram merely to establish a house style. A visual anchor must reduce a real explanation burden.

## Visual routing

Choose one primary mode for each segment:

- `AROLL_FULL`: clear argument, emotion, transition, judgment or conclusion.
- `SOURCE_EVIDENCE`: original news page, report, speech, document or quoted source.
- `PRODUCT_DEMO`: real product UI, screen recording or observable workflow.
- `MOTION_GRAPHICS`: an abstract mechanism, hierarchy, sequence, taxonomy, state change or comparison.
- `ILLUSTRATIVE_METAPHOR`: a visibly non-literal analogy that helps the audience reason about a verified relationship or risk.
- `TEXT_EMPHASIS`: brief numbers, keywords or contrasts layered over A-roll.

Do not convert a source into a re-typeset evidence card when the original page can be shown. Do not prescribe generic push-ins, floating motion or ambient animation that reveals no new information.

## Source-evidence choreography

For `SOURCE_EVIDENCE`, direct an identifiable evidence sequence:

1. establish publisher, document, title, date or speaker identity;
2. move to the exact paragraph, quotation, number, table cell or timestamp;
3. highlight only the supporting region;
4. optionally add a translation or clearly separated editorial interpretation;
5. leave after the evidence is readable and understood.

Keep source text and editorial interpretation visually distinct. Do not let the presenter, subtitles or decoration cover source identity or the evidence region.

## Presenter continuity

Choose `human_presence` deliberately:

- `full_frame` when the presenter is the argument, judgment or reset;
- `split_screen` when presenter and comparison must be read together;
- `pip` when a longer diagram, source or demonstration benefits from a visible guide;
- `absent` when full-screen readability or observation matters more.

Picture-in-picture is not a default. It must not cover readable evidence. Every `AROLL_FULL` segment records why the presenter is on screen through `return_to_aroll_reason`.

## Metaphor and generated-visual safety

An illustrative metaphor may explain or emphasize; it never proves a factual claim. Mark it as `representation.literal_status: metaphor`, record a concrete `misinterpretation_risk`, and require visible disclosure when AI-generated.

Never use generated reconstruction as source evidence, product demonstration or a depiction of an unverified real event. When a metaphor involves real people, companies or political figures, prevent the staging from implying that the depicted event actually happened.

## Opening and ending checks

- Preserve a direct cold open when the locked script already provides one; do not insert a logo bumper before the conflict.
- When a reusable anchor is central to the promise, preview it early enough to show how the video will make the topic understandable.
- Do not introduce new evidence after the final conclusion.
- Return to A-roll for the final factual judgment or scope caveat before a branded outro.
- Outro visuals may recap established elements but must not create new claims.

## Directing workflow

1. Pass the A-roll readiness gate and fix the measured editorial runtime.
2. Divide the transcript into argument beats and chapter boundaries.
3. Identify whether a reusable visual anchor will materially reduce repeated explanation.
4. Apply the visual-necessity gate to each beat, keeping clear beats as A-roll.
5. Route justified interventions to one visual mode and choose presenter presence.
6. Design stateful information beats and source-evidence choreography.
7. Create `broll_requests.json` entries only for independently sourceable real assets required by `SOURCE_EVIDENCE` or `PRODUCT_DEMO` segments.
8. Calculate observed visual durations by mode. Report the result without a target or pass/fail percentage.
9. Validate the plan, request mapping, anchor consistency, source fidelity, semantic motion and metaphor safety.

Read [references/style-profile.md](references/style-profile.md) when the user has not supplied a stronger project style. Read [references/handoff-schema.md](references/handoff-schema.md) before producing final files.

## Output contract

After the A-roll gate passes, produce:

1. `director_plan.json` using `director_plan/3.1`.
2. `broll_requests.json` using `broll_requests/3.0`. An empty `requests` array is valid when no external asset acquisition is required.

Run:

```bash
python3 scripts/validate_director_handoff.py /path/to/director_plan.json /path/to/broll_requests.json
```

The director plan carries editorial treatments. The B-roll request file remains acquisition-oriented and must not contain fabricated UI, rewritten evidence, generic editing commentary, generated metaphors or new narration.

## Quality gates

Reject the handoff until:

- final A-roll and aligned transcript pass readiness checks;
- the timeline is measured, complete and non-overlapping;
- every non-A-roll segment states a real comprehension, proof, demonstration, metaphor or emphasis need;
- every treatment beat records a meaningful state change and information gain;
- every referenced visual anchor exists, remains consistent and is reused only where declared;
- source evidence preserves original identity, exact evidence region and readable exposure time;
- motion graphics explain a relationship, sequence, state change or comparison rather than decorate the frame;
- metaphors are visibly non-literal, cannot act as proof and disclose AI generation when applicable;
- presenter presence has a stated purpose and never obstructs evidence;
- text emphasis remains brief and does not become a substitute B-roll card;
- every real-asset request maps to a director segment and no unrequested asset appears;
- observed visual coverage is reported without being used as a success target;
- long A-roll is accepted whenever narration is already clear and the presenter should remain the anchor.
