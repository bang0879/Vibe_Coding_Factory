# Self-Audit Rubric

Use this rubric to check whether this repository contains the workflow controls it claims to provide. It is not an external benchmark, not a SWE-bench score, and not a claim that Vibe Coding Factory outperforms named tools.

The intended comparison frame is lightweight cold-start side projects, not enterprise SDLC platforms. A strong score means the local repository has the guardrails needed for rough personal app ideas: direction control, preflight blocking, monitor state, and fake-completion checks.

## No Peer Ranking

Do not hand-write scores for other projects. Do not print a rank against public tools unless those repositories were evaluated by the same published harness, on the same revision, with reproducible inputs.

Acceptable claims:

- The local repository passed its self-audit.
- The local repository has or lacks specific workflow artifacts.
- A separate external evaluation, if added later, produced a reproducible result.

Unacceptable claims:

- This project ranks above named peer tools based on constants.
- This self-audit proves runtime coding quality.
- This self-audit proves adoption, maturity, or ecosystem strength.

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
| External evaluation readiness | 6 | Git/worktree patterns, public limitations, and a path to reproducible scenario evaluation exist. |

## Interpretation

- 90-100: the repository's own workflow artifacts are broadly present.
- 80-89: strong local workflow coverage, with missing guardrails or packaging gaps.
- 70-79: useful method but likely depends on operator discipline.
- Below 70: too many requirements live only in prose.

## External Evaluation Plan

To turn this into a real benchmark, add all of the following:

1. A scenario suite with rough ideas, skip-discovery requests, revision requests, and fake-completion traps.
2. Lightweight cold-start fixtures such as recommendation apps, trip briefings, local dashboards, and mockup-only traps.
3. A reproducible runner that evaluates multiple agent runtimes with the same prompts and project fixtures.
4. Objective scoring for Direction Lock compliance, artifact quality, monitor freshness, harness failures caught, and rework avoided.
5. CI that runs the fixtures on every change.
6. Case studies comparing the same project with and without the factory workflow.

Run the local self-audit after major workflow, monitor, state schema, or verification changes:

```bash
python scripts/benchmark_factory_skill.py --skill-root .
```
