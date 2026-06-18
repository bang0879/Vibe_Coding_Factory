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


STATE_SCRIPT_START = '<script id="fallback-state" type="application/json">'
STATE_SCRIPT_END = "</script>"
DOCUMENTS_SCRIPT_START = '<script id="fallback-documents" type="application/json">'
DOCUMENTS_SCRIPT_END = "</script>"
DOCUMENT_SUFFIXES = {".md", ".markdown", ".txt", ".json", ".yaml", ".yml"}
MAX_EMBEDDED_DOCUMENT_BYTES = 256 * 1024


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


def load_template_state(skill_root: Path) -> dict[str, Any]:
    template_state = skill_root / "templates" / "factory-state.json"
    if not template_state.exists():
        return {}
    data = json.loads(template_state.read_text(encoding="utf-8-sig"))
    return data if isinstance(data, dict) else {}


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def script_safe_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2).replace("</", "<\\/")


def replace_json_script(text: str, start_marker: str, end_marker: str, data: Any, missing_message: str) -> str:
    start = text.find(start_marker)
    if start == -1:
        raise SystemExit(missing_message)
    json_start = start + len(start_marker)
    end = text.find(end_marker, json_start)
    if end == -1:
        raise SystemExit(f"{missing_message}: script is not closed")
    return text[:json_start] + "\n" + script_safe_json(data) + "\n" + text[end:]


def normalize_doc_path(project_root: Path, path_text: str) -> str:
    text = str(path_text or "").strip().strip('"')
    if text.startswith("file:///"):
        text = text[8:]
    text = text.replace("\\", "/")
    candidate = Path(text)
    if candidate.is_absolute():
        try:
            return candidate.resolve().relative_to(project_root).as_posix()
        except ValueError:
            parts = candidate.parts
            if "docs" in parts:
                index = parts.index("docs")
                return "/".join(parts[index:])
            return ""
    normalized = text.lstrip("./")
    marker = "/docs/"
    lowered = normalized.lower()
    if marker in lowered:
        return normalized[lowered.index(marker) + 1 :]
    return normalized


def collect_state_doc_paths(state: dict[str, Any]) -> set[str]:
    paths: set[str] = set()

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {"path", "artifact_path", "qa_evidence_path"} and isinstance(child, str):
                    paths.add(child)
                elif key in {"related_docs", "artifact_paths", "artifacts"}:
                    for item in child if isinstance(child, list) else [child]:
                        if isinstance(item, str):
                            paths.add(item)
                else:
                    visit(child)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(state)
    return paths


def collect_document_snapshots(project_root: Path, state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    documents: dict[str, dict[str, Any]] = {}
    candidate_paths = {
        "docs/DECISION_BRIEF.md",
        "docs/DIRECTION_LOCK.md",
        "docs/PRD.md",
        "docs/GTM.md",
        "docs/REQUIREMENTS.md",
        "docs/IMPLEMENTATION_PLAN.md",
        "docs/QA_EVIDENCE.md",
        "docs/DESIGN_BRIEF.md",
        "docs/ACCEPTANCE_CONTRACT.json",
    }
    candidate_paths.update(collect_state_doc_paths(state))
    docs_dir = project_root / "docs"
    if docs_dir.exists():
        for path in docs_dir.rglob("*"):
            if path.is_file() and path.suffix.lower() in DOCUMENT_SUFFIXES:
                candidate_paths.add(path.relative_to(project_root).as_posix())

    for raw_path in sorted(candidate_paths):
        rel_path = normalize_doc_path(project_root, raw_path)
        if not rel_path or ".." in Path(rel_path).parts:
            continue
        path = project_root / rel_path
        if not path.exists() or not path.is_file() or path.suffix.lower() not in DOCUMENT_SUFFIXES:
            continue
        size = path.stat().st_size
        if size > MAX_EMBEDDED_DOCUMENT_BYTES:
            content = f"[Document not embedded because it is larger than {MAX_EMBEDDED_DOCUMENT_BYTES} bytes.]"
        else:
            content = path.read_text(encoding="utf-8-sig", errors="replace")
        item = {
            "path": rel_path,
            "absolute_path": str(path.resolve()),
            "updated_at": _dt.datetime.fromtimestamp(path.stat().st_mtime, _dt.timezone.utc).isoformat(),
            "bytes": size,
            "content": content,
        }
        documents[rel_path] = item
        documents[str(path.resolve()).replace("\\", "/")] = item
    return documents


def embed_monitor_snapshots(dashboard_path: Path, state: dict[str, Any], documents: dict[str, Any]) -> None:
    text = dashboard_path.read_text(encoding="utf-8")
    snapshot = dict(state)
    snapshot["__embedded_snapshot"] = True
    text = replace_json_script(
        text,
        STATE_SCRIPT_START,
        STATE_SCRIPT_END,
        snapshot,
        "dashboard template is missing fallback-state script",
    )
    text = replace_json_script(
        text,
        DOCUMENTS_SCRIPT_START,
        DOCUMENTS_SCRIPT_END,
        documents,
        "dashboard template is missing fallback-documents script",
    )
    dashboard_path.write_text(text, encoding="utf-8")


def embed_state_snapshot(dashboard_path: Path, state: dict[str, Any], documents: dict[str, Any] | None = None) -> None:
    embed_monitor_snapshots(dashboard_path, state, documents or {})


def ensure_monitor(project_root: Path, skill_root: Path, state_path: Path, should_open: bool) -> dict[str, Any]:
    factory_dir = project_root / ".factory"
    factory_dir.mkdir(parents=True, exist_ok=True)

    template_path = skill_root / "templates" / "factory-dashboard.html"
    dashboard_path = factory_dir / "factory-dashboard.html"
    if not template_path.exists():
        raise SystemExit(f"dashboard template does not exist: {template_path}")
    shutil.copyfile(template_path, dashboard_path)

    state = load_state(state_path) or load_template_state(skill_root)

    dashboard_uri = dashboard_path.resolve().as_uri()

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
            "dashboard_sha256": "embedded-state-snapshot",
            "template_sha256": sha256(template_path),
            "served_url": dashboard_uri,
            "served_matches_local": True,
            "embedded_state_snapshot": True,
            "embedded_document_snapshot": True,
            "stale_reason": "",
        }
    )
    save_state(state_path, state)
    documents = collect_document_snapshots(project_root, state)
    embed_state_snapshot(dashboard_path, state, documents)
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
        "embedded_state_snapshot": True,
        "embedded_document_snapshot": True,
        "embedded_document_count": len({item["path"] for item in documents.values()}),
        "updated_at": now(),
    }
    (factory_dir / "monitor-meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (factory_dir / "monitor-url.txt").write_text(f"{dashboard_uri}\nproject_root={project_root.resolve()}\n", encoding="utf-8")
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
