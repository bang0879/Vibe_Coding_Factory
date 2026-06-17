#!/usr/bin/env python3
"""Deterministic checks for vibe-coding-factory runs.

This script intentionally uses only the Python standard library so it can run
inside small generated projects without installing dependencies.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import sys
import urllib.request
from urllib.parse import urlparse
from pathlib import Path
from typing import Any


PASS_VALUES = {"passed", "pass", "done", "approved", True}
COMPLETE_PHASES = {"complete", "completed", "done"}
POST_DIRECTION_PHASES = {
    "planning",
    "planned",
    "design",
    "tasking",
    "implementation",
    "implementing",
    "build",
    "building",
    "qa",
    "review",
    "complete",
    "completed",
    "done",
}
COMPLETE_TASK_STATUS = {"done", "approved"}
REQUIRED_COUNCIL_AGENTS = {
    "product-strategist",
    "technical-feasibility-architect",
    "growth-moat-strategist",
    "ux-strategist",
    "risk-critic",
    "planner",
}
USER_FACING_HINTS = (
    "app",
    "ui",
    "ux",
    "screen",
    "browser",
    "frontend",
    "dashboard",
    "product",
    "interactive",
    "user-facing",
)
APP_DIRS = {"app", "src", "components", "pages", "views", "routes"}
APP_SUFFIXES = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte"}
IGNORED_APP_SCAN_DIRS = {".git", ".factory", "node_modules", "__pycache__", ".next", "dist", "build"}
APPROVED_LOCK_STATUSES = {"approved", "locked", "skipped_by_user"}
CAPABILITY_MODES = {"live", "user_data", "local_functional", "partial"}
OUT_OF_SEED_MARKERS = (
    "out-of-seed",
    "out_of_seed",
    "unlisted input",
    "outside seed",
    "not present in preset",
    "not one of the preset",
    "not in seed",
    "open-ended",
    "free input",
)


class Finding:
    def __init__(self, level: str, code: str, message: str) -> None:
        self.level = level
        self.code = code
        self.message = message

    def as_dict(self) -> dict[str, str]:
        return {"level": self.level, "code": self.code, "message": self.message}


class Collector:
    def __init__(self) -> None:
        self.findings: list[Finding] = []

    def fail(self, code: str, message: str) -> None:
        self.findings.append(Finding("fail", code, message))

    def warn(self, code: str, message: str) -> None:
        self.findings.append(Finding("warn", code, message))

    @property
    def failed(self) -> bool:
        return any(item.level == "fail" for item in self.findings)


def load_json(path: Path, collector: Collector, label: str) -> Any | None:
    if not path.exists():
        collector.fail("missing-file", f"{label} does not exist: {path}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:  # pragma: no cover - message matters more here
        collector.fail("invalid-json", f"{label} is not valid JSON: {path} ({exc})")
        return None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_pass(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in PASS_VALUES
    return value in PASS_VALUES


def as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [value]


def slug(value: Any) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")
    return text.replace("growth-and-moat", "growth-moat")


def contains_any_marker(value: Any, markers: tuple[str, ...]) -> bool:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True).lower()
    return any(marker in text for marker in markers)


def rel_inside_factory(path_text: str) -> bool:
    normalized = path_text.replace("\\", "/").lstrip("./")
    return normalized.startswith(".factory/") or normalized.startswith("factory/")


def resolve_project_path(project_root: Path, path_text: str) -> Path:
    candidate = Path(path_text)
    if not candidate.is_absolute():
        candidate = project_root / candidate
    return candidate


def is_ignored_app_scan_path(path: Path, root: Path) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return True
    return any(part in IGNORED_APP_SCAN_DIRS for part in parts)


def discover_app_files(project_root: Path) -> list[str]:
    hits: list[str] = []
    for path in project_root.rglob("*"):
        if not path.is_file() or is_ignored_app_scan_path(path, project_root):
            continue
        rel = path.relative_to(project_root)
        parts = rel.parts
        if not parts:
            continue
        under_app_dir = parts[0] in APP_DIRS
        root_entry = len(parts) == 1 and path.name.lower() in {"index.html", "main.jsx", "main.tsx", "app.jsx", "app.tsx"}
        if (under_app_dir or root_entry) and path.suffix.lower() in APP_SUFFIXES:
            hits.append(rel.as_posix())
    return sorted(hits)


def task_is_user_facing(task: dict[str, Any]) -> bool:
    text = " ".join(
        str(task.get(key, ""))
        for key in ("title", "goal", "verification", "agent_owner")
    ).lower()
    if any(hint in text for hint in USER_FACING_HINTS):
        return True
    if task.get("scenario_harness") or task.get("design_parity") or task.get("completion_contract"):
        return True
    return False


def has_generic_evidence(text: str) -> bool:
    lowered = text.lower()
    generic_bits = (
        "persona",
        "looks good",
        "seems fine",
        "as described",
        "completed the assigned task",
        "performed the configured role",
    )
    return any(bit in lowered for bit in generic_bits)


def check_required_docs(project_root: Path, state: dict[str, Any], collector: Collector) -> None:
    phase = str(state.get("project", {}).get("current_phase", "")).lower()
    if phase not in COMPLETE_PHASES:
        return
    for rel in (
        "docs/REQUIREMENTS.md",
        "docs/ACCEPTANCE_CONTRACT.json",
        "docs/IMPLEMENTATION_PLAN.md",
        "docs/QA_EVIDENCE.md",
    ):
        if not (project_root / rel).exists():
            collector.fail("missing-completion-doc", f"complete run is missing {rel}")


def check_direction_lock(project_root: Path, state: dict[str, Any], collector: Collector) -> None:
    phase = str(state.get("project", {}).get("current_phase", "")).lower()
    tasks = as_list(state.get("tasks"))
    needs_lock = phase in POST_DIRECTION_PHASES or bool(tasks)
    if not needs_lock:
        return

    direction_lock = state.get("direction_lock")
    if not isinstance(direction_lock, dict):
        collector.fail("missing-direction-lock", "state needs direction_lock before planning, tasks, or completion")
        return

    status = str(direction_lock.get("status", "")).lower()
    if status not in {"approved", "locked", "skipped_by_user"}:
        collector.fail(
            "direction-lock-not-approved",
            f"direction_lock.status must be approved, locked, or skipped_by_user before planning/tasks; got {status or 'empty'}",
        )

    path_text = str(direction_lock.get("path") or "docs/DIRECTION_LOCK.md")
    if status in {"approved", "locked"} and not resolve_project_path(project_root, path_text).exists():
        collector.fail("missing-direction-lock-doc", f"approved direction lock doc does not exist: {path_text}")

    locked_items = direction_lock.get("locked_items")
    if status in {"approved", "locked"} and not isinstance(locked_items, dict):
        collector.fail("direction-lock-items", "approved direction_lock must contain locked_items object")
        return

    if isinstance(locked_items, dict) and status in {"approved", "locked"}:
        for key in ("target_user", "user_job", "mvp_scope", "non_goals", "technical_approach", "moat_hypothesis", "accepted_risks"):
            value = locked_items.get(key)
            if value in ("", None, []):
                collector.fail("direction-lock-field", f"direction_lock.locked_items.{key} is empty")

        source_decision_ids = [str(item) for item in as_list(direction_lock.get("source_decision_ids")) if str(item)]
        source_report_ids = [str(item) for item in as_list(direction_lock.get("source_report_ids")) if str(item)]
        handoff_message_ids = [str(item) for item in as_list(direction_lock.get("handoff_message_ids")) if str(item)]

        if not source_decision_ids:
            collector.fail("direction-lock-source-decision", "approved direction_lock must record source_decision_ids")
        if not source_report_ids:
            collector.fail("direction-lock-source-report", "approved direction_lock must record source_report_ids")
        if not handoff_message_ids:
            collector.fail("direction-lock-handoff", "approved direction_lock must record handoff_message_ids")

        decisions = state.get("decisions")
        if isinstance(decisions, list):
            known_decisions = {str(item.get("id")) for item in decisions if isinstance(item, dict) and item.get("id")}
            for decision_id in source_decision_ids:
                if decision_id not in known_decisions:
                    collector.fail("direction-lock-decision-missing", f"source decision does not exist in decisions[]: {decision_id}")
        elif source_decision_ids:
            collector.fail("direction-lock-decisions-shape", "state.decisions must be a list when source_decision_ids are recorded")

        reports = state.get("council_reports")
        if isinstance(reports, list):
            known_reports = {str(item.get("id")) for item in reports if isinstance(item, dict) and item.get("id")}
            sourced_report_agents = {
                slug(item.get("agent"))
                for item in reports
                if isinstance(item, dict) and str(item.get("id")) in source_report_ids
            }
            for report_id in source_report_ids:
                if report_id not in known_reports:
                    collector.fail("direction-lock-report-missing", f"source report does not exist in council_reports[]: {report_id}")
            missing_agents = sorted(REQUIRED_COUNCIL_AGENTS - sourced_report_agents)
            if missing_agents:
                collector.fail("direction-lock-council-incomplete", f"source_report_ids must include every Discovery Council role; missing: {', '.join(missing_agents)}")
        elif source_report_ids:
            collector.fail("direction-lock-reports-shape", "state.council_reports must be a list when source_report_ids are recorded")

        messages = state.get("messages")
        if isinstance(messages, list):
            known_messages = {str(item.get("id")) for item in messages if isinstance(item, dict) and item.get("id")}
            for message_id in handoff_message_ids:
                if message_id not in known_messages:
                    collector.fail("direction-lock-message-missing", f"handoff message does not exist in messages[]: {message_id}")
        elif handoff_message_ids:
            collector.fail("direction-lock-messages-shape", "state.messages must be a list when handoff_message_ids are recorded")

    if status == "skipped_by_user":
        alerts = as_list(state.get("operator_alerts"))
        if not alerts:
            collector.warn("direction-lock-skipped-no-alert", "discovery was skipped but operator_alerts is empty")


def check_app_files_before_direction_lock(project_root: Path, state: dict[str, Any], collector: Collector) -> None:
    direction_lock = state.get("direction_lock")
    status = ""
    if isinstance(direction_lock, dict):
        status = str(direction_lock.get("status", "")).strip().lower()
    if status in APPROVED_LOCK_STATUSES:
        return
    app_files = discover_app_files(project_root)
    if app_files:
        collector.fail(
            "app-files-before-direction-lock",
            "app/product files exist before Direction Lock approval: " + ", ".join(app_files[:12]),
        )


def monitor_view_exists(project_root: Path, value: Any) -> bool:
    if value in ("", None, []):
        return False
    text = str(value)
    parsed = urlparse(text)
    if parsed.scheme in {"http", "https"}:
        return True
    if parsed.scheme == "file":
        return Path(parsed.path).exists()
    path = Path(text)
    if not path.is_absolute():
        path = project_root / path
    return path.exists()


def check_user_wait_monitor_report(project_root: Path, state: dict[str, Any], collector: Collector) -> None:
    approval_queue = [
        item for item in as_list(state.get("approval_queue"))
        if isinstance(item, dict) and str(item.get("status", "")).lower() in {"waiting_user", "pending"}
    ]
    report_sync = state.get("report_sync")
    if not approval_queue and not (isinstance(report_sync, dict) and report_sync.get("last_prompt_requires_user")):
        return
    if not isinstance(report_sync, dict):
        collector.fail("user-wait-monitor-missing", "user decision is waiting but report_sync is missing")
        return

    required_fields = {
        "latest_decision_id": report_sync.get("latest_decision_id"),
        "latest_decision_summary": report_sync.get("latest_decision_summary"),
        "user_waiting_summary": report_sync.get("user_waiting_summary"),
        "monitor_view": report_sync.get("monitor_view") or report_sync.get("monitor_url"),
    }
    for key, value in required_fields.items():
        if value in ("", None, []):
            collector.fail("user-wait-monitor-missing", f"user wait report_sync.{key} is empty")

    monitor_value = required_fields["monitor_view"]
    if monitor_value not in ("", None, []) and not monitor_view_exists(project_root, monitor_value):
        collector.fail("user-wait-monitor-path-missing", f"user wait monitor view does not exist: {monitor_value}")

    monitor_status = str(report_sync.get("monitor_status", "")).lower()
    if monitor_status not in {"current", "state_only"}:
        collector.fail("user-wait-monitor-stale", f"user wait monitor_status must be current or state_only; got {monitor_status or 'empty'}")


def check_acceptance_contract(project_root: Path, collector: Collector) -> dict[str, Any] | None:
    contract_path = project_root / "docs" / "ACCEPTANCE_CONTRACT.json"
    if not contract_path.exists():
        return None
    contract = load_json(contract_path, collector, "acceptance contract")
    if not isinstance(contract, dict):
        collector.fail("contract-shape", "docs/ACCEPTANCE_CONTRACT.json must be an object")
        return None

    scenarios = as_list(contract.get("primary_scenarios"))
    if not scenarios:
        collector.fail("contract-scenarios", "acceptance contract must define primary_scenarios")
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            collector.fail("contract-scenario-shape", "each primary scenario must be an object")
            continue
        scenario_id = scenario.get("id", "unknown")
        for key in ("given", "when", "then", "evidence"):
            if not scenario.get(key):
                collector.fail("contract-scenario-field", f"{scenario_id} is missing {key}")

    capability = contract.get("capability_contract")
    open_input_required = False
    if not isinstance(capability, dict):
        collector.fail("contract-capability-missing", "acceptance contract must define capability_contract")
    else:
        mode = str(capability.get("mode", "")).strip().lower()
        if mode not in CAPABILITY_MODES:
            collector.fail("contract-capability-mode", f"capability_contract.mode must be one of {sorted(CAPABILITY_MODES)}")

        input_freedom = as_list(capability.get("input_freedom"))
        if not input_freedom:
            collector.fail("contract-input-freedom", "capability_contract.input_freedom must define user input freedom")
        for index, item in enumerate(input_freedom, start=1):
            if not isinstance(item, dict):
                collector.fail("contract-input-freedom-shape", f"input_freedom #{index} must be an object")
                continue
            field = item.get("field")
            expected_control = item.get("expected_control")
            if field in ("", None):
                collector.fail("contract-input-field", f"input_freedom #{index} is missing field")
            if expected_control in ("", None):
                collector.fail("contract-input-control", f"input_freedom #{index} is missing expected_control")
            if "closed_set_allowed" not in item:
                collector.fail("contract-input-closed-set", f"input_freedom #{index} must state closed_set_allowed")
            if item.get("closed_set_allowed") is False:
                open_input_required = True

        if not as_list(capability.get("forbidden_downgrades")):
            collector.fail("contract-forbidden-downgrades", "capability_contract.forbidden_downgrades must name disallowed downgrades")

        requires_live = capability.get("requires_live_data_or_api") is True
        if requires_live and mode != "live" and not as_list(capability.get("approved_fallbacks")):
            collector.fail("contract-live-fallback-unapproved", "live/API capability requires approved_fallbacks when mode is not live")

        sample_policy = capability.get("sample_data_policy", {})
        if mode in {"local_functional", "partial"}:
            if not isinstance(sample_policy, dict):
                collector.fail("contract-sample-policy", "local_functional or partial mode must define sample_data_policy")
            elif sample_policy.get("must_label_sample_mode") is not True:
                collector.fail("contract-sample-label", "sample/local mode must label sample mode to the user")

    if open_input_required and not any(contains_any_marker(scenario, OUT_OF_SEED_MARKERS) for scenario in scenarios):
        collector.fail(
            "contract-out-of-seed-scenario",
            "open-ended input requires at least one out-of-seed or unlisted-input primary scenario",
        )

    verification = contract.get("verification", {})
    entrypoint = verification.get("real_entrypoint") if isinstance(verification, dict) else ""
    if entrypoint:
        path = resolve_project_path(project_root, str(entrypoint))
        if rel_inside_factory(str(entrypoint)):
            collector.fail("factory-entrypoint", f"real app entrypoint cannot be inside .factory: {entrypoint}")
        elif not path.exists():
            collector.fail("missing-entrypoint", f"contract real_entrypoint does not exist: {entrypoint}")

    return contract


def check_task_contracts(project_root: Path, tasks: list[Any], collector: Collector) -> None:
    for index, raw_task in enumerate(tasks, start=1):
        if not isinstance(raw_task, dict):
            collector.fail("task-shape", f"task #{index} is not an object")
            continue
        task = raw_task
        task_id = str(task.get("id") or f"task-{index}")
        status = str(task.get("status", "")).lower()
        done = status in COMPLETE_TASK_STATUS

        for required in ("id", "title", "difficulty", "status", "allowed_files", "verification"):
            if not task.get(required):
                collector.fail("task-required-field", f"{task_id} is missing {required}")

        allowed = as_list(task.get("allowed_files"))
        if not allowed:
            collector.fail("task-allowed-files", f"{task_id} must define allowed_files")

        steps = as_list(task.get("agent_steps"))
        if done and task.get("agent_flow") and not steps:
            collector.fail("missing-agent-steps", f"{task_id} is done but has no agent_steps evidence")
        for step in steps:
            if not isinstance(step, dict):
                collector.fail("agent-step-shape", f"{task_id} has a non-object agent step")
                continue
            agent = step.get("agent", "unknown")
            did = str(step.get("did", "")).strip()
            evidence = str(step.get("evidence", "")).strip()
            if done and not did:
                collector.fail("agent-step-did", f"{task_id}/{agent} is missing concrete did text")
            if did and has_generic_evidence(did):
                collector.fail("generic-agent-step", f"{task_id}/{agent} has generic did text: {did}")
            if done and agent in {"qa-tester", "ux-checker", "consumer-appeal-reviewer", "scope-auditor"} and not evidence:
                collector.fail("agent-step-evidence", f"{task_id}/{agent} is missing evidence")

        if not task_is_user_facing(task):
            continue

        scenarios = as_list(task.get("scenario_harness"))
        design_checks = as_list(task.get("design_parity"))
        completion = task.get("completion_contract")

        if done and not scenarios:
            collector.fail("missing-scenarios", f"{task_id} is user-facing and done but has no scenario_harness")
        for scenario in scenarios:
            if not isinstance(scenario, dict):
                collector.fail("scenario-shape", f"{task_id} has a non-object scenario")
                continue
            scenario_id = scenario.get("id", "unknown")
            if done and not is_pass(scenario.get("status")):
                collector.fail("scenario-not-passed", f"{task_id}/{scenario_id} is not passed")
            for key in ("given", "when", "then", "evidence"):
                if done and not scenario.get(key):
                    collector.fail("scenario-field", f"{task_id}/{scenario_id} is missing {key}")

        if done and not design_checks:
            collector.fail("missing-design-parity", f"{task_id} is user-facing and done but has no design_parity")
        for check in design_checks:
            if isinstance(check, dict):
                status_value = check.get("status", check.get("checked"))
                label = check.get("check", "design check")
            else:
                status_value = check
                label = str(check)
            if done and not is_pass(status_value):
                collector.fail("design-not-passed", f"{task_id} design parity is not passed: {label}")

        if done and not completion:
            collector.fail("missing-completion-contract", f"{task_id} is done but has no completion_contract")
        if isinstance(completion, dict):
            for key in ("scenario_status", "design_parity_status", "qa_evidence_status"):
                if done and not is_pass(completion.get(key)):
                    collector.fail("completion-status", f"{task_id} completion_contract.{key} is not passed")
            entrypoint = completion.get("real_entrypoint")
            if done and entrypoint:
                if rel_inside_factory(str(entrypoint)):
                    collector.fail("factory-entrypoint", f"{task_id} real_entrypoint is inside .factory: {entrypoint}")
                elif not resolve_project_path(project_root, str(entrypoint)).exists():
                    collector.fail("missing-entrypoint", f"{task_id} real_entrypoint does not exist: {entrypoint}")
        elif isinstance(completion, list):
            if done and not all(is_pass(item) for item in completion):
                collector.fail("completion-list", f"{task_id} completion_contract checklist is not fully passed")


def check_artifacts(project_root: Path, state: dict[str, Any], collector: Collector) -> None:
    for artifact in as_list(state.get("artifacts")):
        if not isinstance(artifact, dict):
            continue
        path_text = artifact.get("path")
        if not path_text or str(path_text).startswith(("http://", "https://")):
            continue
        path = resolve_project_path(project_root, str(path_text))
        if not path.exists():
            collector.warn("missing-artifact", f"artifact path is not present on disk: {path_text}")


def check_state(project_root: Path, state_path: Path, collector: Collector) -> dict[str, Any] | None:
    state = load_json(state_path, collector, "factory state")
    if not isinstance(state, dict):
        collector.fail("state-shape", "factory state must be a JSON object")
        return None

    if not isinstance(state.get("project"), dict):
        collector.fail("state-project", "factory state is missing project object")
    if not isinstance(state.get("tasks"), list):
        collector.fail("state-tasks", "factory state is missing tasks array")
        tasks: list[Any] = []
    else:
        tasks = state["tasks"]

    phase = str(state.get("project", {}).get("current_phase", "")).lower()
    if phase in COMPLETE_PHASES and not tasks:
        collector.fail("complete-no-tasks", "project is complete but has no tasks")

    check_required_docs(project_root, state, collector)
    check_direction_lock(project_root, state, collector)
    check_app_files_before_direction_lock(project_root, state, collector)
    check_user_wait_monitor_report(project_root, state, collector)
    check_task_contracts(project_root, tasks, collector)
    check_artifacts(project_root, state, collector)
    return state


def check_dashboard(
    project_root: Path,
    template_path: Path | None,
    served_url: str | None,
    write_meta: bool,
    collector: Collector,
) -> None:
    dashboard_path = project_root / ".factory" / "factory-dashboard.html"
    state_path = project_root / ".factory" / "factory-state.json"
    if not dashboard_path.exists():
        collector.fail("missing-dashboard", f"dashboard does not exist: {dashboard_path}")
        return

    dashboard_hash = sha256(dashboard_path)
    template_hash = ""
    if template_path and template_path.exists():
        template_hash = sha256(template_path)
        if template_hash != dashboard_hash:
            collector.fail(
                "stale-dashboard",
                "project dashboard hash differs from current template; refresh .factory/factory-dashboard.html",
            )
    elif template_path:
        collector.warn("missing-template", f"dashboard template not found: {template_path}")

    fetched_hash = ""
    if served_url:
        try:
            with urllib.request.urlopen(served_url, timeout=5) as response:
                body = response.read()
            fetched_hash = hashlib.sha256(body).hexdigest()
            if fetched_hash != dashboard_hash:
                collector.fail("served-dashboard-mismatch", "served monitor URL does not match local dashboard file")
        except Exception as exc:  # pragma: no cover - environment dependent
            collector.fail("served-dashboard-fetch", f"could not fetch served monitor URL: {served_url} ({exc})")

    if write_meta:
        meta = {
            "project_root": str(project_root),
            "dashboard_path": str(dashboard_path),
            "template_path": str(template_path) if template_path else "",
            "dashboard_sha256": dashboard_hash,
            "template_sha256": template_hash,
            "served_sha256": fetched_hash,
            "state_path": str(state_path),
            "server_port": served_url.split(":")[2].split("/")[0] if served_url and ":" in served_url else "",
            "served_url": served_url or "",
            "updated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        }
        meta_path = project_root / ".factory" / "monitor-meta.json"
        url_path = project_root / ".factory" / "monitor-url.txt"
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        url_path.write_text(f"{served_url or ''}\nproject_root={project_root}\n", encoding="utf-8")


def check_app_entry(project_root: Path, app_entry: str | None, collector: Collector) -> None:
    if not app_entry:
        return
    if rel_inside_factory(app_entry):
        collector.fail("factory-entrypoint", f"app entrypoint cannot be inside .factory: {app_entry}")
        return
    path = resolve_project_path(project_root, app_entry)
    if not path.exists():
        collector.fail("missing-entrypoint", f"app entrypoint does not exist: {app_entry}")
        return
    if path.suffix.lower() in {".html", ".htm"}:
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        if "factory-dashboard" in text or "factory monitor" in text:
            collector.fail("monitor-as-app", f"app entrypoint appears to be the factory monitor: {app_entry}")
        interactive_markers = ("addEventListener", "onclick", "onchange", "<form", "<input", "<select", "<button")
        if not any(marker.lower() in text for marker in interactive_markers):
            collector.warn("weak-interactivity-signal", f"HTML entrypoint has no obvious interaction markers: {app_entry}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify a vibe-coding-factory run.")
    parser.add_argument("--project-root", default=".", help="Active project root.")
    parser.add_argument("--mode", choices=("all", "state", "dashboard", "app"), default="all")
    parser.add_argument("--state", default=".factory/factory-state.json", help="Factory state path.")
    parser.add_argument("--template", default="", help="Current dashboard template path.")
    parser.add_argument("--served-url", default="", help="Monitor URL to fetch and compare.")
    parser.add_argument("--app-entry", default="", help="Real app entrypoint to check.")
    parser.add_argument("--write-monitor-meta", action="store_true", help="Write monitor-meta.json and monitor-url.txt.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    collector = Collector()
    project_root = Path(args.project_root).resolve()
    state_path = resolve_project_path(project_root, args.state)
    template_path = Path(args.template).resolve() if args.template else None
    if not args.template:
        local_template = project_root / "vibe-coding-factory" / "templates" / "factory-dashboard.html"
        template_path = local_template if local_template.exists() else None

    state: dict[str, Any] | None = None
    if args.mode in {"all", "state"}:
        state = check_state(project_root, state_path, collector)
        check_acceptance_contract(project_root, collector)

    if args.mode in {"all", "dashboard"}:
        check_dashboard(
            project_root=project_root,
            template_path=template_path,
            served_url=args.served_url or None,
            write_meta=args.write_monitor_meta,
            collector=collector,
        )

    app_entry = args.app_entry
    if not app_entry and isinstance(state, dict):
        contract = state.get("quality_harness", {}).get("real_entrypoint") if isinstance(state.get("quality_harness"), dict) else ""
        app_entry = str(contract or "")
    if args.mode in {"all", "app"}:
        check_app_entry(project_root, app_entry or None, collector)

    result = {
        "ok": not collector.failed,
        "project_root": str(project_root),
        "findings": [finding.as_dict() for finding in collector.findings],
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        status = "PASS" if result["ok"] else "FAIL"
        print(f"{status} vibe-coding-factory verification")
        for finding in collector.findings:
            print(f"[{finding.level.upper()}] {finding.code}: {finding.message}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
