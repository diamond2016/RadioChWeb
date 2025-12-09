from typing import Literal
from flask_login import UserMixin
from sqlalchemy.sql import func
from database import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    hash_password = db.Column(db.String(512), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')

    # Timestamps: keep `created_at` and `updated_at`
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    proposals = db.relationship("Proposal", back_populates="user")
    stream_analyses = db.relationship("StreamAnalysis", back_populates="user")
    radio_sources = db.relationship("RadioSource", back_populates="user")

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
        return self.role == 'admin'
    
    @property
    def is_admin(self) -> bool:
        return self.role == 'admin'
    
    @property
    def is_active(self) -> bool:
        return True
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
