import json
import unittest
from pathlib import Path

from test_capability_realism import (
    base_contract,
    run_verify,
    valid_capability_contract,
    write_minimal_state,
)


ROOT = Path(__file__).resolve().parents[1]


def add_out_of_seed_scenario(contract: dict) -> None:
    contract["primary_scenarios"].append(
        {
            "id": "SCN-OUT-OF-SEED",
            "requirement_ids": ["REQ-001"],
            "given": "out-of-seed place or landmark outside preset chips",
            "when": "the user enters it as free text",
            "then": "the app normalizes it or reports an honest provider/data blocker",
            "evidence": "browser or provider adapter evidence",
            "status": "pending",
        }
    )


def live_capability_contract() -> dict:
    capability = valid_capability_contract()
    capability["mode"] = "live"
    capability["requires_live_data_or_api"] = True
    capability["external_dependencies"] = ["Kakao Local API"]
    capability["approved_fallbacks"] = []
    return capability


def valid_integration_contract() -> dict:
    return {
        "provider_candidates": ["Kakao Local API", "Naver Local Search API", "CatchTable"],
        "required_live_integrations": ["Kakao Local API"],
        "provider_docs_checked": [
            "https://developers.kakao.com/docs/latest/ko/local/dev-guide",
            "https://developers.naver.com/docs/serviceapi/search/local/local.md",
        ],
        "auth_env_vars": ["KAKAO_REST_API_KEY"],
        "rate_limit_policy": "Back off on provider throttling and show a retryable error state.",
        "cache_policy": "Cache place search responses briefly and label source freshness.",
        "terms_or_tos_constraints": [
            "Use official APIs or user-approved deep links only; do not scrape booking providers."
        ],
        "booking_mode": "provider_deeplink",
        "requires_final_user_confirmation": True,
        "completion_proof": [],
    }


class VenueAgentPlaybookTests(unittest.TestCase):
    def write_contract(self, project: Path, contract: dict) -> None:
        docs = project / "docs"
        docs.mkdir()
        (docs / "ACCEPTANCE_CONTRACT.json").write_text(json.dumps(contract), encoding="utf-8")

    def test_skill_loads_venue_agent_playbook(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        discovery = (ROOT / "references" / "discovery-council.md").read_text(encoding="utf-8")
        affordances = (ROOT / "references" / "domain-affordances.md").read_text(encoding="utf-8")
        playbook = (ROOT / "references" / "venue-agent-playbook.md").read_text(encoding="utf-8")

        self.assertIn("Venue And Reservation Agent Rule", skill)
        self.assertIn("venue-agent-playbook.md", skill)
        self.assertIn("venue-agent-playbook.md", discovery)
        self.assertIn("Venue And Reservation Agent Shortcut", affordances)
        self.assertIn("Kakao Local API", playbook)
        self.assertIn("Naver Local Search API", playbook)
        self.assertIn("CatchTable", playbook)
        self.assertIn("booking_mode", playbook)
        self.assertIn("confirmation proof", playbook)
        self.assertIn("Do not invent ratings", playbook)

    def test_acceptance_contract_template_has_integration_contract(self) -> None:
        template = json.loads((ROOT / "templates" / "acceptance-contract.json").read_text(encoding="utf-8"))

        self.assertIn("integration_contract", template)
        integration = template["integration_contract"]
        self.assertIn("provider_candidates", integration)
        self.assertIn("provider_docs_checked", integration)
        self.assertIn("auth_env_vars", integration)
        self.assertEqual(integration["booking_mode"], "not_applicable")
        self.assertTrue(integration["requires_final_user_confirmation"])

    def test_verify_requires_integration_contract_for_live_dependency(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            write_minimal_state(project)
            contract = base_contract()
            contract["capability_contract"] = live_capability_contract()
            add_out_of_seed_scenario(contract)
            self.write_contract(project, contract)

            result = run_verify(project)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("contract-integration-missing", result.stdout)

    def test_verify_fails_for_invalid_booking_mode(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            write_minimal_state(project)
            contract = base_contract()
            contract["capability_contract"] = valid_capability_contract()
            contract["integration_contract"] = valid_integration_contract()
            contract["integration_contract"]["booking_mode"] = "magic_bot_booking"
            add_out_of_seed_scenario(contract)
            self.write_contract(project, contract)

            result = run_verify(project)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("contract-booking-mode", result.stdout)

    def test_verify_fails_when_live_integration_lacks_docs(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            write_minimal_state(project)
            contract = base_contract()
            contract["capability_contract"] = live_capability_contract()
            contract["integration_contract"] = valid_integration_contract()
            contract["integration_contract"]["provider_docs_checked"] = []
            add_out_of_seed_scenario(contract)
            self.write_contract(project, contract)

            result = run_verify(project)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("contract-provider-docs-missing", result.stdout)

    def test_verify_fails_when_booking_lacks_user_confirmation(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            write_minimal_state(project)
            contract = base_contract()
            contract["capability_contract"] = valid_capability_contract()
            contract["integration_contract"] = valid_integration_contract()
            contract["integration_contract"]["requires_final_user_confirmation"] = False
            add_out_of_seed_scenario(contract)
            self.write_contract(project, contract)

            result = run_verify(project)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("contract-booking-user-confirmation", result.stdout)

    def test_verify_fails_when_completed_booking_lacks_proof(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            write_minimal_state(project)
            contract = base_contract()
            contract["capability_contract"] = live_capability_contract()
            contract["integration_contract"] = valid_integration_contract()
            contract["integration_contract"]["booking_mode"] = "official_api"
            contract["completion_status"]["overall"] = "passed"
            add_out_of_seed_scenario(contract)
            self.write_contract(project, contract)

            result = run_verify(project)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("contract-booking-completion-proof", result.stdout)

    def test_verify_accepts_valid_live_integration_contract(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            write_minimal_state(project)
            contract = base_contract()
            contract["capability_contract"] = live_capability_contract()
            contract["integration_contract"] = valid_integration_contract()
            add_out_of_seed_scenario(contract)
            self.write_contract(project, contract)

            result = run_verify(project)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
