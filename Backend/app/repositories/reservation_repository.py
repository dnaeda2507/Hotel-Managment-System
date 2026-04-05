from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.reservation import Reservation, ReservationStatusEnum
from typing import List, Optional
from datetime import date


class ReservationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Reservation]:
        return self.db.query(Reservation).order_by(Reservation.created_at.desc()).all()

    def get_by_id(self, reservation_id: int) -> Optional[Reservation]:
        return self.db.query(Reservation).filter(Reservation.id == reservation_id).first()

    def get_by_room(self, room_id: int) -> List[Reservation]:
        return self.db.query(Reservation).filter(
            Reservation.room_id == room_id
        ).order_by(Reservation.check_in_date.desc()).all()

    def get_by_status(self, status: str) -> List[Reservation]:
        try:
            status_enum = ReservationStatusEnum(status)
        except ValueError:
            return []
        return self.db.query(Reservation).filter(
            Reservation.status == status_enum
        ).order_by(Reservation.check_in_date).all()

    def get_by_guest_email(self, email: str) -> List[Reservation]:
        return self.db.query(Reservation).filter(
            Reservation.guest_email == email
        ).order_by(Reservation.created_at.desc()).all()

    def get_active_reservations_for_room(self, room_id: int) -> List[Reservation]:
        """Oda için aktif (iptal edilmemiş ve çıkış yapılmamış) rezervasyonları getir"""
        return self.db.query(Reservation).filter(
            Reservation.room_id == room_id,
            Reservation.status.in_([
                ReservationStatusEnum.PENDING,
                ReservationStatusEnum.CONFIRMED,
                ReservationStatusEnum.CHECKED_IN,
            ])
        ).all()

    def check_room_availability(self, room_id: int, check_in: date, check_out: date, exclude_id: int = None) -> bool:
        """Verilen tarih aralığında oda müsait mi kontrol et"""
        query = self.db.query(Reservation).filter(
            Reservation.room_id == room_id,
            Reservation.status.in_([
                ReservationStatusEnum.PENDING,
                ReservationStatusEnum.CONFIRMED,
                ReservationStatusEnum.CHECKED_IN,
            ]),
            # Tarih çakışması kontrolü
            and_(
                Reservation.check_in_date < check_out,
                Reservation.check_out_date > check_in,
            )
        )
        if exclude_id:
            query = query.filter(Reservation.id != exclude_id)
        return query.first() is None  # True = müsait

    def get_today_checkins(self) -> List[Reservation]:
        from datetime import date as date_type
        today = date_type.today()
        return self.db.query(Reservation).filter(
            Reservation.check_in_date == today,
            Reservation.status == ReservationStatusEnum.CONFIRMED
        ).all()

    def get_today_checkouts(self) -> List[Reservation]:
        from datetime import date as date_type
        today = date_type.today()
        return self.db.query(Reservation).filter(
            Reservation.check_out_date == today,
            Reservation.status == ReservationStatusEnum.CHECKED_IN
        ).all()

    def create(self, data: dict) -> Reservation:
        if "status" in data and isinstance(data["status"], str):
            data["status"] = ReservationStatusEnum(data["status"])
        reservation = Reservation(**data)
        self.db.add(reservation)
        self.db.commit()
        self.db.refresh(reservation)
        return reservation

    def update(self, reservation_id: int, data: dict) -> Optional[Reservation]:
        reservation = self.get_by_id(reservation_id)
        if reservation:
            if "status" in data and isinstance(data["status"], str):
                data["status"] = ReservationStatusEnum(data["status"])
            for key, value in data.items():
                setattr(reservation, key, value)
            self.db.commit()
            self.db.refresh(reservation)
        return reservation

    def update_status(self, reservation_id: int, status: str) -> Optional[Reservation]:
        from datetime import datetime
        reservation = self.get_by_id(reservation_id)
        if reservation:
            try:
                status_enum = ReservationStatusEnum(status)
            except ValueError:
                return None
            reservation.status = status_enum
            if status_enum == ReservationStatusEnum.CHECKED_IN:
                reservation.actual_check_in = datetime.now()
            elif status_enum == ReservationStatusEnum.CHECKED_OUT:
                reservation.actual_check_out = datetime.now()
            self.db.commit()
            self.db.refresh(reservation)
        return reservation

    def delete(self, reservation_id: int) -> bool:
        reservation = self.get_by_id(reservation_id)
        if reservation:
            self.db.delete(reservation)
            self.db.commit()
            return True
        return False

    def get_stats(self) -> dict:
        all_res = self.get_all()
        return {
            "total": len(all_res),
            "beklemede": len([r for r in all_res if r.status == ReservationStatusEnum.PENDING]),
            "onaylandı": len([r for r in all_res if r.status == ReservationStatusEnum.CONFIRMED]),
            "giriş_yapıldı": len([r for r in all_res if r.status == ReservationStatusEnum.CHECKED_IN]),
            "çıkış_yapıldı": len([r for r in all_res if r.status == ReservationStatusEnum.CHECKED_OUT]),
            "iptal_edildi": len([r for r in all_res if r.status == ReservationStatusEnum.CANCELLED]),
        }
