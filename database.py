"""
Database configuration and SQLAlchemy instance.
"""

from flask_sqlalchemy import SQLAlchemy

# Provide an explicit type annotation so mypy and type checkers
# understand that `db` is a Flask-SQLAlchemy `SQLAlchemy` instance.
# This makes `db.Model`, `db.session` and related attributes resolvable
# by static type checkers (with appropriate stubs/plugins installed).
db: SQLAlchemy = SQLAlchemy()
   