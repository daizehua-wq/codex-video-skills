# B-roll Execution Policy v1.0

## Source ranking

Use the request’s explicit order. When it only supplies source classes, use:

1. `T1_OFFICIAL_CORPORATE` — named company, product or person’s official source.
2. `T2_LEGAL_PRIMARY` — regulatory filing, court record, standard, dataset or other first-party primary document.
3. `T3_AUTHORITATIVE_MEDIA` — established editorial source with clear attribution.
4. `T4_NAMED_PARTNER` — named technology provider, partner or distributor.
5. `T5_LICENSED_STOCK` — licensed generic footage for explicitly generic scenes.

Source tier never repairs project mismatch. Reject a high-tier source that depicts the wrong product, period or person.

## Project consistency

Record one of:

- `CONFIRMED_EXACT`: exact requested product, person, event, document or workflow.
- `CONFIRMED_CONTEXT`: correct project context but not the exact requested action.
- `GENERIC_SCENE_NOT_PROJECT_SPECIFIC`: permitted generic licensed scene.
- `MISMATCH_REJECTED`: discovered but excluded from candidates.
- `UNVERIFIED_REJECTED`: identity or period could not be established.

Do not deliver rejected assets inside `assets/`.

## Rights status

Record one of the following or a more specific compatible value:

- `LICENSED_FREE_USE`
- `LICENSED_PAID`
- `OFFICIAL_MEDIA_CLEARANCE_REQUIRED`
- `EDITORIAL_USE_REVIEW_REQUIRED`
- `EDITORIAL_LICENSE_REQUIRED`
- `PUBLIC_RECORD_EDITORIAL_REVIEW`
- `RIGHTS_UNKNOWN_REJECTED`

Record the license name and license URL when a license exists. Do not infer a Creative Commons, press-use or commercial-use grant from the absence of a copyright notice.

## Acquisition and processing

- Save the original source or a stable source reference before transformation when legally and technically possible.
- Use lossless PNG for text-heavy screenshots and document renders.
- Use high-quality JPEG only when the source is photographic and text fidelity is not material.
- Deliver ordinary video as H.264 MP4 unless the request or editing system requires another codec.
- Remove audio only when it is unnecessary and the removal is recorded.
- Record crop, resize, frame-rate conversion, duration trim, audio removal and transcoding.
- Keep requested pre-roll and post-roll handles for video candidates.
- Preserve page identity, publication date, speaker/event identity or product branding when those establish evidence.

## Candidate selection

The recommended candidate should maximize, in order:

1. exact request fit;
2. source reliability;
3. rights clarity;
4. edit usability and readability;
5. technical quality.

Alternates should be independently usable substitutes. A second crop of the same source is acceptable when it serves a genuinely different editorial need such as source identity versus readable detail; record that relationship.

## Stopping conditions

Mark a request blocked rather than weakening its guardrails when:

- every discoverable asset is a forbidden or adjacent product;
- the person, date, event or document cannot be verified;
- only unknown-source material is available;
- acquisition would require credentials, payment or rights authority not granted by the user;
- the permitted fallback is also unavailable.

Report the searches attempted, the blocking condition and the smallest director-side change that would make the request executable. Do not make that change yourself.

