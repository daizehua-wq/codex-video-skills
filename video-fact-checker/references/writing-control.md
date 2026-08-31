# Writing-control handoff

Use this reference for schema 1.5 fact cards. Its purpose is to make a verified fact card constrain later writing, not merely store research.

## Claim locks

Every claim must carry the following controls in addition to evidence status and allowed wording.

### Event and time

- `event_stage` records whether the claim concerns a plan, announcement, pilot, rollout, deployment, operation, retrospective result, forecast or current status.
- `temporal_scope` records whether the claim is a point-in-time statement, bounded period, ongoing only as of a date, historical statement, future plan or unresolved status.
- A planned, announced or forecast claim must forbid `plan_to_completed`. Its title use must be conditional or prohibited so a headline cannot silently turn intent into completion.
- Later evidence stays attached to its own stage and date. Do not use a later deployment statement to rewrite what an earlier announcement established.

### Metrics

Every `number` claim must provide one atomic `metric_scope` with:

- the metric and exact value text;
- the subject being measured;
- population and measurement window when known;
- baseline or comparator;
- process start and process end when the number measures a workflow duration;
- aggregation type such as average, maximum, percentage or single case;
- measurement method when disclosed;
- evidence character: official record, independent measurement, company/vendor/joint-case performance report, participant self-report, award material or unknown.

Use `null` for genuinely undisclosed dimensions and explain the gap in `notes`; never fill it by inference. A number claim must forbid `metric_scope_change`. Self-reported, vendor-reported, joint-case and award-material performance metrics require spoken attribution and cannot be title-safe without limitations.

### Causality

- `source_established`: the source directly establishes the causal link at the claimed scope.
- `company_attributed`: the company or named source asserts the causal link; narration must attribute it.
- `sequence_only`: the order is verified but causation is not. It must forbid `sequence_to_causation`.
- `bounded_synthesis`: the link is an editorial inference from cited facts and must remain visibly analytical.
- `disputed` or `prohibited`: do not hand off as a factual causal claim.
- Non-causal claims use `not_causal`. If a sentence mixes an event and a causal conclusion, split it into atomic claims.

## Handoff roles

Classify necessity separately from truth:

- `core_proof`: necessary to establish the case or primary lesson;
- `required_boundary`: must appear close to a used claim because it changes interpretation;
- `optional_context`: accurate but removable without breaking the argument;
- `fact_card_only`: useful for audit, conflict tracking or writer awareness but should not enter narration;
- `prohibited`: not publishable as fact.

Do not use `fact_card_only` material merely to demonstrate that cross-checking occurred. A conflict must be assigned to `required_boundary`, `fact_card_only` or `prohibited` so the writer knows whether it changes the spoken claim or belongs only in the audit trail.

## Title controls and forbidden transformations

`title_use` answers whether the claim may anchor a title. `conditional` and `prohibited` claims require explicit `title_limitations`.

Record the likely amplification error in `forbidden_transformations`, including when relevant:

- plan to completed action;
- one rollout stage to another;
- metric-object, baseline, time-window or aggregation changes;
- peak or maximum to average;
- subset to company-wide scope;
- sequence to causation;
- attributed report to independent confirmation;
- single case to universal result;
- capability or scenario transfer between products.

These are transformation classes, not a substitute for concrete `forbidden_wording`. Keep both.

## Lesson ranking

For an applicable case, rank exactly one lesson `primary`. Other lessons are `supporting` or `context`. A primary lesson must be `script_ready` or `conditional`, preserve a spoken boundary and list the generalizations the writer must not make.

Ranking prevents the writer from treating every available lesson as a competing main line. It does not choose the final hook or editorial style.

## Guidance parameters

Every implementation stage must state its parameterization:

- `none`: no precise number, duration, threshold or range is prescribed;
- `source_bounded`: precise parameters come from cited claims;
- `analyst_proposed`: parameters are editorial guidance and the note must say they are not case facts.

If stage text contains a precise numeric parameter, `none` is invalid. Source-bounded parameters require supporting claim IDs. Scale gates for a ready or conditional path must cover efficiency, quality and risk.

## Canonical artifact

Treat `fact_card.json` as the canonical source. Render `fact_card.md` and `sources.md` from the final JSON after validation. Do not independently repair a derived file and leave the JSON unchanged. On revision, regenerate all derived artifacts from the same validated JSON and record the base artifact in `revision_audit`.
