from sqlalchemy.orm import Session
from app.models.housekeeping import HousekeepingTask, HousekeepingStatusEnum
from typing import List, Optional


class HousekeepingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_tasks(self) -> List[HousekeepingTask]:
        """Tüm görevleri getir"""
        return self.db.query(HousekeepingTask).order_by(HousekeepingTask.created_at.desc()).all()

    def get_task_by_id(self, task_id: int) -> Optional[HousekeepingTask]:
        """ID'ye göre görev getir"""
        return self.db.query(HousekeepingTask).filter(HousekeepingTask.id == task_id).first()

    def get_tasks_by_room(self, room_id: int) -> List[HousekeepingTask]:
        """Oda bazlı görevleri getir"""
        return self.db.query(HousekeepingTask).filter(
            HousekeepingTask.room_id == room_id
        ).order_by(HousekeepingTask.created_at.desc()).all()

    def get_tasks_by_status(self, status: str) -> List[HousekeepingTask]:
        """Duruma göre görevleri getir"""
        # FIX: String'i Enum'a çevir
        try:
            status_enum = HousekeepingStatusEnum(status)
        except ValueError:
            return []
        return self.db.query(HousekeepingTask).filter(
            HousekeepingTask.status == status_enum
        ).order_by(HousekeepingTask.created_at.desc()).all()

    def get_pending_tasks(self) -> List[HousekeepingTask]:
        """Bekleyen görevleri getir"""
        # FIX: String yerine Enum kullan
        return self.db.query(HousekeepingTask).filter(
            HousekeepingTask.status == HousekeepingStatusEnum.PENDING
        ).order_by(HousekeepingTask.created_at.desc()).all()

    def get_dirty_rooms(self) -> List[HousekeepingTask]:
        """Kirli odaları getir (status: beklemede veya temizleniyor)"""
        # FIX: String list yerine Enum list kullan
        return self.db.query(HousekeepingTask).filter(
            HousekeepingTask.status.in_([
                HousekeepingStatusEnum.PENDING,
                HousekeepingStatusEnum.IN_PROGRESS
            ])
        ).order_by(HousekeepingTask.created_at.desc()).all()

    def get_tasks_by_staff(self, staff_id: int) -> List[HousekeepingTask]:
        """Personele atanmış görevleri getir"""
        return self.db.query(HousekeepingTask).filter(
            HousekeepingTask.assigned_staff_id == staff_id
        ).order_by(HousekeepingTask.created_at.desc()).all()

    def get_active_task_for_room(self, room_id: int) -> Optional[HousekeepingTask]:
        """Oda için aktif görev var mı?"""
        # FIX: Enum kullan
        return self.db.query(HousekeepingTask).filter(
            HousekeepingTask.room_id == room_id,
            HousekeepingTask.status.in_([
                HousekeepingStatusEnum.PENDING,
                HousekeepingStatusEnum.IN_PROGRESS
            ])
        ).first()

    def create_task(self, task_data: dict) -> HousekeepingTask:
        """Yeni görev oluştur"""
        # FIX: status string ise Enum'a çevir
        if "status" in task_data and isinstance(task_data["status"], str):
            task_data["status"] = HousekeepingStatusEnum(task_data["status"])
        db_task = HousekeepingTask(**task_data)
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def update_task(self, task_id: int, update_data: dict) -> Optional[HousekeepingTask]:
        """Görev güncelle"""
        task = self.db.query(HousekeepingTask).filter(HousekeepingTask.id == task_id).first()
        if task:
            # FIX: status string ise Enum'a çevir
            if "status" in update_data and isinstance(update_data["status"], str):
                update_data["status"] = HousekeepingStatusEnum(update_data["status"])
            for key, value in update_data.items():
                setattr(task, key, value)
            self.db.commit()
            self.db.refresh(task)
        return task

    def assign_staff(self, task_id: int, staff_id: int) -> Optional[HousekeepingTask]:
        """Personel ata"""
        task = self.db.query(HousekeepingTask).filter(HousekeepingTask.id == task_id).first()
        if task:
            task.assigned_staff_id = staff_id
            # FIX: Enum karşılaştırması
            if task.status == HousekeepingStatusEnum.PENDING:
                task.status = HousekeepingStatusEnum.IN_PROGRESS
            self.db.commit()
            self.db.refresh(task)
        return task

    def update_status(self, task_id: int, status: str) -> Optional[HousekeepingTask]:
        """Durum güncelle"""
        from datetime import datetime
        task = self.db.query(HousekeepingTask).filter(HousekeepingTask.id == task_id).first()
        if task:
            # FIX: String'i Enum'a çevir
            try:
                status_enum = HousekeepingStatusEnum(status)
            except ValueError:
                return None
            task.status = status_enum
            if status_enum == HousekeepingStatusEnum.CLEAN:
                task.completed_at = datetime.now()
            self.db.commit()
            self.db.refresh(task)
        return task

    def approve_task(self, task_id: int) -> Optional[HousekeepingTask]:
        """Görevi onayla"""
        from datetime import datetime
        task = self.db.query(HousekeepingTask).filter(HousekeepingTask.id == task_id).first()
        if task:
            task.status = HousekeepingStatusEnum.APPROVED  # FIX: Enum kullan
            task.completed_at = datetime.now()
            self.db.commit()
            self.db.refresh(task)
        return task

    def delete_task(self, task_id: int) -> bool:
        """Görev sil"""
        task = self.db.query(HousekeepingTask).filter(HousekeepingTask.id == task_id).first()
        if task:
            self.db.delete(task)
            self.db.commit()
            return True
        return False