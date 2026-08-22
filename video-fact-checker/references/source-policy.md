# Source and claim policy

Read this reference when the task requires external research, source ranking, quotation checking or conflict resolution.

## Source tiers

### A — Primary official record

Examples: official product documentation, company release, regulator filing, court record, legislation, public dataset, original research paper, event recording or organizer transcript.

Use it to establish what the issuing body officially published. Company-authored metrics remain company-reported unless independently audited.

### B — Primary attributed statement

Examples: named executive speech, interview, earnings-call answer, signed post or identifiable first-person account.

Use it to establish that the person made the statement. Carry attribution when the underlying event, number or outcome is not independently verified.

### C — Independent authoritative secondary source

Examples: original reporting by a reputable newsroom, expert analysis with disclosed evidence, or an independent institution's review.

Independence requires a distinct evidence-gathering chain. A different domain or headline is not enough.

### D — Other secondary or republished source

Examples: syndicated stories, aggregators, rewritten press releases, transcript reposts and commentary accounts.

Use these for discovery, context or access to a text that is clearly labeled as a repost. Do not count multiple republications as independent corroboration.

### E — User-supplied or unattributed material

Examples: notes, screenshots without provenance, anonymous posts, generated summaries and unsourced data cards.

Treat as a lead. Do not use as the sole evidence for a publishable factual claim unless the user explicitly wants a personal-experience statement and its status is labeled.

## Verification status

- independently_verified: supported by an appropriate primary record or genuinely independent evidence.
- primary_source_confirmed: confirmed by the entity's own official record; underlying self-reported performance may remain unaudited.
- attributed_claim: established only as a named source's statement.
- secondary_only: supported only by secondary reporting with no accessible primary record.
- unverified: insufficient evidence.
- disputed: credible sources materially conflict.
- false: contradicted by reliable evidence.

Verification status and source tier are separate. An official source can still contain a self-reported claim that requires attribution.

## Script-use decisions

- direct: the fact may be stated within its recorded scope. Attribution may still be stylistically useful.
- attributed: the narration must identify the source close to the claim.
- prohibited: the claim must not appear as fact. It may be discussed only as an explicitly labeled rumor, dispute or unknown when the user's brief requires that discussion.

## Conflict handling

When sources disagree:

1. Compare dates, definitions, measurement windows and entity scope.
2. Trace secondary reports to their upstream source.
3. Prefer the closest primary record for what was said or published.
4. Do not average incompatible numbers.
5. Record the conflict and the publication consequence.

## Temporal and revision audit

For dates, numbers, quotations, causal claims, forecasts and source-sensitive results, search across time rather than only inside the page supplied by the user.

- Search the named event window and later official updates through the fact card's `checked_at` date.
- Search relevant entity, partner, supplier, regulator or filing domains when they can publish a primary record.
- Keep later evidence attached to its own rollout stage, product version and measurement window. Later confirmation does not retroactively make a result part of an earlier release.
- When checking a revised card, diff the revision to locate changes, then reverify every material claim and regenerate dependent statuses, conflicts and wording.

## Negative evidence scope

Use the narrowest conclusion supported by the completed search:

- `specified_source_only`: the claim was not found in one or more named documents;
- `official_sources_checked`: the claim was not found after a recorded search of relevant official domains and dates;
- `broad_search_completed`: the claim was not found after the official search plus appropriate independent and secondary discovery routes.

Do not write "untraceable", "no official source", "not disclosed", "never" or an equivalent global negative when the audit supports only `specified_source_only`. Record searched domains, source IDs, date range, upstream-trace status and a concise result summary in `verification_audit.negative_claim_audits`.

## Upstream tracing

For every D-tier secondary source that carries a material result:

1. search the distinctive number, quotation or phrase;
2. compare publication dates and wording;
3. follow cited links or identify the earliest accessible primary record;
4. record the upstream source IDs and give the secondary page the same `independence_group` as its upstream chain;
5. if the trace remains unresolved, label it unresolved and do not upgrade the claim beyond secondary evidence.

## Wording discipline

Allowed wording must carry all material limitations. In particular:

- replace an unaudited absolute with a named attribution;
- distinguish one day or one peak from an ongoing daily rate;
- distinguish one case from a company-wide result;
- distinguish association or sequence from causation;
- distinguish a product, model, company and campaign with similar names;
- distinguish a direct quote from a paraphrase.

Prohibited wording should capture likely amplification errors, not every imaginable sentence.
