# Case-to-method writing

Read this reference for company cases, implementation stories and any script whose value depends on what another organization can learn.

## The writing problem

A verified case is not yet a useful script. The writer must convert:

    what happened → why it matters → what may transfer → under what conditions → how to begin

Do not skip directly from “what happened” to named tools. That produces a product walkthrough, not a transferable argument.

## Lesson gate

Before writing, choose one central lesson from `fact_card.transferability.lessons`.

The lesson must:

- be `script_ready`, or `conditional` with its conditions preserved;
- answer a real decision faced by the target audience;
- have enough supporting claim IDs to explain why it follows from the case;
- contain an operational action, not only a slogan;
- have a credible implementation difficulty and minimum pilot.

If several lessons matter, rank them. Use one as the thesis; other lessons may support it only when removing them would create a real gap. Do not write a catalogue of takeaways.

Then read `fact_card.transferability.implementation_path`. A `ready` or `conditional` path is guidance, not a sourced description of the case company's rollout. Preserve its assumptions, human-control points, difficulty and exit criteria. If its status is `insufficient_evidence`, state the blocker rather than inventing missing stages.

## Case-to-method spine

Use this shape when it fits the selected lesson:

1. **Audience consequence or decision:** what the viewer risks, loses, gains or must choose.
2. **Case mechanism:** the minimum facts showing what the organization did differently.
3. **Transferable lesson:** the operational principle supported by that mechanism.
4. **Applicability boundary:** when the lesson works, when it fails and what is case-specific.
5. **Implementation path:** use the fact card's staged guidance, beginning with the lowest-risk version and advancing only when its exit criteria are met.
6. **Difficulty:** what makes implementation simple, moderate, complex or unknown.
7. **Scale gate:** what efficiency, quality and risk signals must improve before expansion.

The case is evidence inside this spine, not the thesis by itself.

## Detail order

Explain the business design before implementation detail:

    task division → handoff or operating boundary → prerequisites → staged adoption → tools if explicitly needed

Named products belong late and only when the user requests them or the decision depends on their verified capabilities. Never imply that selecting a tool creates integrations, permissions, channels or operating rules that have not been established.

## Writing diagnostics

Reject or revise a draft when:

- it accurately summarizes the company but cannot state what another organization should learn;
- the “lesson” is merely a result number or product name;
- the domestic or audience application appears without a bridge from case mechanism to local constraint;
- several paragraphs repeat the same takeaway in different words;
- structural layers and rollout stages are mixed into one list;
- implementation detail arrives before the audience understands the method;
- “simple” or “easy” appears without concrete dependency analysis;
- the ending celebrates the case instead of answering the audience's decision.

## Spoken compression

Each paragraph should do one new job. After a longer mechanism sentence, use a short judgment or transition to create breathing room. Keep framework labels stable, but do not repeat their definitions later. When two consecutive paragraphs mean the same thing, keep the sharper one.

The ending should compress the selected lesson into one bounded action. Stop once that action answers the opening.
