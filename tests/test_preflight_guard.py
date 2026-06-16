import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREFLIGHT = ROOT / "scripts" / "factory_preflight.py"
VERIFY = ROOT / "scripts" / "verify_factory_run.py"


def run_script(script: Path, project_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), "--project-root", str(project_root), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def write_state(project_root: Path, direction_status: str = "waiting_user") -> None:
    factory = project_root / ".factory"
    factory.mkdir()
    state = {
        "project": {"current_phase": "discovery"},
        "discovery": {"status": "done", "idea_snapshot": {"raw_idea": "lunch app"}},
        "council_reports": [],
        "option_matrix": [],
        "direction_lock": {"status": direction_status, "locked_items": {}},
        "tasks": [],
        "artifacts": [],
        "operator_alerts": [],
    }
    (factory / "factory-state.json").write_text(json.dumps(state), encoding="utf-8")


class PreflightGuardTests(unittest.TestCase):
    def test_preflight_blocks_app_files_without_factory_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "app").mkdir()
            (project / "app" / "index.html").write_text("<button>Mock</button>", encoding="utf-8")

            result = run_script(PREFLIGHT, project)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing-factory-state", result.stdout)
            self.assertIn("app-files-before-direction-lock", result.stdout)

    def test_preflight_blocks_app_files_before_direction_lock(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            write_state(project, "waiting_user")
            (project / "src").mkdir()
            (project / "src" / "App.tsx").write_text("export default function App(){return null}", encoding="utf-8")

            result = run_script(PREFLIGHT, project)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("direction-lock-not-approved", result.stdout)
            self.assertIn("app-files-before-direction-lock", result.stdout)

    def test_verify_run_flags_app_files_before_direction_lock(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            write_state(project, "waiting_user")
            (project / "components").mkdir()
            (project / "components" / "Mockup.tsx").write_text("export const Mockup = () => null", encoding="utf-8")

            result = run_script(VERIFY, project, "--mode", "state")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("app-files-before-direction-lock", result.stdout)

    def test_skill_mentions_preflight_as_first_action(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("Preflight Stop Rule", skill)
        self.assertIn("factory_preflight.py", skill)
        self.assertIn("lightweight cold-start", skill)


if __name__ == "__main__":
    unittest.main()
