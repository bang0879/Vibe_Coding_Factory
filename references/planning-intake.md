# Planning Intake

Borrow useful idea-refinement patterns from Gajae-Code without running GJC.

Do not install or invoke `gjc` by default. This factory runs inside Codex. GJC external-runner integration is a later optional path only when the user explicitly wants it.

## Principle

The user's first idea is not a build spec. Treat it as raw product intent until Discovery Council has reported options and the user has approved Direction Lock.

Do not turn a vague idea directly into implementation tasks. The safe path is:

```text
idea snapshot
-> discovery council reports
-> option matrix
-> decision brief
-> deep interview only where needed
-> direction lock
-> PRD/GTM/design/planning
```

## Phase 0: Idea Snapshot

Run for every new project or major product direction.

Capture:

- Raw idea in the user's language.
- Known facts.
- Assumptions Codex is making.
- Unknowns that affect product direction.
- Likely technical, UX, business, legal, privacy, or data risks.
- Whether visual monitoring is requested.

Output:

- Update `discovery.idea_snapshot`.
- Add an `idea_captured` event.
- Set `project.current_phase` to `discovery`.

## Phase 1: Discovery Council

Run before PRD/GTM/design and before any implementation task decomposition.

Required reports:

- Product Strategist: target user, problem, JTBD, core value, MVP scope candidates.
- Technical Feasibility Architect: feasible parts, impossible or risky parts, workarounds, stack constraints, integration risks.
- Growth and Moat Strategist: positioning, distribution, monetization, retention, defensibility, business moat ideas.
- UX Strategist: first-use flow, product feel, information hierarchy, UI complexity, trust and onboarding risks.
- Risk Critic: security, privacy, legal, safety, data, operational, and execution risks.
- Planner: viable build paths, sequence, dependencies, confidence, and open blockers.

Each report must include:

- `verdict`: `promising`, `watch`, `risky`, or `block`.
- `top_findings`: 3-5 concise findings.
- `opportunities`: what becomes better if added now.
- `risks`: what could waste time or force rework.
- `questions_for_user`: only questions that materially affect direction.
- `recommended_next_action`.

Store each report in `council_reports[]` and, when useful, in a document artifact such as `docs/FEASIBILITY_REPORT.md`, `docs/MOAT_STRATEGY.md`, or `docs/RISK_REGISTER.md`.

## Phase 2: Option Matrix and Decision Brief

The Orchestrator turns reports into 2-3 direction options.

Each option must include:

- User segment and job.
- MVP scope.
- Differentiator or moat hypothesis.
- Technical path and workaround notes.
- Excluded scope.
- Main risks.
- Estimated difficulty.
- Recommended or not recommended.

Write `docs/DECISION_BRIEF.md` from `templates/decision-brief.md` when the decision is non-trivial.

Decision Brief must end with one decision request:

```text
Decision needed: choose product direction
Recommended: <option id>
Reason: <short reason>
Options: A / B / C
Monitor: <decision id>
Proceeding automatically: wait for Direction Lock approval
```

## Phase 3: Deep Interview

Use Deep Interview only when the option matrix cannot be decided safely.

Rules:

- Ask one question at a time.
- Ask at most 5 rounds by default.
- Target the weakest open decision.
- Preserve the user's language.
- For existing codebases, inspect local evidence before asking about facts Codex can discover.
- Do not implement during Deep Interview.

Clarity areas:

- Goal: what outcome should exist?
- User: who is this for?
- Scope: what is included and excluded?
- Experience: what should it feel like?
- Success: how will we know it is good enough?
- Constraints: stack, files, time, design, integrations, risks.

Output:

- Update `discovery.deep_interview`.
- Add intake question/answer events.
- Update `option_matrix[]` when answers change direction.

## Phase 4: Direction Lock

Direction Lock is the first product contract. It must exist before PRD/GTM/design become final implementation inputs.

Write `docs/DIRECTION_LOCK.md` from `templates/direction-lock.md`.

Direction Lock must include:

- Target user.
- User job.
- Product promise.
- MVP scope.
- Non-goals.
- Technical approach.
- Technical workarounds or constraints.
- Moat hypothesis.
- Business assumptions.
- Design posture.
- Accepted risks.
- Open questions allowed to remain.
- Source council report ids.
- Source decision ids.

Gate passes only when:

- `direction_lock.status` is `approved` or `skipped_by_user`.
- A matching decision exists in `decisions[]`.
- The monitor shows the locked direction and next planning owner.
- A message hands the locked direction to Product Strategist, Growth Marketer, Planner, and Design Studio when relevant.

If the user changes direction later, mark Direction Lock `stale`, reopen affected planning artifacts, and return to Discovery Council or Decision Brief only for the changed scope.

## Phase 5: Consensus Planning

Use Consensus Planning after Direction Lock is approved.

Roles:

- Product Strategist: PRD, product scope, user workflows.
- Growth Marketer: GTM, positioning, activation, retention.
- Planner: implementation approach, task sequence, dependencies.
- Architect: architecture review, tradeoffs, boundaries, risk.
- Critic: actionability, acceptance criteria, verification quality.

Flow:

```text
Direction Lock
-> Product Strategist
-> Growth Marketer
-> Planner
-> Architect review
-> Critic review
-> revision if needed
-> planning approval
```

Consensus passes only when:

- Planner produced a concrete sequence.
- Architect verdict is `approve` or `watch` with accepted risk.
- Critic verdict is `approve`.
- Acceptance criteria and verification are testable.
- The user has approved moving forward when approval is required.

If Architect or Critic rejects the plan:

1. Mark planning as `reopened`.
2. Add the findings to `messages`.
3. Revise only the plan, not implementation.
4. Re-run Architect then Critic.

Default max consensus iterations: 3.

## Monitor Requirements

Show these explicitly:

- Idea Snapshot status.
- Discovery Council report statuses and verdicts.
- Option Matrix with recommended option.
- Latest unresolved user decision.
- Direction Lock status.
- Deep Interview latest question when active.
- Project Brief summary.
- Planner verdict.
- Architect verdict.
- Critic verdict.
- Planning approval gate.

Every verdict should be stored as an artifact or message summary, not buried in prose.
