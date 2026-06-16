# Loop Rules

## Loop Engineering Principle

The factory is not a one-shot prompt. It is a repeatable loop:

1. Execute.
2. Verify.
3. Fix if needed.
4. Stop after 3 repeated failures.
5. Report the blocker clearly.

## Difficulty Gates

Use these machine labels:

- `low`: small, local, low-risk change. Execute automatically.
- `medium`: bounded feature or refactor with clear files. Execute automatically, then verify.
- `high`: broad, ambiguous, destructive, cross-system, security-sensitive, payment-related, data-loss risk, or requiring external installation. Ask the user first.

## Three-Failure Rule

Track repeated failures by cause, not by command.

If the same cause fails 3 times:

- Stop the loop.
- Do not invent a risky workaround.
- Report what was tried.
- Report the best next question or required external action.

## Allowed Files Rule

Every task must name `allowed_files`.

During execution:

- Read any needed project files.
- Write only the allowed files.
- If another file must change, stop and update the task card or ask the user.

## Proceed Rule

Move to the next task only when all are true:

- Engineer says done.
- Claimed app files actually exist on disk.
- User-facing app behavior is exercised through the app URL, not through the factory monitor URL.
- At least one real input/state change causes a visible output change when the task claims interactivity.
- Every primary scenario in the task's Scenario Harness passes.
- The executable Factory Harness passes for the active project when the task is user-facing or the run is being marked complete.
- QA passes or documents accepted risk.
- UX check passes when UI/user flow is involved.
- Consumer Appeal passes when the work is user-facing.
- Scope audit passes.
- User approval was collected for any `high` task.

## Real App Gate

The factory monitor is not the app. A dashboard, static mockup, generated screenshot, or embedded sample state never counts as implementation.

For any task that claims a usable app or interactive feature:

1. Open the actual app entrypoint, such as `app/index.html`, `localhost`, or the framework route.
2. Change at least one user input, filter, selection, or control.
3. Verify the displayed result changes because of app state or app logic.
4. Verify every claimed artifact path exists.
5. If the app entrypoint or behavior does not exist, mark the task `failed` or `reopened`, not `done`.

Do not mark the factory phase `complete` when only `.factory/**`, monitor HTML, docs, or static screenshots exist.

## Product Quality Gate

Before marking a user-facing app task `done`, verify:

- The task satisfies `references/product-quality.md`.
- There is meaningful data or option breadth for the product category.
- Two contrasting input scenarios produce different visible outputs.
- The rendered app still matches the approved design structure and does not look like a broken scaffold.
- Edge states are present or the accepted risk is recorded.
- The rendered UI passes design parity against `docs/DESIGN_BRIEF.md`.
- The Completion Contract in `references/completion-harness.md` passes when the user requested a complete product.
- `references/factory-harness.md` has been followed and the verification script result is recorded.

If any check fails, mark the task `reopened` and send it back to Engineer, Design Studio, or Planner as appropriate.

## No False Completion Rule

Do not report a factory run as `complete` when any promised primary flow is unimplemented, hard-coded, visually detached from the approved concept, or only superficially clickable.

Do not report a factory run as `complete` when `scripts/verify_factory_run.py` fails, unless the final report clearly says `partial` or `failed` and lists the failing checks.

Use:

- `partial` when a useful subset works but promised flows remain.
- `reopened` when the defect can be fixed in the current flow.
- `failed` when the claimed app entrypoint or core behavior does not exist.

## Decision Reporting Rule

Do not make user reports long by default.

If user input is needed:

- Ask for one decision at a time.
- State the recommendation.
- State the consequence of each option briefly.
- Record the decision in the monitor.
- Hand the selected decision to the next agent as an observable message.

If no user input is needed:

- Say what is proceeding automatically.
- Say where it appears in the monitor.
- Continue.

## Revision Rule

Done does not mean immutable. When the user asks for a change:

1. Identify affected artifacts and tasks.
2. Mark artifacts as `stale`.
3. Mark tasks as `reopened`.
4. Start a revision loop.
5. Run only the affected part of the flow.

Use this state transition:

```text
done -> stale -> reopened -> running -> reviewing -> done
```

If the same revision problem fails 3 times, stop and report the blocker.

## Blocking Report

Use this shape when blocked:

```text
BLOCKED <task-id>
CAUSE <short cause>
TRIED <attempt count>/3
NEED <specific user decision or external action>
```
