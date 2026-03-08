from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RoomPricingBase(BaseModel):
    room_type: str
    capacity: str
    price_per_night: float
    is_active: bool = True


class RoomPricingCreate(RoomPricingBase):
    pass


class RoomPricingUpdate(BaseModel):
    room_type: Optional[str] = None
    capacity: Optional[str] = None
    price_per_night: Optional[float] = None
    is_active: Optional[bool] = None


class RoomPricing(RoomPricingBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RoomPricingResponse(BaseModel):
    """Fiyat sorgulama yanıtı"""
    room_type: str
    capacity: str
    price_per_night: float

    class Config:
        from_attributes = True

