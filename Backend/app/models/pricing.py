from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class RoomPricing(Base):
    """
    Oda Fiyatlandırma Tablosu
    Oda tipi ve kişi sayısına göre fiyat belirlenir
    """
    __tablename__ = "room_pricing"

    id = Column(Integer, primary_key=True, index=True)
    room_type = Column(String, nullable=False)  # "Standard", "Deluxe", "Suite"
    capacity = Column(String, nullable=False)   # "1 kişilik", "2 kişilik", "2+1 kişilik", "3 kişilik", "3+1 kişilik", "4 kişilik"
    price_per_night = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

