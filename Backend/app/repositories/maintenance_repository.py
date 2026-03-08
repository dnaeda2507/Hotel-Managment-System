from sqlalchemy.orm import Session
from app.models.maintenance import MaintenanceTicket, MaintenanceStatusEnum, PriorityEnum
from typing import List, Optional


class MaintenanceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_tickets(self) -> List[MaintenanceTicket]:
        """Tüm ticketları getir"""
        return self.db.query(MaintenanceTicket).order_by(MaintenanceTicket.created_at.desc()).all()

    def get_ticket_by_id(self, ticket_id: int) -> Optional[MaintenanceTicket]:
        """ID'ye göre ticket getir"""
        return self.db.query(MaintenanceTicket).filter(MaintenanceTicket.id == ticket_id).first()

    def get_tickets_by_room(self, room_id: int) -> List[MaintenanceTicket]:
        """Oda bazlı ticketları getir"""
        return self.db.query(MaintenanceTicket).filter(
            MaintenanceTicket.room_id == room_id
        ).order_by(MaintenanceTicket.created_at.desc()).all()

    def get_tickets_by_status(self, status: str) -> List[MaintenanceTicket]:
        """Duruma göre ticketları getir"""
        # FIX: String'i Enum'a çevir
        try:
            status_enum = MaintenanceStatusEnum(status)
        except ValueError:
            return []
        return self.db.query(MaintenanceTicket).filter(
            MaintenanceTicket.status == status_enum
        ).order_by(MaintenanceTicket.created_at.desc()).all()

    def get_tickets_by_priority(self, priority: str) -> List[MaintenanceTicket]:
        """Önceliğe göre ticketları getir"""
        # FIX: String'i Enum'a çevir
        try:
            priority_enum = PriorityEnum(priority)
        except ValueError:
            return []
        return self.db.query(MaintenanceTicket).filter(
            MaintenanceTicket.priority == priority_enum
        ).order_by(MaintenanceTicket.created_at.desc()).all()

    def get_open_tickets(self) -> List[MaintenanceTicket]:
        """Açık ticketları getir"""
        # FIX: Enum kullan
        return self.db.query(MaintenanceTicket).filter(
            MaintenanceTicket.status != MaintenanceStatusEnum.CLOSED
        ).order_by(MaintenanceTicket.created_at.desc()).all()

    def get_tickets_by_technician(self, technician_id: int) -> List[MaintenanceTicket]:
        """Teknisyene atanmış ticketları getir"""
        return self.db.query(MaintenanceTicket).filter(
            MaintenanceTicket.assigned_technician_id == technician_id
        ).order_by(MaintenanceTicket.created_at.desc()).all()

    def create_ticket(self, ticket_data: dict) -> MaintenanceTicket:
        """Yeni ticket oluştur"""
        # FIX: status ve priority string ise Enum'a çevir
        if "status" in ticket_data and isinstance(ticket_data["status"], str):
            ticket_data["status"] = MaintenanceStatusEnum(ticket_data["status"])
        if "priority" in ticket_data and isinstance(ticket_data["priority"], str):
            ticket_data["priority"] = PriorityEnum(ticket_data["priority"])
        db_ticket = MaintenanceTicket(**ticket_data)
        self.db.add(db_ticket)
        self.db.commit()
        self.db.refresh(db_ticket)
        return db_ticket

    def update_ticket(self, ticket_id: int, update_data: dict) -> Optional[MaintenanceTicket]:
        """Ticket güncelle"""
        ticket = self.db.query(MaintenanceTicket).filter(MaintenanceTicket.id == ticket_id).first()
        if ticket:
            # FIX: Enum dönüşümleri
            if "status" in update_data and isinstance(update_data["status"], str):
                update_data["status"] = MaintenanceStatusEnum(update_data["status"])
            if "priority" in update_data and isinstance(update_data["priority"], str):
                update_data["priority"] = PriorityEnum(update_data["priority"])
            for key, value in update_data.items():
                setattr(ticket, key, value)
            self.db.commit()
            self.db.refresh(ticket)
        return ticket

    def assign_technician(self, ticket_id: int, technician_id: int) -> Optional[MaintenanceTicket]:
        """Teknisyen ata"""
        ticket = self.db.query(MaintenanceTicket).filter(MaintenanceTicket.id == ticket_id).first()
        if ticket:
            ticket.assigned_technician_id = technician_id
            # FIX: Enum karşılaştırması ve ataması
            if ticket.status == MaintenanceStatusEnum.OPEN:
                ticket.status = MaintenanceStatusEnum.IN_PROGRESS
            self.db.commit()
            self.db.refresh(ticket)
        return ticket

    def close_ticket(self, ticket_id: int) -> Optional[MaintenanceTicket]:
        """Ticket kapat"""
        from datetime import datetime
        ticket = self.db.query(MaintenanceTicket).filter(MaintenanceTicket.id == ticket_id).first()
        if ticket:
            ticket.status = MaintenanceStatusEnum.CLOSED  # FIX: Enum kullan
            ticket.resolved_at = datetime.now()
            self.db.commit()
            self.db.refresh(ticket)
        return ticket

    def delete_ticket(self, ticket_id: int) -> bool:
        """Ticket sil"""
        ticket = self.db.query(MaintenanceTicket).filter(MaintenanceTicket.id == ticket_id).first()
        if ticket:
            self.db.delete(ticket)
            self.db.commit()
            return True
        return False