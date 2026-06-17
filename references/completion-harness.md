# Completion Harness

Use this harness whenever the factory is expected to produce a complete working product, not only a prototype.

## Intent Lock

Before implementation, convert the user's production intent into an acceptance contract:

- User job: what the user is trying to get done.
- Non-negotiable outcomes: what must work for the product to count as useful.
- Primary scenarios: 3-5 end-to-end flows the product must support.
- Data breadth: minimum realistic data/examples needed for the scenarios.
- Capability contract: whether the product is `live`, `user_data`, `local_functional`, or `partial`, plus approved fallbacks and open-input constraints.
- Design invariants: approved layout, hierarchy, component set, visual tokens, and states that must not degrade.
- Done means: observable behavior, not file existence or visual similarity alone.

If these are unclear, ask one targeted question or mark the run `partial`. Do not silently weaken the product goal.

If the approved product implies live data, broad real-world search, external APIs, user accounts, scraping, or open-ended input, do not replace it with fixed seed data without a user decision. Record any approved fallback in `capability_contract.approved_fallbacks`.

## Acceptance Contract File

For complete product requests, write `docs/ACCEPTANCE_CONTRACT.json` from `templates/acceptance-contract.json`.

The contract must contain:

- `product_intent`
- `requirements[]` with stable ids such as `REQ-001`
- `primary_scenarios[]` with stable ids such as `SCN-001`
- `capability_contract`
- `design_invariants`
- `data_breadth`
- `verification.real_entrypoint`
- `completion_status`

Task cards must reference the relevant `requirement_ids` and scenario ids. If a requirement has no task and no verification path, planning is not complete.

## Scenario Harness

For each primary scenario, define:

```text
SCENARIO <id>
GIVEN <initial data/state>
WHEN <user input/action>
THEN <visible output/result changes>
EVIDENCE <browser/test/command proof to collect>
```

Rules:

- Include at least one happy path, one contrasting input path, and one empty/error/edge path.
- For recommendation, comparison, generation, search, planning, or dashboard apps, include at least two contrasting input scenarios with different visible outputs.
- When any approved input is open-ended, include at least one out-of-seed or unlisted-input scenario. Example: a location, topic, customer, URL, or date range that is not one of the preset chips.
- For generated-output products, verify the output is derived from current inputs, not hard-coded copy.
- For dashboards/tools, verify a real state change, filter, selection, edit, save, export, or calculation.

## Design Parity Harness

After implementation, compare the rendered app to `docs/DESIGN_BRIEF.md`:

- Same first-screen structure.
- Same primary action and visual hierarchy.
- Same component inventory.
- Same density/spacing intent.
- Same responsive collapse behavior.
- Required states are present: empty, loading when relevant, selected, disabled, error/blocked, success.

If the implementation diverges from the approved concept, mark UX failed and reopen the design or implementation task. Do not report the app as complete.

## Completion Contract

The factory may mark a user-facing app task `done` only when all are true:

- Real app entrypoint exists outside `.factory/**`.
- The app opens in a browser or app runtime.
- Every primary scenario in the Scenario Harness passes.
- At least two input/state changes produce different visible outputs when the product is interactive.
- Data breadth meets the product category.
- Capability mode, input freedom, and approved fallbacks in `capability_contract` match the implemented UI and behavior.
- Open-ended inputs are not narrowed to a closed dropdown unless explicitly approved.
- Design parity passes against the approved brief.
- QA evidence records URL, actions, before/after outputs, files checked, commands run, and remaining risks.
- UX and Consumer Appeal pass without "rough scaffold", "toy data", or "generic template" findings.
- `scripts/verify_factory_run.py` passes for the active project.

If any required item is missing:

- Mark the task `reopened` or `failed`.
- Record the missing evidence in the Factory Monitor.
- Route the task back to the responsible agent.
- Mark the run `partial`, not `complete`, if the missing item cannot be fixed within the current task.

## Anti-Patterns

Reject these as incomplete:

- "buttons click" but no meaningful output changes.
- One hard-coded result disguised as generated output.
- A UI shell with no data model or state transitions.
- A live/API/open-world product silently downgraded to a local seed-data demo.
- A free-input requirement implemented as a tiny closed dropdown without approval.
- A design concept that is approved but not traceable in the rendered UI.
- A dashboard or mockup treated as the product.
- "looks good" QA with no scenario evidence.
- Completion reports that omit remaining broken flows.
