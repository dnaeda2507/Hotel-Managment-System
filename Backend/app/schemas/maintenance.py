from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MaintenanceTicketBase(BaseModel):
    room_id: int
    title: str
    description: str
    priority: str = "orta"  # düşük, orta, kritik
    status: str = "açık"    # açık, devam_ediyor, kapalı


class MaintenanceTicketCreate(MaintenanceTicketBase):
    pass


class MaintenanceTicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assigned_technician_id: Optional[int] = None


class MaintenanceTicketAssign(BaseModel):
    """Teknisyen atama"""
    assigned_technician_id: int


class MaintenanceTicket(MaintenanceTicketBase):
    id: int
    assigned_technician_id: Optional[int] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MaintenanceTicketWithRoom(MaintenanceTicket):
    """Oda bilgisi ile birlikte ticket"""
    room_number: Optional[str] = None

    class Config:
        from_attributes = True

