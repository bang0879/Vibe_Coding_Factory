# Project Management

Use lightweight project discipline so parallel Codex work does not corrupt the main workspace.

## Feature-Slice Discipline

Treat each implementation feature as the unit of isolation:

- One feature slice gets one branch.
- Parallel feature slices get separate worktrees.
- One AI/Codex session should focus on one feature slice, then be closed or archived when the slice is done.
- One PR should represent one feature slice or one fix.
- Avoid carrying implementation context from a finished feature into the next feature unless it is part of the integration summary.

## Branch and Worktree

For real implementation work:

- Prefer one branch per feature.
- Prefer one worktree per parallel session.
- Keep each agent's write scope disjoint.
- Close or archive sessions when their feature task ends.
- If two agents need to edit overlapping files, do not run them in parallel unless the orchestrator has a clear merge plan.

## GitHub Issue and PR

When GitHub is available and the user wants it:

- Create one issue per implementation plan or feature slice.
- Put task cards in the issue body.
- Include requirement ids, scenario ids, acceptance criteria, expected app entrypoint, and verification commands in the issue body.
- Use PR descriptions that close the issue automatically with `Closes #123`, `Fixes #123`, or equivalent keywords.
- Keep PRs small and tied to one feature or fix.
- Ask AI/Codex to create or update issues from the approved implementation plan when the user wants GitHub tracking.
- Link every PR back to exactly one primary issue unless the change is intentionally cross-cutting.
- A PR cannot be treated as ready unless its description includes the Factory Harness command and result.

## Context Hygiene

Reduce session contamination:

- Start a fresh AI session for a new feature slice when possible.
- End the session with a short integration note: branch, worktree, issue, PR, files changed, checks run, and remaining risks.
- Do not let follow-up sessions infer old context from chat memory alone; point them to the issue, PR, task card, and monitor state.
- Keep the Factory Monitor as the cross-session state source, not a substitute for GitHub issues or PRs.

## Task Card Fields

Each task should include:

- `branch_name`: suggested branch.
- `worktree_path`: suggested worktree.
- `issue_id`: GitHub issue id or `none`.
- `allowed_files`: files the task may edit.
- `checklist`: concrete pass/fail items.
- `verification`: exact command or manual check.

## Parallel Work Rule

Run parallel agents only when:

- Tasks are independent.
- Write scopes do not overlap.
- The orchestrator can integrate results without guessing.

If scopes overlap, run tasks sequentially.
