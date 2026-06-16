# Benchmark Rubric

Use this rubric when comparing vibe-coding-factory against public AI coding workflows. It is a workflow-maturity benchmark, not a runtime SWE-bench score.

## Peer Set

The baseline peers are:

- GitHub Spec Kit: spec-driven development with specify, plan, tasks, analyze, checklist, and implement commands.
- OpenHands: general software-development agent platform with CLI, local GUI, cloud, SDK, sandboxing, and benchmark/evaluation infrastructure.
- BMAD Method: agile AI development method with structured workflows, domain agents, adaptive planning depth, and lifecycle coverage.
- Aider: terminal pair-programming tool with codebase map, git integration, language breadth, and benchmark culture.
- Task Master: PRD-to-task management workflow for AI coding tools.
- SWE-agent: issue-fixing agent with SWE-bench orientation and configurable research-grade agent-computer interface.

## Scoring Dimensions

Total score: 100.

| Dimension | Weight | What Good Looks Like |
| --- | ---: | --- |
| Product discovery and direction control | 15 | Rough ideas become options and an approved Direction Lock before build. |
| Spec and artifact discipline | 12 | PRD, GTM, design, requirements, acceptance, plan, and task artifacts stay linked. |
| Task decomposition quality | 10 | Tasks include owner, allowed files, dependencies, difficulty, acceptance, and verification. |
| Monitor observability | 12 | State, dashboard, events, decisions, handoffs, artifacts, and health are visible. |
| Deterministic verification harness | 12 | Scripts catch missing gates, stale state, incomplete tasks, and fake completion. |
| Agent-role coverage and handoffs | 10 | Specialist roles report independently and hand off through machine-readable state. |
| Product-quality gates | 10 | QA, UX, consumer appeal, scope audit, browser evidence, and input-driven behavior are required. |
| Revision and failure-loop control | 7 | Stale artifacts, reopen loops, retry limits, and blockers are explicit. |
| Skill packaging and discoverability | 6 | Frontmatter, UI metadata, references, templates, and helper scripts are discoverable. |
| External integration and benchmark evidence | 6 | Git/GitHub/worktree patterns, benchmark script, and comparable peer scoring exist. |

## Interpretation

- 90-100: top-tier workflow method; remaining work is ecosystem/integration depth.
- 80-89: strong public-tool level; gaps are usually observability, reproducible gates, or product discovery.
- 70-79: useful method but likely depends on operator discipline.
- Below 70: too many requirements live only in prose.

Recalculate after major workflow, monitor, state schema, or verification changes:

```bash
python scripts/benchmark_factory_skill.py --skill-root .
```
