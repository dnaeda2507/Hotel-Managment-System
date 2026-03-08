from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db, require_role
from app.models.user import RoleEnum
from app.repositories.room_repository import RoomRepository
from app.repositories.pricing_repository import PricingRepository
from app.services.room_service import RoomService
from app.services.pricing_service import PricingService
from app.schemas.room import RoomCreate, Room as RoomSchema


router = APIRouter(prefix="/rooms", tags=["Rooms"])


def get_room_service(db: Session = Depends(get_db)) -> RoomService:
    """RoomService'i pricing_service ile birlikte oluştur"""
    room_repo = RoomRepository(db)
    pricing_repo = PricingRepository(db)
    pricing_service = PricingService(pricing_repo)
    return RoomService(room_repo, pricing_service=pricing_service)


@router.get("/", response_model=List[RoomSchema])
def get_rooms(service: RoomService = Depends(get_room_service)):
    return service.list_rooms()


@router.get("/available", response_model=List[RoomSchema])
def get_available_rooms(service: RoomService = Depends(get_room_service)):
    """Boş ve temiz odaları getir"""
    return service.check_availability()


@router.post("/", response_model=RoomSchema)
def create_room(
    room_data: RoomCreate,
    service: RoomService = Depends(get_room_service),
    _=Depends(require_role(RoleEnum.MODERATOR)),
):
    existing = service.room_repo.get_room_by_number(room_data.room_number)
    if existing:
        raise HTTPException(status_code=400, detail="Bu oda numarası zaten kayıtlı.")
    return service.create_room(room_data.model_dump())


@router.put("/{room_id}", response_model=RoomSchema)
def update_room(
    room_id: int,
    update_data: dict,
    service: RoomService = Depends(get_room_service),
):
    # Allow any authenticated user to update room status (like cleaning)
    updated_room = service.update_room(room_id, update_data)
    if not updated_room:
        raise HTTPException(status_code=404, detail="Oda güncellenemedi.")
    return updated_room


@router.post("/{room_id}/check-out", response_model=RoomSchema)
def check_out_room(
    room_id: int,
    service: RoomService = Depends(get_room_service),
    _=Depends(require_role(RoleEnum.MODERATOR)),
):
    """Check-out: Oda boşaltılır, otomatik kirli olarak işaretlenir"""
    room = service.check_out(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Oda bulunamadı.")
    return room


@router.post("/{room_id}/check-in", response_model=RoomSchema)
def check_in_room(
    room_id: int,
    service: RoomService = Depends(get_room_service),
    _=Depends(require_role(RoleEnum.MODERATOR)),
):
    """Check-in: Oda dolu olarak işaretlenir"""
    room = service.check_in(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Oda bulunamadı.")
    return room


@router.post("/{room_id}/clean", response_model=RoomSchema)
def mark_room_clean(
    room_id: int,
    service: RoomService = Depends(get_room_service),
):
    """Oda temizlendi olarak işaretlenir - moderator gerekli"""
    room = service.mark_clean(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Oda bulunamadı.")
    return room


@router.post("/{room_id}/dirty", response_model=RoomSchema)
def mark_room_dirty(
    room_id: int,
    service: RoomService = Depends(get_room_service),
):
    """Oda kirli olarak işaretlenir - moderator gerekli"""
    room = service.mark_dirty(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Oda bulunamadı.")
    return room
