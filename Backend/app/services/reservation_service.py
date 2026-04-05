from app.repositories.reservation_repository import ReservationRepository
from app.repositories.room_repository import RoomRepository
from app.models.reservation import ReservationStatusEnum
from fastapi import HTTPException
from datetime import date
from typing import List, Optional


class ReservationService:
    def __init__(self, reservation_repo: ReservationRepository, room_repo: RoomRepository = None):
        self.reservation_repo = reservation_repo
        self.room_repo = room_repo

    def get_all(self) -> List:
        res = self.reservation_repo.get_all()
        if self.room_repo:
            for r in res:
                room = self.room_repo.get_room_by_id(r.room_id)
                if room:
                    setattr(r, 'room_number', room.room_number)
                    setattr(r, 'room_type', room.room_type)
                    setattr(r, 'capacity', room.capacity)
                    setattr(r, 'features', room.features)
        return res

    def get_reservation(self, reservation_id: int):
        r = self.reservation_repo.get_by_id(reservation_id)
        if r and self.room_repo:
            room = self.room_repo.get_room_by_id(r.room_id)
            if room:
                setattr(r, 'room_number', room.room_number)
                setattr(r, 'room_type', room.room_type)
                setattr(r, 'capacity', room.capacity)
                setattr(r, 'features', room.features)
        return r

    def get_by_room(self, room_id: int) -> List:
        res = self.reservation_repo.get_by_room(room_id)
        if self.room_repo:
            room = self.room_repo.get_room_by_id(room_id)
            for r in res:
                if room:
                    setattr(r, 'room_number', room.room_number)
                    setattr(r, 'room_type', room.room_type)
                    setattr(r, 'capacity', room.capacity)
                    setattr(r, 'features', room.features)
        return res

    def get_by_status(self, status: str) -> List:
        res = self.reservation_repo.get_by_status(status)
        if self.room_repo:
            for r in res:
                room = self.room_repo.get_room_by_id(r.room_id)
                if room:
                    setattr(r, 'room_number', room.room_number)
                    setattr(r, 'room_type', room.room_type)
                    setattr(r, 'capacity', room.capacity)
                    setattr(r, 'features', room.features)
        return res

    def get_today_checkins(self) -> List:
        res = self.reservation_repo.get_today_checkins()
        if self.room_repo:
            for r in res:
                room = self.room_repo.get_room_by_id(r.room_id)
                if room:
                    setattr(r, 'room_number', room.room_number)
                    setattr(r, 'room_type', room.room_type)
                    setattr(r, 'capacity', room.capacity)
                    setattr(r, 'features', room.features)
        return res

    def get_today_checkouts(self) -> List:
        res = self.reservation_repo.get_today_checkouts()
        if self.room_repo:
            for r in res:
                room = self.room_repo.get_room_by_id(r.room_id)
                if room:
                    setattr(r, 'room_number', room.room_number)
                    setattr(r, 'room_type', room.room_type)
                    setattr(r, 'capacity', room.capacity)
                    setattr(r, 'features', room.features)
        return res

    def check_availability(self, room_id: int, check_in: date, check_out: date):
        """Müsaitlik kontrolü + fiyat hesaplama"""
        if check_in >= check_out:
            raise HTTPException(status_code=400, detail="Çıkış tarihi giriş tarihinden sonra olmalıdır.")

        if check_in < date.today():
            raise HTTPException(status_code=400, detail="Geçmiş tarihe rezervasyon yapılamaz.")

        room = None
        if self.room_repo:
            room = self.room_repo.get_room_by_id(room_id)
            if not room:
                raise HTTPException(status_code=404, detail="Oda bulunamadı.")

        is_available = self.reservation_repo.check_room_availability(room_id, check_in, check_out)

        total_nights = (check_out - check_in).days
        price_per_night = room.price_per_night if room else 0
        total_price = price_per_night * total_nights

        return {
            "available": is_available,
            "room_id": room_id,
            "check_in_date": check_in,
            "check_out_date": check_out,
            "price_per_night": price_per_night,
            "total_nights": total_nights,
            "total_price": total_price,
            "message": "Oda müsait" if is_available else "Bu tarih aralığında oda dolu",
        }

    def create_reservation(self, data: dict):
        """Yeni rezervasyon oluştur"""
        check_in = data.get("check_in_date")
        check_out = data.get("check_out_date")
        room_id = data.get("room_id")

        if isinstance(check_in, str):
            from datetime import date as date_type
            check_in = date_type.fromisoformat(check_in)
        if isinstance(check_out, str):
            from datetime import date as date_type
            check_out = date_type.fromisoformat(check_out)

        if check_in >= check_out:
            raise HTTPException(status_code=400, detail="Çıkış tarihi giriş tarihinden sonra olmalıdır.")

        is_available = self.reservation_repo.check_room_availability(room_id, check_in, check_out)
        if not is_available:
            raise HTTPException(status_code=409, detail="Bu tarihler için oda müsait değil.")

        room = None
        if self.room_repo:
            room = self.room_repo.get_room_by_id(room_id)
            if not room:
                raise HTTPException(status_code=404, detail="Oda bulunamadı.")

        total_nights = (check_out - check_in).days
        price_per_night = room.price_per_night if room else 0

        data["total_nights"] = total_nights
        data["price_per_night"] = price_per_night
        data["total_price"] = price_per_night * total_nights
        data["status"] = ReservationStatusEnum.CONFIRMED.value

        created = self.reservation_repo.create(data)
        if created and self.room_repo:
            room = self.room_repo.get_room_by_id(created.room_id)
            if room:
                setattr(created, 'room_number', room.room_number)
                setattr(created, 'room_type', room.room_type)
                setattr(created, 'capacity', room.capacity)
                setattr(created, 'features', room.features)
        return created

    def update_reservation(self, reservation_id: int, data: dict):
        reservation = self.reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise HTTPException(status_code=404, detail="Rezervasyon bulunamadı.")

        # Tarihler değiştiyse çakışma kontrolü yap
        new_check_in = data.get("check_in_date", reservation.check_in_date)
        new_check_out = data.get("check_out_date", reservation.check_out_date)
        if data.get("check_in_date") or data.get("check_out_date"):
            is_available = self.reservation_repo.check_room_availability(
                reservation.room_id, new_check_in, new_check_out, exclude_id=reservation_id
            )
            if not is_available:
                raise HTTPException(status_code=409, detail="Bu tarihler için oda müsait değil.")

            total_nights = (new_check_out - new_check_in).days
            data["total_nights"] = total_nights
            data["total_price"] = reservation.price_per_night * total_nights

        return self.reservation_repo.update(reservation_id, data)

    def check_in(self, reservation_id: int):
        """Check-in işlemi: Oda dolu olarak işaretle"""
        reservation = self.reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise HTTPException(status_code=404, detail="Rezervasyon bulunamadı.")
        if reservation.status not in [ReservationStatusEnum.CONFIRMED, ReservationStatusEnum.PENDING]:
            raise HTTPException(status_code=400, detail="Bu rezervasyon için check-in yapılamaz.")

        updated = self.reservation_repo.update_status(reservation_id, ReservationStatusEnum.CHECKED_IN.value)

        if self.room_repo:
            self.room_repo.check_in(reservation.room_id)

        return updated

    def check_out(self, reservation_id: int):
        """Check-out işlemi: Oda boş+kirli olarak işaretle"""
        reservation = self.reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise HTTPException(status_code=404, detail="Rezervasyon bulunamadı.")
        if reservation.status != ReservationStatusEnum.CHECKED_IN:
            raise HTTPException(status_code=400, detail="Bu rezervasyon için check-out yapılamaz.")

        updated = self.reservation_repo.update_status(reservation_id, ReservationStatusEnum.CHECKED_OUT.value)

        if self.room_repo:
            self.room_repo.check_out(reservation.room_id)

        return updated

    def cancel_reservation(self, reservation_id: int):
        """Rezervasyon iptal"""
        reservation = self.reservation_repo.get_by_id(reservation_id)
        if not reservation:
            raise HTTPException(status_code=404, detail="Rezervasyon bulunamadı.")
        if reservation.status in [ReservationStatusEnum.CHECKED_OUT, ReservationStatusEnum.CANCELLED]:
            raise HTTPException(status_code=400, detail="Bu rezervasyon iptal edilemez.")

        return self.reservation_repo.update_status(reservation_id, ReservationStatusEnum.CANCELLED.value)

    def delete_reservation(self, reservation_id: int) -> bool:
        return self.reservation_repo.delete(reservation_id)

    def get_stats(self) -> dict:
        return self.reservation_repo.get_stats()
