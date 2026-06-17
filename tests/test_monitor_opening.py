import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENSURE_MONITOR = ROOT / "scripts" / "ensure_factory_monitor.py"
VERIFY = ROOT / "scripts" / "verify_factory_run.py"
TEMPLATE_STATE = ROOT / "templates" / "factory-state.json"


class MonitorOpeningTests(unittest.TestCase):
    def test_ensure_monitor_creates_dashboard_and_updates_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            state_path = project / ".factory" / "factory-state.json"
            state_path.parent.mkdir()
            state_path.write_text(TEMPLATE_STATE.read_text(encoding="utf-8"), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(ENSURE_MONITOR),
                    "--project-root",
                    str(project),
                    "--skill-root",
                    str(ROOT),
                    "--state",
                    str(state_path),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )

            self.assertIn("factory-dashboard.html", result.stdout)
            dashboard = project / ".factory" / "factory-dashboard.html"
            self.assertTrue(dashboard.exists())

            state = json.loads(state_path.read_text(encoding="utf-8"))
            monitor_view = Path(state["report_sync"]["monitor_view"])
            self.assertTrue(monitor_view.exists())
            self.assertEqual(monitor_view.parent.name, ".factory")
            self.assertTrue(state["report_sync"]["monitor_opened_at"])

    def test_verify_fails_when_monitor_view_path_is_wrong(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            state_path = project / ".factory" / "factory-state.json"
            state_path.parent.mkdir()
            state = json.loads(TEMPLATE_STATE.read_text(encoding="utf-8"))
            state["approval_queue"] = [
                {"id": "dec-001", "type": "decision", "status": "waiting_user", "question": "Approve?"}
            ]
            state["report_sync"].update(
                {
                    "last_prompt_requires_user": True,
                    "latest_decision_id": "dec-001",
                    "latest_decision_summary": "Approve?",
                    "user_waiting_summary": "결정 필요: Approve?",
                    "monitor_status": "current",
                    "monitor_view": str(project.with_name(project.name + ".factory") / "factory-dashboard.html"),
                }
            )
            state_path.write_text(json.dumps(state), encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(VERIFY), "--project-root", str(project), "--mode", "state"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("user-wait-monitor-path-missing", result.stdout)

    def test_skill_requires_opening_monitor_before_waiting(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("ensure_factory_monitor.py", skill)
        self.assertIn("--open", skill)
        self.assertIn("Do not ask the user to decide from chat alone", skill)


if __name__ == "__main__":
    unittest.main()
