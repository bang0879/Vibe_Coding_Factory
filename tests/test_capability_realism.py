import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFY = ROOT / "scripts" / "verify_factory_run.py"


def write_minimal_state(project: Path) -> None:
    factory = project / ".factory"
    factory.mkdir()
    state = {
        "project": {"current_phase": "discovery"},
        "tasks": [],
        "artifacts": [],
        "direction_lock": {"status": "waiting_user"},
        "approval_queue": [],
        "report_sync": {},
    }
    (factory / "factory-state.json").write_text(json.dumps(state), encoding="utf-8")


def base_contract() -> dict:
    return {
        "version": 1,
        "product_intent": {
            "user_job": "find a real recommendation",
            "target_user": "solo user",
            "non_negotiable_outcomes": ["open input is preserved"],
            "done_means": "observable behavior",
        },
        "requirements": [
            {
                "id": "REQ-001",
                "user_story": "As a user, I want open input, so that presets do not trap me.",
                "acceptance_criteria": ["WHEN I enter a custom value THE SYSTEM SHALL handle it."],
                "priority": "must",
            }
        ],
        "primary_scenarios": [
            {
                "id": "SCN-001",
                "requirement_ids": ["REQ-001"],
                "given": "seeded choices exist",
                "when": "the user picks a preset",
                "then": "visible output changes",
                "evidence": "browser evidence",
                "status": "pending",
            }
        ],
        "design_invariants": valid_design_invariants(),
        "data_breadth": {"minimum_items": 12, "minimum_examples": 0, "rationale": "recommendation app"},
        "verification": {"real_entrypoint": "", "commands": []},
        "completion_status": {"overall": "pending"},
    }


def valid_capability_contract() -> dict:
    return {
        "mode": "local_functional",
        "requires_live_data_or_api": False,
        "external_dependencies": [],
        "approved_fallbacks": ["User approved clearly labeled local functional demo."],
        "forbidden_downgrades": [
            "Do not replace approved open-ended inputs with a closed preset list.",
            "Do not present seed data as live coverage.",
        ],
        "input_freedom": [
            {
                "field": "location",
                "expected_control": "free_text",
                "may_use_presets_as_shortcuts": True,
                "closed_set_allowed": False,
                "rationale": "The user may enter any area.",
            }
        ],
        "sample_data_policy": {
            "allowed": True,
            "must_label_sample_mode": True,
            "replacement_path": "app/data.js",
            "minimum_realistic_items_is_floor_not_ceiling": True,
        },
    }


def valid_design_invariants() -> dict:
    return {
        "first_screen_zones": ["search panel", "recommendation results", "summary report"],
        "primary_actions": ["search", "select venue", "generate notice"],
        "component_inventory": ["free text location input", "filter chips", "venue card", "report panel"],
        "state_inventory": ["empty", "selected", "success", "error"],
        "responsive_rules": ["results stack below filters on mobile"],
        "visual_tokens": {
            "background": "#f7f8fb",
            "surface": "#ffffff",
            "accent": "#2563eb",
            "radius": "8px",
        },
        "do_not_degrade": ["do not collapse into a generic card grid"],
        "fidelity_contract": {
            "approved_design_artifacts": ["docs/DESIGN_BRIEF.md"],
            "layout_fingerprint": "left filters, right ranked results, bottom report panel",
            "component_count_floor": 4,
            "must_keep_components": ["free text location input", "venue cards", "report panel"],
            "visual_quality_floor": "polished operational dashboard, not browser-default form",
            "forbidden_degradations": ["generic card grid", "browser-default form"],
            "screenshot_or_browser_evidence_required": True,
        },
    }


def run_verify(project: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VERIFY), "--project-root", str(project), "--mode", "state"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class CapabilityRealismTests(unittest.TestCase):
    def write_contract(self, project: Path, contract: dict) -> None:
        docs = project / "docs"
        docs.mkdir()
        (docs / "ACCEPTANCE_CONTRACT.json").write_text(json.dumps(contract), encoding="utf-8")

    def test_docs_define_no_silent_capability_downgrade(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        product_quality = (ROOT / "references" / "product-quality.md").read_text(encoding="utf-8")
        completion = (ROOT / "references" / "completion-harness.md").read_text(encoding="utf-8")

        self.assertIn("No Silent Capability Downgrade Rule", skill)
        self.assertIn("Minimum data breadth is a floor", skill)
        self.assertIn("Capability Realism Gate", product_quality)
        self.assertIn("out-of-seed", product_quality)
        self.assertIn("capability_contract", completion)

    def test_acceptance_contract_template_has_capability_contract(self) -> None:
        template = json.loads((ROOT / "templates" / "acceptance-contract.json").read_text(encoding="utf-8"))

        self.assertIn("capability_contract", template)
        self.assertIn("input_freedom", template["capability_contract"])
        self.assertIn("forbidden_downgrades", template["capability_contract"])
        self.assertTrue(any(item["id"] == "SCN-OUT-OF-SEED" for item in template["primary_scenarios"]))
        self.assertIn("fidelity_contract", template["design_invariants"])

    def test_verify_fails_when_design_fidelity_contract_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            write_minimal_state(project)
            contract = base_contract()
            contract["capability_contract"] = valid_capability_contract()
            contract["design_invariants"] = {"fidelity_contract": {}}
            contract["primary_scenarios"].append(
                {
                    "id": "SCN-OUT-OF-SEED",
                    "requirement_ids": ["REQ-001"],
                    "given": "out-of-seed location outside preset chips",
                    "when": "the user enters it",
                    "then": "the app handles it honestly",
                    "evidence": "browser evidence",
                    "status": "pending",
                }
            )
            self.write_contract(project, contract)

            result = run_verify(project)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("contract-design-fidelity", result.stdout)

    def test_verify_fails_without_capability_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            write_minimal_state(project)
            self.write_contract(project, base_contract())

            result = run_verify(project)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("contract-capability-missing", result.stdout)

    def test_verify_fails_when_open_input_lacks_out_of_seed_scenario(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            write_minimal_state(project)
            contract = base_contract()
            contract["capability_contract"] = valid_capability_contract()
            self.write_contract(project, contract)

            result = run_verify(project)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("contract-out-of-seed-scenario", result.stdout)

    def test_verify_fails_when_live_fallback_is_unapproved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            write_minimal_state(project)
            contract = base_contract()
            capability = valid_capability_contract()
            capability["requires_live_data_or_api"] = True
            capability["approved_fallbacks"] = []
            contract["capability_contract"] = capability
            contract["primary_scenarios"].append(
                {
                    "id": "SCN-OUT-OF-SEED",
                    "requirement_ids": ["REQ-001"],
                    "given": "out-of-seed location outside preset chips",
                    "when": "the user enters it",
                    "then": "the app handles it honestly",
                    "evidence": "browser evidence",
                    "status": "pending",
                }
            )
            self.write_contract(project, contract)

            result = run_verify(project)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("contract-live-fallback-unapproved", result.stdout)

    def test_verify_accepts_capability_contract_with_out_of_seed_scenario(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            write_minimal_state(project)
            contract = base_contract()
            contract["capability_contract"] = valid_capability_contract()
            contract["primary_scenarios"].append(
                {
                    "id": "SCN-OUT-OF-SEED",
                    "requirement_ids": ["REQ-001"],
                    "given": "out-of-seed location outside preset chips",
                    "when": "the user enters it",
                    "then": "the app handles it honestly",
                    "evidence": "browser evidence",
                    "status": "pending",
                }
            )
            self.write_contract(project, contract)

            result = run_verify(project)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
