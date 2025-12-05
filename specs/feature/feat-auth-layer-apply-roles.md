# Auth Roles — Phase 2 Proposal

## TL;DR
Add role-aware authorization (user vs admin). Use the existing role column on User, add `is_admin` helper and an `admin_required` decorator, enforce admin checks server-side on admin actions (approve/reject, deletes), add a small seed/CLI for creating an initial admin, update UI to surface admin controls, and add integration tests to lock the behavior. The plan keeps changes minimal and testable.

## Steps (high level)
- Create feature branch: `git checkout -b feat/auth-roles`.
- Add `is_admin` helper to `user.py`.
- Add an `admin_required` decorator (new file `service/authorization.py` or add to `auth_service.py`).
- Protect admin-only endpoints (proposal approvals, analysis approve/delete, any management endpoints).
- Add a CLI/utility script to create the initial admin account (`scripts/create_admin.py`).
- Update templates to show/hide admin UI elements and add server-side checks for visibility only (do not rely on UI alone).
- Add tests: integration tests to verify admin can perform admin actions and normal users cannot (403 or redirect).
- Run full test suite and fix regressions; documentation and a short release checklist.

## Files to change (suggested)
### Add/modify:
- `user.py` — add `is_admin` property.
- `service/authorization.py` (new) — implement `admin_required` decorator.
- `proposal_route.py` — add `@admin_required` to `approve_proposal` (and any admin actions).
- `analysis_route.py` — add `@admin_required` to approve/delete actions.
- `index.html` and relevant templates — show admin links conditionally (use `current_user.is_admin`).
- `scripts/create_admin.py` (new) — CLI to create admin user through `AuthService.register_user(..., role='admin')`.
- `tests/integration/test_auth_admin_flow.py` (new) — integration tests for admin flows.

## Minimal code examples
### User.is_admin property (add to user.py):
```python
@property
def is_admin(self) -> bool:
    return (self.role or '').lower() == 'admin'
```

### admin_required decorator (new service/authorization.py):
```python
from functools import wraps
from flask import abort
from flask_login import current_user, login_required

def admin_required(func):
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if not getattr(current_user, "is_admin", False):
            abort(403)
        return func(*args, **kwargs)
    return wrapper
```

### Protecting an endpoint:
```python
@proposal_bp.route('/approve/<int:proposal_id>', methods=['POST'])
@admin_required
def approve_proposal(proposal_id):
    ...
```

## Database / migration notes
- No schema change required: role already exists on users.
- If you want a DB-level constraint or an enum later, create a migration step in `migrate_db`.
- Seeding admin can be done with a small script (preferred) rather than committing secrets in migrations.

## Seed / CLI script (recommended)
Create `scripts/create_admin.py` to be run locally/once:

```bash
python scripts/create_admin.py --email admin@example.com --password 'StrongPass!'
```

The script should:
- Import app context or call `AuthService(app)` with test/production config.
- Call `AuthService.register_user(email, password, role='admin')`.
- Print the created user's id/email (do not echo password).

## Tests to add
`tests/integration/test_auth_admin_flow.py`:
- Register a user with `role='admin'` using the service (not the public registration page) or the seed script in test.
- Log in via test client.
- POST to `/proposal/approve/<id>` and assert redirect/status and DB effect (proposal converted to radio source).
- Repeat same action as a normal user and assert 403 (or appropriate denial).
- Add unit tests:
  - `User.is_admin` correctness.
  - `admin_required` returns 403 for non-admins.

## UI changes
- Navbar: show an "Admin" area or admin links if `current_user.is_admin`.
- Buttons for approve/delete: continue to render only when `current_user.is_admin`, but server must enforce checks regardless.
- Keep UX minimal — a top-level "Admin" dropdown linking to panels for proposals/analysis is fine.

## Security & behavior rules
- Server-side enforcement always required — do not rely on UI hiding.
- Use `abort(403)` for unauthorized admin attempts (tests should expect 403).
- Audit: consider adding a simple audit log for admin actions (table `admin_actions` with `user_id`, `action`, `target`, `timestamp`). Optional but recommended for production.

## Rollout checklist
- Create feature branch `feat/auth-roles`.
- Implement `is_admin` and `admin_required`.
- Protect endpoints and add tests.
- Add `scripts/create_admin.py` and run locally to create initial admin.
- Update templates to surface admin UI.
- Run full test suite: `pytest -q`.
- Commit & push branch, open PR.
- Manual smoke test: create admin, login, try approve/reject/delete flows; verify normal user cannot.
- (Optional) Add migration if you later enforce DB-level constraints.

## Commands & recommended workflow
Create branch and run tests locally:
```bash
git checkout -b feat/auth-roles
# implement changes...
source .venv/bin/activate
python -m pip install -r requirements.txt
pytest -q
```

Create an admin locally using the seed script (after adding it):
```bash
python scripts/create_admin.py --email admin@local.test --password 'ReplaceMe!'
```

## Estimated effort
- Basic implementation + tests: 2–4 hours.
- With audit logging + polished admin UI: 4–8 hours.

## Optional future enhancements
- Granular RBAC (roles + permissions table).
- Admin UI pages for user management.
- Audit trail (DB table).
- Rate-limits / throttling for admin endpoints.
- Admin-only API keys and 2FA for admin accounts.