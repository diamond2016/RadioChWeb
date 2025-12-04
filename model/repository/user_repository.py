from typing import Optional
from database import db
from model.entity.user import User


class UserRepository:
    def __init__(self, session=None):
        self.session = session or db.session

    def find_by_id(self, user_id: int) -> Optional[User]:
        return self.session.query(User).filter(User.id == user_id).first()

    def find_by_email(self, email: str) -> Optional[User]:
        return self.session.query(User).filter(User.email == email).first()
    
    def create(self, email: str, hash_password: str, role: str = 'user') -> User:
        user = User(email=email, hash_password=hash_password, role=role)

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update_password(self, user: User, new_hash: str) -> User:
        user.hash_password = new_hash

        self.session.commit()
        self.session.refresh(user)
        return user

    def set_role(self, user: User, role: str) -> User:
        user.role = role
        
        self.session.commit()
        self.session.refresh(user)
        return user
