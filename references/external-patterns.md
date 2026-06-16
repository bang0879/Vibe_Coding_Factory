# External Patterns

Use these patterns as guardrails when running the factory. They are distilled from current public docs and open-source agent builders, then translated into local, executable rules.

## Isolation and Parallel Work

- Use feature-scoped branches or worktrees when parallel sessions can edit overlapping files.
- Keep one AI session per feature or issue, then close or summarize it when the PR is ready.
- Do not share noisy exploration logs through the main context; use agent summaries and task cards.

## Planning Before Editing

- Start from a written requirement contract before implementation.
- Convert user intent into requirement IDs, scenario IDs, design invariants, and acceptance checks.
- Require the user to decide only on product direction, risky scope, or unrecoverable blockers.

## Subagent Discipline

- Use specialized agents for self-contained work that can return a summary.
- Chain agents only when the handoff artifact is explicit: input, output, next owner, and verification status.
- Every agent card must say what changed or what was discovered, not just repeat its persona.

## Executable Completion

- Treat user-visible behavior as the primary test target.
- Prefer browser/E2E checks that operate through rendered UI, accessible names, and real inputs.
- Require at least two contrasting successful scenarios and one edge/error state before claiming done.
- A button that clicks without changing persisted or derived state is not completion evidence.

## Issue and PR Traceability

- Implementation plans should become issues when the project is under GitHub workflow.
- PR descriptions must link or close the related issue and include verification commands/results.
- Task cards should include the issue/PR IDs when they exist, so the dashboard can show what is done and what remains.

## Open-Source Builder Lessons

- Natural-language code generators are strongest when the product spec is explicit and checked repeatedly.
- Multi-agent systems need visible workflow topology, not just a list of personas.
- Durable memory and reusable experience should be written as small project facts, decisions, and failure recoveries.
- Dashboards should show acceptance, handoff, evidence, and blockers more prominently than decorative progress.
