"""
Database configuration and SQLAlchemy instance.
"""
from typing import cast
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Session

# Provide an explicit type annotation so mypy and type checkers
# understand that `db` is a Flask-SQLAlchemy `SQLAlchemy` instance.
# This makes `db.Model`, `db.session` and related attributes resolvable
# by static type checkers (with appropriate stubs/plugins installed).
db: SQLAlchemy = SQLAlchemy()


def get_db_session() -> Session:
	"""Return the active SQLAlchemy session typed as `Session`.

	This uses a simple `cast` because `flask_sqlalchemy` exposes a
	`scoped_session` at runtime. Call sites should prefer this helper
	so repository constructors receive the canonical `Session` type.
	"""
	return cast(Session, db.session)
