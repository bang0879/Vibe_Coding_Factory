# Vibe Coding Factory Agent Guide

Use this repository as a runtime-neutral workflow for approval-gated app building, especially lightweight cold-start side projects from rough one-line ideas.

## Core Contract

1. Capture the rough idea as discovery input.
2. Run Discovery Council before implementation unless the user explicitly skips discovery.
3. Produce a Decision Brief with 2-3 options.
4. Wait for Direction Lock before planning implementation.
5. Keep `.factory/factory-state.json` and `.factory/factory-log.md` current.
6. Update the monitor state before every user-facing report.
7. Run the Factory Harness before claiming completion:

```bash
python scripts/verify_factory_run.py --project-root . --mode all
```

Before writing app/product files, run:

```bash
python scripts/factory_preflight.py --project-root .
```

## Boundaries

- Do not turn a vague idea into app code without Direction Lock.
- Do not skip preflight before implementation.
- Do not treat dashboard HTML as a working app.
- Do not claim benchmark superiority from `scripts/benchmark_factory_skill.py`; it is a local self-audit only.
- If your runtime has no sub-agents, run each role serially and write separate council reports.

## Main Files

- `SKILL.md`: Codex skill entrypoint.
- `references/runtime-portability.md`: host-neutral portability rules.
- `references/benchmark-rubric.md`: local self-audit rubric.
- `templates/factory-state.json`: monitor/state schema.
- `scripts/verify_factory_run.py`: completion verifier.
