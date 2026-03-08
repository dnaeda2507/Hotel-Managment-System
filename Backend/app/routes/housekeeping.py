
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db
from app.services.housekeeping_service import HousekeepingService
from app.repositories.housekeeping_repository import HousekeepingRepository
from app.repositories.room_repository import RoomRepository
from app.schemas.housekeeping import (
    HousekeepingTask,
    HousekeepingTaskCreate,
    HousekeepingTaskUpdate,
    HousekeepingTaskAssign,
    HousekeepingTaskStatusUpdate
)

router = APIRouter(prefix="/housekeeping", tags=["Housekeeping"])


@router.get("/", response_model=List[HousekeepingTask])
def get_all_tasks(db: Session = Depends(get_db)):
    """Tüm görevleri getir"""
    housekeeping_repo = HousekeepingRepository(db)
    room_repo = RoomRepository(db)
    service = HousekeepingService(housekeeping_repo, room_repo)
    return service.get_all_tasks()


@router.get("/pending", response_model=List[HousekeepingTask])
def get_pending_tasks(db: Session = Depends(get_db)):
    """Bekleyen görevleri getir"""
    housekeeping_repo = HousekeepingRepository(db)
    room_repo = RoomRepository(db)
    service = HousekeepingService(housekeeping_repo, room_repo)
    return service.get_pending_tasks()


@router.get("/dirty-rooms", response_model=List[HousekeepingTask])
def get_dirty_rooms(db: Session = Depends(get_db)):
    """Kirli odaları getir"""
    housekeeping_repo = HousekeepingRepository(db)
    room_repo = RoomRepository(db)
    service = HousekeepingService(housekeeping_repo, room_repo)
    return service.get_dirty_rooms()


@router.get("/room/{room_id}", response_model=List[HousekeepingTask])
def get_tasks_by_room(room_id: int, db: Session = Depends(get_db)):
    """Oda bazlı görevleri getir"""
    housekeeping_repo = HousekeepingRepository(db)
    room_repo = RoomRepository(db)
    service = HousekeepingService(housekeeping_repo, room_repo)
    return service.get_tasks_by_room(room_id)


@router.get("/status/{status}", response_model=List[HousekeepingTask])
def get_tasks_by_status(status: str, db: Session = Depends(get_db)):
    """Duruma göre görevleri getir"""
    housekeeping_repo = HousekeepingRepository(db)
    room_repo = RoomRepository(db)
    service = HousekeepingService(housekeeping_repo, room_repo)
    return service.get_tasks_by_status(status)


@router.get("/staff/{staff_id}", response_model=List[HousekeepingTask])
def get_tasks_by_staff(staff_id: int, db: Session = Depends(get_db)):
    """Personele atanmış görevleri getir"""
    housekeeping_repo = HousekeepingRepository(db)
    room_repo = RoomRepository(db)
    service = HousekeepingService(housekeeping_repo, room_repo)
    return service.get_tasks_by_staff(staff_id)


@router.get("/{task_id}", response_model=HousekeepingTask)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """ID'ye göre görev getir"""
    housekeeping_repo = HousekeepingRepository(db)
    room_repo = RoomRepository(db)
    service = HousekeepingService(housekeeping_repo, room_repo)
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Görev bulunamadı")
    return task


@router.post("/", response_model=HousekeepingTask, status_code=201)
def create_task(task_data: HousekeepingTaskCreate, db: Session = Depends(get_db)):
    """Yeni görev oluştur"""
    housekeeping_repo = HousekeepingRepository(db)
    room_repo = RoomRepository(db)
    service = HousekeepingService(housekeeping_repo, room_repo)
    return service.create_task(task_data.model_dump())


@router.post("/room/{room_id}/create", response_model=HousekeepingTask)
def create_task_for_room(room_id: int, notes: str = "", db: Session = Depends(get_db)):
    """Oda için görev oluştur"""
    housekeeping_repo = HousekeepingRepository(db)
    room_repo = RoomRepository(db)
    service = HousekeepingService(housekeeping_repo, room_repo)
    task = service.create_task_for_room(room_id, notes)
    if not task:
        raise HTTPException(status_code=400, detail="Bu oda için aktif görev zaten mevcut")
    return task


@router.put("/{task_id}", response_model=HousekeepingTask)
def update_task(task_id: int, update_data: HousekeepingTaskUpdate, db: Session = Depends(get_db)):
    """Görev güncelle"""
    housekeeping_repo = HousekeepingRepository(db)
    room_repo = RoomRepository(db)
    service = HousekeepingService(housekeeping_repo, room_repo)
    
    updated = service.update_task(task_id, update_data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Görev bulunamadı")
    return updated


@router.post("/{task_id}/assign", response_model=HousekeepingTask)
def assign_staff(task_id: int, assign_data: HousekeepingTaskAssign, db: Session = Depends(get_db)):
    """Personel ata"""
    housekeeping_repo = HousekeepingRepository(db)
    room_repo = RoomRepository(db)
    service = HousekeepingService(housekeeping_repo, room_repo)
    
    updated = service.assign_staff(task_id, assign_data.assigned_staff_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Görev bulunamadı")
    return updated


@router.post("/{task_id}/status", response_model=HousekeepingTask)
def update_status(task_id: int, status_data: HousekeepingTaskStatusUpdate, db: Session = Depends(get_db)):
    """Durum güncelle"""
    housekeeping_repo = HousekeepingRepository(db)
    room_repo = RoomRepository(db)
    service = HousekeepingService(housekeeping_repo, room_repo)
    
    updated = service.update_status(task_id, status_data.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Görev bulunamadı")
    return updated


@router.post("/{task_id}/complete", response_model=HousekeepingTask)
def complete_cleaning(task_id: int, db: Session = Depends(get_db)):
    """Temizlik tamamlandı"""
    housekeeping_repo = HousekeepingRepository(db)
    room_repo = RoomRepository(db)
    service = HousekeepingService(housekeeping_repo, room_repo)
    
    updated = service.complete_cleaning(task_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Görev bulunamadı")
    return updated


@router.post("/{task_id}/approve", response_model=HousekeepingTask)
def approve_task(task_id: int, db: Session = Depends(get_db)):
    """Görevi onayla"""
    housekeeping_repo = HousekeepingRepository(db)
    room_repo = RoomRepository(db)
    service = HousekeepingService(housekeeping_repo, room_repo)
    
    approved = service.approve_task(task_id)
    if not approved:
        raise HTTPException(status_code=404, detail="Görev bulunamadı")
    return approved


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Görev sil"""
    housekeeping_repo = HousekeepingRepository(db)
    room_repo = RoomRepository(db)
    service = HousekeepingService(housekeeping_repo, room_repo)
    
    deleted = service.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Görev bulunamadı")
    return {"message": "Görev silindi"}


@router.get("/stats/counts")
def get_task_counts(db: Session = Depends(get_db)):
    """Görev sayılarını getir"""
    housekeeping_repo = HousekeepingRepository(db)
    room_repo = RoomRepository(db)
    service = HousekeepingService(housekeeping_repo, room_repo)
    return service.get_task_count_by_status()


@router.get("/stats/pending-count")
def get_pending_count(db: Session = Depends(get_db)):
    """Bekleyen görev sayısı"""
    housekeeping_repo = HousekeepingRepository(db)
    room_repo = RoomRepository(db)
    service = HousekeepingService(housekeeping_repo, room_repo)
    return {"pending_count": service.get_pending_count()}

