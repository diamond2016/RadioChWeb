# Feature: Authentication Layer

## Checklist (High Level)

- Implement user authentication (register / login / logout)

- Password hashing with bcrypt/passlib

- Session-based login using Flask-login

- Add roles/permissions: user (generic), admin (manage resources)

- Policy: 
    * listen and browsing without permissions
    * role user (authenticated) may analyze stream, propose stream, save as radio source. The user_name is associated to the radio source saved
    * only admin may resources
    * Edit of a proposal is allowed to the user who created it or to admin
    * Deletion of analysis is only allowed to admin

- Protect sensitive routes
    - Require login functions as needed
    - Show/hide UI actions based on current user

- Tests & environment
    - Add test users/fixtures, test client auth helpers
    - Run full test suite

- After auth is in place:
    - Revisit listen-logging plan: Include user_id for next feat implementation

# User model
```python
@data class
    id: int
    user_name: str
    email: str
    hash_password: str
    last_modified_at: datetime
    role: str  # 'user' or 'admin'
```

## PLAN

### Plan: Implement User Authentication
TL;DR — Add a proper user model, repository, and an auth service using Passlib + Flask-Login; create protected routes and three templates (login.html, register.html, change_password.html) with CSRF; update app registration and templates to respect roles. 

This gives session-based auth, role checks, and a migration-ready DB model with tests for register/login/logout and access control.

### Steps
1. Add DB model & migration: create model/entity/user.py and a migration migrate_db/migrations/V8_0__create_users_table.sql with columns id, email (unique), username (unique), password_hash, role (user/admin), is_active, created_at, updated_at.
1. Add UserRepository: add model/repository/user_repository.py with create, find_by_id, find_by_email, find_by_username, update_password, set_role, exists helpers.
1. Add AuthService + password policy: add service/auth_service.py using passlib (Argon2id preferred, bcrypt fallback) and helpers for register_user, verify_password (with lazy rehash on login), and expose a simple interface for routes. Initialize Flask-Login user loader in this service or a small auth initializer.
1. New routes & templates: add route/user_route.py (blueprint auth_bp) with GET/POST /login, GET/POST /register, GET/POST /change_password, POST /logout. Create templates/login.html, templates/register.html, templates/change_password.html reusing the app's Bootstrap layout and including CSRF tokens (Flask-WTF or csrf_token() calls).
1. Protect routes & UI: apply @login_required (Flask-Login) and @role_required('admin') where needed (e.g., analysis delete). Update templates to show/hide actions based on current_user.is_authenticated and current_user.role. Add a small helper route/_auth_helpers.py if you prefer decorator-based role checks.
1. Tests & fixtures: add tests in tests/unit/test_auth.py and integration tests for route protection. Add fixtures for a test user and admin, client helpers to log in. Ensure CSRF disabled in test config or include tokens.
1. App wiring & docs: update app.py to register the auth_bp, initialize Flask-Login and CSRFProtect, add required packages to requirements.txt, and add a short doc/spec in specs/feat-auth-layer.md describing env vars and migration steps.

### Further Considerations
- Password hashing options: use Argon2id via passlib[argon2] (recommended). If Argon2 not available, use passlib[bcrypt]. Use pwd_context.verify_and_update() for lazy migration. Ensure DB field length (>= 255).
- Session management: use Flask-Login (recommended). It integrates cleanly with Flask and simplifies current_user logic. Provide an adapter so User entity implements required attributes/methods or a lightweight wrapper.
- Security & UX: enable CSRF on all forms, rate-limit login endpoint (simple rate limiter or use Flask-Limiter later), require email confirmation and/or password reset as next steps.
- For proposal edit permissions: allow only the author or admin to edit.
- For delete of analysis: admin-only, as in spec.
- For proposal edit permissions: allow only the author or admin to edit.
- For delete of analysis: admin-only, as in spec.

- Migration & rollout: add SQL migration; deploy to staging; test registration/login flows and verify that lazy rehashing updates stored hashes. Set SECRET_KEY and any passlib salts in environment.

- Tests: include unit tests for AuthService password flows and integration tests for protected routes. Mock expensive Argon2 parameters in tests to keep runtime fast.

## FOLLOW EXAMPLES

## Quick Route-Protection Decorator (Example)

```python
from functools import wraps
from flask import session, redirect, url_for, flash, request

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please log in to continue', 'error')
            return redirect(url_for('auth.login', next=request.path))
        return view(*args, **kwargs)
    return wrapped

def role_required(role):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user_role = session.get('user_role')
            if user_role != role:
                flash('Permission denied', 'error')
                return redirect(url_for('proposal.index'))
            return view(*args, **kwargs)
        return wrapped
    return decorator
```

## How to Apply to Analysis Routes (Example)

```python
# ...existing imports...
from route._auth_helpers import login_required, role_required

@analysis_bp.route('/delete/<int:analysis_id>', methods=['POST'])
@login_required
@role_required('admin')  # optional: only admins can delete
def delete_analysis(analysis_id):
    ...
```

## Testing Tips

- Add helper in tests to log in test users via client (set session or post to login route).
- Test three flows: Anonymous (no buttons / blocked), logged-in normal user (can propose but not delete), admin (can delete).
- For background logging tests, mock repository methods to avoid timing/flakiness.

## Migrating to Stronger Password Hashing

Switching from werkzeug's pbkdf2:sha256 to passlib-managed bcrypt or (preferably) Argon2id. Passlib is the de-facto Python library for password hashing and makes upgrades and policy management easy.

### Why

- PBKDF2 (sha256) is OK if you use very high iteration counts, but it’s CPU-bound and less resistant to GPU/ASIC attackers than memory-hard schemes.
- Argon2id is the modern recommended choice (memory-hard, best resistance).
- Bcrypt is also widely used and safe; easier to deploy than Argon2 if you lack libs.
- Passlib centralizes algorithms, parameters, and supports automatic hash-upgrade on login (verify_and_update), easing migration.

### Concrete recommendation

- Use passlib with Argon2id if you can install the dependency; fallback to bcrypt otherwise.
- Store full hash strings (DB column length >= 255).
- Migrate lazily: on successful login, re-hash old pbkdf2 hashes to the new scheme.

### Install

- Argon2: `pip install passlib[argon2]`
- Bcrypt: `pip install passlib[bcrypt]`

### Example (passlib, safe, short)

```python
from passlib.context import CryptContext

# Prefer argon2id, fallback to bcrypt if argon2 not available
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
    # optional tuning for argon2: time_cost=2, memory_cost=102400, parallelism=8
)

# Registration
hash = pwd_context.hash(plain_password)
user.hash_password = hash

# Login: verify and upgrade if needed
verified, new_hash = pwd_context.verify_and_update(plain_password, user.hash_password)
if verified:
    if new_hash:
        user.hash_password = new_hash  # update DB
    # login user
else:
    # bad password
```

### Parameters guidance

- Argon2: tune `time_cost`/`memory_cost`/`parallelism` for your environment (example: `time_cost=2`, `memory_cost=102400` KB for moderate).
- Bcrypt: rounds (`log_rounds`) 12 is a reasonable start; increase with hardware.
- Avoid tiny `salt_length` — passlib handles salts.

### Migration strategy

1. Add passlib context (as above).
2. Change registration to use `pwd_context.hash`.
3. On login, use `verify_and_update` to re-hash older pbkdf2 hashes transparently.
4. Optionally run an offline rehash job if you prefer bulk migration (no plaintext needed; you must re-hash on user login or ask users to reset password).

### Other notes

- Ensure DB column length fits argon2 strings (~200+).
- Document chosen scheme and parameters; store no plaintext.
- Consider rate-limiting login endpoints and account lockout to reduce brute-force risk.