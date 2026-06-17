import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UPDATER = ROOT / "scripts" / "update_factory_state.py"
VERIFY = ROOT / "scripts" / "verify_factory_run.py"
TEMPLATE = ROOT / "templates" / "factory-state.json"


class DecisionMonitorReportingTests(unittest.TestCase):
    def test_skill_requires_monitor_when_waiting_for_user(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        reporting = (ROOT / "references" / "reporting-sync.md").read_text(encoding="utf-8")

        self.assertIn("User-Wait Monitor Rule", skill)
        self.assertIn("open or surface the monitor", skill)
        self.assertIn("Decision summary", skill)
        self.assertIn("User-Wait Monitor Rule", reporting)
        self.assertIn("Monitor view", reporting)

    def test_state_template_has_user_wait_monitor_fields(self) -> None:
        state = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        report_sync = state["report_sync"]

        self.assertIn("last_prompt_requires_user", report_sync)
        self.assertIn("latest_decision_summary", report_sync)
        self.assertIn("user_waiting_summary", report_sync)
        self.assertIn("monitor_view", report_sync)
        self.assertIn("monitor_opened_at", report_sync)

    def test_decision_helper_populates_monitor_report_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            state_path = project / ".factory" / "factory-state.json"
            state_path.parent.mkdir()
            state_path.write_text(TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    str(UPDATER),
                    "--state",
                    str(state_path),
                    "--monitor-status",
                    "current",
                    "decision",
                    "--question",
                    "방향을 A로 잠글까요?",
                    "--recommended",
                    "A",
                    "--option",
                    "A: 가장 빠른 MVP",
                    "--option",
                    "B: 더 예쁜 MVP",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            self.assertIn("evt", result.stdout)

            state = json.loads(state_path.read_text(encoding="utf-8"))
            report_sync = state["report_sync"]
            self.assertTrue(report_sync["last_prompt_requires_user"])
            self.assertIn("방향을 A로 잠글까요?", report_sync["latest_decision_summary"])
            self.assertIn("결정 필요", report_sync["user_waiting_summary"])
            self.assertIn("모니터 보기", report_sync["user_waiting_summary"])
            self.assertTrue(report_sync["monitor_view"])

    def test_verify_fails_when_user_waits_without_monitor_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            state_path = project / ".factory" / "factory-state.json"
            state_path.parent.mkdir()
            state = json.loads(TEMPLATE.read_text(encoding="utf-8"))
            state["approval_queue"] = [
                {"id": "dec-001", "type": "decision", "status": "waiting_user", "question": "Approve?"}
            ]
            state["report_sync"]["last_prompt_requires_user"] = True
            state["report_sync"]["latest_decision_id"] = "dec-001"
            state["report_sync"]["latest_decision_summary"] = ""
            state["report_sync"]["monitor_view"] = ""
            state_path.write_text(json.dumps(state), encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(VERIFY), "--project-root", str(project), "--mode", "state"],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("user-wait-monitor-missing", result.stdout)


if __name__ == "__main__":
    unittest.main()
