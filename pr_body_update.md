WIP: feat(dto): migrate DTOs and move service tests

Summary of recent work in this branch:

- Tests & fixtures
  - Moved service tests into `tests/service` and updated related fixtures.
  - Fixed test DB isolation by replacing commits with `flush()` in test fixtures and tests where appropriate.
  - Made `test_user`/`test_admin` fixture emails unique per run to avoid UNIQUE constraint collisions in CI/local runs.

- Route tests
  - Updated `tests/route/test_analysis_route.py` to authenticate the test user inside the request context by setting `session['_user_id']` and `session['_fresh']`. This allows `StreamAnalysisService` ownership checks to pass during route handler invocation.
  - Ensured created `StreamAnalysis` rows have `created_by` set to the test user's id so delete/approve flows exercise the intended paths.

- Services
  - No invasive service changes in this patch; focus was on tests and fixtures to make the DTO migration work reliably in tests.

Notes & next steps:

- Remaining work: controller/template migration to fully adopt DTO returns for views (planned next).
- CI: Run full test-suite in CI to confirm environment differences; local runs show most tests passing with one earlier teardown error observed intermittently (related to app context pop ordering). If that resurfaces in CI, we'll investigate teardown ordering in `tests/conftest.py` app fixture.

Local validation checklist I used:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
pytest -q tests/route
pytest -q
```

If you want, I can open a follow-up branch for the controller/template migration (`feat/dto-migration-controllers`).
