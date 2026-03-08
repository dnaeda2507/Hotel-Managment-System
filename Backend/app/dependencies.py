from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.utils.security import decode_access_token
from app.repositories.user_repository import UserRepository
from app.models.user import RoleEnum

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    email = payload.get("sub")
    user = UserRepository(db).get_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_role(required_role: RoleEnum):
    def role_checker(current_user = Depends(get_current_user)):
        # current_user.role may be a RoleEnum member
        user_role = current_user.role
        if isinstance(user_role, RoleEnum):
            if user_role != required_role:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        else:
            if str(user_role) != required_role.value:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return current_user

    return role_checker