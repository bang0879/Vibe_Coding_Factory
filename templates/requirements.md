# Requirements

> Language: Korean by default for user-facing content. Keep ids, commands, JSON keys, and file paths in English.

## Intent Lock

- User job:
- Target user:
- Non-negotiable outcomes:
- Done means:

## Capability Contract

- Capability mode: `live` / `api_ready` / `user_data` / `local_functional` / `partial`
- Requires live data or API:
- External dependencies:
- Approved fallbacks:
- Forbidden downgrades:
- Open-ended input fields:
- Closed-set fields explicitly approved:
- Sample data label and replacement path:

## Integration Contract

Use this section when the product promise depends on maps, search, booking, payments, calendars, messages, or another outside provider.

- Provider candidates:
- Required live integrations:
- Official docs checked:
- Auth env vars, with secret values omitted:
- Rate limit policy:
- Cache policy:
- Terms or ToS constraints:
- Booking mode: `official_api` / `provider_deeplink` / `browser_assisted` / `manual_call` / `unavailable` / `not_applicable`
- Final user confirmation required before external action:
- Completion proof required:

## Requirements

Use testable acceptance criteria. Prefer this shape:

```text
WHEN <condition or user action>
THE SYSTEM SHALL <observable behavior>
```

### REQ-001

User story:

Acceptance criteria:

- WHEN
  THE SYSTEM SHALL

Priority: must

## Primary Scenarios

### SCN-001

- Requirement ids:
- Given:
- When:
- Then:
- Evidence to collect:
- Status: pending

### SCN-OUT-OF-SEED

Use this scenario when any approved input is open-ended.

- Requirement ids:
- Given: an input value not present in preset chips or seed categories
- When:
- Then:
- Evidence to collect:
- Status: pending

## Data Breadth

- Minimum realistic items:
- Minimum examples:
- Rationale:

## Non-Goals

-
