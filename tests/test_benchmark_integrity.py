import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "benchmark_factory_skill.py"


class BenchmarkIntegrityTests(unittest.TestCase):
    def run_benchmark(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--skill-root", str(ROOT), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    def test_text_output_is_self_audit_not_peer_ranking(self) -> None:
        result = self.run_benchmark()
        output = result.stdout.lower()

        self.assertIn("self-audit", output)
        self.assertNotIn("rank:", output)
        self.assertNotIn("peer ranking", output)
        self.assertNotIn("bmad method", output)
        self.assertNotIn("github spec kit", output)
        self.assertNotIn("openhands", output)

    def test_json_output_has_no_hand_written_peer_scores(self) -> None:
        result = self.run_benchmark("--json")
        payload = json.loads(result.stdout)

        self.assertEqual(payload["benchmark_type"], "self-audit")
        self.assertNotIn("ranking", payload)
        self.assertNotIn("peer_baselines", payload)
        self.assertNotIn("rank", payload)
        self.assertTrue(payload["limitations"])


if __name__ == "__main__":
    unittest.main()

