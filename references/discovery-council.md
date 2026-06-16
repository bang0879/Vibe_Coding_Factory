# Discovery Council

Use Discovery Council whenever the user gives a raw product idea, broad app request, business-sensitive feature, or any request likely to waste work if Codex assumes the direction.

## Goal

Make the factory report before it builds. The council turns a rough idea into grounded options, then asks the user to approve the direction.

## Council Roles

### Product Strategist

Report:

- Target users and likely early adopter segment.
- Job-to-be-done.
- Problem severity and why now.
- MVP scope candidates.
- Non-goals and scope traps.
- Success metrics.

### Technical Feasibility Architect

Report:

- Feasible parts.
- Technically hard, unavailable, or risky parts.
- Workarounds and degraded modes.
- Stack and integration constraints.
- Data/API requirements.
- Security and privacy constraints.
- Estimated implementation difficulty.

### Growth and Moat Strategist

Report:

- Positioning.
- Acquisition channel hypotheses.
- Activation and retention loop.
- Monetization or conversion path.
- Differentiators and moat ideas.
- Business assumptions to validate.

### UX Strategist

Report:

- First-use flow.
- Primary user action.
- Information architecture.
- Trust, onboarding, and empty-state needs.
- Design posture and product feel.
- User-facing complexity risks.

### Risk Critic

Report:

- Legal, privacy, safety, and security risks.
- Data quality and operational risks.
- Rework risks caused by ambiguous direction.
- Hidden scope or dependency traps.
- Blocking questions.

### Planner

Report:

- Viable build paths.
- Recommended sequence.
- Dependencies and unknowns.
- What can be deferred safely.
- What must be decided before PRD or implementation.

## Report Shape

Use this object shape in `council_reports[]`:

```json
{
  "id": "rpt-001",
  "agent": "technical-feasibility-architect",
  "status": "done",
  "verdict": "watch",
  "summary": "Core flow is feasible, but calendar sync needs fallback behavior.",
  "top_findings": [],
  "opportunities": [],
  "risks": [],
  "questions_for_user": [],
  "recommended_next_action": "",
  "artifact_path": "docs/FEASIBILITY_REPORT.md",
  "created_at": ""
}
```

Verdict values:

- `promising`: strong path with normal risk.
- `watch`: viable with risks or assumptions to track.
- `risky`: likely to waste work unless narrowed.
- `block`: cannot proceed without a decision or external dependency.

## Option Matrix

After reports, create `option_matrix[]`.

Each option:

```json
{
  "id": "opt-a",
  "label": "Focused MVP",
  "status": "recommended",
  "target_user": "",
  "user_job": "",
  "mvp_scope": [],
  "differentiator": "",
  "moat_hypothesis": "",
  "technical_path": "",
  "workarounds": [],
  "excluded_scope": [],
  "risks": [],
  "difficulty": "medium",
  "why_choose": "",
  "why_not": ""
}
```

Use 2-3 options unless the direction is already clearly chosen.

## Direction Lock Gate

Do not proceed to final PRD/GTM/design handoff, task decomposition, or implementation until Direction Lock passes.

Direction Lock passes when:

- User selects or approves a direction.
- `docs/DIRECTION_LOCK.md` exists.
- `direction_lock.status` is `approved` or `skipped_by_user`.
- `direction_lock.locked_items` covers target user, user job, MVP scope, non-goals, technical approach, moat hypothesis, and accepted risks.
- A selected decision in `decisions[]` references the lock.
- A `messages[]` entry hands the lock to planning.

## Skip Policy

If the user explicitly says to skip discovery:

1. Set `direction_lock.status` to `skipped_by_user`.
2. Record `operator_alerts[]` with the skipped discovery risk.
3. Continue only with the user's explicit scope.
4. Keep implementation freeze disabled only for that approved scope.

Do not infer skip from urgency or simplicity.
