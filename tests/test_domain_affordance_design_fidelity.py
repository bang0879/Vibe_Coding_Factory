import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DomainAffordanceDesignFidelityTests(unittest.TestCase):
    def test_skill_requires_domain_affordance_discovery(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        discovery = (ROOT / "references" / "discovery-council.md").read_text(encoding="utf-8")
        affordances = (ROOT / "references" / "domain-affordances.md").read_text(encoding="utf-8")

        self.assertIn("Domain Affordance Discovery Rule", skill)
        self.assertIn("candidate_capabilities[]", skill)
        self.assertIn("candidate_capabilities[]", discovery)
        self.assertIn("회식", affordances)
        self.assertIn("지도/장소 자동완성", affordances)
        self.assertIn("Naver/Kakao/Google Maps API", affordances)

    def test_decision_brief_and_state_track_candidate_capabilities(self) -> None:
        decision_brief = (ROOT / "templates" / "decision-brief.md").read_text(encoding="utf-8")
        state = json.loads((ROOT / "templates" / "factory-state.json").read_text(encoding="utf-8"))

        self.assertIn("Candidate Capabilities", decision_brief)
        self.assertIn("Needs approval", decision_brief)
        self.assertIn("candidate_capabilities", state)

    def test_design_fidelity_contract_is_required_by_docs(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        design_studio = (ROOT / "references" / "design-studio.md").read_text(encoding="utf-8")
        product_quality = (ROOT / "references" / "product-quality.md").read_text(encoding="utf-8")
        design_brief = (ROOT / "templates" / "design-brief.md").read_text(encoding="utf-8")

        self.assertIn("Design Fidelity Lock Rule", skill)
        self.assertIn("Design Fidelity Lock", product_quality)
        self.assertIn("layout fingerprint", design_studio)
        self.assertIn("browser evidence or screenshots", design_studio)
        self.assertIn("Design Fidelity Contract", design_brief)

    def test_acceptance_contract_has_design_fidelity_fields(self) -> None:
        contract = json.loads((ROOT / "templates" / "acceptance-contract.json").read_text(encoding="utf-8"))
        fidelity = contract["design_invariants"]["fidelity_contract"]

        self.assertIn("layout_fingerprint", fidelity)
        self.assertIn("must_keep_components", fidelity)
        self.assertIn("forbidden_degradations", fidelity)
        self.assertTrue(fidelity["screenshot_or_browser_evidence_required"])


if __name__ == "__main__":
    unittest.main()
