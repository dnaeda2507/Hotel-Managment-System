from sqlalchemy import Column, Integer, String, Boolean, Float, Text, Enum as SQLEnum
from app.database import Base
import enum

class RoomStatusEnum(enum.Enum):
    """Oda durumu enum"""
    ACTIVE = "Aktif"
    MAINTENANCE = "Bakımda"
    CLOSED = "Kapalı"

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String, unique=True, index=True, nullable=False)
    floor = Column(Integer, nullable=False, default=1)  # Kat bilgisi
    room_type = Column(String, nullable=False)  # "Suite", "Standard", "Deluxe"
    capacity = Column(String, default="2 kişilik")
    features = Column(String, default="")
    description = Column(Text, default="")  # Oda açıklaması
    service_notes = Column(Text, default="")  # Servis notu (kişi notu)
    price_per_night = Column(Float, nullable=False)
    is_occupied = Column(Boolean, default=False)
    is_clean = Column(Boolean, default=True)
    maintenance_status = Column(String, default="Functional")
    status = Column(SQLEnum(RoomStatusEnum), default=RoomStatusEnum.ACTIVE)  # Oda durumu

