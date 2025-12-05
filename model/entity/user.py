from typing import Literal
from sqlalchemy.sql import func
from database import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    hash_password = db.Column(db.String(512), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Timestamps: keep `created_at` and `last_modified_at` per project preference
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    last_modified_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def get_id(self):
        return str(self.id)

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    @property
    def is_admin(self) -> bool:
        return (self.role or '').lower() == 'admin'

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
