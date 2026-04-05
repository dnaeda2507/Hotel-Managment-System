from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    text: str
    rating: Optional[int] = None


class ReviewRead(BaseModel):
    id: int
    room_id: int
    user_id: Optional[int] = None
    rating: Optional[int] = None
    text: str
    created_at: datetime

    class Config:
        orm_mode = True
