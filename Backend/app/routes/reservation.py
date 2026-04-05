from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.dependencies import get_db
from app.services.reservation_service import ReservationService
from app.repositories.reservation_repository import ReservationRepository
from app.repositories.room_repository import RoomRepository
from app.schemas.reservation import (
    Reservation,
    ReservationCreate,
    ReservationUpdate,
    ReservationStatusUpdate,
    AvailabilityResponse,
)

router = APIRouter(prefix="/reservations", tags=["Reservations"])


def get_service(db: Session = Depends(get_db)) -> ReservationService:
    return ReservationService(
        ReservationRepository(db),
        RoomRepository(db),
    )


@router.get("/", response_model=List[Reservation])
def get_all(service: ReservationService = Depends(get_service)):
    return service.get_all()


@router.get("/today/checkins", response_model=List[Reservation])
def today_checkins(service: ReservationService = Depends(get_service)):
    return service.get_today_checkins()


@router.get("/today/checkouts", response_model=List[Reservation])
def today_checkouts(service: ReservationService = Depends(get_service)):
    return service.get_today_checkouts()


@router.get("/stats/counts")
def get_stats(service: ReservationService = Depends(get_service)):
    return service.get_stats()


@router.get("/status/{status}", response_model=List[Reservation])
def by_status(status: str, service: ReservationService = Depends(get_service)):
    return service.get_by_status(status)


@router.get("/room/{room_id}", response_model=List[Reservation])
def by_room(room_id: int, service: ReservationService = Depends(get_service)):
    return service.get_by_room(room_id)


@router.get("/availability")
def check_availability(
    room_id: int,
    check_in_date: date,
    check_out_date: date,
    service: ReservationService = Depends(get_service),
):
    return service.check_availability(room_id, check_in_date, check_out_date)


@router.get("/{reservation_id}", response_model=Reservation)
def get_one(reservation_id: int, service: ReservationService = Depends(get_service)):
    res = service.get_reservation(reservation_id)
    if not res:
        raise HTTPException(status_code=404, detail="Rezervasyon bulunamadı.")
    return res


@router.post("/", response_model=Reservation, status_code=201)
def create(data: ReservationCreate, service: ReservationService = Depends(get_service)):
    return service.create_reservation(data.model_dump())


@router.put("/{reservation_id}", response_model=Reservation)
def update(
    reservation_id: int,
    data: ReservationUpdate,
    service: ReservationService = Depends(get_service),
):
    return service.update_reservation(reservation_id, data.model_dump(exclude_unset=True))


@router.post("/{reservation_id}/check-in", response_model=Reservation)
def check_in(reservation_id: int, service: ReservationService = Depends(get_service)):
    return service.check_in(reservation_id)


@router.post("/{reservation_id}/check-out", response_model=Reservation)
def check_out(reservation_id: int, service: ReservationService = Depends(get_service)):
    return service.check_out(reservation_id)


@router.post("/{reservation_id}/cancel", response_model=Reservation)
def cancel(reservation_id: int, service: ReservationService = Depends(get_service)):
    return service.cancel_reservation(reservation_id)


@router.delete("/{reservation_id}")
def delete(reservation_id: int, service: ReservationService = Depends(get_service)):
    deleted = service.delete_reservation(reservation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Rezervasyon bulunamadı.")
    return {"message": "Rezervasyon silindi"}