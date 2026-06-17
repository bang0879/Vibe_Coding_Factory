# Factory Monitor

Use Factory Monitor to show how the Codex-only factory is configured, how the project is flowing, what each task is doing, which agents are currently involved, and what outputs are being produced.

The monitor is observational. It does not run agents, call tools, or make decisions. Codex updates the monitor files only while the vibe-coding-factory skill is being used.

The monitor is never a substitute for the actual app. Do not use monitor cards, embedded state, dashboard metrics, or static V2 monitor HTML as evidence that a user-facing app works. The monitor may only report verification that was performed against the real app entrypoint.

The dashboard must remain project-flow and agent-flow first. Do not replace it with a one-page static app summary. Even when state loading fails, show the agent lanes, gates, task roadmap, artifacts, and a clear state-source error.

## Files

Use this structure in the active project:

```text
.factory/
  factory-state.json
  factory-log.md
  factory-dashboard.html
  monitor-url.txt
  monitor-meta.json
  events/
```

Refresh and surface the monitor with:

```bash
python "<skill-root>/scripts/ensure_factory_monitor.py" --project-root . --open
```

## Stale Monitor Guard

Before opening or reporting a monitor URL, verify that the served dashboard belongs to the active project and matches the current template.

Required steps:

1. Copy `templates/factory-dashboard.html` into the active project's `.factory/factory-dashboard.html` whenever the monitor is initialized or refreshed.
2. Write `.factory/monitor-meta.json` with:
   - `project_root`
   - `dashboard_path`
   - `template_path`
   - `dashboard_sha256`
   - `template_sha256`
   - `state_path`
   - `server_port`
   - `served_url`
   - `updated_at`
3. Write `.factory/monitor-url.txt` with the current served URL and project root.
4. If a local server is reused, confirm the server root is the active project root before opening the URL.
5. Fetch the URL once and compare a dashboard version marker or SHA-256-equivalent marker against the local dashboard file.
6. If the URL serves a dashboard from another project folder or an older copy, do not call it current. Restart the monitor from the active project root or copy the current dashboard into that project's `.factory` folder.

Query strings such as `?v=...` only bypass browser cache. They do not fix a wrong server root or a stale physical `.factory/factory-dashboard.html` file.

## Project-Centric State

`factory-state.json` is the state source for the dashboard. The state must be project-centric, not agent-card-centric.

Top-level priority:

1. `project`: what the project is and why it exists.
2. `discovery`: raw idea, assumptions, unknowns, and Deep Interview state.
3. `council_reports`: agent reports that shape direction before planning.
4. `option_matrix`: concrete product direction options and tradeoffs.
5. `direction_lock`: approved or skipped product direction contract.
6. `approval_queue`: user decisions waiting for approval.
7. `plan`: PRD, GTM, design, approvals, and plan summary.
8. `tasks`: roadmap with order, dependencies, difficulty, status, and owner flow.
9. `active_flow`: the currently active task and the agent lane it is moving through.
10. `messages`: observable agent-to-agent handoffs.
11. `artifacts`: produced outputs, summaries, approval state, and stale/revised state.
12. `decisions`: user decisions, options, selected choice, and downstream agent action.
13. `revision_loops`: user change requests and reopened work.
14. `events`: timeline of observable work.
15. `agents`: role cards as supporting information.
16. `quality_harness`: executable acceptance, QA evidence, and fresh-review state.
17. `report_sync`: whether the latest user report matches monitor state.
18. `operator_alerts`: unresolved risks, skipped gates, stale monitor, or blocked work.
19. `monitor_health`: dashboard freshness, source, and last refresh.

Each task that moves through agents should include `agent_steps`. The dashboard uses this to show what each persona actually did and where the output went next:

```json
{
  "agent": "engineer",
  "persona": "Implements approved task cards inside allowed files.",
  "did": "Built the condition-based venue ranking function and wired form input changes to rerender recommendations.",
  "output": "Working recommendation logic",
  "artifacts": ["app/app.js", "data/venues.js"],
  "handoff_to": "qa-tester",
  "handoff_summary": "Verify two contrasting inputs produce different top recommendations.",
  "evidence": "Browser check changed top result from A to B.",
  "status": "done"
}
```

Do not let the dashboard invent generic work text. If `agent_steps` is missing, show "작업 기록 없음" or derive only from concrete events/messages.

Each user-facing app task should also include completion evidence:

```json
{
  "scenario_harness": [
    {
      "id": "scenario-001",
      "given": "Initial filters and seeded data",
      "when": "User changes area and budget",
      "then": "Top recommendation and report contents change",
      "evidence": "Browser check recorded before/after visible output",
      "status": "passed"
    }
  ],
  "design_parity": [
    { "check": "first-screen structure matches approved brief", "status": "passed" }
  ],
  "completion_contract": {
    "real_entrypoint": "app/index.html",
    "scenario_status": "passed",
    "design_parity_status": "passed",
    "qa_evidence_status": "passed",
    "remaining_risks": []
  }
}
```

If scenario or design evidence is missing, show the task as `partial`, `reopened`, or `failed`, not simply `done`.

The state should also include `quality_harness`:

```json
{
  "status": "running",
  "acceptance_contract_path": "docs/ACCEPTANCE_CONTRACT.json",
  "qa_evidence_path": "docs/QA_EVIDENCE.md",
  "real_entrypoint": "app/index.html",
  "harness_command": "python vibe-coding-factory/scripts/verify_factory_run.py --project-root . --mode all",
  "last_result": "failed",
  "failing_checks": ["scenario-not-passed: SCN-002"],
  "fresh_review_status": "pending"
}
```

Direction discovery should include:

```json
{
  "discovery": {
    "status": "running",
    "idea_snapshot": {
      "raw_user_idea": "",
      "known_facts": [],
      "assumptions": [],
      "unknowns": [],
      "risk_areas": []
    },
    "deep_interview": {
      "status": "idle",
      "round": 0,
      "max_rounds": 5,
      "latest_question": "",
      "latest_answer": "",
      "weakest_open_decision": ""
    },
    "summary": ""
  },
  "direction_lock": {
    "status": "waiting_user",
    "path": "docs/DIRECTION_LOCK.md",
    "selected_option_id": "",
    "locked_items": {
      "target_user": "",
      "user_job": "",
      "product_promise": "",
      "mvp_scope": [],
      "non_goals": [],
      "technical_approach": "",
      "moat_hypothesis": "",
      "accepted_risks": []
    },
    "source_decision_ids": [],
    "source_report_ids": [],
    "handoff_message_ids": []
  }
}
```

## Update Triggers

Create state from `templates/factory-state.json` and update it after:

- Factory start.
- Idea Snapshot creation or update.
- Discovery Council report start or completion.
- Option Matrix creation or revision.
- Decision Brief creation.
- Deep Interview question, answer, clarity update, or completion.
- Direction Lock approval, rejection, skip, stale mark, or revision.
- Report Sync update before every user-facing report.
- Deep Intake question, answer, clarity update, or completion.
- Consensus Planner, Architect, or Critic verdict.
- Project brief creation or update.
- Planning agent start or completion.
- Human approval wait.
- Design option creation.
- Design concept creation.
- Design concept approval, rejection, or revision.
- Task decomposition.
- Task roadmap update.
- Active flow step start or completion.
- Agent message or handoff.
- Artifact creation, approval, revision, or stale mark.
- User decision request, selection, or decision handoff.
- Any user-wait report that asks the user to answer, approve, pick, or revise. The monitor must be opened or surfaced with the decision summary.
- Engineer start or completion.
- QA result.
- UX result.
- Consumer Appeal result.
- Scope audit result.
- Revision request.
- Blocker.
- Factory completion.

## Dashboard

Create `.factory/factory-dashboard.html` from `templates/factory-dashboard.html` when the user wants a visual view.

If a static snapshot is needed for `file://` viewing, embed the current factory state into `.factory/factory-dashboard.html` at creation time while still showing all monitor panels. Do not embed old sample projects.

The dashboard should show, in this order:

- Project purpose and success criteria.
- Immediate operator panels: latest user decision, Direction Lock status, monitor freshness, loop/error resolution, and unresolved escalations.
- Discovery summary, Council report verdicts, Option Matrix, and Deep Interview status.
- Direction Lock locked items and source decisions.
- Deep Intake and Consensus Planning status.
- Plan board.
- Design concept approval state.
- Task roadmap as an ordered task grid, not a status-column Kanban, unless the user specifically asks for Kanban. Each task card should show order, status, difficulty, agents, and task-produced artifacts.
- Completion evidence: show whether scenario harness, design parity, and QA evidence passed for user-facing app tasks.
- Active work lane.
- Message bus.
- Artifact panel.
- Decision panel.
- Decision panel with Markdown document links or preview for related PRD/GTM/PLAN/DESIGN docs.
- Flow timeline.
- Gate status.
- Factory Harness status, failing checks, real app entrypoint, and QA evidence path.
- Agent role flow as a bottom horizontal panel: show a compact org-chart or pipeline view with grouped agent cards and arrows/handoff labels, not a flat list.

The agent role flow should make it obvious how work moves:

- Orchestrator coordinates the factory.
- Product/Growth/Planner/Architect/Critic shape and review the plan.
- Design Studio and Task Decomposer convert direction into implementable work.
- Engineer builds.
- QA, UX, Consumer Appeal, and Scope Audit verify and close the task.

Each agent card should show role, latest concrete work, participation count, and main handoff targets when state data is available.

Because browser security may block local `fetch()` for `file://`, `scripts/ensure_factory_monitor.py` must embed the current `.factory/factory-state.json` snapshot into `.factory/factory-dashboard.html` and set `monitor_health.embedded_state_snapshot`. The fallback state must not be empty placeholder state when a real state file exists. If no state file exists, initialize from `templates/factory-state.json` so agent lanes, gates, and baseline monitor structure are still visible.

The dashboard must show:

- decision history, not only decisions currently waiting for the user;
- task roadmap with `agent_steps`, handoffs, evidence, and artifacts;
- agent flow lanes even before tasks exist;
- artifacts, gates, messages, and timeline from concrete state entries.

## Status Values

Use these values:

- `idle`
- `queued`
- `running`
- `reviewing`
- `waiting_user`
- `waiting_agent`
- `waiting_direction_lock`
- `needs_decision`
- `done`
- `stale`
- `reopened`
- `blocked`
- `failed`
- `approved`
- `rejected`
- `skipped_by_user`
- `locked`
- `watching`

## Message Shape

Each observable agent message should describe who talks to whom and why:

```json
{
  "id": "msg-001",
  "time": "2026-06-13 18:20 KST",
  "from": "task-decomposer",
  "to": "engineer",
  "task_id": "task-002",
  "status": "sent",
  "input_summary": "Approved design and parser task card.",
  "expected_output": "Implement natural language parser inside allowed files.",
  "output_summary": ""
}
```

## Decision Shape

Record decisions whenever the user must choose or approve something:

```json
{
  "id": "dec-001",
  "time": "2026-06-13 18:30 KST",
  "status": "selected",
  "question": "Which design concept should be implemented?",
  "recommended": "concept-002",
  "options": [
    { "id": "concept-001", "label": "Minimal dashboard", "consequence": "Fastest but less distinctive." },
    { "id": "concept-002", "label": "Project flow control room", "consequence": "Best for explaining the factory." }
  ],
  "selected": "concept-002",
  "reason": "User selected the project-flow direction.",
  "handoff_to": "engineer",
  "handoff_message_id": "msg-010"
}
```

After recording a selected decision, add a message showing the decision being handed to the next agent.

## Revision Loops

When the user asks for changes after completion:

1. Add a `revision_requested` event.
2. Mark the affected artifact as `stale`.
3. Mark the affected task as `reopened`.
4. Add an entry to `revision_loops`.
5. Set `active_flow` to the reopened task.
6. Show which agent is reworking it.
7. If the revision affects UI direction, set the `design-concept-approval` gate back to `pending` or `waiting_user`.

Do not leave stale work displayed as simply `done`.

## Event Log

Append important events to `.factory/factory-log.md`.

Use concise lines:

```text
2026-06-13 18:20 KST | DONE product-strategy | OUT docs/PRD.md
2026-06-13 18:24 KST | WAIT user-design-approval | NEED selected direction
2026-06-13 18:40 KST | REOPEN task-003 | CAUSE user revision request
```

## Update Discipline

Do not over-log every private reasoning step. Log observable work states:

- Started.
- Waiting.
- Done.
- Failed.
- Blocked.
- Files changed.
- Checks passed.
- Message sent.
- Artifact produced.
- Revision requested.
- Task reopened.

Use Korean for user-facing summaries and short English identifiers for machine-readable fields.

## User-Wait Display

When the factory waits for the user, the dashboard and the chat report should show the same decision:

- Latest question.
- Recommended option.
- Option consequences.
- Latest decision id and event id.
- Whether the monitor is `current`, `state_only`, `stale`, or `unavailable`.

If the monitor cannot be opened, report `.factory/factory-dashboard.html` or the served monitor URL as `Monitor view`.
