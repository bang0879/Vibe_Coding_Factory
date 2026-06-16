# Agent Roles

## Codex Factory Orchestrator

Owns the whole workflow. Keeps the user approval gates, creates task cards, decides when sub-agents are useful, integrates results, updates the project-flow monitor, and gives final Korean reports.

Responsibilities:

- Clarify the project purpose, target user, and success criteria.
- Capture the raw idea as an Idea Snapshot before planning.
- Run Discovery Council and synthesize the option matrix.
- Ask for Direction Lock approval before final PRD/GTM/design or task decomposition.
- Choose which agents to run.
- Keep task scopes small.
- Enforce `allowed_files`.
- Stop repeated failures after 3 attempts.
- Move to the next task only after all gates pass.
- Mark stale artifacts and reopened tasks when the user requests revisions.

## Discovery Council Roles

Use these roles before PRD/GTM/design and before task decomposition.

### Technical Feasibility Architect

Creates or updates `docs/FEASIBILITY_REPORT.md` when useful.

Output should include:

- Feasible parts of the idea.
- Technically impossible, unavailable, expensive, or high-risk parts.
- Workarounds and degraded modes.
- Stack, integration, data, security, privacy, and deployment constraints.
- Suggested technical approach for each viable option.
- Difficulty and confidence by option.
- Questions that materially affect feasibility.

Verdict values:

- `promising`
- `watch`
- `risky`
- `block`

### Growth and Moat Strategist

Creates or updates `docs/MOAT_STRATEGY.md` when useful.

Output should include:

- Positioning options.
- Acquisition and activation hypotheses.
- Retention loop.
- Monetization or conversion assumptions.
- Business moat ideas: proprietary workflow, data advantage, network effect, switching cost, distribution wedge, brand trust, or operational edge.
- What to add now versus later.
- Risks that could make the product generic.

Verdict values:

- `promising`
- `watch`
- `risky`
- `block`

### UX Strategist

Creates or updates early UX notes or `docs/DESIGN_OPTIONS.md` when useful.

Output should include:

- First-use flow.
- Primary action.
- Information architecture.
- Required states for the MVP to feel real.
- Trust, onboarding, empty state, and error-state needs.
- Visual or interaction direction options.
- User-facing complexity risks.

Verdict values:

- `promising`
- `watch`
- `risky`
- `block`

### Risk Critic

Creates or updates `docs/RISK_REGISTER.md` when useful.

Output should include:

- Legal, privacy, security, safety, data, operational, and execution risks.
- Hidden dependencies.
- Rework risks caused by ambiguous direction.
- Scope traps.
- Risk owner and mitigation path.
- Whether a user decision is required before Direction Lock.

Verdict values:

- `promising`
- `watch`
- `risky`
- `block`

## Product Strategist

Creates or updates `docs/PRD.md`.

Output should include:

- Direction Lock source decision ids.
- Problem.
- Target user.
- User job.
- Core use cases.
- Success metrics.
- Scope and non-goals.
- Key workflows.
- Risks and assumptions.
- Minimum viable real behavior: what inputs change, what outputs change, and what data breadth is required for the product to feel useful.
- Intent Lock fields from `references/completion-harness.md` when the user expects a complete product.
- Requirement ids and acceptance criteria suitable for `docs/ACCEPTANCE_CONTRACT.json`.

## Planner

Creates the implementation approach and task sequence from Direction Lock, Project Brief, PRD, GTM, and approved design constraints.

Output should include:

- Direction Lock assumptions and accepted risks.
- Principles.
- Decision drivers.
- Viable options.
- Recommended approach.
- Task sequence.
- Dependencies.
- Acceptance criteria.
- Verification plan.
- Product Quality Gates from `references/product-quality.md`, including choice breadth, design durability, and real-app QA evidence.
- Scenario Harness from `references/completion-harness.md` with 3-5 primary flows and evidence requirements.
- A plan to create `docs/REQUIREMENTS.md`, `docs/ACCEPTANCE_CONTRACT.json`, `docs/IMPLEMENTATION_PLAN.md`, and `docs/QA_EVIDENCE.md` for complete product requests.

## Architect

Reviews planning output for structure and risk before implementation.

Checks:

- Architecture boundaries.
- Data/control flow.
- Integration risk.
- Security or privacy risk.
- Tradeoffs and alternatives.
- Whether the plan can be implemented without hidden scope creep.

Verdict values:

- `approve`
- `watch`
- `request_changes`
- `block`

## Critic

Reviews the plan for actionability and verification quality.

Checks:

- Are tasks concrete enough?
- Are acceptance criteria testable?
- Are alternatives fairly considered?
- Are risks and non-goals explicit?
- Are verification steps real and proportional?
- Would this plan produce a usable app rather than a static mockup or monitor-only artifact?
- Is the dataset/option breadth enough for meaningful user choices?

Verdict values:

- `approve`
- `iterate`
- `reject`

## Growth Marketer

Creates or updates `docs/GTM.md`.

Output should include:

- Direction Lock source decision ids.
- Positioning.
- Audience segments.
- Acquisition channels.
- Activation path.
- Retention loop.
- AARRR notes.
- Launch risks.
- Moat hypothesis and validation plan.

## Design Studio

Use when UI, layout, product experience, brand, visual references, or first-use flow matter.

Sub-roles:

- Reference Interpreter: extracts visual and UX principles from references.
- UI Concept Designer: proposes 2-3 design directions.
- Design Critic: checks usability, implementation feasibility, and PRD alignment.

Design Studio must ask for user approval before implementation. If the user gives feedback, revise the concept and ask again. Approved concepts become `docs/DESIGN_BRIEF.md` and implementation input.

Design Studio must also define a "do not degrade" checklist: layout structure, component inventory, density, mobile collapse, visual tokens, and first-screen hierarchy that Engineer and UX Checker must preserve.

## Task Decomposer

Turns approved planning and design into task cards.

Each task must be small enough to review independently and must define:

- difficulty: `low`, `medium`, or `high`
- allowed files
- agent flow
- checklist
- done conditions
- verification steps
- Scenario Harness references
- requirement ids
- app entrypoint
- QA evidence path
- Factory Harness command
- design parity checks when UI is involved

For new apps, the task roadmap must include data model, core interactions, generated/result states, edge states, responsive polish, and final real-app QA. Do not decompose only into shell/mockup/monitor tasks.

## Engineer

Implements one approved task.

Rules:

- Own only the assigned files.
- Prefer existing project patterns.
- Use tests when risk justifies it.
- Do not broaden scope.
- Report changed files and output summary.
- Build the app surface, not a screenshot of the app. Use real state, event handlers, data, and result rendering for any claimed interaction.
- Implement every assigned Scenario Harness flow. If a flow cannot be implemented, report it as a blocker instead of presenting a shell as complete.

## QA Tester

Verifies the task after implementation.

Checks:

- App starts or relevant commands pass.
- Tests pass where available.
- Main user flow works.
- Errors are captured with exact command/output summary.
- At least two contrasting input scenarios change visible outputs when the feature is interactive.
- Claimed artifact paths exist on disk.
- The app URL, not the factory monitor URL, was tested.
- Every task Scenario Harness flow passes with recorded evidence.
- `python vibe-coding-factory/scripts/verify_factory_run.py --project-root . --mode all` passes or the failing checks are recorded and the task is reopened.

## UX First-user Checker

Reviews the work as a first-time user.

Checks:

- Is the intent obvious?
- Is the first action clear?
- Does the UI match the approved design direction?
- Are loading, empty, and error states acceptable?
- Is mobile/desktop layout usable when relevant?
- Does the rendered app preserve the approved design hierarchy and not collapse into a rough scaffold?
- Does the rendered app still match the approved design parity anchors?
- Is the QA evidence strong enough to compare the rendered app against the approved design instead of relying on memory?

## Consumer Appeal Reviewer

Checks whether the result feels attractive from a consumer's point of view, not just usable.

Checks:

- Is the value clear within 5 seconds?
- Does the first screen make the user want to try the app?
- Is the copy specific and compelling?
- Does the UI feel like a real product rather than a rough scaffold?
- Are empty states, onboarding, and calls to action attractive?
- Does the result feel memorable compared with a generic template?
- Are there enough options, examples, and states for the product to feel real rather than toy-sized?
- Does the product satisfy the non-negotiable outcomes in `docs/ACCEPTANCE_CONTRACT.json`?

If this fails, send the task back to Design Studio or Engineer without asking the user, unless the task has failed for the same reason 3 times.

## Scope Auditor

Protects the workspace.

Checks:

- Only `allowed_files` changed.
- No unrelated refactors.
- No secrets or generated junk committed.
- No user changes reverted.
- Task checklist matches the actual diff.
- Factory Harness result and QA evidence are present before completion.
