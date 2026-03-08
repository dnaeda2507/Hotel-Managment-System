from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import enum


class PriorityEnum(enum.Enum):
    """Arıza öncelik seviyesi"""
    LOW = "düşük"
    MEDIUM = "orta"
    HIGH = "kritik"


class MaintenanceStatusEnum(enum.Enum):
    """Teknik servis ticket durumu"""
    OPEN = "açık"
    IN_PROGRESS = "devam_ediyor"
    CLOSED = "kapalı"


class MaintenanceTicket(Base):
    """
    Teknik Servis Arıza Bildirimi
    Oda bazlı ticket sistemi
    """
    __tablename__ = "maintenance_tickets"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(SQLEnum(PriorityEnum), default=PriorityEnum.MEDIUM)
    status = Column(SQLEnum(MaintenanceStatusEnum), default=MaintenanceStatusEnum.OPEN)
    assigned_technician_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)