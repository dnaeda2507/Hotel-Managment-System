from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base


class RoleEnum(PyEnum):
    USER = "user"
    MODERATOR = "moderator"


class DepartmentEnum(PyEnum):
    """Kullanıcı departmanı"""
    RECEPTION = "Resepsiyon"
    HOUSEKEEPING = "Temizlik"
    TECHNICAL = "Teknik"
    ADMIN = "Yönetim"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, default="")  # Tam isim
    role = Column(SQLEnum(RoleEnum), nullable=False, default=RoleEnum.USER)
    department = Column(String, default="")  # Departman: "Resepsiyon", "Temizlik", "Teknik"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

