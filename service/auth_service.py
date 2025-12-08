from functools import wraps
from typing import Any, Callable
from flask import abort
from passlib.context import CryptContext
from flask_login import LoginManager, current_user, login_required

from model.repository.user_repository import UserRepository
from model.entity.user import User

# Prefer a pure-Python secure scheme for portability in dev/test; keep bcrypt available
# Use pbkdf2_sha256 as default to avoid system bcrypt C-extension issues in some environments
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], default="pbkdf2_sha256", deprecated="auto")


class AuthService:
    def __init__(self, app=None):
        self.user_repo = UserRepository()
        self.login_manager = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        lm = LoginManager()
        lm.login_view = 'auth.login'
        lm.init_app(app)

        @lm.user_loader
        def load_user(user_id):
            return self.user_repo.find_by_id(int(user_id))

        self.login_manager = lm

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain: str, hashed: str) -> (bool, str | None):
        """
        Verify password; return (verified, new_hash_or_none)
        new_hash_or_none is non-None when the hash should be updated (lazy upgrade)
        """
        
        new_hash: str | None = None
        try:
            # verify_and_update returns (bool, new_hash)
            verified, new_hash = pwd_context.verify_and_update(plain, hashed)
        except Exception:
            # fallback to simple verify if verify_and_update unavailable
            verified = pwd_context.verify(plain, hashed)
            new_hash = None

        return verified, new_hash

    def register_user(self, email: str, password: str, role: str = 'user') -> User:
        existing: User | None = self.user_repo.find_by_email(email)
        
        if existing:
            raise ValueError('Email already registered')
        
        hashed: str = self.hash_password(password)
        return self.user_repo.create(email=email, hash_password=hashed, role=role)

    def change_password(self, user: User, new_password: str) -> User:
        new_hash: str = self.hash_password(new_password)
        return self.user_repo.update_password(user, new_hash)


def admin_required(func: Callable[..., Any]) -> Callable[..., Any]:   
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if not getattr(current_user, "is_admin", False):
            abort(403)
        return func(*args, **kwargs)
    return wrapper
