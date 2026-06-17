# Claude Code Adapter: Vibe Coding Factory

Use this file when running Vibe Coding Factory from Claude Code or another Claude-oriented coding workflow. The default niche is lightweight cold-start side projects from rough app ideas.

## Role

Act as the factory orchestrator. Keep the source of truth in project files, not chat memory.

## Required Flow

1. Create or update `.factory/factory-state.json` from `templates/factory-state.json`.
2. Record the user's rough idea as an Idea Snapshot.
3. Run the Discovery Council roles separately:
   - Product Strategist
   - Technical Feasibility Architect
   - Growth and Moat Strategist
   - UX Strategist
   - Risk Critic
   - Planner
4. Write `docs/DECISION_BRIEF.md`.
5. Ask for Direction Lock.
6. Do not implement app/product code until Direction Lock is approved or the user explicitly skips discovery.
7. Before writing app/product files, run:

```bash
python scripts/factory_preflight.py --project-root .
```

8. Keep monitor/report sync current before user-facing updates.
9. When waiting for the user, surface `.factory/factory-dashboard.html` or the served monitor URL with the decision summary.
   Prefer:

```bash
python scripts/ensure_factory_monitor.py --project-root . --open
```

10. Before completion, run:

```bash
python scripts/verify_factory_run.py --project-root . --mode all
```

11. Write user-facing decision prompts, planning artifacts, monitor summaries, blocker reports, and completion reports in Korean by default. Internal handoffs, ids, commands, paths, and JSON keys may stay English.
12. Do not silently downgrade live/API/open-ended product intent into a fixed seed-data demo, canned result, or tiny closed dropdown. Ask the user and record the fallback in `docs/ACCEPTANCE_CONTRACT.json`.
13. During discovery, propose domain-native capabilities before Direction Lock; for location products, include map/place search and provider constraints.
14. Preserve the approved design concept with a design fidelity contract and browser/screenshot evidence before completion.

## Claude Code Notes

- Use Claude Code task or sub-agent features only when the work can be separated cleanly.
- If multiple agents are unavailable, run the roles serially.
- Apply any Claude Code testing or review workflow in addition to the Factory Harness.
- Do not report `scripts/benchmark_factory_skill.py` as a competitive benchmark; it is a local self-audit.
