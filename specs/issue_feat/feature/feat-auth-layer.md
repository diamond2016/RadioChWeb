# Feature: Authentication Layer

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
from flask import session, redirect, url_for, flash

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