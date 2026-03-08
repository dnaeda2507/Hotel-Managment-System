from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from app.models.user import RoleEnum


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    # Public register — role intentionally excluded


class AdminUserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Optional[RoleEnum] = RoleEnum.USER


class Login(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str          # Frontend'e string gönder: "user" / "moderator"
    is_active: bool

    # FIX 1: Pydantic v2 — orm_mode yerine from_attributes
    model_config = {"from_attributes": True}

    # FIX 2: RoleEnum → string'e çevir
    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, v):
        if isinstance(v, RoleEnum):
            return v.value   # "user" veya "moderator"
        return str(v)


class Token(BaseModel):
    access_token: str
    token_type: str
    # FIX 3: Frontend'in role'e göre redirect etmesi için user bilgisini ekle
    user: UserOut


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None