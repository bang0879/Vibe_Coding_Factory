# Design Studio

Use Design Studio before implementation when the user provides references or when layout, brand, product feel, onboarding, dashboard design, landing pages, or interaction design matter.

## Flow

1. Reference Interpreter analyzes the user's references.
2. UI Concept Designer proposes 2-3 directions.
3. Design Critic reviews each direction.
4. Codex reports the options in Korean.
5. User chooses or revises one direction.
6. If the user gives feedback, revise the chosen direction and present the revised concept again.
7. The selected and approved direction becomes implementation input.

## Reference Interpreter Output

Create `docs/DESIGN_BRIEF.md` when useful.

Include:

- Visual tone.
- Layout patterns.
- Color and typography cues.
- Interaction cues.
- Information hierarchy.
- What to copy as inspiration.
- What not to copy.
- Accessibility or usability concerns.
- Design durability rules: what must not visually degrade during implementation.

## UI Concept Designer Output

Create `docs/DESIGN_OPTIONS.md` when useful.

For each option:

- Name.
- Target feeling.
- Screen structure.
- Key components.
- Layout notes.
- Implementation complexity.
- Best fit / weak fit.
- Required states and interactions.
- Dataset or content breadth needed for the concept to feel real.

When the user has already selected a direction and gives feedback, produce one revised concept instead of 2-3 unrelated new options.

The revised concept must include:

- What changed from the previous concept.
- Which user feedback it addresses.
- Updated first screen structure.
- Updated visual hierarchy.
- Updated component/layout notes.
- Remaining tradeoffs.

## Design Critic Checklist

Check:

- Does it satisfy the PRD?
- Can a first-time user understand it?
- Is the primary action obvious?
- Does it avoid visual clutter?
- Can it be implemented with the current stack?
- Does it work on mobile and desktop when relevant?
- Is the design specific enough that Engineer cannot collapse it into a generic template?
- Are the required states, option breadth, and generated/result views designed?

## Approval Rule

Do not let Engineer implement a visual UI task until the user approves a design direction.

If the user says to skip design, record:

```text
DESIGN skipped by user
```

## Concept Approval Gate

Use this gate whenever there is user-facing UI:

```text
reference_intake -> concept_options -> design_critique -> user_concept_approval -> implementation_brief
```

The gate passes only when the user clearly approves a concept or says to skip design.

Approval must include enough implementation detail to preserve quality: layout structure, component inventory, primary states, mobile behavior, and visual tokens. If these are missing, ask Design Studio for a stronger concept before implementation.

Design Studio must produce design parity anchors that can be checked after implementation:

- First-screen layout zones.
- Primary and secondary actions.
- Component inventory.
- State inventory.
- Spacing/density rules.
- Visual token summary.
- Concrete "implementation must still look like this" notes.
- Design fidelity contract: approved artifacts, layout fingerprint, component count floor, must-keep components, visual quality floor, forbidden degradations, and screenshot/browser evidence requirement.

For complete product requests, copy these anchors into `docs/ACCEPTANCE_CONTRACT.json` under `design_invariants`. The Engineer and UX Checker must treat those invariants as a contract, not inspiration.

After implementation, UX Checker must compare the rendered app against these anchors with browser evidence or screenshots. If the output looks like a different design, generic template, browser-default form, or visibly cheaper version of the approved concept, the concept is not implemented and the task fails.

UX Checker must record design parity evidence in `docs/QA_EVIDENCE.md` before a user-facing task can be marked `done`.

If the user provides a reference or feedback after approval:

1. Mark the previous concept artifact as `stale`.
2. Mark the design task as `reopened`.
3. Produce a revised concept.
4. Ask for approval again.
