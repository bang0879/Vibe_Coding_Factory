# Factory Harness

Use this reference whenever the factory is expected to produce a working app or user-facing product.

The harness turns advisory rules into executable gates. If a required harness check fails, do not report the run as complete.

## Required Artifacts

Create these files before implementation for complete product requests:

- `docs/REQUIREMENTS.md` from `templates/requirements.md`
- `docs/ACCEPTANCE_CONTRACT.json` from `templates/acceptance-contract.json`
- `docs/IMPLEMENTATION_PLAN.md` from `templates/implementation-plan.md`
- `docs/QA_EVIDENCE.md` from `templates/qa-evidence.md`

The acceptance contract is the source of truth for user intent, primary scenarios, design invariants, data breadth, verification commands, and completion status.

## Executable Gate

Run this before marking a user-facing app task or factory run complete:

```powershell
python vibe-coding-factory/scripts/verify_factory_run.py --project-root . --mode all
```

Use the path that matches the active project. If the skill is installed globally, use the installed skill path for the script.

The gate checks:

- `factory-state.json` is valid JSON.
- completed tasks contain concrete agent handoff evidence.
- completed user-facing tasks have passing scenario, design parity, QA, and completion contract evidence.
- claimed app entrypoints exist outside `.factory`.
- monitor dashboard and template hashes match when the template is available.
- monitor metadata records the active project root and served URL.
- required docs and artifacts exist when the project is marked complete.

## Browser Evidence

For interactive apps, the script is necessary but not sufficient. QA must also use the app URL, browser automation, or manual browser evidence to record:

- two contrasting input/state changes with different visible outputs;
- one empty, error, or blocked state when relevant;
- before/after visible result summaries;
- the exact app URL or file path tested.

Store this in `docs/QA_EVIDENCE.md` and in `tasks[].agent_steps[].evidence`.

## Fresh Reviewer Gate

Before final completion, use an independent review pass when the run created or changed user-facing behavior:

- Reviewer receives only the diff, `docs/ACCEPTANCE_CONTRACT.json`, `docs/DESIGN_BRIEF.md`, and `docs/QA_EVIDENCE.md`.
- Reviewer reports requirement gaps, missing tests, broken user flows, design drift, security/privacy risks, and scope drift.
- Style preferences are optional and do not block completion.

If independent review finds a requirement-level gap, reopen the affected task.

## Failure Policy

Do not soften failed gates in the final report.

Use:

- `reopened` when the current flow can fix the issue;
- `partial` when useful behavior exists but promised scenarios remain;
- `failed` when the real app entrypoint or core behavior does not exist.
