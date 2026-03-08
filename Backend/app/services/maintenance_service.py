from app.repositories.maintenance_repository import MaintenanceRepository
from app.repositories.room_repository import RoomRepository
from app.models.maintenance import MaintenanceStatusEnum, PriorityEnum
from app.models.room import RoomStatusEnum
from typing import List, Optional


class MaintenanceService:
    """Teknik servis iş mantığı"""

    def __init__(self, maintenance_repo: MaintenanceRepository, room_repo: RoomRepository = None):
        self.maintenance_repo = maintenance_repo
        self.room_repo = room_repo

    def get_all_tickets(self) -> List:
        """Tüm ticketları getir"""
        return self.maintenance_repo.get_all_tickets()

    def get_ticket(self, ticket_id: int):
        """ID'ye göre ticket getir"""
        return self.maintenance_repo.get_ticket_by_id(ticket_id)

    def get_tickets_by_room(self, room_id: int) -> List:
        """Oda bazlı ticketları getir"""
        return self.maintenance_repo.get_tickets_by_room(room_id)

    def get_tickets_by_status(self, status: str) -> List:
        """Duruma göre ticketları getir"""
        return self.maintenance_repo.get_tickets_by_status(status)

    def get_tickets_by_priority(self, priority: str) -> List:
        """Önceliğe göre ticketları getir"""
        return self.maintenance_repo.get_tickets_by_priority(priority)

    def get_open_tickets(self) -> List:
        """Açık ticketları getir"""
        return self.maintenance_repo.get_open_tickets()

    def get_tickets_by_technician(self, technician_id: int) -> List:
        """Teknisyene atanmış ticketları getir"""
        return self.maintenance_repo.get_tickets_by_technician(technician_id)

    def create_ticket(self, ticket_data: dict):
        """Yeni ticket oluştur"""
        if self.room_repo:
            room = self.room_repo.get_room_by_id(ticket_data.get("room_id"))
            if room:
                # FIX: String değil Enum kullan
                self.room_repo.update_room(room.id, {"status": RoomStatusEnum.MAINTENANCE})

        return self.maintenance_repo.create_ticket(ticket_data)

    def update_ticket(self, ticket_id: int, update_data: dict):
        """Ticket güncelle"""
        return self.maintenance_repo.update_ticket(ticket_id, update_data)

    def assign_technician(self, ticket_id: int, technician_id: int):
        """Teknisyen ata"""
        return self.maintenance_repo.assign_technician(ticket_id, technician_id)

    def close_ticket(self, ticket_id: int):
        """Ticket kapat"""
        ticket = self.maintenance_repo.get_ticket_by_id(ticket_id)
        if ticket and self.room_repo:
            # FIX: String değil Enum kullan
            self.room_repo.update_room(ticket.room_id, {"status": RoomStatusEnum.ACTIVE})

        return self.maintenance_repo.close_ticket(ticket_id)

    def delete_ticket(self, ticket_id: int):
        """Ticket sil"""
        return self.maintenance_repo.delete_ticket(ticket_id)

    def get_ticket_count_by_status(self) -> dict:
        """Duruma göre ticket sayısı"""
        # FIX: Enum ile karşılaştır
        tickets = self.maintenance_repo.get_all_tickets()
        return {
            "açık": len([t for t in tickets if t.status == MaintenanceStatusEnum.OPEN]),
            "devam_ediyor": len([t for t in tickets if t.status == MaintenanceStatusEnum.IN_PROGRESS]),
            "kapalı": len([t for t in tickets if t.status == MaintenanceStatusEnum.CLOSED]),
        }

    def get_ticket_count_by_priority(self) -> dict:
        """Önceliğe göre ticket sayısı"""
        # FIX: Enum ile karşılaştır
        tickets = self.maintenance_repo.get_all_tickets()
        return {
            "düşük": len([t for t in tickets if t.priority == PriorityEnum.LOW]),
            "orta": len([t for t in tickets if t.priority == PriorityEnum.MEDIUM]),
            "kritik": len([t for t in tickets if t.priority == PriorityEnum.HIGH]),
        }