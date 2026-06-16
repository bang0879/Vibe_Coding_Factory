# Task Card

id:
title:
difficulty: low
status: pending

goal:

requirement_ids:
- REQ-001

scenario_ids:
- SCN-001

allowed_files:

branch_name:
worktree_path:
issue_id:

agent_flow:
- engineer
- qa-tester
- ux-checker
- consumer-appeal-reviewer
- scope-auditor

agent_steps:
- agent:
  persona:
  did:
  output:
  artifacts:
  handoff_to:
  handoff_summary:
  evidence:
  status:

checklist:
- [ ] 

done_conditions:
- [ ] 

verification:

app_entrypoint:
qa_evidence_path: docs/QA_EVIDENCE.md
harness_command: python vibe-coding-factory/scripts/verify_factory_run.py --project-root . --mode all

scenario_harness:
- id:
  requirement_ids:
  - REQ-001
  given:
  when:
  then:
  evidence:
  status:

design_parity:
- [ ] first-screen structure matches approved brief
- [ ] component inventory matches approved brief
- [ ] primary action and hierarchy match approved brief
- [ ] required states are implemented

completion_contract:
- [ ] real app entrypoint exists outside .factory
- [ ] scenario harness passed
- [ ] input/state changes produce visible output changes
- [ ] design parity passed
- [ ] QA evidence recorded
- [ ] UX and Consumer Appeal passed
- [ ] Factory Harness passed

fresh_review:
- reviewer:
  scope:
  findings:
  status:

agent_owner:

notes:
