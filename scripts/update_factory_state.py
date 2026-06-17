#!/usr/bin/env python3
"""Small state updater for vibe-coding-factory monitor files."""

from __future__ import annotations

import argparse
import datetime as _dt
import json
from pathlib import Path
from typing import Any


DEFAULT_STATE = ".factory/factory-state.json"


def now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"state file does not exist: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise SystemExit("state file must contain a JSON object")
    return data


def save_state(path: Path, state: dict[str, Any]) -> None:
    state.setdefault("factory", {})["updated_at"] = now()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def next_id(items: list[Any], prefix: str) -> str:
    return f"{prefix}-{len(items) + 1:03d}"


def ensure_list(state: dict[str, Any], key: str) -> list[Any]:
    value = state.setdefault(key, [])
    if not isinstance(value, list):
        raise SystemExit(f"state.{key} must be a list")
    return value


def append_event(state: dict[str, Any], event_type: str, agent: str, message: str, status: str, artifact_id: str = "", task_id: str = "") -> str:
    events = ensure_list(state, "events")
    event_id = next_id(events, "evt")
    events.append(
        {
            "id": event_id,
            "time": now(),
            "type": event_type,
            "agent": agent,
            "task_id": task_id,
            "message": message,
            "artifact_id": artifact_id,
            "status": status,
        }
    )
    return event_id


def monitor_view(state: dict[str, Any]) -> str:
    report_sync = state.get("report_sync", {}) if isinstance(state.get("report_sync"), dict) else {}
    monitor_health = state.get("monitor_health", {}) if isinstance(state.get("monitor_health"), dict) else {}
    return str(
        report_sync.get("monitor_url")
        or monitor_health.get("served_url")
        or monitor_health.get("dashboard_path")
        or ".factory/factory-dashboard.html"
    )


def sync_report(
    state: dict[str, Any],
    event_id: str,
    summary: str,
    monitor_status: str = "state_only",
    decision_id: str = "",
    requires_user: bool = False,
    decision_summary: str = "",
) -> None:
    report_sync = state.setdefault("report_sync", {})
    view = monitor_view(state)
    report_sync.update(
        {
            "status": "synced",
            "last_state_update_at": now(),
            "last_report_summary": summary,
            "last_prompt_requires_user": requires_user,
            "latest_event_id": event_id,
            "monitor_status": monitor_status,
            "monitor_view": view,
            "failed_update_reason": "",
        }
    )
    if requires_user:
        report_sync["monitor_opened_at"] = now()
        report_sync["latest_decision_summary"] = decision_summary or summary
        report_sync["user_waiting_summary"] = (
            f"Decision needed: {decision_summary or summary} | "
            f"Monitor view: {view} | Event: {event_id}"
        )
    else:
        report_sync.setdefault("monitor_opened_at", "")
        report_sync.setdefault("latest_decision_summary", "")
        report_sync.setdefault("user_waiting_summary", "")
    if decision_id:
        report_sync["latest_decision_id"] = decision_id


def upsert_by_id(items: list[Any], item: dict[str, Any]) -> None:
    item_id = item.get("id")
    for index, existing in enumerate(items):
        if isinstance(existing, dict) and existing.get("id") == item_id:
            merged = dict(existing)
            merged.update(item)
            items[index] = merged
            return
    items.append(item)


def collect_ids(items: Any) -> list[str]:
    if not isinstance(items, list):
        return []
    return [str(item.get("id")) for item in items if isinstance(item, dict) and item.get("id")]


def append_message(state: dict[str, Any], to_agent: str, input_summary: str, expected_output: str, task_id: str = "") -> str:
    messages = ensure_list(state, "messages")
    message_id = next_id(messages, "msg")
    messages.append(
        {
            "id": message_id,
            "time": now(),
            "from": "orchestrator",
            "to": to_agent,
            "task_id": task_id,
            "status": "sent",
            "input_summary": input_summary,
            "expected_output": expected_output,
            "output_summary": "",
        }
    )
    return message_id


def cmd_phase(args: argparse.Namespace, state: dict[str, Any]) -> str:
    state.setdefault("project", {})["current_phase"] = args.name
    if args.summary:
        state.setdefault("project", {})["purpose"] = args.summary
    event_id = append_event(state, "phase_updated", "orchestrator", f"phase set to {args.name}", args.status)
    sync_report(state, event_id, f"Phase updated to {args.name}", args.monitor_status)
    return event_id


def cmd_report(args: argparse.Namespace, state: dict[str, Any]) -> str:
    reports = ensure_list(state, "council_reports")
    report_id = args.id or next_id(reports, "rpt")
    reports.append(
        {
            "id": report_id,
            "agent": args.agent,
            "status": args.status,
            "verdict": args.verdict,
            "summary": args.summary,
            "top_findings": args.finding or [],
            "opportunities": args.opportunity or [],
            "risks": args.risk or [],
            "questions_for_user": args.question or [],
            "recommended_next_action": args.next_action,
            "artifact_path": args.artifact,
            "created_at": now(),
        }
    )
    event_id = append_event(state, "council_report_done", args.agent, args.summary, args.status, args.artifact)
    sync_report(state, event_id, f"{args.agent} report recorded", args.monitor_status)
    return event_id


def cmd_option(args: argparse.Namespace, state: dict[str, Any]) -> str:
    options = ensure_list(state, "option_matrix")
    option_id = args.id or next_id(options, "opt")
    options.append(
        {
            "id": option_id,
            "label": args.label,
            "status": args.status,
            "target_user": args.target_user,
            "user_job": args.user_job,
            "mvp_scope": args.mvp_scope or [],
            "differentiator": args.differentiator,
            "moat_hypothesis": args.moat,
            "technical_path": args.technical_path,
            "workarounds": args.workaround or [],
            "excluded_scope": args.excluded_scope or [],
            "risks": args.risk or [],
            "difficulty": args.difficulty,
            "why_choose": args.why_choose,
            "why_not": args.why_not,
        }
    )
    event_id = append_event(state, "option_matrix_ready", "orchestrator", f"option recorded: {option_id}", "done")
    sync_report(state, event_id, f"Option {option_id} recorded", args.monitor_status)
    return event_id


def cmd_decision(args: argparse.Namespace, state: dict[str, Any]) -> str:
    decisions = ensure_list(state, "decisions")
    decision_id = args.id or next_id(decisions, "dec")
    decision_record = {
        "id": decision_id,
        "time": now(),
        "status": args.status,
        "question": args.question,
        "recommended": args.recommended,
        "options": [{"id": item.split(":", 1)[0], "label": item.split(":", 1)[-1], "consequence": ""} for item in (args.option or [])],
        "selected": args.selected,
        "reason": args.reason,
        "handoff_to": args.handoff_to,
        "related_docs": args.doc or [],
        "artifact_paths": args.artifact or [],
    }
    upsert_by_id(decisions, decision_record)
    queue = ensure_list(state, "approval_queue")
    queue[:] = [item for item in queue if not (isinstance(item, dict) and item.get("id") == decision_id)]
    if args.status in {"waiting_user", "pending"}:
        queue.append(
            {
                "id": decision_id,
                "type": "decision",
                "status": args.status,
                "question": args.question,
                "recommended": args.recommended,
                "selected": args.selected,
                "options": [{"id": item.split(":", 1)[0], "label": item.split(":", 1)[-1]} for item in (args.option or [])],
                "created_at": now(),
            }
        )
    event_id = append_event(state, "decision_requested", "orchestrator", args.question, args.status)
    decision_summary = f"{args.question} Recommended: {args.recommended}".strip()
    sync_report(
        state,
        event_id,
        f"Decision recorded: {args.question}",
        args.monitor_status,
        decision_id,
        requires_user=args.status in {"waiting_user", "pending"},
        decision_summary=decision_summary,
    )
    return event_id


def cmd_lock(args: argparse.Namespace, state: dict[str, Any]) -> str:
    direction_lock = state.setdefault("direction_lock", {})
    decisions = ensure_list(state, "decisions")
    reports = ensure_list(state, "council_reports")
    source_decision_ids = (args.decision_id or collect_ids(decisions[-1:])) if decisions else (args.decision_id or [])
    source_report_ids = args.report_id or collect_ids(reports)
    direction_lock["status"] = args.status
    direction_lock["selected_option_id"] = args.selected_option_id
    direction_lock["approved_at"] = now() if args.status in {"approved", "locked"} else direction_lock.get("approved_at", "")
    direction_lock["approved_by"] = args.approved_by
    direction_lock["source_decision_ids"] = source_decision_ids
    direction_lock["source_report_ids"] = source_report_ids
    locked_items = direction_lock.setdefault("locked_items", {})
    for key in ("target_user", "user_job", "product_promise", "technical_approach", "moat_hypothesis", "design_posture"):
        value = getattr(args, key)
        if value:
            locked_items[key] = value
    for key in ("mvp_scope", "non_goals", "technical_constraints", "workarounds", "business_assumptions", "accepted_risks", "open_questions_allowed"):
        value = getattr(args, key)
        if value:
            locked_items[key] = value
    if args.status == "skipped_by_user":
        alerts = ensure_list(state, "operator_alerts")
        alerts.append({"id": next_id(alerts, "alert"), "status": "watching", "summary": "Discovery was skipped by user.", "created_at": now()})
    if args.status in {"approved", "locked"}:
        for decision in decisions:
            if isinstance(decision, dict) and decision.get("id") in source_decision_ids:
                decision["status"] = "approved"
                if args.selected_option_id and not decision.get("selected"):
                    decision["selected"] = args.selected_option_id
                if not decision.get("reason"):
                    decision["reason"] = "Direction Lock approved."
        queue = ensure_list(state, "approval_queue")
        queue[:] = [
            item
            for item in queue
            if not (isinstance(item, dict) and item.get("id") in source_decision_ids)
        ]
        handoff_summary = (
            f"Direction Lock {args.status}: "
            f"{locked_items.get('target_user', 'target user not set')} / "
            f"{locked_items.get('user_job', 'user job not set')}"
        )
        handoff_ids = [
            append_message(state, "product-strategist", handoff_summary, "Create or update PRD from the approved Direction Lock."),
            append_message(state, "growth-marketer", handoff_summary, "Create or update GTM from the approved Direction Lock."),
            append_message(state, "planner", handoff_summary, "Create implementation approach and task sequencing from the approved Direction Lock."),
            append_message(state, "design-studio", handoff_summary, "Prepare design direction or design brief from the approved Direction Lock."),
        ]
        direction_lock["handoff_message_ids"] = handoff_ids
    event_type = "direction_lock_approved" if args.status in {"approved", "locked"} else "direction_lock_updated"
    event_id = append_event(state, event_type, "orchestrator", f"direction lock {args.status}", args.status, direction_lock.get("path", ""))
    sync_report(state, event_id, f"Direction Lock {args.status}", args.monitor_status, (source_decision_ids or [""])[0])
    return event_id


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Update a vibe-coding-factory state file.")
    parser.add_argument("--state", default=DEFAULT_STATE, help="Path to factory-state.json")
    parser.add_argument("--monitor-status", default="state_only", choices=("current", "state_only", "stale", "unavailable"))
    sub = parser.add_subparsers(dest="command", required=True)

    phase = sub.add_parser("phase")
    phase.add_argument("--name", required=True)
    phase.add_argument("--status", default="running")
    phase.add_argument("--summary", default="")

    report = sub.add_parser("report")
    report.add_argument("--id", default="")
    report.add_argument("--agent", required=True)
    report.add_argument("--status", default="done")
    report.add_argument("--verdict", default="watch")
    report.add_argument("--summary", required=True)
    report.add_argument("--artifact", "--artifact-id", dest="artifact", default="")
    report.add_argument("--finding", action="append")
    report.add_argument("--opportunity", action="append")
    report.add_argument("--risk", action="append")
    report.add_argument("--question", action="append")
    report.add_argument("--next-action", default="")

    option = sub.add_parser("option")
    option.add_argument("--id", default="")
    option.add_argument("--label", required=True)
    option.add_argument("--status", default="candidate")
    option.add_argument("--target-user", default="")
    option.add_argument("--user-job", default="")
    option.add_argument("--mvp-scope", action="append")
    option.add_argument("--differentiator", default="")
    option.add_argument("--moat", default="")
    option.add_argument("--technical-path", default="")
    option.add_argument("--workaround", action="append")
    option.add_argument("--excluded-scope", action="append")
    option.add_argument("--risk", action="append")
    option.add_argument("--difficulty", default="medium")
    option.add_argument("--why-choose", default="")
    option.add_argument("--why-not", default="")

    decision = sub.add_parser("decision")
    decision.add_argument("--id", default="")
    decision.add_argument("--status", default="waiting_user")
    decision.add_argument("--question", required=True)
    decision.add_argument("--recommended", default="")
    decision.add_argument("--option", action="append")
    decision.add_argument("--selected", default="")
    decision.add_argument("--reason", default="")
    decision.add_argument("--handoff-to", default="")
    decision.add_argument("--doc", action="append")
    decision.add_argument("--artifact", action="append")

    lock = sub.add_parser("lock")
    lock.add_argument("--status", default="approved", choices=("approved", "locked", "skipped_by_user", "stale", "waiting_user"))
    lock.add_argument("--selected-option-id", default="")
    lock.add_argument("--approved-by", default="")
    lock.add_argument("--decision-id", action="append")
    lock.add_argument("--report-id", action="append")
    lock.add_argument("--target-user", default="")
    lock.add_argument("--user-job", default="")
    lock.add_argument("--product-promise", default="")
    lock.add_argument("--mvp-scope", action="append")
    lock.add_argument("--non-goals", action="append")
    lock.add_argument("--technical-approach", default="")
    lock.add_argument("--technical-constraints", action="append")
    lock.add_argument("--workarounds", action="append")
    lock.add_argument("--moat-hypothesis", default="")
    lock.add_argument("--business-assumptions", action="append")
    lock.add_argument("--design-posture", default="")
    lock.add_argument("--accepted-risks", action="append")
    lock.add_argument("--open-questions-allowed", action="append")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    state_path = Path(args.state)
    state = load_state(state_path)
    command = {
        "phase": cmd_phase,
        "report": cmd_report,
        "option": cmd_option,
        "decision": cmd_decision,
        "lock": cmd_lock,
    }[args.command]
    event_id = command(args, state)
    save_state(state_path, state)
    print(event_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
