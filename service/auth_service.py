from functools import wraps
from typing import Any, Callable
from flask import abort
from passlib.context import CryptContext
from flask_login import LoginManager, current_user, login_required

from model.repository.user_repository import UserRepository
from model.dto.user import UserDTO
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
        def user_loader(user_id: int) -> User | None:
            return self.user_repo.find_by_id(int(user_id))

        self.login_manager = lm

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain: str, hashed: str) -> tuple[bool, str | None]:
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

    def register_user(self, user: UserDTO, password: str) -> User:
        existing: User | None = self.user_repo.find_by_email(user.email)
        if existing:
            raise ValueError('Email already registered')
        
        hashed: str = self.hash_password(password)
        return self.user_repo.create(email=user.email, hash_password=hashed, role=user.role)


    def change_password(self, user: UserDTO, new_password: str) -> User:
        new_hash: str = self.hash_password(new_password)
        existing: User | None = self.user_repo.find_by_email(user.email)
        if not existing:
            raise ValueError('user not found')        
        return self.user_repo.update_password(existing, new_hash)

    def get_user_by_email(self, email: str) -> UserDTO | None:
        user = self.user_repo.find_by_email(email)
        if not user:
            return None
        return UserDTO.model_validate(user)
    
    def get_user_by_id(self, user_id: int) -> UserDTO | None:
        if user_id is None:
            return None
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return None
        return UserDTO.model_validate(user)
    
    def register_user_dto(self, user_dto: UserDTO, password: str) -> UserDTO | None:
        user = self.register_user(user_dto, password)
        return self.get_user_by_id(user.id)

    def change_password_dto(self, user_dto: UserDTO, new_password: str) -> UserDTO | None:
        user = self.change_password(user_dto, new_password)
        return self.get_user_by_id(user.id)

def admin_required(func: Callable[..., Any]) -> Callable[..., Any]:   
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if not getattr(current_user, "is_admin", False):
            abort(403)
        return func(*args, **kwargs)
    return wrapper
