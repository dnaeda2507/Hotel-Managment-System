from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db, require_role
from app.models.user import RoleEnum
from app.repositories.room_repository import RoomRepository
from app.repositories.pricing_repository import PricingRepository
from app.services.room_service import RoomService
from app.repositories.reservation_repository import ReservationRepository
from app.dependencies import get_db
from sqlalchemy.orm import Session
from datetime import date as _date
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
def get_available_rooms(
    service: RoomService = Depends(get_room_service),
    db: Session = Depends(get_db),
    check_in_date: _date | None = None,
    check_out_date: _date | None = None,
):
    """Boş ve temiz odaları getir. Opsiyonel `check_in_date` ve `check_out_date` verildiğinde
    tarih aralığına göre müsaitlik kontrolü yapılır (rezerveli odalar filtrelenir).
    """
    rooms = service.check_availability()

    # Eğer tarih aralığı verilmemişse, sadece is_occupied/is_clean filtresi uygulandıktan sonra dön
    if not check_in_date or not check_out_date:
        return rooms

    # Eğer tarihleri string olarak geldiyse parse et (FastAPI genelde date tipinde verir)
    try:
        if isinstance(check_in_date, str):
            from datetime import date as _dt
            check_in_date = _dt.fromisoformat(check_in_date)
        if isinstance(check_out_date, str):
            from datetime import date as _dt
            check_out_date = _dt.fromisoformat(check_out_date)
    except Exception:
        # Hatalı format verildiyse, FastAPI zaten 422 döner; burası ekstra güvenlik
        return rooms

    reservation_repo = ReservationRepository(db)

    available_rooms = []
    for r in rooms:
        is_free = reservation_repo.check_room_availability(r.id, check_in_date, check_out_date)
        if is_free:
            available_rooms.append(r)

    return available_rooms


@router.get("/{room_id}", response_model=RoomSchema)
def get_room(room_id: int, service: RoomService = Depends(get_room_service)):
    """Tek bir oda getir"""
    room = service.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Oda bulunamadı")
    return room


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
