# Spoken factual-video style v2.0

Read this reference when the user has not supplied an overriding style guide or asks to improve hook strength, structure, pacing, oral delivery or concision.

For Chinese narration, also read [chinese-spoken-logic.md](chinese-spoken-logic.md). A Chinese draft must first be reorganized into native listening order; shortening translated report sentences is not enough.

## Voice

- Sound like a well-informed person explaining one important thing to another person.
- Prefer short, speakable sentences and concrete verbs.
- Keep necessary technical terms, then translate them into plain language.
- Avoid report-like headings in the spoken body, ceremonial transitions and stacked abstractions.
- Do not become casual at the cost of factual precision.

## Opening: verified anchor plus promise

For short factual commentary, begin from a specific, defensible spoken anchor: a consequence, result, cost, contrast, decision or recognizable problem. Then establish why the viewer should continue. Read [hook-framework.md](hook-framework.md) when designing, comparing or revising the opening.

A useful progression is:

    verified spoken anchor → audience entry → compressed question → honest content promise

Put attribution and minimum context beside the step that needs them. The viewing promise tells the audience what will become understandable by the end. It must not promise a visual device, investigation, test or conclusion the script does not actually deliver.

Aim to establish the tension within roughly the first five spoken seconds and the central question or promise shortly afterward. This is a default, not permission to distort weak evidence.

Avoid:

- chronology before the audience knows why it matters;
- unsupported superlatives or catastrophe language;
- withholding the source of a self-reported number for too long;
- restating the opening consequence in the next two paragraphs;
- a vague promise such as “今天聊聊这件事”.
- using “你” as a substitute for a real audience stake;
- presenting several unrelated questions before the viewer knows which one the video answers.

## Information waves

Organize substantial sections as a useful variation of:

    question → evidence → explanation → judgment

- A question creates a specific knowledge gap.
- Evidence states what the approved facts establish.
- Explanation translates the mechanism or meaning into plain language.
- Judgment closes the gap and creates the next question.

Not every section needs all four lines. The test is whether the viewer can tell what was established, what it means and why the next paragraph follows.

## Case before method, method before tools

For case-based scripts, first state what the case establishes, then extract the permitted lesson, then explain its applicability and difficulty. Do not jump from a company example directly to a named tool or setup sequence.

Keep structural concepts separate from rollout stages. A framework describing “what parts exist” should not repeat a maturity path describing “what happens first”. Each list must answer a different audience question.

## Separate fact from interpretation

Keep these layers audible:

1. **Source fact:** who said, published or observed what.
2. **Plain-language explanation:** what the fact means in context.
3. **Editorial takeaway:** the bounded conclusion the script draws.

Do not fuse an attributed statement and the writer's interpretation into one sentence if the audience could mistake the interpretation for source wording. Useful spoken separators include “按他的复盘”, “换句话说”, “这意味着” and “更准确地说”. Treat them as patterns, not mandatory phrases.

## Fact-card completeness versus narration completeness

The fact card retains the full evidence record: usable claims, conflicts, unknowns, source rankings and prohibited wording. Narration uses only what the audience needs to answer the locked core question.

Before adding a verified fact, ask:

- Does it establish what happened, explain the mechanism, bound the conclusion or change the final judgment?
- Would deleting it create a real misunderstanding or evidence gap?
- Is it merely interesting, numerically strong or available from research?

Omit the fact when only the last answer is yes. “New information” is not enough; it must create useful cognitive progress.

Do not introduce a metric, adjacent product, technical unknown or source conflict solely to explain why it will not be used. Keep that audit trail in the fact card and machine handoff.

## Attribution economy

Spoken attribution is necessary when the fact card requires it or when the source changes how the audience should weigh the claim, especially for:

- company-reported performance or adoption numbers;
- allegations, disputes and named opinions;
- claims supported only by a supplier, executive or single case;
- quotations and wording whose source matters.

Do not list several sources to demonstrate cross-validation when one clean, safely worded sentence will do. Do not narrate agreement between sources unless that agreement is itself relevant to the story.

Traceability still belongs in `script_claims.json`; removing source names from speech does not remove factual mapping.

## Frameworks and lists

When presenting a named framework or list, make every item concrete:

    stable term → recognizable manifestation → practical consequence

Keep the original labels stable. Arrange items in a cognitive or causal sequence when the evidence allows it, so each prepares the next. Use one concise manifestation per item; do not pad every item to equal length.

A list fails when the audience can repeat the labels but cannot explain how the items differ.

## Transitions

Connect paragraphs by answering the question created by the previous paragraph. Prefer plain spoken bridges such as:

- 但真正的问题还不是这个。
- 可认识 AI，和把 AI 变成生产力，是两回事。
- 钱和模型都有了，为什么还是没跑通？
- 那后来他们怎么调？

Use these as patterns, not mandatory phrases. Avoid announcing a section that could simply begin.

## Scope and attribution

- Put attribution before or immediately after a sensitive number, allegation or self-report.
- State a boundary before the audience can overgeneralize.
- Introduce a single case as a case and close it with its limitation.
- Distinguish a first-phase problem from the outcome of an entire transformation.
- Do not let a forceful takeaway silently upgrade the evidence.
- Do not let a “why” question imply causation when the evidence establishes only sequence, coexistence or one organization's implementation choices. Reframe toward “what was designed”, “what changed” or “what the case can show”.

## Ending closure

The ending should:

1. answer the central question raised near the opening;
2. compress the explanation into a transferable judgment;
3. add no new factual claim, number, example or source;
4. stop after the strongest clean line instead of explaining the conclusion again.

A call to action may follow, but it cannot replace the conclusion.

## Compression pass

Delete or rewrite a paragraph when it only:

- restates the previous sentence;
- announces that an explanation is coming;
- repeats a disclaimer already understood;
- uses professional language where a concrete action is available;
- delays the next piece of information;
- names a framework item without making it distinguishable;
- adds intensity without adding meaning.
- reports how sources were cross-checked instead of explaining the subject;
- introduces information only to disclaim, exclude or compare it;
- is factual and new but unnecessary to the locked core question.

Intentional repetition is allowed for a final rhetorical beat, but accidental duplicate lines must be removed.

Completeness is not the use of every verified claim. Concision is not a preset word count or duration. When the user leaves duration open, finish the explanation first, then measure it.

## Read-aloud and duration pass

Read the script as speech, not as prose. Fix:

- sentences that require a second breath;
- noun piles and nested clauses;
- consecutive sentences with the same rhythm;
- unclear pronouns;
- numbers that are difficult to hear;
- punctuation that does not match the intended pause.

For Chinese, perform the logic-order pass before this sentence-level pass. Confirm that qualifications are present at first mention, concrete actors and actions precede abstract labels, and audit language has not become the narration's transition system.

Estimate duration from the narration body, excluding the Markdown title. For ordinary Mandarin commentary, `4.0–5.0` non-whitespace characters per second is a planning range; choose and record the actual assumption. Revise when the estimate misses a stated target by more than 15 seconds or 15 percent, whichever is larger. Human recording remains the final timing source.
