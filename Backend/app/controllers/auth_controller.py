from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.services.auth_service import authenticate_user, create_token_for_user
from app.utils.security import decode_access_token
from app.repositories.user_repository import UserRepository
from app.database import SessionLocal
from app.schemas.user import Token, UserOut


def login_controller(email: str, password: str, db: Session) -> Token:
    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    token = create_token_for_user(user)

    # FIX: Token response içinde user bilgisini de döndür
    # Frontend bunu alıp role'e göre redirect yapar
    return Token(
        access_token=token,
        token_type="bearer",
        user=UserOut.model_validate(user),
    )


def me_controller(token: str):
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    email = payload["sub"]

    # FIX: me_controller'a db inject et (aşağıdaki route'a bakın)
    db = SessionLocal()
    try:
        user = UserRepository(db).get_by_email(email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return UserOut.model_validate(user)
    finally:
        db.close()