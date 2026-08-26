# Evidence-bounded transferability analysis

Use this reference for case studies, implementation stories, comparisons and any request asking what another organization can learn or reuse.

## Purpose

Bridge the gap between a verified case and a script-ready business lesson without turning one case into universal advice. The output should answer:

1. What operational problem was addressed?
2. What task did the technology perform, and what remained with people?
3. What mechanism plausibly connects the design to the reported value?
4. Which parts may transfer to another organization?
5. What conditions must exist for the lesson to work?
6. Which case-specific parts should not be copied?
7. How difficult is the minimum credible implementation?
8. What should a pilot measure before expansion?

## Three evidence layers

Keep these layers explicit:

- `source_established`: the source directly describes the practice, boundary, dependency or result. Cite the supporting claim IDs and preserve attribution where required.
- `bounded_synthesis`: an analyst's transferable conclusion drawn from named verified claims. It may be script-ready as editorial synthesis when the reasoning is explicit and its conditions are stated.
- `implementation_hypothesis`: a proposed application, product path or operating design not established by the case evidence. Keep it context-only until separately verified; never present it as what the case proved.

## Transferability gate

For each proposed lesson, require all of the following:

- a concrete operational action rather than a slogan;
- at least one supporting verified claim;
- an explanation of why the lesson follows from those claims;
- `applies_when` conditions that another organization can check;
- `fails_when` conditions or a clear unknown;
- case-specific elements that should not be generalized;
- an implementation difficulty rating with named drivers;
- a minimum pilot that does not assume unavailable channels, data or permissions;
- evaluation signals covering efficiency, quality and risk when relevant.

Reject a lesson when it merely restates a result, names a product, copies a workflow without prerequisites, or claims a general outcome from a single case.

## Implementation difficulty

Use:

- `simple`: can be piloted inside an existing authorized workflow with human confirmation and no new system integration.
- `moderate`: requires one bounded data flow, permission change or system integration, with human review still in the loop.
- `complex`: requires two-way external channels, persistent state, multiple integrations, automated actions, exception handling or governance across teams.
- `unknown`: available evidence does not establish the required dependencies.

Do not rate a polished demo or vendor tutorial as simple merely because the interface looks easy.

## Minimum pilot rule

The minimum pilot should test the transferable mechanism, not imitate the final architecture. Prefer the lowest-automation version that can reveal whether:

- the selected task is sufficiently repetitive and well-bounded;
- the system extracts or proposes the right information;
- people accept, correct or override its output;
- the handoff preserves context;
- performance differs across relevant groups;
- the required channel and data permissions actually exist.

## Handoff to writing

The fact card should give the writer a small number of ranked lessons, not an inventory of every possible takeaway. Each script-ready lesson must retain its supporting claim IDs, evidence layer and scope. The writer may choose an angle among those lessons but must not upgrade a conditional lesson into a universal recommendation.
