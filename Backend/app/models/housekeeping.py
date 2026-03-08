from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import enum


class HousekeepingStatusEnum(enum.Enum):
    """Housekeeping görev durumu"""
    PENDING = "beklemede"
    IN_PROGRESS = "temizleniyor"
    CLEAN = "temiz"
    APPROVED = "onayli"


class HousekeepingTask(Base):
    """
    Housekeeping (Temizlik) Görev Tablosu
    Checkout olan odalar otomatik kirli olarak işaretlenir
    Personele görev atama ve durum takibi
    """
    __tablename__ = "housekeeping_tasks"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    assigned_staff_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(SQLEnum(HousekeepingStatusEnum), default=HousekeepingStatusEnum.PENDING)
    notes = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)