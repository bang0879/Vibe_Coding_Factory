import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8").lower()


class RuntimePortabilityTests(unittest.TestCase):
    def test_skill_no_longer_claims_codex_only_runtime(self) -> None:
        skill = read("SKILL.md")

        self.assertNotIn("codex-only", skill)
        self.assertIn("runtime-neutral", skill)
        self.assertIn("codex host", skill)

    def test_repository_exposes_non_codex_entrypoints(self) -> None:
        readme = read("README.md")

        self.assertIn("runtime portability", readme)
        self.assertIn("claude code", readme)
        self.assertTrue((ROOT / "AGENTS.md").exists())
        self.assertTrue((ROOT / "adapters" / "claude-code" / "CLAUDE.md").exists())


if __name__ == "__main__":
    unittest.main()
