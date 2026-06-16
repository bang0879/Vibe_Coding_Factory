---
name: vibe-coding-factory
description: Use when the user gives a rough or one-line side-project app idea, asks for a lightweight cold-start build, wants an AI coding agent not to choose product direction silently, or needs approval-gated planning and verification before app implementation.
---

# Vibe Coding Factory

Use this skill to operate a runtime-neutral agent factory. The current agent runtime acts as the orchestrator. In a Codex host, Codex may spawn sub-agents only when the user explicitly asks for agent/team/delegated/parallel work or when this skill is invoked for factory execution.

Do not use an external app as the source of truth. Keep the workflow state in the current project files so the same method can be adapted to Codex, Claude Code, or another coding-agent host. The dashboard is a monitor only.

## Purpose Fit

Optimize for lightweight cold-start side projects: casual one-line ideas, low-domain-risk apps, Korean-first solo workflows, and small products where the main danger is an agent silently choosing the wrong direction or shipping a pretty mockup that does not work.

Keep the council concise for lightweight cold-start work. Each role can report in 1-3 high-signal bullets, but the gate cannot be skipped unless the user explicitly says to skip discovery.

For heavyweight regulated domains, existing large codebases, enterprise SDLC, or deep domain research, treat this skill as a control layer only and add domain-specific skills, tests, and expert review.

## Preflight Stop Rule

First action for any app build request: stop before writing app/product code. Create or update `.factory/factory-state.json` and `.factory/factory-log.md`, record the Idea Snapshot, and run Discovery Council unless the user explicitly skips discovery.

Before creating or editing app/product files, run:

```bash
python "<skill-root>/scripts/factory_preflight.py" --project-root .
```

If `factory_preflight.py` fails, do not implement. Report the blocker, update `operator_alerts[]`, and continue only with discovery, Direction Lock, or explicit user skip handling. App/product code written before Direction Lock is a workflow violation and must be treated as stale or reverted only with user approval.

## Core Flow

1. Capture the user's project idea, purpose, target user, and success criteria.
2. Initialize the Factory Monitor when visual monitoring is requested.
3. Create an Idea Snapshot:
   - Record the raw user idea without expanding it into implementation.
   - Identify known facts, assumptions, missing decisions, and likely risk areas.
   - Update `discovery.idea_snapshot` and `project.current_phase`.
4. Run Discovery Council before planning or implementation:
   - Product Strategist reports user, problem, value, scope, and MVP candidates.
   - Technical Feasibility Architect reports feasibility, constraints, impossible parts, workarounds, and stack risks.
   - Growth and Moat Strategist reports positioning, distribution, revenue, defensibility, and business moat ideas.
   - UX Strategist reports first-use flow, product feel, information architecture, and experience risks.
   - Risk Critic reports legal, privacy, security, operational, and execution risks.
   - Planner reports viable paths, sequencing, dependencies, and implementation risk.
   - Store reports in `council_reports[]` and summarize options in `option_matrix[]`.
5. Produce `docs/DECISION_BRIEF.md` and ask for user direction when product direction is not locked:
   - Present 2-3 concrete direction options.
   - Include recommendation, tradeoffs, technical workarounds, moat ideas, scope cuts, and explicit decisions needed.
   - If more clarity is required, run Deep Interview one question at a time from the weakest open decision.
6. Create Direction Lock after the user approves a direction:
   - Write `docs/DIRECTION_LOCK.md`.
   - Set `direction_lock.status` to `approved`.
   - Record the decision under `decisions[]` and hand it to planning through `messages[]`.
7. Enforce implementation freeze until Direction Lock is approved:
   - Do not let Task Decomposer create implementation tasks.
   - Do not let Engineer write app/product code.
   - Do not create PRD/GTM/Design as final build inputs, only draft notes, unless the user explicitly says to skip discovery.
8. Run planning from the approved Direction Lock:
   - Product Strategist creates or updates `docs/PRD.md`.
   - Growth Marketer creates or updates `docs/GTM.md`.
9. Run Consensus Planning:
   - Planner creates the implementation approach and task sequencing.
   - Architect reviews architecture, boundaries, risks, and tradeoffs.
   - Critic checks actionability, acceptance criteria, and verification.
   - Revise until consensus passes or a blocker is reported.
10. Ask the user for planning approval before task decomposition.
11. Run Design Studio when UI, brand, page layout, product experience, visual references, or user design feedback matter.
12. Run the Design Concept Approval gate:
   - Capture references and feedback.
   - Produce 2-3 concrete design concepts or one revised concept when the user has already chosen a direction.
   - Ask the user to approve, reject, or revise the concept before implementation.
   - Convert the approved concept into `docs/DESIGN_BRIEF.md`.
13. Create the executable product contract for complete product requests:
   - `docs/REQUIREMENTS.md`
   - `docs/ACCEPTANCE_CONTRACT.json`
   - `docs/IMPLEMENTATION_PLAN.md`
   - `docs/QA_EVIDENCE.md`
14. Decompose work into task cards and show the task roadmap.
15. Execute each task through the flow:
   - Engineer implements.
   - QA Tester verifies behavior.
   - UX First-user Checker reviews first-use clarity.
   - Consumer Appeal Reviewer checks whether the result feels attractive to a real user.
   - Scope Auditor checks allowed files and unintended changes.
16. Run the executable Factory Harness before marking any user-facing task or full run complete.
17. Update the Factory Monitor before every user-facing report with the same state that the report summarizes.
18. Report to the user in a concise decision-first format.
19. Continue to the next task only when all required gates pass.

## Load References

Load only what is needed:

- For agent responsibilities, read `references/agent-roles.md`.
- For loop engineering, difficulty gates, and failure handling, read `references/loop-rules.md`.
- For Deep Intake and Consensus Planning, read `references/planning-intake.md`.
- For Discovery Council, Direction Lock, option matrices, and idea-to-decision flow, read `references/discovery-council.md`.
- For synchronized user reports and monitor updates, read `references/reporting-sync.md`.
- For concise agent-to-agent status messages, read `references/caveman-reporting.md`.
- For reference-driven design and mockup approval, read `references/design-studio.md`.
- For branch, worktree, issue, and PR discipline, read `references/project-management.md`.
- For outside patterns distilled from Claude Code, Playwright, Git/GitHub, and open-source agent builders, read `references/external-patterns.md`.
- For visual project-flow monitoring with JSON and HTML, read `references/factory-monitor.md`.
- For real app depth, option breadth, design durability, and app QA gates, read `references/product-quality.md` before decomposing or implementing any user-facing app.
- For complete product delivery, read `references/completion-harness.md` before task decomposition and again before marking any user-facing app task `done`.
- For executable product contracts, deterministic completion checks, and fresh-review gates, read `references/factory-harness.md` before implementation and before final completion.
- For runtime portability across Codex, Claude Code, and generic coding agents, read `references/runtime-portability.md`.
- For local self-audit scoring, read `references/benchmark-rubric.md` and run `scripts/benchmark_factory_skill.py`.
- For lightweight cold-start side-project fit, read `references/cold-start-side-projects.md`.

## Operating Rules

- The user-facing language is Korean unless the user requests otherwise.
- Agent-to-agent reports use Caveman format.
- This skill's default niche is lightweight cold-start side projects, not heavyweight enterprise SDLC replacement.
- `factory_preflight.py` must pass before app/product implementation starts.
- The first user idea is not a build spec. Treat it as discovery input until Direction Lock is approved.
- Enforce implementation freeze before Direction Lock: no implementation tasks, no Engineer code, and no final PRD/GTM/design handoff may proceed unless the user explicitly skips discovery.
- If discovery is skipped by the user, set `direction_lock.status` to `skipped_by_user`, record the risk in `operator_alerts[]`, and continue with the user's selected scope.
- Do only the assigned task.
- Do not touch files outside `allowed_files`.
- Use machine difficulty labels: `low`, `medium`, `high`.
- If task difficulty is `high`, ask the user before execution.
- If task difficulty is `medium` or `low`, execute without asking unless blocked.
- Retry the same failure at most 3 times.
- If the same failure happens 3 times, stop and report the blocker.
- Do not proceed to the next task unless Engineer, QA, UX, Consumer Appeal when user-facing, and Scope Auditor gates pass.
- Do not count `.factory` monitor HTML, static dashboard HTML, screenshots, or embedded sample state as a working app. If a task claims an interactive app, verify the real app entrypoint and at least one input-driven output change before marking it done.
- For user-facing apps, enforce Product Quality Gates: meaningful data breadth, input-driven behavior, design durability, responsive states, and QA evidence. If these are missing, mark the task `reopened` or `failed`, not `done`.
- For complete product requests, create an Intent Lock and Scenario Harness before implementation. Do not mark the run `complete` unless every primary scenario, design parity check, and QA evidence item in `references/completion-harness.md` passes.
- Treat "buttons click" as insufficient. Completion requires meaningful state transitions and visible outputs derived from current user input.
- For complete product requests, create `docs/REQUIREMENTS.md`, `docs/ACCEPTANCE_CONTRACT.json`, `docs/IMPLEMENTATION_PLAN.md`, and `docs/QA_EVIDENCE.md` from the templates before implementation. Keep requirement ids and scenario ids linked to task cards.
- Run `python "<skill-root>/scripts/verify_factory_run.py" --project-root . --mode all` before reporting any user-facing app task or factory run as complete. Use the installed path of this skill as `<skill-root>`. If the script fails, reopen the responsible task and record the failing check in `.factory/factory-state.json`.
- When editing this skill's discovery workflow or state schema, run `python scripts/validate_factory_schema.py --skill-root .` from the skill root before calling the update complete.
- When editing this skill's workflow, monitor, state schema, helper scripts, or validation gates, run `python scripts/benchmark_factory_skill.py --skill-root .` from the skill root and review self-audit regressions before calling the update complete. Do not present this self-audit as a peer benchmark.
- For interactive apps, the executable harness is necessary but not sufficient: QA must record browser evidence for two contrasting input/state changes and one edge state when relevant.
- Before final completion of a user-facing product, use a fresh-context review pass against the diff, acceptance contract, design brief, and QA evidence. Requirement-level gaps reopen the task.
- If the approved design concept cannot be recognized in the rendered app, mark UX failed and reopen the task. Do not ask the user to catch basic design drift.
- When factory execution starts, create or update `.factory/factory-state.json` and `.factory/factory-log.md`.
- When the user wants a visual monitor, copy or create `.factory/factory-dashboard.html` from `templates/factory-dashboard.html`.
- Before opening or reporting a monitor URL, apply the Stale Monitor Guard in `references/factory-monitor.md`: verify the active project root, refresh the dashboard from the current template, record monitor metadata, and do not treat a `?v=` cache-bust URL as proof that the served file is current.
- The monitor must be project-flow first: show project purpose, plan status, task roadmap, active execution lane, messages, artifacts, and revision state before agent cards.
- When the user requests changes after a task or artifact is done, mark affected artifacts as `stale`, affected tasks as `reopened`, and start a new revision loop.
- Do not let Engineer implement user-facing UI until `design-concept-approval` is `approved`, unless the user explicitly says to skip design.
- Do not let Engineer implement a new app from only a monitor, PRD, or rough shell. Task Decomposer must include data model, interaction logic, result generation, edge states, responsive polish, and real-app QA tasks.
- For real implementation work, use feature-slice discipline from `references/project-management.md`: one feature branch, one worktree for parallel sessions, one focused AI session, one small PR, and issue/PR linkage when GitHub tracking is available.
- Do not use GJC as an external runner by default. Only borrow the Deep Intake and Consensus Planning patterns unless the user later asks to run GJC beside Codex.
- Deep Intake asks one question at a time, not a batch of five questions.
- Discovery Council must include Product Strategist, Technical Feasibility Architect, Growth and Moat Strategist, UX Strategist when user-facing, Risk Critic, and Planner reports before Direction Lock approval.
- Direction Lock must include target user, user job, MVP scope, non-goals, technical approach, moat hypothesis, accepted risks, and source decision ids.
- Consensus Planning must include Planner, Architect, and Critic verdicts before planning approval.
- Separate user-facing reports into `Decision needed` and `Proceeding automatically`.
- Keep decision requests short: one decision, the options, the recommended option, and the consequence.
- Record every user decision in `.factory/factory-state.json` under `decisions`.
- Show decision records in the monitor and create a message from Orchestrator to the next agent that uses the decision.
- Before every user-facing report, update `report_sync` with `last_state_update_at`, `last_report_summary`, `monitor_status`, and `latest_event_id`. If the monitor update fails, report that failure plainly instead of implying the monitor is current.
- For every task handoff, update `tasks[].agent_steps[]` with `agent`, `persona`, `did`, `output`, `artifacts`, `handoff_to`, `handoff_summary`, `evidence`, and `status`. Do not rely on persona descriptions as work evidence.
- For decisions, include `related_docs` or `artifact_paths` when relevant so the dashboard can open the supporting Markdown.

## Monitor Update Minimum

For every observable work step, update at least one of:

- `project.current_phase`
- `discovery`
- `council_reports`
- `option_matrix`
- `direction_lock`
- `approval_queue`
- `plan`
- `tasks`
- `active_flow`
- `messages`
- `artifacts`
- `events`
- `revision_loops`
- `decisions`
- `agents`
- `quality_harness`
- `report_sync`
- `operator_alerts`
- `monitor_health`

Do not leave the dashboard at `done` if the user has requested a revision.

## Task Card Shape

Use `templates/task-card.md` for each task. Every task must include:

- `id`
- `title`
- `difficulty`
- `goal`
- `allowed_files`
- `branch_name`
- `worktree_path`
- `issue_id`
- `agent_flow`
- `checklist`
- `done_conditions`
- `verification`
- `status`
- `requirement_ids`
- `app_entrypoint`
- `qa_evidence_path`
- `harness_command`

## Sub-Agent Use

When spawning agents, give each one:

- Its role.
- The exact task.
- Its owned files or responsibility boundary.
- The expected output.
- The Caveman report format.
- A reminder that other agents may be working and it must not revert unrelated changes.

Prefer parallel agents only for independent work with disjoint write scopes. Keep tightly coupled or blocking work local.

## Human Approval Gates

Ask the user before:

- Approving or changing Direction Lock.
- Starting implementation after PRD/GTM.
- Implementing any user-facing UI before the design concept is approved.
- Running any `high` difficulty task.
- Installing tools or writing outside the current workspace.
- Taking destructive actions.

## User Report Format

Use this shape when the user must decide:

```text
결정 필요: <one-line decision>
추천: <option>
이유: <one short reason>
선택지: A / B / C
모니터: <decision id, latest event id, and monitor status>
자동 진행: <what will continue without user input>
```

Use this shape when no decision is needed:

```text
자동 진행: <what is happening>
모니터: <what to check>
다음 결정 지점: <next expected approval or none>
```

Avoid long background explanations unless the user asks.

Canonical report format:

```text
Decision needed: <one-line decision>
Recommended: <option>
Reason: <one short reason>
Options: A / B / C
Monitor: <decision id, latest event id, and monitor status>
Proceeding automatically: <what will continue without user input>
```

```text
Proceeding automatically: <what is happening>
Monitor: <what was updated, latest event id, and monitor status>
Next decision: <next expected approval or none>
```

Use the canonical format above if older labels render incorrectly.

## Completion Report

When the factory run ends, report:

- Project purpose and current phase.
- What was planned.
- What was implemented.
- Which task flow ran.
- Which checks passed.
- Which artifacts were produced.
- Which files changed.
- Remaining risks or blocked items.
- Recommended next task.
- Monitor files created or updated.
- Factory Harness command and pass/fail result.
