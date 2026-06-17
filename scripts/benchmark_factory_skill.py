#!/usr/bin/env python3
"""Self-audit workflow rubric for vibe-coding-factory.

This script checks whether the local repository contains the workflow artifacts
that Vibe Coding Factory claims to provide. It is intentionally not a peer
benchmark and does not rank this project against named tools.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DIMENSIONS = [
    {
        "id": "product_discovery_direction_control",
        "weight": 15,
        "checks": [
            ("SKILL.md", "Discovery Council"),
            ("SKILL.md", "Direction Lock"),
            ("references/discovery-council.md", "Direction Lock Gate"),
            ("scripts/verify_factory_run.py", "direction-lock-source-decision"),
            ("scripts/verify_factory_run.py", "direction-lock-council-incomplete"),
        ],
    },
    {
        "id": "spec_artifact_discipline",
        "weight": 12,
        "checks": [
            ("templates/prd.md", "Direction Lock"),
            ("templates/gtm.md", "Direction Lock"),
            ("templates/design-brief.md", "Direction Lock"),
            ("templates/acceptance-contract.json", "primary_scenarios"),
            ("templates/acceptance-contract.json", "capability_contract"),
            ("templates/implementation-plan.md", "Implementation"),
            ("templates/implementation-plan.md", "Language: Korean by default for user-facing content"),
            ("templates/requirements.md", "Requirement"),
        ],
    },
    {
        "id": "task_decomposition_quality",
        "weight": 10,
        "checks": [
            ("templates/task-card.md", "allowed_files"),
            ("templates/task-card.md", "done_conditions"),
            ("templates/task-card.md", "verification"),
            ("templates/task-card.md", "requirement_ids"),
            ("SKILL.md", "Task Card Shape"),
        ],
    },
    {
        "id": "monitor_observability",
        "weight": 12,
        "checks": [
            ("templates/factory-state.json", '"report_sync"'),
            ("templates/factory-state.json", '"user_waiting_summary"'),
            ("templates/factory-state.json", '"monitor_view"'),
            ("templates/factory-state.json", '"monitor_health"'),
            ("templates/factory-dashboard.html", 'data-panel="handoffs"'),
            ("templates/factory-dashboard.html", 'data-panel="direction-lock"'),
            ("templates/factory-dashboard.html", "renderCouncilReports"),
            ("references/factory-monitor.md", "Stale Monitor Guard"),
            ("scripts/ensure_factory_monitor.py", "monitor-meta.json"),
            ("scripts/ensure_factory_monitor.py", "webbrowser.open"),
        ],
    },
    {
        "id": "deterministic_verification_harness",
        "weight": 12,
        "checks": [
            ("scripts/verify_factory_run.py", "def check_direction_lock"),
            ("scripts/verify_factory_run.py", "check_acceptance_contract"),
            ("scripts/verify_factory_run.py", "check_dashboard"),
            ("scripts/verify_factory_run.py", "app-files-before-direction-lock"),
            ("scripts/verify_factory_run.py", "user-wait-monitor-missing"),
            ("scripts/verify_factory_run.py", "user-wait-monitor-path-missing"),
            ("scripts/factory_preflight.py", "missing-factory-state"),
            ("scripts/factory_preflight.py", "direction-lock-not-approved"),
            ("scripts/validate_factory_schema.py", "BAD_TEXT_MARKERS"),
            ("scripts/benchmark_factory_skill.py", "benchmark_type"),
        ],
    },
    {
        "id": "agent_roles_handoffs",
        "weight": 10,
        "checks": [
            ("references/agent-roles.md", "Technical Feasibility Architect"),
            ("references/agent-roles.md", "Growth and Moat Strategist"),
            ("references/agent-roles.md", "Risk Critic"),
            ("scripts/update_factory_state.py", "append_message"),
            ("templates/factory-state.json", '"handoff_message_ids"'),
        ],
    },
    {
        "id": "product_quality_gates",
        "weight": 10,
        "checks": [
            ("references/product-quality.md", "Product Quality Gates"),
            ("references/product-quality.md", "Capability Realism Gate"),
            ("references/completion-harness.md", "Scenario Harness"),
            ("references/completion-harness.md", "out-of-seed"),
            ("references/cold-start-side-projects.md", "lightweight cold-start side projects"),
            ("references/cold-start-side-projects.md", "Completion Standard"),
            ("SKILL.md", "Consumer Appeal Reviewer"),
            ("SKILL.md", "input-driven"),
            ("SKILL.md", "No Silent Capability Downgrade Rule"),
            ("templates/qa-evidence.md", "Evidence"),
        ],
    },
    {
        "id": "revision_failure_loop_control",
        "weight": 7,
        "checks": [
            ("references/loop-rules.md", "fails 3 times"),
            ("SKILL.md", "reopened"),
            ("templates/factory-state.json", '"revision_loops"'),
            ("templates/factory-state.json", '"operator_alerts"'),
        ],
    },
    {
        "id": "skill_packaging_discoverability",
        "weight": 6,
        "checks": [
            ("SKILL.md", "description: Use when"),
            ("SKILL.md", "Preflight Stop Rule"),
            ("SKILL.md", "User-Wait Monitor Rule"),
            ("SKILL.md", "User-Facing Korean Output Rule"),
            ("README.md", "lightweight cold-start side projects"),
            ("agents/openai.yaml", "display_name"),
            ("agents/openai.yaml", "default_prompt"),
            ("references/benchmark-rubric.md", "Self-Audit Rubric"),
        ],
    },
    {
        "id": "external_evaluation_readiness",
        "weight": 6,
        "checks": [
            ("references/project-management.md", "worktree"),
            ("references/external-patterns.md", "GitHub"),
            ("references/runtime-portability.md", "Claude Code"),
            ("references/runtime-portability.md", "Korean by default"),
            ("AGENTS.md", "factory_preflight.py"),
            ("references/benchmark-rubric.md", "External Evaluation Plan"),
            ("references/benchmark-rubric.md", "No Peer Ranking"),
            ("scripts/benchmark_factory_skill.py", "limitations"),
        ],
    },
]

LIMITATIONS = [
    "This is a local self-audit, not an external benchmark.",
    "It checks repository artifacts and guardrails, not runtime coding quality.",
    "It does not compare against named peer projects unless their repositories are independently evaluated with the same harness.",
    "Evidence of real impact requires scenario suites, before/after case studies, and CI-backed fixtures.",
]


def read_text(root: Path, rel_path: str) -> str:
    path = root / rel_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8-sig")


def score_dimension(root: Path, dimension: dict[str, Any]) -> dict[str, Any]:
    checks = dimension["checks"]
    passed: list[str] = []
    failed: list[str] = []
    for rel_path, marker in checks:
        text = read_text(root, rel_path)
        label = f"{rel_path}::{marker}"
        if marker in text:
            passed.append(label)
        else:
            failed.append(label)
    ratio = len(passed) / len(checks) if checks else 0
    score = round(dimension["weight"] * ratio, 2)
    return {
        "id": dimension["id"],
        "weight": dimension["weight"],
        "score": score,
        "passed": passed,
        "failed": failed,
    }


def benchmark(root: Path) -> dict[str, Any]:
    dimensions = [score_dimension(root, item) for item in DIMENSIONS]
    total = round(sum(item["score"] for item in dimensions), 2)
    return {
        "benchmark_type": "self-audit",
        "score": total,
        "max_score": 100,
        "dimensions": dimensions,
        "limitations": LIMITATIONS,
    }


def print_text(result: dict[str, Any]) -> None:
    print(f"vibe-coding-factory self-audit: {result['score']:.2f}/100")
    print("type: self-audit (not a peer benchmark)")
    print("")
    print("Dimensions:")
    for item in result["dimensions"]:
        print(f"- {item['id']}: {item['score']:.2f}/{item['weight']}")
        if item["failed"]:
            for failed in item["failed"]:
                print(f"  missing: {failed}")
    print("")
    print("Limitations:")
    for limitation in result["limitations"]:
        print(f"- {limitation}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark vibe-coding-factory workflow maturity.")
    parser.add_argument("--skill-root", default=".", help="Path to the vibe-coding-factory skill root.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = benchmark(Path(args.skill_root).resolve())
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_text(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
