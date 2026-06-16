#!/usr/bin/env python3
"""Heuristic workflow-maturity benchmark for vibe-coding-factory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PEER_BASELINES = {
    "BMAD Method": 91,
    "vibe-coding-factory target": 90,
    "GitHub Spec Kit": 88,
    "OpenHands": 86,
    "SWE-agent": 82,
    "Task Master": 78,
    "Aider": 76,
}


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
            ("templates/implementation-plan.md", "Implementation"),
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
            ("templates/factory-state.json", '"monitor_health"'),
            ("templates/factory-dashboard.html", 'data-panel="handoffs"'),
            ("templates/factory-dashboard.html", 'data-panel="direction-lock"'),
            ("templates/factory-dashboard.html", "renderCouncilReports"),
            ("references/factory-monitor.md", "Stale Monitor Guard"),
        ],
    },
    {
        "id": "deterministic_verification_harness",
        "weight": 12,
        "checks": [
            ("scripts/verify_factory_run.py", "def check_direction_lock"),
            ("scripts/verify_factory_run.py", "check_acceptance_contract"),
            ("scripts/verify_factory_run.py", "check_dashboard"),
            ("scripts/validate_factory_schema.py", "BAD_TEXT_MARKERS"),
            ("scripts/benchmark_factory_skill.py", "PEER_BASELINES"),
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
            ("references/completion-harness.md", "Scenario Harness"),
            ("SKILL.md", "Consumer Appeal Reviewer"),
            ("SKILL.md", "input-driven"),
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
            ("agents/openai.yaml", "display_name"),
            ("agents/openai.yaml", "default_prompt"),
            ("references/benchmark-rubric.md", "Benchmark Rubric"),
        ],
    },
    {
        "id": "external_integration_benchmark_evidence",
        "weight": 6,
        "checks": [
            ("references/project-management.md", "worktree"),
            ("references/external-patterns.md", "GitHub"),
            ("references/benchmark-rubric.md", "Peer Set"),
            ("scripts/benchmark_factory_skill.py", "PEER_BASELINES"),
        ],
    },
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
    peers = dict(PEER_BASELINES)
    peers["vibe-coding-factory local"] = total
    ranking = sorted(peers.items(), key=lambda item: item[1], reverse=True)
    rank = [name for name, _score in ranking].index("vibe-coding-factory local") + 1
    return {
        "benchmark_type": "heuristic workflow maturity, not runtime coding benchmark",
        "score": total,
        "max_score": 100,
        "rank": rank,
        "peer_count": len(ranking),
        "dimensions": dimensions,
        "peer_baselines": PEER_BASELINES,
        "ranking": [{"name": name, "score": score} for name, score in ranking],
    }


def print_text(result: dict[str, Any]) -> None:
    print(f"vibe-coding-factory benchmark: {result['score']:.2f}/100")
    print(f"rank: {result['rank']}/{result['peer_count']} ({result['benchmark_type']})")
    print("")
    print("Dimensions:")
    for item in result["dimensions"]:
        print(f"- {item['id']}: {item['score']:.2f}/{item['weight']}")
        if item["failed"]:
            for failed in item["failed"]:
                print(f"  missing: {failed}")
    print("")
    print("Peer ranking:")
    for item in result["ranking"]:
        print(f"- {item['name']}: {item['score']}")


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
