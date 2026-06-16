#!/usr/bin/env python3
"""Preflight guard for Vibe Coding Factory runs.

Use before implementation work starts. The script intentionally blocks app code
creation until factory state exists and Direction Lock is approved or explicitly
skipped by the user.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


APP_DIRS = {"app", "src", "components", "pages", "views", "routes"}
APP_SUFFIXES = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte"}
IGNORED_DIRS = {".git", ".factory", "node_modules", "__pycache__", ".next", "dist", "build"}
APPROVED_LOCK_STATUSES = {"approved", "locked", "skipped_by_user"}


class Finding:
    def __init__(self, level: str, code: str, message: str) -> None:
        self.level = level
        self.code = code
        self.message = message


def load_state(path: Path, findings: list[Finding]) -> dict[str, Any] | None:
    if not path.exists():
        findings.append(Finding("fail", "missing-factory-state", f"factory state not found: {path}"))
        return None
    try:
        state = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        findings.append(Finding("fail", "invalid-factory-state", f"factory state is invalid JSON: {exc}"))
        return None
    if not isinstance(state, dict):
        findings.append(Finding("fail", "invalid-factory-state", "factory state must be a JSON object"))
        return None
    return state


def is_ignored(path: Path, root: Path) -> bool:
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        return True
    return any(part in IGNORED_DIRS for part in rel_parts)


def discover_app_files(root: Path) -> list[str]:
    hits: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or is_ignored(path, root):
            continue
        rel = path.relative_to(root)
        parts = rel.parts
        if not parts:
            continue
        under_app_dir = parts[0] in APP_DIRS
        root_entry = len(parts) == 1 and path.name.lower() in {"index.html", "main.jsx", "main.tsx", "app.jsx", "app.tsx"}
        if (under_app_dir or root_entry) and path.suffix.lower() in APP_SUFFIXES:
            hits.append(rel.as_posix())
    return sorted(hits)


def direction_status(state: dict[str, Any] | None) -> str:
    if not isinstance(state, dict):
        return ""
    direction_lock = state.get("direction_lock")
    if not isinstance(direction_lock, dict):
        return ""
    return str(direction_lock.get("status", "")).strip().lower()


def check_before_implementation(project_root: Path, state_path: Path, findings: list[Finding]) -> None:
    state = load_state(state_path, findings)
    app_files = discover_app_files(project_root)
    status = direction_status(state)

    if status not in APPROVED_LOCK_STATUSES:
        findings.append(
            Finding(
                "fail",
                "direction-lock-not-approved",
                f"Direction Lock must be approved or skipped_by_user before implementation; got {status or 'missing'}",
            )
        )

    if app_files and status not in APPROVED_LOCK_STATUSES:
        findings.append(
            Finding(
                "fail",
                "app-files-before-direction-lock",
                "App files exist before Direction Lock: " + ", ".join(app_files[:12]),
            )
        )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Vibe Coding Factory preflight checks.")
    parser.add_argument("--project-root", default=".", help="Project root to inspect.")
    parser.add_argument("--state", default=".factory/factory-state.json", help="Factory state JSON path.")
    parser.add_argument(
        "--stage",
        choices=("before-implementation",),
        default="before-implementation",
        help="Preflight stage to check.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    project_root = Path(args.project_root).resolve()
    state_path = Path(args.state)
    if not state_path.is_absolute():
        state_path = project_root / state_path

    findings: list[Finding] = []
    check_before_implementation(project_root, state_path, findings)

    failed = any(item.level == "fail" for item in findings)
    if args.json:
        print(
            json.dumps(
                {
                    "ok": not failed,
                    "stage": args.stage,
                    "project_root": str(project_root),
                    "findings": [item.__dict__ for item in findings],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print("PASS factory preflight" if not failed else "FAIL factory preflight")
        for item in findings:
            print(f"[{item.level.upper()}] {item.code}: {item.message}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
