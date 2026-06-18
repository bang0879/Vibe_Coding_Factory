# Venue And Reservation Agent Playbook

Use this reference when the idea mentions team dinner, restaurant, venue, local place search, map search, reservation, Naver Map, Kakao Map, CatchTable, or a "junior employee" style agent that should find and report real candidates.

This domain is not a seed-list recommendation app. The default expectation is a live or API-ready place discovery workflow with honest booking handoff. A local sample mode is allowed only when the user approves it after seeing the tradeoff.

## Product Promise

The app should take loose constraints such as region, place, mood, alcohol type, budget, headcount, date, time, accessibility, and dietary notes, then produce a sourced venue report:

- Which candidates were selected.
- Why each candidate fits or misses the constraints.
- How to get there from the requested area or landmark.
- What source produced the address, coordinates, category, phone, place URL, review/rating signal, or booking route.
- What the user must do next to reserve, or whether the app can complete a booking with confirmation evidence.

Do not invent ratings, review summaries, availability, or booking completion. If a source does not expose the data, say so and provide the provider link or user-approved fallback.

## Discovery Council Requirements

Before Direction Lock, report these candidate capabilities when relevant:

- Place normalization: free-text region, landmark, address, station, or building input mapped to coordinates.
- Live place discovery: Kakao Local API, Naver Local Search API, Google Places, or another approved provider.
- Radius and access logic: distance from input coordinates, walking/transit estimate if a provider is available, and map deep links.
- Venue enrichment: category, address, road address, phone, provider place URL, distance, source confidence, and data freshness.
- Review and atmosphere evidence: only from allowed provider fields, official links, user-provided data, or a clearly marked unavailable state.
- Booking workflow: official reservation API, provider deep link, browser-assisted flow, manual call handoff, or unavailable.
- Report generation: ranked shortlist, tradeoffs, source citations, route summary, and final notice/message draft.

Ask the user to approve one of:

- `live`: build against provider APIs now, with required keys and terms checked.
- `api_ready`: implement provider adapter boundaries, env vars, mocks only for tests, and a live replacement path.
- `user_data`: use imported venue lists or user-provided URLs as the source of truth.
- `local_functional`: clearly labeled local demo with real ranking/report logic, approved as a fallback.
- `partial`: stop at planning or provider setup when legal/API access is not available.

## Reference Provider Facts

Kakao Local API can convert address text to coordinates and search keyword/category places around coordinates. It returns fields such as place id, name, category, phone, address, road address, longitude, latitude, place URL, and distance when coordinates are supplied.

Naver Local Search API can search local businesses and returns fields such as title, link, category, description, address, road address, and WGS84 coordinate values. Its public local search result window is small, so large candidate discovery may need Kakao, Google Places, user data, or another licensed source.

Naver Reservation and CatchTable booking automation must be treated as unavailable unless an official API, partner API, or allowed browser-assisted workflow is confirmed during implementation. Do not scrape, bypass login, or automate a booking against provider terms.

## Architecture Pattern

Use adapters instead of wiring provider calls directly into UI code:

```text
Constraint intake
  -> place normalization adapter
  -> candidate discovery adapter
  -> enrichment and dedupe
  -> explainable ranking
  -> report generator
  -> booking state machine
  -> QA evidence and audit log
```

Minimum data model:

- `SearchConstraints`: free-text place, normalized coordinates, date/time, headcount, budget, mood, alcohol type, cuisine, hard filters, soft preferences.
- `VenueCandidate`: provider id, name, category, address, road address, coordinates, phone, place URL, distance, source, freshness, confidence.
- `VenueScore`: hard-filter pass/fail, weighted score, reasons, tradeoffs, missing evidence.
- `BookingRoute`: provider, `booking_mode`, URL or API action, required user confirmation, status, proof.
- `RecommendationReport`: top candidates, why selected, how to get there, atmosphere/review evidence, booking next step.

Deduplicate candidates by normalized name, address, coordinates, and provider id. Preserve provider source links so the user can inspect the evidence.

## Ranking Rules

Separate hard filters from scoring:

- Hard filters: closed date/time if known, party size impossible if known, budget impossible if source supports it, user-declared exclusions.
- Soft scores: distance, cuisine/drink fit, mood fit, budget confidence, review/source confidence, reservation route quality, novelty.
- Missing data: penalize uncertainty and show it in the report instead of filling gaps with invented details.

Every top candidate needs a plain-language explanation and a source-confidence note.

## Booking Modes

Use one of these values in `docs/ACCEPTANCE_CONTRACT.json` under `integration_contract.booking_mode`:

- `official_api`: the app can create or hold a reservation through an official/partner API.
- `provider_deeplink`: the app opens a provider booking page with candidate and constraints prefilled where supported.
- `browser_assisted`: the app guides a user-approved browser flow; the user confirms final submission.
- `manual_call`: the app provides phone/script/handoff because no safe API exists.
- `unavailable`: booking is explicitly out of scope or blocked.
- `not_applicable`: the app has no booking claim.

Reservation completion is never "done" unless the app captures confirmation proof: provider, venue, date/time, party size, status, and confirmation number or equivalent provider evidence. Final booking submission always requires explicit user confirmation.

## Acceptance Contract Additions

For venue/reservation agents, fill:

- `capability_contract.mode` and `approved_fallbacks`.
- `capability_contract.requires_live_data_or_api`.
- `integration_contract.provider_candidates`.
- `integration_contract.required_live_integrations`.
- `integration_contract.provider_docs_checked`.
- `integration_contract.auth_env_vars`.
- `integration_contract.terms_or_tos_constraints`.
- `integration_contract.booking_mode`.
- `integration_contract.requires_final_user_confirmation`.
- `integration_contract.completion_proof`.
- Primary scenarios for at least two different free-text locations or landmarks.
- One no-results or low-confidence state.
- One booking handoff or booking confirmation state, depending on approved scope.

Forbidden downgrades:

- Replacing free-text place input with a small closed area dropdown.
- Presenting sample venues as live nearby restaurants.
- Reporting reviews, ratings, atmosphere, price, or availability without source evidence.
- Claiming Naver Reservation or CatchTable completion without official/allowed workflow and confirmation proof.

## QA Evidence

Before completion, QA must record:

- Provider docs checked and provider terms constraints.
- Env vars required, with secret values omitted.
- At least two live/API-ready place-search scenarios using different free-text inputs.
- Evidence that preset chips are shortcuts only.
- Source links or provider fields used for every reported venue fact.
- No-results, API error, rate-limit, and missing-key states.
- Booking route evidence and user-confirmation gate.
- Confirmation proof if booking is claimed complete.
