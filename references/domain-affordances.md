# Domain Affordances

Use this during Discovery Council before Direction Lock. A rough idea often hides domain-native capabilities that a high-quality app should at least propose.

Do not implement inferred capabilities without user approval. Do report them as options with feasibility, integration needs, and fallback.

## Required Output

Add `candidate_capabilities[]` to the Decision Brief or council summary:

```json
{
  "capability": "",
  "why_it_matters": "",
  "requires": [],
  "feasibility": "low|medium|high",
  "fallback": "",
  "needs_user_approval": true
}
```

## Common Patterns

| Domain signal | Capabilities to propose | Typical dependency | Safe fallback |
| --- | --- | --- | --- |
| 회식, 맛집, 장소, 여행, 동네, venue, place | 지도/장소 자동완성, geocoding, 좌표/반경 추천, 건물명 매칭, 이동거리, Naver/Kakao/Google Maps API | map/place API key, location dataset, network access | API-ready adapter plus labeled local sample data and free-text input |
| 일정, 미팅, 리마인더, 출장 일정 | calendar sync, conflict checks, time zones, notifications, ICS import/export | Google Calendar/Outlook API, notification channel | manual calendar import/export |
| 예약, 결제, 커머스, 티켓 | booking state, inventory, payment, refund/cancel policy, receipts | Stripe/payment API, booking provider, database | simulated checkout clearly labeled as demo |
| 추천, 검색, 브리핑, 리서치 | data source, ranking logic, freshness, citations, filters, source confidence | search API, web access, corpus, embedding/ranking model | user-provided data or local corpus |
| 문서, 계약, 보고서 | file import/export, versioning, redlines, citations, permissions | document parser, storage, auth | local files with explicit limitations |
| 대시보드, 분석, CRM | data import, charts, filters, saved views, drilldown, export | database/API, CSV import, auth | CSV upload or seed dataset with replacement path |

## Decision Rule

If the inferred capability is central to the product promise, ask the user to choose among:

- `live`: implement the real integration now.
- `api_ready`: build the adapter/config shape, but require keys later.
- `user_data`: use uploaded/pasted/user-provided data.
- `local_functional`: ship a clearly labeled local demo with real logic and replacement path.
- `partial`: pause or mark incomplete until dependency is available.

Never hide the tradeoff by building only a tiny seed-data world.
