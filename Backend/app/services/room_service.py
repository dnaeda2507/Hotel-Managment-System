from app.services.pricing_service import PricingService
from app.repositories.room_repository import RoomRepository
from fastapi import HTTPException


class RoomService:
    CAPACITIES = [
        "1 kişilik", "2 kişilik", "2+1 kişilik",
        "3 kişilik", "3+1 kişilik", "4 kişilik"
    ]

    def __init__(self, room_repo: RoomRepository, pricing_service: PricingService = None):
        self.room_repo = room_repo
        self.pricing_service = pricing_service

    def create_room(self, room_data: dict):
        if not self.pricing_service:
            raise HTTPException(status_code=500, detail="Pricing service not initialized")

        room_type = room_data.get("room_type")
        capacity = room_data.get("capacity")

        pricing = self.pricing_service.get_price_for_room(room_type, capacity)
        if pricing is None:
            raise HTTPException(
                status_code=400,
                detail=f"{room_type} tipi ve {capacity} kapasitesi için fiyat tanımlanmamış."
            )
        room_data["price_per_night"] = pricing.price_per_night

        feature_entry = self.room_repo.get_features_by_type(room_type)
        room_data["features"] = feature_entry.features if feature_entry else "Standart Oda Özellikleri"

        return self.room_repo.create_room(room_data)

    def list_rooms(self):
        return self.room_repo.get_all_rooms()

    def get_room(self, room_id: int):
        return self.room_repo.get_room_by_id(room_id)

    def update_room(self, room_id: int, update_data: dict):
        return self.room_repo.update_room(room_id, update_data)

    def check_availability(self):
        rooms = self.room_repo.get_all_rooms()
        return [r for r in rooms if not r.is_occupied and r.is_clean]

    def check_out(self, room_id: int):
        return self.room_repo.check_out(room_id)

    def check_in(self, room_id: int):
        return self.room_repo.check_in(room_id)

    def mark_clean(self, room_id: int):
        return self.room_repo.mark_clean(room_id)

    def mark_dirty(self, room_id: int):
        return self.room_repo.mark_dirty(room_id)

    def get_capacities(self):
        return self.CAPACITIES