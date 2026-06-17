#!/usr/bin/env python3
"""Create, refresh, and optionally open the Factory Monitor."""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import shutil
import sys
import webbrowser
from pathlib import Path
from typing import Any


def now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return data if isinstance(data, dict) else {}


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ensure_monitor(project_root: Path, skill_root: Path, state_path: Path, should_open: bool) -> dict[str, Any]:
    factory_dir = project_root / ".factory"
    factory_dir.mkdir(parents=True, exist_ok=True)

    template_path = skill_root / "templates" / "factory-dashboard.html"
    dashboard_path = factory_dir / "factory-dashboard.html"
    if not template_path.exists():
        raise SystemExit(f"dashboard template does not exist: {template_path}")
    shutil.copyfile(template_path, dashboard_path)

    dashboard_uri = dashboard_path.resolve().as_uri()
    opened = False
    if should_open:
        opened = bool(webbrowser.open(dashboard_uri))

    meta = {
        "project_root": str(project_root.resolve()),
        "dashboard_path": str(dashboard_path.resolve()),
        "template_path": str(template_path.resolve()),
        "dashboard_sha256": sha256(dashboard_path),
        "template_sha256": sha256(template_path),
        "state_path": str(state_path.resolve()),
        "server_port": "",
        "served_url": dashboard_uri,
        "opened": opened,
        "updated_at": now(),
    }
    (factory_dir / "monitor-meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (factory_dir / "monitor-url.txt").write_text(f"{dashboard_uri}\nproject_root={project_root.resolve()}\n", encoding="utf-8")

    state = load_state(state_path)
    report_sync = state.setdefault("report_sync", {})
    report_sync.update(
        {
            "monitor_status": "current",
            "monitor_url": dashboard_uri,
            "monitor_view": str(dashboard_path.resolve()),
            "monitor_opened_at": now(),
            "state_path": ".factory/factory-state.json",
            "failed_update_reason": "",
        }
    )
    monitor_health = state.setdefault("monitor_health", {})
    monitor_health.update(
        {
            "status": "current",
            "state_path": ".factory/factory-state.json",
            "dashboard_path": str(dashboard_path.resolve()),
            "monitor_url_path": ".factory/monitor-url.txt",
            "meta_path": ".factory/monitor-meta.json",
            "last_refresh_at": now(),
            "dashboard_sha256": meta["dashboard_sha256"],
            "template_sha256": meta["template_sha256"],
            "served_url": dashboard_uri,
            "served_matches_local": True,
            "stale_reason": "",
        }
    )
    save_state(state_path, state)
    return meta


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ensure the Vibe Coding Factory monitor exists and is surfaced.")
    parser.add_argument("--project-root", default=".", help="Project root.")
    parser.add_argument("--skill-root", default=str(Path(__file__).resolve().parents[1]), help="vibe-coding-factory skill root.")
    parser.add_argument("--state", default=".factory/factory-state.json", help="Factory state path.")
    parser.add_argument("--open", action="store_true", help="Try to open the dashboard in the host browser.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    project_root = Path(args.project_root).resolve()
    skill_root = Path(args.skill_root).resolve()
    state_path = Path(args.state)
    if not state_path.is_absolute():
        state_path = project_root / state_path
    meta = ensure_monitor(project_root, skill_root, state_path, args.open)
    if args.json:
        print(json.dumps(meta, ensure_ascii=False, indent=2))
    else:
        print(f"Monitor view: {meta['dashboard_path']}")
        print(f"Monitor URL: {meta['served_url']}")
        print(f"Opened: {meta['opened']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
