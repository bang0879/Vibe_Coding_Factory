import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LANGUAGE_MARKER = "Language: Korean by default for user-facing content"


class KoreanUserOutputTests(unittest.TestCase):
    def test_skill_defines_korean_user_facing_contract(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("User-Facing Korean Output Rule", skill)
        self.assertIn("Write user-facing decision prompts", skill)
        self.assertIn("implementation plans", skill)
        self.assertIn("Internal agent-to-agent messages", skill)
        self.assertIn("결정 필요", skill)
        self.assertIn("자동 진행", skill)

    def test_reporting_sync_uses_korean_primary_format(self) -> None:
        reporting = (ROOT / "references" / "reporting-sync.md").read_text(encoding="utf-8")

        self.assertIn("Use Korean by default", reporting)
        self.assertIn("결정 필요", reporting)
        self.assertIn("추천", reporting)
        self.assertIn("모니터 보기", reporting)
        self.assertIn("English fallback", reporting)

    def test_user_facing_templates_have_language_marker(self) -> None:
        templates = [
            "decision-brief.md",
            "direction-lock.md",
            "prd.md",
            "gtm.md",
            "design-brief.md",
            "implementation-plan.md",
            "requirements.md",
            "qa-evidence.md",
            "feasibility-report.md",
            "moat-strategy.md",
            "risk-register.md",
            "task-card.md",
        ]

        for rel in templates:
            with self.subTest(template=rel):
                text = (ROOT / "templates" / rel).read_text(encoding="utf-8")
                self.assertIn(LANGUAGE_MARKER, text)

    def test_runtime_adapters_preserve_language_contract(self) -> None:
        for rel in ["AGENTS.md", "adapters/claude-code/CLAUDE.md", "references/runtime-portability.md"]:
            with self.subTest(file=rel):
                text = (ROOT / rel).read_text(encoding="utf-8")
                self.assertIn("Korean by default", text)
                self.assertIn("JSON keys may stay English", text)


if __name__ == "__main__":
    unittest.main()
