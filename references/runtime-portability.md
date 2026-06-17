# Runtime Portability

Vibe Coding Factory is a workflow contract, not a dependency on one agent host.

The default product niche is lightweight cold-start side projects: rough one-line ideas, casual solo workflows, and small apps where the main risks are premature direction choice and non-working mockups.

## Portable Invariants

Keep these rules the same across runtimes:

- Store source of truth in project files, especially `.factory/factory-state.json`.
- Treat the first user idea as discovery input, not a build spec.
- Freeze implementation until Direction Lock is approved or explicitly skipped by the user.
- Run Discovery Council before Direction Lock when discovery is not skipped.
- Record user decisions, report sync, handoffs, artifacts, and task gates in machine-readable state.
- Run `scripts/verify_factory_run.py` before claiming a user-facing app or factory run is complete.
- Run `scripts/factory_preflight.py` before creating or editing app/product files.
- Surface the monitor path or URL whenever the host asks the user to approve, choose, answer, or revise.
- Prefer `scripts/ensure_factory_monitor.py --project-root . --open` before every user-wait prompt.

## Runtime Adapters

Use the adapter that matches the host:

- Codex: use `SKILL.md` and `agents/openai.yaml`.
- Claude Code: use `adapters/claude-code/CLAUDE.md`.
- Generic agents: use `AGENTS.md` plus the scripts and templates in this repository.

## Host-Specific Differences

The host may differ in how it launches sub-agents, displays monitors, opens browsers, or manages approvals. Do not let those differences change the core gates.

If a host cannot spawn sub-agents, run the roles serially and still write separate `council_reports[]` entries.

If a host cannot display the HTML monitor, keep `.factory/factory-state.json` and `.factory/factory-log.md` current and report the monitor limitation plainly.

If a host has its own testing or completion skill, require both that host's checks and the Factory Harness to pass.

## Portability Checklist

- [ ] The instructions do not require Codex-specific commands except in Codex adapter files.
- [ ] State and artifacts are plain files.
- [ ] Scripts use the Python standard library unless a file documents otherwise.
- [ ] Completion claims depend on deterministic checks, not host UI state.
- [ ] Adapter docs name host-specific behavior as an adapter concern, not a core workflow rule.
