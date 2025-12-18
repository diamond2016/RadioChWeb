Typing Migration Plan — RadioChWeb

Goal
- Bring repository typing to the point where `mypy` reports only intentional/accepted ignores.
- Do this incrementally, keep tests passing, and make tasks delegable.

Summary of current state
- `mypy` full run failed early due to test module duplication (tests/service/test_proposal_service.py found twice under different module names). A focused `mypy model service route` run shows ~27 errors (entities, services, DTOs, annotations, redefs).
- `database.py` exposes `get_db_session()` and `db: SQLAlchemy` helper already in place; many routes were updated to use it.
- Test suite currently passes locally: `pytest` returned 62 passed earlier.

Immediate blocker (must fix before full mypy)
- Duplicate test module path: `tests/service/test_proposal_service.py` is being collected under two module names which prevents full repo mypy. Fix: ensure tests package imports / layout and/or set a `mypy.ini` `[mypy-tests.*]` ignore. Recommended immediate fix: rename test file or add `tests/__init__.py` and `tests/service/__init__.py` to stabilize import layout, or exclude `tests` from top-level mypy run and run tests separately.

Priority plan (ordered, actionable tasks)

High priority (do these first — safe to start in `model` and `service`)
1) Stabilize mypy run (blocker)
   - Action: Add `tests/__init__.py` and `tests/service/__init__.py` (empty files) OR add `exclude = tests` to `mypy.ini` and run `mypy` per-package. Deliverable: `mypy .` runs past the duplicate-file error.
   - Owner: you (1–5m).

2) Fix `db.Model` entity typing (entities)
   - Files: `model/entity/*.py` (user.py, stream_type.py, stream_analysis.py, radio_source.py, proposal.py).
   - Action: at top of each file add `from database import db` so `db.Model` is defined for mypy, or switch entities to use a typed declarative base (more invasive).
   - Safety: non-invasive; tests should still pass. Run `pytest` after edits.
   - Owner: you or junior dev.

3) Service return-type alignment (services)
   - Files: `service/auth_service.py`, `service/proposal_service.py`, `service/radio_source_service.py`, `service/stream_type_service.py`.
   - Action: For functions that currently can return `None`, update annotations to `-> Optional[...]` or change implementation to raise/return non-None. Prefer minimal change: annotate as `Optional` and update callers, then tighten later.
   - Deliverable: no mypy return-value errors for these functions.
   - Owner: you (design) + delegate (implement).

4) Fix DTO / validation typing issues
   - Files: `model/dto/*.py` (notably `validation.py`, `stream_type.py`).
   - Action: Correct attribute names referenced by mypy and ensure `typing` usage (use `Type[...]`, `Optional[...]`, `Literal` as needed). Replace assignments to types with proper `Optional[Type[...]]` or `None` default patterns.
   - Owner: delegate (needs reading DTO code).

Medium priority
5) Annotation syntax & tuple fixes
   - Files: `service/auth_service.py` (line ~37). Replace parenthesized tuple annotations with `Tuple[...]` or `tuple[...]` per Python version.
   - Owner: quick fix by you or junior dev.

6) Name redefinition fixes in `service/stream_analysis_service.py`
   - Action: resolve local variable reuses (`no-redef`) by renaming or merging logic blocks.
   - Owner: delegate with tests run.

7) Union attribute safe access
   - Files: `service/stream_analysis_service.py` (calls `.value` on possibly-None). Add `if ... is not None` guards or `assert` before attribute access.
   - Owner: delegate.

Low priority / cleanup
8) Replace broad `list[...]` returns with `Sequence[...]` where covariance matters (e.g., `list[RadioSourceDTO]` vs `list[RadioSource]`). Consider `Sequence[RadioSourceDTO]` for service APIs.
9) Add targeted `# type: ignore[...]` comments only for third-party stubs or remaining small irreconcilable cases. Document each ignore with a short comment.
10) Add CI job to run `mypy` (per-package or with tests excluded) and `pytest` on PRs.
11) Update docs: add `docs/typing_migration_plan.md` (this file), and add a short note to `CONTRIBUTING.md` describing the Session typing approach and `get_db_session()`.

Testing and verification
- Commands to run locally (bash):

```bash
# activate venv
source .venv/bin/activate
# run unit tests
pytest -q
# run mypy per-package (recommended during work)
/home/riccardo/Documenti/Programming/Projects/RadioChWeb/.venv/bin/python -m mypy model service route --show-traceback
# or, after fixing test-module duplication:
/home/riccardo/Documenti/Programming/Projects/RadioChWeb/.venv/bin/python -m mypy . --show-traceback
```

Delegation guidance (how to split tasks)
- Task A (starter, you): Stabilize mypy run and fix `db.Model` imports in `model/entity` — quick wins.
- Task B (delegate 1): DTO/validation fixes and annotation syntax fixes — medium complexity, needs reading DTO semantics.
- Task C (delegate 2): Service return-type alignment and union guards — requires careful knowledge of service semantics; add/adjust unit tests if behavior changes.
- Task D (junior): Add `__init__.py` files for packages or update `mypy.ini` excludes, add `# type: ignore` comments when instructed.
- Task E (you or senior): Add CI + document strategy.

Acceptance criteria for each task
- No behavioral changes detected by `pytest` (all tests pass).
- `mypy` invoked for the changed packages shows no new errors beyond excluded ones, and all newly-fixed errors are resolved.
- Any `# type: ignore` is accompanied by a one-line rationale comment.

Next immediate action I can do for you
- Apply the minimal fix to unblock full mypy: add `tests/__init__.py` and `tests/service/__init__.py` (or optionally update `mypy.ini` to exclude `tests`). I can apply and push that now, then re-run `mypy .` and produce the final error map for delegation.

---

File created at: `docs/typing_migration_plan.md`

If you want, I can now apply the test-package fix and re-run mypy to produce the full prioritized error list ready to assign. Which option: apply fix now, or just review the plan first?