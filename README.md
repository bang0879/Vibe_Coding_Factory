# Vibe Coding Factory

Vibe Coding Factory is a Codex skill for turning rough app ideas into monitored, approval-gated build plans before implementation starts.

It is designed for builders who want the speed of vibe coding without letting an agent silently choose the product direction, scope, stack, or business assumptions on its own.

## What It Does

- Converts rough ideas into an Idea Snapshot instead of treating them as a build spec.
- Runs a Discovery Council across product, feasibility, moat, UX, risk, and planning perspectives.
- Produces a Decision Brief with concrete direction options.
- Requires a Direction Lock before implementation planning.
- Keeps a visual Factory Monitor in sync with state, decisions, handoffs, tasks, and gates.
- Uses deterministic scripts to catch fake completion, stale monitor state, missing approvals, and incomplete factory runs.
- Adds product-quality gates for real apps: input-driven behavior, UX review, consumer appeal, scope audit, browser evidence, and acceptance contracts.

## Why This Exists

Most AI coding failures do not begin in the code. They begin when a vague idea is converted into an unapproved product direction.

This skill makes the agent stop at the right moments:

1. Understand the idea.
2. Report options and risks.
3. Ask for the user's decision.
4. Lock the direction.
5. Plan from the lock.
6. Build only after gates pass.

## Install

Copy this directory into your Codex skills directory:

```powershell
Copy-Item -Recurse -Force . "$env:USERPROFILE\.codex\skills\vibe-coding-factory"
```

Then invoke it in Codex:

```text
$vibe-coding-factory
```

## Repository Layout

- `SKILL.md`: main skill instructions and operating rules.
- `references/`: workflow rules, monitor behavior, discovery council, quality gates, and benchmark rubric.
- `templates/`: state schema, monitor dashboard, reports, task cards, and product contract templates.
- `scripts/`: validation, state update, factory-run verification, and benchmark helpers.
- `agents/openai.yaml`: Codex UI metadata.

## Compatibility With Other Skills

This skill is meant to orchestrate product-direction and factory workflow. It can be used with other Codex skills, including Superpowers, as long as responsibilities are kept clear:

- Vibe Coding Factory owns discovery, Direction Lock, monitor state, approval gates, task flow, and factory completion checks.
- TDD, debugging, verification, frontend, GitHub, or platform-specific skills may be used as specialist helpers during the appropriate phase.
- If another skill suggests implementation before Direction Lock, the factory rules should win unless the user explicitly skips discovery.
- If another skill has its own completion criteria, both that skill's checks and the factory harness should pass before completion is reported.

## Validate

Run the schema and packaging validation:

```bash
python scripts/validate_factory_schema.py --skill-root .
```

Run the workflow-maturity benchmark:

```bash
python scripts/benchmark_factory_skill.py --skill-root .
```

The benchmark is a heuristic workflow-maturity rubric, not a runtime SWE-bench score or adoption claim.

## Factory Run Verification

Inside a project that used the skill:

```bash
python "<path-to-skill>/scripts/verify_factory_run.py" --project-root . --mode all
```

Use this before claiming that a user-facing app or factory run is complete.

## Current Focus

Vibe Coding Factory is strongest at:

- decision-first product planning,
- monitored agent workflows,
- preventing premature implementation,
- stateful approval gates,
- and completion verification.

The next frontier is broader external evaluation: scenario-suite benchmarks, CI integration, GitHub issue/PR automation, and browser-level monitor regression tests.

## License

MIT
