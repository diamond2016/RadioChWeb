"""
Database configuration and SQLAlchemy instance.
"""
from typing import cast
import os

# IMPORT THE SQALCHEMY LIBRARY's CREATE_ENGINE METHOD
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine

# Import Flask-SQLAlchemy's SQLAlchemy for the app-level `db` instance
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
instance_dir = os.path.join(basedir, 'instance')
os.makedirs(instance_dir, exist_ok=True)
DATABASE_URL = f'sqlite:///{os.path.join(instance_dir, "radio_sources.db")}'

# Provide an explicit type annotation so mypy and type checkers
# understand that `db` is a Flask-SQLAlchemy `SQLAlchemy` instance.
# This makes `db.Model`, `db.session` and related attributes resolvable
# by static type checkers (with appropriate stubs/plugins installed).
db: SQLAlchemy = SQLAlchemy()
    
# SQLAlchemy 2.0 style engine and sessionmaker for direct usage
engine = create_engine(DATABASE_URL, future=True)
# Create a session factory
session_factory = sessionmaker(bind=engine) 
# Create a scoped session
Session: scoped_session[Session] = scoped_session(session_factory)

def get_db_session() -> Session:
    """Return the active SQLAlchemy session typed as `Session`.

    This uses a simple `cast` because `flask_sqlalchemy` exposes a
    `scoped_session` at runtime. Call sites should prefer this helper
    so repository constructors receive the canonical `Session` type.
    """
    return cast(Session, db.session)




