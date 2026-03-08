from pydantic import BaseModel
from typing import Optional

class RoomBase(BaseModel):
    room_number: str
    room_type: str
    capacity: str = "2 kişilik"
    features: str = ""
    description: str = ""
    service_notes: str = ""
    is_clean: bool = True
    is_occupied: bool = False
    maintenance_status: str = "Functional"

class RoomCreate(RoomBase):
    # price_per_night kaldırıldı, kullanıcıdan alınmayacak.
    pass

class Room(RoomBase):
    id: int
    price_per_night: float # Veritabanından dönerken görünecek

    class Config:
        from_attributes = True