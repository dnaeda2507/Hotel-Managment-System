from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class HousekeepingTaskBase(BaseModel):
    room_id: int
    notes: str = ""


class HousekeepingTaskCreate(HousekeepingTaskBase):
    pass


class HousekeepingTaskUpdate(BaseModel):
    assigned_staff_id: Optional[int] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class HousekeepingTaskAssign(BaseModel):
    """Personele görev atama"""
    assigned_staff_id: int


class HousekeepingTaskStatusUpdate(BaseModel):
    """Durum güncelleme"""
    status: str  # beklemede, temizleniyor, temiz, onayli


class HousekeepingTask(HousekeepingTaskBase):
    id: int
    assigned_staff_id: Optional[int] = None
    status: str = "beklemede"
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HousekeepingTaskWithRoom(HousekeepingTask):
    """Oda bilgisi ile birlikte görev"""
    room_number: Optional[str] = None
    staff_name: Optional[str] = None

    class Config:
        from_attributes = True

