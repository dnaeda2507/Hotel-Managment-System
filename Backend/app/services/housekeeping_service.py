from app.repositories.housekeeping_repository import HousekeepingRepository
from app.repositories.room_repository import RoomRepository
from app.models.housekeeping import HousekeepingStatusEnum
from typing import List, Optional


class HousekeepingService:
    """Housekeeping (Temizlik) iş mantığı"""

    def __init__(self, housekeeping_repo: HousekeepingRepository, room_repo: RoomRepository = None):
        self.housekeeping_repo = housekeeping_repo
        self.room_repo = room_repo

    def get_all_tasks(self) -> List:
        """Tüm görevleri getir"""
        return self.housekeeping_repo.get_all_tasks()

    def get_task(self, task_id: int):
        """ID'ye göre görev getir"""
        return self.housekeeping_repo.get_task_by_id(task_id)

    def get_tasks_by_room(self, room_id: int) -> List:
        """Oda bazlı görevleri getir"""
        return self.housekeeping_repo.get_tasks_by_room(room_id)

    def get_tasks_by_status(self, status: str) -> List:
        """Duruma göre görevleri getir"""
        return self.housekeeping_repo.get_tasks_by_status(status)

    def get_pending_tasks(self) -> List:
        """Bekleyen görevleri getir"""
        return self.housekeeping_repo.get_pending_tasks()

    def get_dirty_rooms(self) -> List:
        """Kirli odaları getir"""
        return self.housekeeping_repo.get_dirty_rooms()

    def get_tasks_by_staff(self, staff_id: int) -> List:
        """Personele atanmış görevleri getir"""
        return self.housekeeping_repo.get_tasks_by_staff(staff_id)

    def create_task(self, task_data: dict):
        """Yeni görev oluştur"""
        return self.housekeeping_repo.create_task(task_data)

    def create_task_for_room(self, room_id: int, notes: str = "") -> Optional:
        """Oda için görev oluştur"""
        # FIX: Aktif görev varsa None döndür — route 400 fırlatabilsin
        existing = self.housekeeping_repo.get_active_task_for_room(room_id)
        if existing:
            return None  # Route: "Bu oda için aktif görev zaten mevcut" → 400

        task_data = {
            "room_id": room_id,
            "status": HousekeepingStatusEnum.PENDING,  # FIX: Enum kullan
            "notes": notes
        }
        return self.housekeeping_repo.create_task(task_data)

    def update_task(self, task_id: int, update_data: dict):
        """Görev güncelle"""
        return self.housekeeping_repo.update_task(task_id, update_data)

    def assign_staff(self, task_id: int, staff_id: int):
        """Personel ata"""
        return self.housekeeping_repo.assign_staff(task_id, staff_id)

    def update_status(self, task_id: int, status: str):
        """Durum güncelle"""
        task = self.housekeeping_repo.get_task_by_id(task_id)

        # FIX: Enum ile karşılaştır
        if self.room_repo and task:
            try:
                status_enum = HousekeepingStatusEnum(status)
            except ValueError:
                return None
            if status_enum in (HousekeepingStatusEnum.CLEAN, HousekeepingStatusEnum.APPROVED):
                self.room_repo.mark_clean(task.room_id)
            elif status_enum == HousekeepingStatusEnum.PENDING:
                self.room_repo.mark_dirty(task.room_id)

        return self.housekeeping_repo.update_status(task_id, status)

    def approve_task(self, task_id: int):
        """Görevi onayla"""
        task = self.housekeeping_repo.get_task_by_id(task_id)

        # Oda temiz olarak işaretle
        if self.room_repo and task:
            self.room_repo.mark_clean(task.room_id)

        return self.housekeeping_repo.approve_task(task_id)

    def complete_cleaning(self, task_id: int):
        """Temizlik tamamlandı"""
        return self.housekeeping_repo.update_status(task_id, HousekeepingStatusEnum.CLEAN.value)

    def delete_task(self, task_id: int):
        """Görev sil"""
        return self.housekeeping_repo.delete_task(task_id)

    def handle_checkout(self, room_id: int):
        """Checkout sonrası otomatik görev oluştur"""
        if self.room_repo:
            self.room_repo.mark_dirty(room_id)
        return self.create_task_for_room(room_id, "Checkout sonrası temizlik")

    def get_task_count_by_status(self) -> dict:
        """Duruma göre görev sayısı"""
        # FIX: Enum ile karşılaştır
        tasks = self.housekeeping_repo.get_all_tasks()
        return {
            "beklemede": len([t for t in tasks if t.status == HousekeepingStatusEnum.PENDING]),
            "temizleniyor": len([t for t in tasks if t.status == HousekeepingStatusEnum.IN_PROGRESS]),
            "temiz": len([t for t in tasks if t.status == HousekeepingStatusEnum.CLEAN]),
            "onayli": len([t for t in tasks if t.status == HousekeepingStatusEnum.APPROVED]),
        }

    def get_pending_count(self) -> int:
        """Bekleyen görev sayısı"""
        return len(self.housekeeping_repo.get_pending_tasks())