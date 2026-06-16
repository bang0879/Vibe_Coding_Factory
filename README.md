# Vibe Coding Factory

Vibe Coding Factory is a runtime-neutral workflow for turning rough app ideas into monitored, approval-gated build plans before implementation starts. It is tuned for lightweight cold-start side projects: the casual one-line ideas where AI agents often pick the wrong direction or ship a mockup that does not actually work.

It is designed for builders who want the speed of vibe coding without letting an agent silently choose the product direction, scope, stack, or business assumptions on its own.

## What It Does

- Converts rough ideas into an Idea Snapshot instead of treating them as a build spec.
- Runs a Discovery Council across product, feasibility, moat, UX, risk, and planning perspectives.
- Produces a Decision Brief with concrete direction options.
- Requires a Direction Lock before implementation planning.
- Keeps a visual Factory Monitor in sync with state, decisions, handoffs, tasks, and gates.
- Uses deterministic scripts to catch fake completion, stale monitor state, missing approvals, and incomplete factory runs.
- Adds product-quality gates for real apps: input-driven behavior, UX review, consumer appeal, scope audit, browser evidence, and acceptance contracts.
- Blocks app implementation with `scripts/factory_preflight.py` until factory state and Direction Lock are ready.

## Why This Exists

Most AI coding failures do not begin in the code. They begin when a vague idea is converted into an unapproved product direction.

For small side projects, that failure is especially expensive: a lunch picker, trip briefing, or local dashboard can look finished while doing almost nothing. This workflow is built to catch that early.

This skill makes the agent stop at the right moments:

1. Understand the idea.
2. Report options and risks.
3. Ask for the user's decision.
4. Lock the direction.
5. Plan from the lock.
6. Build only after gates pass.

## Install For Codex

Copy this directory into your Codex skills directory:

```powershell
Copy-Item -Recurse -Force . "$env:USERPROFILE\.codex\skills\vibe-coding-factory"
```

Then invoke it in Codex:

```text
$vibe-coding-factory
```

## Runtime Portability

The core workflow does not depend on Codex-specific APIs. Codex is the primary packaged skill host, but the state schema, monitor, templates, and verification scripts are plain files.

- Codex: use `SKILL.md` and `agents/openai.yaml`.
- Claude Code: use `adapters/claude-code/CLAUDE.md`.
- Generic coding agents: use `AGENTS.md` and the scripts/templates directly.

The portable invariants are documented in `references/runtime-portability.md`.

## Best Fit

Use this for lightweight cold-start side projects, especially Korean-first solo workflows. It is not trying to replace heavyweight SDLC frameworks. For regulated, enterprise, or deeply domain-specific products, use it as a control layer and add domain-specific review.

## Repository Layout

- `SKILL.md`: main skill instructions and operating rules.
- `references/`: workflow rules, monitor behavior, discovery council, quality gates, and benchmark rubric.
- `templates/`: state schema, monitor dashboard, reports, task cards, and product contract templates.
- `scripts/`: validation, state update, factory-run verification, and benchmark helpers.
- `agents/openai.yaml`: Codex UI metadata.
- `AGENTS.md`: host-neutral agent entrypoint.
- `adapters/`: host-specific adapter instructions.

## Compatibility With Other Skills

This workflow is meant to orchestrate product-direction and factory control. It can be used with other skills or host-native workflows, including Superpowers, as long as responsibilities are kept clear:

- Vibe Coding Factory owns discovery, Direction Lock, monitor state, approval gates, task flow, and factory completion checks.
- TDD, debugging, verification, frontend, GitHub, or platform-specific skills may be used as specialist helpers during the appropriate phase.
- If another skill suggests implementation before Direction Lock, the factory rules should win unless the user explicitly skips discovery.
- If another skill has its own completion criteria, both that skill's checks and the factory harness should pass before completion is reported.

## Validate

Run the schema and packaging validation:

```bash
python scripts/validate_factory_schema.py --skill-root .
```

Run the local self-audit:

```bash
python scripts/benchmark_factory_skill.py --skill-root .
```

The self-audit checks this repository's own workflow artifacts. It is not a peer benchmark, runtime SWE-bench score, adoption claim, or proof that this project outperforms named tools.

Run the implementation preflight before app/product code starts:

```bash
python scripts/factory_preflight.py --project-root .
```

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
