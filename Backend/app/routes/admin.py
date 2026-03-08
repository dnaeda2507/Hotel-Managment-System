from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, require_role
from app.repositories.user_repository import UserRepository
from app.schemas.user import AdminUserCreate, UserOut
from app.models.user import RoleEnum

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _ = Depends(require_role(RoleEnum.MODERATOR))):
    repo = UserRepository(db)
    return repo.list_all()


@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user_admin(form_data: AdminUserCreate, db: Session = Depends(get_db), _ = Depends(require_role(RoleEnum.MODERATOR))):
    repo = UserRepository(db)
    if repo.get_by_email(form_data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    # allow moderator to specify role when creating via admin
    role = form_data.role or RoleEnum.USER
    return repo.create(form_data.email, form_data.password, role=role)
