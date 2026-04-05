from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import enum


class ReservationStatusEnum(enum.Enum):
    PENDING = "beklemede"
    CONFIRMED = "onaylandı"
    CHECKED_IN = "giriş_yapıldı"
    CHECKED_OUT = "çıkış_yapıldı"
    CANCELLED = "iptal_edildi"


class Reservation(Base):
    """
    Rezervasyon Tablosu
    Misafir bilgileri, oda, tarihler ve fiyat içerir
    """
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)

    # Misafir bilgileri
    guest_name = Column(String, nullable=False)
    guest_email = Column(String, nullable=False)
    guest_phone = Column(String, default="")
    guest_id_number = Column(String, default="")  # TC / Pasaport No
    guest_count = Column(Integer, default=1)
    special_requests = Column(Text, default="")

    # Tarihler
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    actual_check_in = Column(DateTime(timezone=True), nullable=True)
    actual_check_out = Column(DateTime(timezone=True), nullable=True)

    # Fiyat
    price_per_night = Column(Float, nullable=False)
    total_nights = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)

    # Durum
    status = Column(SQLEnum(ReservationStatusEnum), default=ReservationStatusEnum.PENDING)
    notes = Column(Text, default="")

    # Zaman damgaları
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())