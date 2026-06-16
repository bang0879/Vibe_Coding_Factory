# Reporting Sync

Use Reporting Sync whenever Codex reports progress to the user while the Factory Monitor is active or expected.

## Principle

The user-facing report and `.factory/factory-state.json` must describe the same reality. Update state first, then report.

## Required Before User Report

Before sending any progress, decision, blocker, or completion report:

1. Update the relevant state area.
2. Append an event with a stable id.
3. Update `report_sync`.
4. Mention the monitor status in the report.

`report_sync` shape:

```json
{
  "status": "synced",
  "last_state_update_at": "",
  "last_report_at": "",
  "last_report_summary": "",
  "latest_event_id": "",
  "latest_decision_id": "",
  "monitor_status": "current",
  "monitor_url": "",
  "state_path": ".factory/factory-state.json",
  "failed_update_reason": ""
}
```

## State Updater Shortcut

Prefer the bundled helper over hand-editing JSON when a simple state transition is enough:

```bash
python "<skill-root>/scripts/update_factory_state.py" --state .factory/factory-state.json phase --name discovery
python "<skill-root>/scripts/update_factory_state.py" --state .factory/factory-state.json report --agent "Technical Feasibility Architect" --summary "Feasibility report ready"
python "<skill-root>/scripts/update_factory_state.py" --state .factory/factory-state.json decision --question "Approve direction?" --option "A: Concierge workflow" --recommended A
python "<skill-root>/scripts/update_factory_state.py" --state .factory/factory-state.json lock --decision-id dec-001 --target-user "solo founder" --user-job "approve direction before build" --mvp-scope "discovery council" --non-goals "blind build" --technical-approach "state schema plus monitor sync" --moat-hypothesis "repeatable decision quality loop" --accepted-risks "extra planning time"
```

The helper appends `events[]`, updates `report_sync`, clears resolved approval queue items, and creates Direction Lock handoff messages when possible.

Status values:

- `synced`: state update succeeded before report.
- `pending`: report will need a state update.
- `failed`: state update failed and the user must be told.

Monitor status values:

- `current`: state and dashboard are current.
- `state_only`: state is current but dashboard copy/server is not confirmed.
- `stale`: dashboard or served URL may be stale.
- `unavailable`: monitor files are not available.

## Report Rules

When a decision is needed, report:

```text
Decision needed: <one-line decision>
Recommended: <option>
Reason: <one short reason>
Options: A / B / C
Monitor: <decision id, latest event id, monitor status>
Proceeding automatically: <what will continue without user input>
```

When no decision is needed, report:

```text
Proceeding automatically: <what is happening>
Monitor: <what was updated, latest event id, monitor status>
Next decision: <next expected approval or none>
```

If monitor update fails:

```text
Monitor: update failed - <short reason>
```

Do not say the monitor is current when `report_sync.status` is `failed`.

## Event Types

Use short machine-readable event types:

- `idea_captured`
- `council_report_done`
- `option_matrix_ready`
- `decision_requested`
- `deep_interview_question`
- `direction_lock_approved`
- `direction_lock_stale`
- `planning_started`
- `artifact_created`
- `task_created`
- `task_step_done`
- `qa_done`
- `blocker`
- `monitor_update_failed`

## Decision Sync

Every selected decision should:

- Exist in `decisions[]`.
- Include `related_docs` or `artifact_paths`.
- Set `handoff_to`.
- Create a `messages[]` handoff entry.
- Update `report_sync.latest_decision_id`.

The monitor should show the latest unresolved decision before task cards.
