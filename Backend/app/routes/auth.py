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
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# FIX: get_db'yi buradan değil dependencies'ten import et
from app.dependencies import get_db                         # ← import
from app.schemas.user import UserCreate, Token, UserOut, Login
from app.models.user import RoleEnum
from app.controllers.auth_controller import login_controller, me_controller
from app.repositories.user_repository import UserRepository

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# FIX: def get_db() KALDIRILDI — artık duplicate yok


@router.post("/login", response_model=Token)
def login(form_data: Login, db: Session = Depends(get_db)):
    return login_controller(form_data.email, form_data.password, db)


@router.get("/me", response_model=UserOut)
def read_me(token: str = Depends(oauth2_scheme)):
    return me_controller(token)


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(form_data: UserCreate, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    if repo.get_by_email(form_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    try:
        # Public register → her zaman USER rolü
        user = repo.create(form_data.email, form_data.password, role=RoleEnum.USER)
        return user
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create user",
        )