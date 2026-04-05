from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime


class ReservationBase(BaseModel):
    room_id: int
    guest_name: str
    guest_email: str
    guest_phone: str = ""
    guest_id_number: str = ""
    guest_count: int = 1
    special_requests: str = ""
    check_in_date: date
    check_out_date: date
    notes: str = ""


class ReservationCreate(ReservationBase):
    pass


class ReservationUpdate(BaseModel):
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None
    guest_phone: Optional[str] = None
    guest_id_number: Optional[str] = None
    guest_count: Optional[int] = None
    special_requests: Optional[str] = None
    check_in_date: Optional[date] = None
    check_out_date: Optional[date] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class ReservationStatusUpdate(BaseModel):
    status: str  # beklemede, onaylandı, giriş_yapıldı, çıkış_yapıldı, iptal_edildi


class Reservation(ReservationBase):
    id: int
    price_per_night: float
    total_nights: int
    total_price: float
    status: str
    actual_check_in: Optional[datetime] = None
    actual_check_out: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReservationWithRoom(Reservation):
    room_number: Optional[str] = None
    room_type: Optional[str] = None
    capacity: Optional[str] = None
    features: Optional[str] = None

    class Config:
        from_attributes = True


class AvailabilityCheck(BaseModel):
    room_id: int
    check_in_date: date
    check_out_date: date


class AvailabilityResponse(BaseModel):
    available: bool
    room_id: int
    check_in_date: date
    check_out_date: date
    price_per_night: Optional[float] = None
    total_nights: Optional[int] = None
    total_price: Optional[float] = None
    message: str = ""