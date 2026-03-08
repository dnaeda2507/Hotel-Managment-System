from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.utils.security import verify_password, create_access_token, decode_access_token
from app.schemas.user import Token, UserOut


def authenticate_user(db: Session, email: str, password: str):
    repo = UserRepository(db)
    user = repo.get_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_token_for_user(user) -> str:
    payload = {
        "sub": user.email,
        # FIX: RoleEnum.value → plain string ("user" / "moderator")
        "role": user.role.value if hasattr(user.role, "value") else str(user.role),
    }
    return create_access_token(payload)
