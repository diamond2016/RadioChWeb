"""
Database configuration and SQLAlchemy instance.
"""
from typing import cast, Any, Optional
import os

# IMPORT THE SQALCHEMY LIBRARY's CREATE_ENGINE METHOD
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from sqlalchemy import create_engine

# Import Flask-SQLAlchemy's SQLAlchemy for the app-level `db` instance
from flask_sqlalchemy import SQLAlchemy

class DatabaseManager:
    """
    Singleton Database Manager to handle SQLAlchemy engine and session factory.
    Ensures that only one instance of the database connection exists.
    """
    _instance: Optional['DatabaseManager'] = None
    _engine: Optional[Any] = None
    _session_factory: Optional[sessionmaker] = None
    _scoped_session: Optional[scoped_session] = None
    _initialized: bool = False

    def __new__(cls) -> 'DatabaseManager':
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance

    def initialize(self, database_url: str) -> None:
        if not self._initialized:
            self._engine = create_engine(database_url, future=True)
            self._session_factory = sessionmaker(bind=self._engine)
            # Create a scoped session that is NOT tied to Flask by default
            self._scoped_session = scoped_session(self._session_factory)
            self._initialized = True

    @property
    def engine(self) -> Any:
        return self._engine

    @property
    def session_factory(self) -> sessionmaker:
        return self._session_factory

    @property
    def standalone_session(self) -> scoped_session:
        return self._scoped_session

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
instance_dir = os.path.join(basedir, 'instance')
os.makedirs(instance_dir, exist_ok=True)
DATABASE_URL = f'sqlite:///{os.path.join(instance_dir, "radio_sources.db")}'

# Initialize Singleton
db_manager = DatabaseManager()
db_manager.initialize(DATABASE_URL)

# Provide references for backward compatibility and direct usage
engine = db_manager.engine
session_factory = db_manager.session_factory
# Use a clear name for the standalone scoped session
StandaloneSession: scoped_session[Session] = db_manager.standalone_session

# Flask-SQLAlchemy instance
db: SQLAlchemy = SQLAlchemy()

def get_db_session() -> Session:
    """Return the active SQLAlchemy session.

    Returns the Flask-SQLAlchemy session if within a Flask app context,
    otherwise returns a session from the standalone scoped_session.
    This allows shared services and repositories to work in both
    Flask (main app) and non-Flask (API, CLI, tests) environments.
    """
    try:
        from flask import has_app_context
        if has_app_context():
            return cast(Session, db.session)
    except (ImportError, RuntimeError):
        pass
    
    # Fallback for non-Flask environments
    return cast(Session, StandaloneSession())




