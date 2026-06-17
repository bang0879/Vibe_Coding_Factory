# Reporting Sync

Use Reporting Sync whenever Codex reports progress to the user while the Factory Monitor is active or expected.

## Principle

The user-facing report and `.factory/factory-state.json` must describe the same reality. Update state first, then report.

## User-Facing Language

Use Korean by default for user-facing decision prompts, progress reports, planning artifacts, monitor summaries, blocker reports, and completion reports. Internal agent-to-agent messages, Caveman handoffs, machine ids, JSON keys, event types, commands, file paths, and code identifiers may stay English.

## Required Before User Report

Before sending any progress, decision, blocker, or completion report:

1. Update the relevant state area.
2. Append an event with a stable id.
3. Update `report_sync`.
4. Mention the monitor status in the report.

## User-Wait Monitor Rule

Whenever the report asks the user to answer, approve, pick an option, revise a direction, or continue/stop work, open or surface the monitor before asking. If the runtime cannot open a browser, show the monitor path or URL.

Preferred helper:

```bash
python "<skill-root>/scripts/ensure_factory_monitor.py" --project-root . --open
```

`report_sync` shape:

```json
{
  "status": "synced",
  "last_state_update_at": "",
  "last_report_at": "",
  "last_report_summary": "",
  "last_prompt_requires_user": false,
  "latest_event_id": "",
  "latest_decision_id": "",
  "latest_decision_summary": "",
  "user_waiting_summary": "",
  "monitor_status": "current",
  "monitor_url": "",
  "monitor_view": ".factory/factory-dashboard.html",
  "monitor_opened_at": "",
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

When a decision is needed, report in Korean by default:

```text
결정 필요: <한 줄 결정 질문>
추천: <추천 옵션>
이유: <짧은 이유>
선택지: A / B / C
결정 요약: <질문, 추천 옵션, 선택 결과>
모니터: <decision id, latest event id, monitor status>
모니터 보기: <served monitor URL or .factory/factory-dashboard.html>
자동 진행: <사용자 답변 없이 계속 가능한 작업>
```

English fallback if the runtime cannot render Korean labels:

```text
Decision needed: <one-line decision>
Recommended: <option>
Reason: <one short reason>
Options: A / B / C
Decision summary: <question, recommended option, options, and consequence>
Monitor: <decision id, latest event id, monitor status>
Monitor view: <served monitor URL or .factory/factory-dashboard.html>
Proceeding automatically: <what will continue without user input>
```

Before this report, `report_sync.last_prompt_requires_user` must be `true`, `latest_decision_summary` must summarize the choice, `user_waiting_summary` must match the user-facing request, and `monitor_view` must point to the dashboard.

When no decision is needed, report in Korean by default:

```text
자동 진행: <진행 중인 작업>
모니터: <업데이트된 내용, latest event id, monitor status>
다음 결정 지점: <다음 승인 지점 또는 없음>
```

English fallback:

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
