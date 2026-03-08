from typing import Union
from sqlalchemy.orm import Session
from app.models.user import User, RoleEnum
from app.utils.security import get_password_hash


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def list_all(self):
        return self.db.query(User).order_by(User.id).all()

    def create(self, email: str, password: str, role: Union[str, RoleEnum] = RoleEnum.USER):
        # accept either a RoleEnum or a string
        if isinstance(role, str):
            role = RoleEnum(role)
        user = User(email=email, hashed_password=get_password_hash(password), role=role)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
