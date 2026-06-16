#!/usr/bin/env python3
"""Validate the factory skill's discovery workflow and state schema."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_TOP_LEVEL = [
    "factory",
    "project",
    "discovery",
    "council_reports",
    "option_matrix",
    "direction_lock",
    "approval_queue",
    "plan",
    "tasks",
    "active_flow",
    "messages",
    "decisions",
    "artifacts",
    "events",
    "report_sync",
    "operator_alerts",
    "monitor_health",
    "agents",
]

REQUIRED_GATES = [
    "idea-snapshot",
    "discovery-council",
    "decision-brief",
    "direction-lock",
    "report-sync",
]

REQUIRED_AGENTS = [
    "product-strategist",
    "technical-feasibility-architect",
    "growth-moat-strategist",
    "ux-strategist",
    "risk-critic",
    "planner",
]

REQUIRED_SKILL_TEXT = [
    "Discovery Council",
    "Direction Lock",
    "implementation freeze",
    "report_sync",
    "council_reports[]",
    "option_matrix[]",
]

REQUIRED_FILES = [
    "agents/openai.yaml",
    "references/discovery-council.md",
    "references/reporting-sync.md",
    "references/benchmark-rubric.md",
    "templates/decision-brief.md",
    "templates/direction-lock.md",
    "templates/feasibility-report.md",
    "templates/moat-strategy.md",
    "templates/risk-register.md",
    "scripts/update_factory_state.py",
    "scripts/benchmark_factory_skill.py",
]

REQUIRED_DASHBOARD_TEXT = [
    'data-panel="approval-queue"',
    'data-panel="direction-lock"',
    'data-panel="discovery-council"',
    'data-panel="option-matrix"',
    'data-panel="report-sync"',
    'data-panel="handoffs"',
    "renderDirectionLock",
    "renderCouncilReports",
    "renderDiscovery",
    "renderOptions",
]

BAD_TEXT_MARKERS = [
    "\ufffd",
    "寃곗젙",
    "異붿쿇",
    "?꾩",
    "?먮룞",
    "?ㅼ쓬",
]


def fail(findings: list[str], message: str) -> None:
    findings.append(message)


def load_json(path: Path, findings: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - diagnostic path
        fail(findings, f"invalid-json: {path}: {exc}")
        return {}


def check_state(skill_root: Path, findings: list[str]) -> None:
    state_path = skill_root / "templates" / "factory-state.json"
    state = load_json(state_path, findings)
    if not state:
        return
    if state.get("factory", {}).get("schema_version") != 2:
        fail(findings, "factory-state schema_version must be 2")

    for key in REQUIRED_TOP_LEVEL:
        if key not in state:
            fail(findings, f"missing-top-level-key: {key}")

    direction_lock = state.get("direction_lock", {})
    locked_items = direction_lock.get("locked_items", {}) if isinstance(direction_lock, dict) else {}
    for key in ["source_decision_ids", "source_report_ids", "handoff_message_ids"]:
        if key not in direction_lock:
            fail(findings, f"missing-direction-lock-field: {key}")
    for key in [
        "target_user",
        "user_job",
        "product_promise",
        "mvp_scope",
        "non_goals",
        "technical_approach",
        "moat_hypothesis",
        "accepted_risks",
    ]:
        if key not in locked_items:
            fail(findings, f"missing-direction-lock-item: {key}")

    gates = {gate.get("id") for gate in state.get("gates", []) if isinstance(gate, dict)}
    for gate_id in REQUIRED_GATES:
        if gate_id not in gates:
            fail(findings, f"missing-gate: {gate_id}")

    agents = {agent.get("id") for agent in state.get("agents", []) if isinstance(agent, dict)}
    for agent_id in REQUIRED_AGENTS:
        if agent_id not in agents:
            fail(findings, f"missing-agent: {agent_id}")

    report_sync = state.get("report_sync", {})
    for key in ["status", "latest_event_id", "monitor_status", "state_path"]:
        if key not in report_sync:
            fail(findings, f"missing-report-sync-field: {key}")

    harness_command = state.get("quality_harness", {}).get("harness_command", "")
    if "<skill-root>/scripts/verify_factory_run.py" not in harness_command:
        fail(findings, "harness-command must use <skill-root>/scripts/verify_factory_run.py placeholder")


def check_text(skill_root: Path, findings: list[str]) -> None:
    skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    if "description: Use when" not in skill_text.split("---", 2)[1]:
        fail(findings, "frontmatter description must start with Use when and describe triggers")
    for required in REQUIRED_SKILL_TEXT:
        if required not in skill_text:
            fail(findings, f"missing-skill-text: {required}")

    planning = (skill_root / "references" / "planning-intake.md").read_text(encoding="utf-8")
    for required in ["Idea Snapshot", "Discovery Council", "Option Matrix", "Direction Lock"]:
        if required not in planning:
            fail(findings, f"missing-planning-text: {required}")

    monitor = (skill_root / "references" / "factory-monitor.md").read_text(encoding="utf-8")
    for required in ["council_reports", "option_matrix", "direction_lock", "report_sync"]:
        if required not in monitor:
            fail(findings, f"missing-monitor-text: {required}")

    benchmark = (skill_root / "references" / "benchmark-rubric.md").read_text(encoding="utf-8")
    for required in ["Peer Set", "Scoring Dimensions", "Total score: 100"]:
        if required not in benchmark:
            fail(findings, f"missing-benchmark-text: {required}")

    dashboard = (skill_root / "templates" / "factory-dashboard.html").read_text(encoding="utf-8")
    for required in REQUIRED_DASHBOARD_TEXT:
        if required not in dashboard:
            fail(findings, f"missing-dashboard-text: {required}")

    openai_yaml = (skill_root / "agents" / "openai.yaml").read_text(encoding="utf-8")
    for required in ["display_name", "short_description", "default_prompt", "$vibe-coding-factory"]:
        if required not in openai_yaml:
            fail(findings, f"missing-openai-yaml-text: {required}")

    dashboard_v2 = skill_root / "templates" / "factory-dashboard-v2.html"
    if dashboard_v2.exists() and "?v=" in dashboard_v2.read_text(encoding="utf-8"):
        fail(findings, "dashboard-v2 redirect must not rely on cache-bust query strings")


def check_text_integrity(skill_root: Path, findings: list[str]) -> None:
    for path in sorted(skill_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".json", ".html", ".py"}:
            continue
        if path.name == "validate_factory_schema.py":
            continue
        text = path.read_text(encoding="utf-8")
        rel_path = path.relative_to(skill_root).as_posix()
        for marker in BAD_TEXT_MARKERS:
            if marker in text:
                fail(findings, f"text-integrity marker found in {rel_path}: {marker}")


def check_files(skill_root: Path, findings: list[str]) -> None:
    for rel_path in REQUIRED_FILES:
        if not (skill_root / rel_path).exists():
            fail(findings, f"missing-file: {rel_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate vibe-coding-factory discovery schema.")
    parser.add_argument("--skill-root", default=".", help="Path to the vibe-coding-factory skill root.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_root = Path(args.skill_root).resolve()
    findings: list[str] = []

    check_files(skill_root, findings)
    check_state(skill_root, findings)
    check_text(skill_root, findings)
    check_text_integrity(skill_root, findings)

    if findings:
        print("FAIL")
        for finding in findings:
            print(f"- {finding}")
        return 1

    print("PASS discovery workflow and state schema checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
