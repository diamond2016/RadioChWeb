RadioChWeb Typing Strategy

Purpose
- Provide short, practical rules and examples for adding/maintaining types in this codebase.
- Keep changes small and safe: tests must pass; prefer incremental improvements.

Key Principles
- Prefer safety over perfection: make small, reviewable typing changes that keep tests green.
- Use explicit `Optional[...]` for functions that may return `None`.
- Standardize on `sqlalchemy.orm.Session` as the canonical DB-session type across repositories and services.
- Keep route handlers thin; put business logic in `service/` and type those modules first.
- When a runtime pattern prevents perfect typing (Flask-SQLAlchemy dynamic models), prefer a small, documented `# type: ignore[...]` rather than broad refactors.

DB session handling
- Use the helper in `database.py`:

  - `get_db_session() -> Session` — returns a `Session` (casts `db.session` at runtime).

- Repositories and services should accept a `Session` in constructors, e.g.:

  - `class RadioSourceRepository: def __init__(self, db_session: Session): ...`

- In route factories use `get_db_session()` to create repo instances.

Entities / ORM models
- Runtime: keep `class X(db.Model): ...` for Flask-SQLAlchemy behavior.
- Type-checking: avoid brittle, invasive changes. We used small `# type: ignore[name-defined]` on entity classes to keep mypy happy while preserving runtime behavior.
- Long-term: consider migrating to a typed Declarative base and explicit `Mapped[...]` attributes if you want stricter model typing.

DTOs (Pydantic v2)
- Use `pydantic.BaseModel` (v2) DTOs for IO and validation.
- Use `model_validate(...)` (or `model_validate` with `from_attributes=True`) to convert ORM objects to DTOs.
- Prefer explicit field names and correct attribute references (e.g., `metadata_type` vs `metadata`).

Services
- Annotate return types precisely. If a method can return `None`, use `Optional[...]`.
- When returning collections where variance matters, prefer `Sequence[T]` for covariant returns if callers expect read-only sequences.
- Avoid using variables as type aliases. Use `Type[...]` or explicit `from typing import Type` for type objects.
- Guard union attribute access (e.g., when an enum may be `None`) with `if x is not None:` before calling `.value`.

Routes / Factories
- Keep route factories small and typed where possible. Use `get_db_session()` for repository construction.
- Avoid duplicate function definitions; keep factory names unique.

Dealing with third‑party typing gaps
- We installed `sqlalchemy2-stubs` and other stubs for better coverage.
- Where a third-party exposes dynamic attributes not covered by stubs, add targeted `# type: ignore[code]` with a one-line rationale comment.

Mypy configuration & runs
- Run mypy per-package during work to reduce analysis time:

```bash
python -m mypy model service route --show-traceback --no-incremental
```

- For a full repo check (CI), run:

```bash
python -m mypy . --show-traceback
```

- If mypy shows duplicate-module errors from tests, make tests a package (add `tests/__init__.py`) or exclude `tests` in `mypy.ini`.

When to use `# type: ignore`
- Only for small, localized problems that are _not_ worth an immediate refactor.
- Always add a short comment explaining why the ignore is safe and when to remove it.

PR checklist for typing changes
- Run `pytest -q` locally and ensure all tests pass.
- Run targeted mypy for changed packages and fix any new issues.
- Keep commits small and focused (one logical typing change per commit when possible).
- Include a short note in PR describing any `# type: ignore` used and rationale.

CI recommendation
- Add GitHub Actions job to run:
  - `pip install -r requirements.txt` in venv
  - `pytest -q`
  - `python -m mypy . --show-traceback`

Notes / Future work
- Consider migrating ORM models to SQLAlchemy 2.0 typed Declarative with `Mapped[...]` to remove runtime stubs/ignores.
- Gradually reduce `# type: ignore` comments by fixing upstream stubs or code paths.

Contact
- If uncertain about a typing decision, create a small PR and request a quick review — typing changes are low-risk when backed by tests.
