
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db
from app.services.maintenance_service import MaintenanceService
from app.repositories.maintenance_repository import MaintenanceRepository
from app.repositories.room_repository import RoomRepository
from app.schemas.maintenance import (
    MaintenanceTicket,
    MaintenanceTicketCreate,
    MaintenanceTicketUpdate,
    MaintenanceTicketAssign,
    MaintenanceTicketWithRoom
)

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])


@router.get("/", response_model=List[MaintenanceTicket])
def get_all_tickets(db: Session = Depends(get_db)):
    """Tüm ticketları getir"""
    maintenance_repo = MaintenanceRepository(db)
    room_repo = RoomRepository(db)
    service = MaintenanceService(maintenance_repo, room_repo)
    return service.get_all_tickets()


@router.get("/open", response_model=List[MaintenanceTicket])
def get_open_tickets(db: Session = Depends(get_db)):
    """Açık ticketları getir"""
    maintenance_repo = MaintenanceRepository(db)
    room_repo = RoomRepository(db)
    service = MaintenanceService(maintenance_repo, room_repo)
    return service.get_open_tickets()


@router.get("/room/{room_id}", response_model=List[MaintenanceTicket])
def get_tickets_by_room(room_id: int, db: Session = Depends(get_db)):
    """Oda bazlı ticketları getir"""
    maintenance_repo = MaintenanceRepository(db)
    room_repo = RoomRepository(db)
    service = MaintenanceService(maintenance_repo, room_repo)
    return service.get_tickets_by_room(room_id)


@router.get("/status/{status}", response_model=List[MaintenanceTicket])
def get_tickets_by_status(status: str, db: Session = Depends(get_db)):
    """Duruma göre ticketları getir"""
    maintenance_repo = MaintenanceRepository(db)
    room_repo = RoomRepository(db)
    service = MaintenanceService(maintenance_repo, room_repo)
    return service.get_tickets_by_status(status)


@router.get("/priority/{priority}", response_model=List[MaintenanceTicket])
def get_tickets_by_priority(priority: str, db: Session = Depends(get_db)):
    """Önceliğe göre ticketları getir"""
    maintenance_repo = MaintenanceRepository(db)
    room_repo = RoomRepository(db)
    service = MaintenanceService(maintenance_repo, room_repo)
    return service.get_tickets_by_priority(priority)


@router.get("/technician/{technician_id}", response_model=List[MaintenanceTicket])
def get_tickets_by_technician(technician_id: int, db: Session = Depends(get_db)):
    """Teknisyene atanmış ticketları getir"""
    maintenance_repo = MaintenanceRepository(db)
    room_repo = RoomRepository(db)
    service = MaintenanceService(maintenance_repo, room_repo)
    return service.get_tickets_by_technician(technician_id)


@router.get("/{ticket_id}", response_model=MaintenanceTicket)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """ID'ye göre ticket getir"""
    maintenance_repo = MaintenanceRepository(db)
    room_repo = RoomRepository(db)
    service = MaintenanceService(maintenance_repo, room_repo)
    ticket = service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket bulunamadı")
    return ticket


@router.post("/", response_model=MaintenanceTicket, status_code=201)
def create_ticket(ticket_data: MaintenanceTicketCreate, db: Session = Depends(get_db)):
    """Yeni ticket oluştur"""
    maintenance_repo = MaintenanceRepository(db)
    room_repo = RoomRepository(db)
    service = MaintenanceService(maintenance_repo, room_repo)
    return service.create_ticket(ticket_data.model_dump())


@router.put("/{ticket_id}", response_model=MaintenanceTicket)
def update_ticket(ticket_id: int, update_data: MaintenanceTicketUpdate, db: Session = Depends(get_db)):
    """Ticket güncelle"""
    maintenance_repo = MaintenanceRepository(db)
    room_repo = RoomRepository(db)
    service = MaintenanceService(maintenance_repo, room_repo)
    
    updated = service.update_ticket(ticket_id, update_data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Ticket bulunamadı")
    return updated


@router.post("/{ticket_id}/assign", response_model=MaintenanceTicket)
def assign_technician(ticket_id: int, assign_data: MaintenanceTicketAssign, db: Session = Depends(get_db)):
    """Teknisyen ata"""
    maintenance_repo = MaintenanceRepository(db)
    room_repo = RoomRepository(db)
    service = MaintenanceService(maintenance_repo, room_repo)
    
    updated = service.assign_technician(ticket_id, assign_data.assigned_technician_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Ticket bulunamadı")
    return updated


@router.post("/{ticket_id}/close", response_model=MaintenanceTicket)
def close_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Ticket kapat"""
    maintenance_repo = MaintenanceRepository(db)
    room_repo = RoomRepository(db)
    service = MaintenanceService(maintenance_repo, room_repo)
    
    updated = service.close_ticket(ticket_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Ticket bulunamadı")
    return updated


@router.delete("/{ticket_id}")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Ticket sil"""
    maintenance_repo = MaintenanceRepository(db)
    room_repo = RoomRepository(db)
    service = MaintenanceService(maintenance_repo, room_repo)
    
    deleted = service.delete_ticket(ticket_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ticket bulunamadı")
    return {"message": "Ticket silindi"}


@router.get("/stats/counts")
def get_ticket_counts(db: Session = Depends(get_db)):
    """Ticket sayılarını getir"""
    maintenance_repo = MaintenanceRepository(db)
    room_repo = RoomRepository(db)
    service = MaintenanceService(maintenance_repo, room_repo)
    return {
        "by_status": service.get_ticket_count_by_status(),
        "by_priority": service.get_ticket_count_by_priority()
    }

