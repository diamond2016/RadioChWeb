**Title**
WIP: feat(dto): migrate DTOs and move service tests

**Summary**
- Completed initial DTO migration and moved service tests into `tests/service`.
- Updated services to consume/produce Pydantic v2 DTOs and added defensive compatibility where needed.
- Fixed tests and integration flows (StreamAnalysis → Proposal → RadioSource).
- Added and adjusted fixtures for DB-backed tests so integration tests work without manual changes.

**What’s done**
- Moved service tests from `tests/unit` → `tests/service`.
- Implemented canonical DTOs in `model/dto/` and added temporary compatibility aliases for renamed DTO types.
- Updated `service/radio_source_service.py`:
  - Added proposal helper methods used by routes (`save_from_proposal`, `reject_proposal`, `update_proposal`, `get_proposal`, `get_all_proposals`).
  - Defensive conversion for nested `user` / `stream_type` to avoid pydantic errors with mocks and real DTOs.
- Updated `service/auth_service.py` to safely return `None` when repository returns no user.
- Bound `StreamTypeService` and `AuthService` to test DB session in integration tests so lookups happen against test data.
- Fixed `tests/conftest.py` fixtures (use `flush()` where needed) to preserve transactional isolation during tests.
- Tests updated/added:
  - `tests/service/*` (radio source, proposal, validation, stream-type, stream-analysis, auth)
  - `tests/integration/test_validate_and_add_workflow.py`

**Local test status**
- Unit/service: all `tests/service` passed (48 tests).
- Integration: all `tests/integration` passed.
- (I can run the full `pytest -q` if you want a final sweep.)

**Files touched (high level)**
- `service/radio_source_service.py` — added methods + defensive DTO construction
- `service/auth_service.py` — made user lookups defensive
- `service/stream_type_service.py` — no API change, used by new flow
- `tests/service/*` and `tests/integration/*` — moved/added tests and fixtures

**Remaining work (high level)**
- Controller (route) layer: update controllers to pass DTOs, call services with explicit params (avoid request-bound side-effects).
- Templates: update forms and views to align with new DTO fields and flows.
- Remove temporary compatibility shims once controllers/templates are migrated.
- Prepare targeted PRs for controller changes to keep the main migration draft manageable.

**Checklist (for PR)**
- [x] Move service tests to `tests/service`
- [x] DTO canonicalization + compatibility aliases
- [x] Service-level changes + unit tests passing
- [x] Integration tests passing
- [ ] Controller (routes) refactor to new DTO flow
- [ ] Template updates and UI validation changes
- [ ] Remove compatibility aliases and retest
- [ ] Final full-suite run and documentation update
- [ ] Merge to `main` (after review)

**Notes**
- I kept a few defensive compatibility behaviors in services to make the migration incremental and review-friendly; we should remove them after controllers/templates are migrated.
- If you want I can: update the Draft PR body now (requires `gh` CLI available + auth), or I can create the `feat/dto-migration-controllers` branch and start the controller work.

---
Generated on 2025-12-10 by the migration assistant.
