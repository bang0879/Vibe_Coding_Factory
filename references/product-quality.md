# Product Quality Gates

Use these gates for any factory task that claims to build a real app, product surface, dashboard, game, workflow tool, or user-facing feature.

## Minimum App Standard

The output must be a usable app, not a presentation of an app.

Require all of:

- A real app entrypoint outside `.factory/**`.
- Local state, app logic, or backend/API behavior that changes visible output.
- Enough realistic data to exercise the product. Default minimum: 12 items for recommendation/search/list apps, 5 rows for tables, 3 complete examples for generated-output flows, unless the domain clearly needs fewer.
- Empty, partial, success, and error or blocked states where relevant.
- Mobile and desktop layouts that do not collapse into broken cards.
- Controls with disabled, selected, loading, and result states when applicable.
- A Scenario Harness from `references/completion-harness.md` with evidence for each primary flow.
- A passing executable Factory Harness result from `references/factory-harness.md`.

Reject as incomplete:

- Static HTML that only looks like a product.
- A single hard-coded result dressed as output.
- Controls that do not change state.
- A factory monitor, screenshot, or design mockup used as the app.
- Sample data so tiny that the user's main choice has no meaningful range.
- A real-world or open-ended capability silently downgraded into a closed seed-data demo.

## Capability Realism Gate

Before implementation, classify the app's capability mode in `docs/ACCEPTANCE_CONTRACT.json`:

- `live`: the app uses real integration, live data, or a real backend/API.
- `user_data`: the app works from user-provided files, pasted data, or configured local data.
- `local_functional`: the app is intentionally local with realistic sample data and clearly labeled limits.
- `partial`: useful behavior exists, but promised real-world capability remains incomplete.

Rules:

- Do not use `local_functional` or `partial` as a silent substitute for `live`. Ask the user first and record the approved fallback.
- Minimum data breadth is a floor, not a ceiling. "At least 12 candidates" does not allow narrowing the product to only 12 candidates or 5 preset filters.
- Preserve approved input freedom. If the contract says location, topic, customer, URL, date range, or other field is open-ended, implement free input or import. Preset chips are shortcuts only.
- Closed dropdowns are allowed only when Direction Lock or `capability_contract.input_freedom[].closed_set_allowed` explicitly approves a closed set.
- For recommendation, search, briefing, or planning apps, QA must test at least one out-of-seed or unlisted input and record whether the app handles it honestly.
- If an external API key, network access, account, scraper, or dataset is required, Technical Feasibility Architect must report the requirement and the user must approve the fallback before implementation.

## Choice Breadth Gate

If the app helps the user choose, compare, recommend, plan, filter, generate, schedule, or decide:

- Define the decision dimensions before implementation.
- Include enough options to make filtering meaningful.
- Verify at least two different input combinations produce different top results.
- Verify selected items and generated reports are derived from current state.

For recommendation apps, use at least 8-12 seeded candidates by default and test two contrasting scenarios.

Seeded candidates may support local testing, but they do not define the full product domain unless the user explicitly approved a seed-only product. When seed data is the chosen mode, label it in the UI or docs and provide a replacement path such as import, config file, API adapter, or data module.

## Design Durability Gate

Before implementation, Design Studio must produce implementation-ready design constraints:

- Layout model: sidebar, board, list, table, canvas, wizard, split-pane, or other exact structure.
- Component inventory: inputs, cards, rows, reports, buttons, empty states, dialogs, navigation.
- Density and spacing rules.
- Mobile collapse rules.
- Visual tokens: background, surface, border, text, accent, radius, shadow.
- A "do not degrade" checklist for the approved concept.

During QA, compare the rendered app against the approved design brief. If the layout has collapsed, hierarchy is unclear, controls look browser-default, or the first screen no longer communicates the product, mark UX or Consumer Appeal as failed.

The Design Fidelity Lock requires:

- A layout fingerprint precise enough to compare against the rendered first screen.
- A component count floor and must-keep component list.
- Visual token preservation for background, surface, border, text, accent, radius, shadow, and density.
- A forbidden-degradations list.
- Browser or screenshot evidence in `docs/QA_EVIDENCE.md`.

If the shipped UI is materially cheaper, flatter, more generic, or less structured than the approved concept, mark the task `reopened`; do not call it a style preference.

## Implementation Depth Gate

Task Decomposer must avoid ending with a shell-only task. For a new app, create task cards that cover:

1. App shell and design system.
2. Data model and seed data.
3. Core input and state flow.
4. Result generation or primary transaction.
5. Edge states and responsive polish.
6. Final real-app QA and scope audit.

If there is not enough time or clarity for all six, mark the run as `partial`, not `complete`.

## QA Evidence

QA must record concrete evidence:

- App URL or local file opened.
- Inputs changed.
- Before and after visible outputs.
- Files checked for existence.
- Commands run.
- Remaining risks.

Do not accept "looks good" or monitor metrics as QA evidence.

## Complete Product Rule

When the user's goal is a finished app or product, do not downgrade the goal to a clickable prototype.

Before completion:

- Verify every Scenario Harness flow.
- Verify generated or recommended outputs depend on the current input/state.
- Verify at least one out-of-seed or unlisted-input scenario when the approved input is open-ended.
- Verify the rendered app matches the approved design brief.
- Verify enough data/examples exist for the user to judge the product.
- Run `python vibe-coding-factory/scripts/verify_factory_run.py --project-root . --mode all` and record the pass/fail result in `docs/QA_EVIDENCE.md` and `.factory/factory-state.json`.
- Mark missing flows as `reopened`, `failed`, or `partial`; never hide them behind a successful final report.
