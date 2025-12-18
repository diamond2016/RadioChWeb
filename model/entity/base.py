from typing import Any
from sqlalchemy.orm import DeclarativeBase

from database import db


class Base(DeclarativeBase):
    pass

# Ensure migrated DeclarativeBase uses the same MetaData as Flask-SQLAlchemy
# so `db.create_all()` will create tables for both legacy and migrated models.
Base.metadata = db.metadata