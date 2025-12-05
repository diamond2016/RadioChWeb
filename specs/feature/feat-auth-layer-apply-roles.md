# Auth Roles — Phase 2 Proposal

## TL;DR
Add server-side role-based authorization (user vs admin). Use the existing `role` column on `User`, add a convenient `is_admin` helper and an `admin_required` decorator, protect admin actions (approve/reject, deletes, management) at the controller level, seed an initial admin account via a small CLI helper, update templates to show admin UI elements, and add integration tests to prevent regressions. Keep changes minimal, well-tested and auditable.

## Goals
- Enforce admin-only operations server-side (not just hidden UI elements).
- Provide a simple, auditable mechanism to create an initial admin locally.
- Keep the role model simple (string role) with easy migration path to more granular RBAC later.
- Add tests exercising admin vs normal user behavior.

## Non-Goals
- Complex RBAC (permissions table) — defer to later if needed.
- UI redesign — add minimal UI changes only (navbar badges/links).

## Implementation Steps (concrete)
1. Branch:
   - `git checkout -b feat/auth-roles`
2. Domain: `model/entity/user.py`
   - Add property:
     ```python
     @property
     def is_admin(self) -> bool:
         return (self.role or '').lower() == 'admin'
     ```
3. Authorization helper: new `service/authorization.py`
   - Add `admin_required` decorator:
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
4. Protect server routes (examples)
   - `route/proposal_route.py`:
     - Add `from service.authorization import admin_required`
     - Annotate:
       ```python
       @proposal_bp.route('/approve/<int:proposal_id>', methods=['POST'])
       @admin_required
       def approve_proposal(proposal_id):
           ...
       ```
   - `route/analysis_route.py`:
     - Protect `approve_analysis` and `delete_analysis`.
5. Templates: show admin UI (examples)
   - `templates/index.html` (navbar):
     ```jinja
     {% if current_user.is_authenticated and current_user.is_admin %}
       <a class="nav-link" href="{{ url_for('proposal.index') }}">Admin: Proposals</a>
     {% endif %}
     ```
   - Buttons for approve/delete: keep server enforcement and render only for admin:
     ```jinja
     {% if current_user.is_authenticated and current_user.is_admin %}
       <form ...> <button ...>Approve</button> </form>
     {% endif %}
     ```
6. Seed CLI (new) `scripts/create_admin.py` — minimal safe script:
   ```python
   # scripts/create_admin.py
   import argparse
   from app import app
   from service.auth_service import AuthService

   def main():
       p = argparse.ArgumentParser()
       p.add_argument('--email', required=True)
       p.add_argument('--password', required=True)
       args = p.parse_args()

       AuthService(app).register_user(email=args.email, password=args.password, role='admin')
       print(f"Admin user '{args.email}' created.")

   if __name__ == '__main__':
       main()
   ```
   - Run locally (do not commit secrets): `python scripts/create_admin.py --email admin@example.com --password 'Strong!'`
7. Tests (new)
   - `tests/integration/test_auth_admin_flow.py` (skeleton):
     - Create admin via `AuthService.register_user(..., role='admin')` or create via the repo directly in test DB.
     - Log in with test client, POST to admin-only endpoints and assert success and DB side-effect.
     - Log in as normal user and assert 403 on admin endpoints.
   - Unit tests:
     - `test_user_is_admin` (verify `is_admin` behavior).
     - `test_admin_required_decorator` (use Flask test_request_context and a mocked `current_user` to assert abort).
8. Audit (optional)
   - Consider a simple `admin_actions` table for future auditing. Optional for MVP.

## File Summary (exact edits)
- `model/entity/user.py` — add `is_admin` property.
- `service/authorization.py` — new.
- `route/proposal_route.py` — import decorator + protect `approve_proposal`.
- `route/analysis_route.py` — protect `approve_analysis` and `delete_analysis`.
- `templates/index.html`, `templates/proposals.html`, `templates/analysis.html` — conditional UI.
- `scripts/create_admin.py` — new seed script.
- `tests/integration/test_auth_admin_flow.py` — new integration tests.

## Example: Protecting Analysis endpoints
In `route/analysis_route.py`:
```python
from service.authorization import admin_required

@analysis_bp.route('/approve/<int:id>', methods=['POST'])
@admin_required
def approve_analysis(id: int):
    ...

@analysis_bp.route('/delete/<int:id>', methods=['POST'])
@admin_required
def delete_analysis(id: int):
    ...
```

## Testing notes and expected behavior
- Admin success: approve endpoint returns redirect and DB effect (proposal created / radio source saved).
- Normal user: call returns HTTP 403 (Abort), or custom error page — tests should expect 403.
- Test fixtures: use `tests/conftest.py` test DB and call `AuthService.register_user(..., role='admin')` or create user directly via repository + hashed password.

## Migration & DB notes
- No DB schema change required — `role` exists.
- If you later want DB-level constraints, add a migration in `migrate_db/`.

## Security considerations
- Do not expose admin UI as the only protection — always enforce on server.
- Seed script should be run locally and never commit credentials. Consider generating a one-time password printed to stdout and requiring rotation.
- Consider adding logging for admin actions (timestamp, user id, action, target).

## Rollout checklist
1. Create branch `feat/auth-roles`.
2. Implement code changes and tests.
3. Run `pytest -q` locally, fix failures.
4. Add `scripts/create_admin.py` and create an initial admin locally to test admin flows.
5. Commit and push branch; open PR with description and test run output.

## Commands & workflow
```bash
git checkout -b feat/auth-roles
# implement changes...
source .venv/bin/activate
python -m pip install -r requirements.txt
pytest -q
```

## Estimated effort
- Basic implementation + tests: 2–4 hours.
- With audit logging + nicer admin UI: 4–8 hours.

## Optional extensions
- Granular permissions table.
- Admin user management UI.
- 2FA for admin accounts.

## Final notes
- Keep changes small and test-first. Add the seed script to your local `scripts/` folder and do not check passwords into source control.
- If you'd like, I can produce the skeleton files and patches for all file edits and the tests so you can apply them in one go.