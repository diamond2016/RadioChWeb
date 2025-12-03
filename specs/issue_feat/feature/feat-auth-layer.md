# Feature: Authentication Layer# Feature: Authentication Layer

## Checklist (High Level)

- Implement user authentication (register / login / logout)
- Password hashing (bcrypt/passlib)
- Session-based login (Flask-Login or custom session)
- Add roles/permissions (at least: user, admin)
- Decide policy: Who can delete analysis? Who can propose?
- Protect sensitive routes
    - Require login for propose/delete (and optionally require role for delete)
    - Show/hide UI actions based on current user
- Tests & environment
    - Add test users/fixtures, test client auth helpers
    - Run full test suite
- After auth is in place:
    - Revisit listen-logging plan: Include user_id (optional) or keep anonymized-only
    - Implement logging (migration + repo + route)
    - Add integration tests for the protected routes and logging

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