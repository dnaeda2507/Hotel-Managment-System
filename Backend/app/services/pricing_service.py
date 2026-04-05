from app.repositories.pricing_repository import PricingRepository
from typing import List, Optional, Dict


class PricingService:
    """Fiyatlandırma iş mantığı"""

    # Oda tipleri
    ROOM_TYPES = ["Standard", "Deluxe", "Suite"]

    # Kapasite seçenekleri
    CAPACITIES = [
        "1 kişilik",
        "2 kişilik",
        "2+1 kişilik",
        "3 kişilik",
        "3+1 kişilik",
        "4 kişilik"
    ]

    def __init__(self, pricing_repo: PricingRepository):
        self.pricing_repo = pricing_repo

    def get_all_pricing(self) -> List:
        """Tüm fiyatlandırmaları getir"""
        return self.pricing_repo.get_all_pricing()

    def get_active_pricing(self) -> List:
        """Aktif fiyatlandırmaları getir"""
        return self.pricing_repo.get_active_pricing()

    def get_pricing(self, pricing_id: int):
        """ID'ye göre fiyatlandırma getir"""
        return self.pricing_repo.get_pricing_by_id(pricing_id)

    def get_price_for_room(self, room_type: str, capacity: str):
        """Oda tipi ve kapasiteye göre fiyat getir"""
        pricing = self.pricing_repo.get_price_by_room_type_and_capacity(room_type, capacity)
        if pricing:
            return pricing.price_per_night
        return None

    def create_pricing(self, pricing_data: dict):
        """Yeni fiyatlandırma oluştur"""
        # Aynı kombinasyon varsa güncelle
        existing = self.pricing_repo.get_price_by_room_type_and_capacity(
            pricing_data.get("room_type"),
            pricing_data.get("capacity")
        )
        if existing:
            return self.pricing_repo.update_pricing(existing.id, pricing_data)
        return self.pricing_repo.create_pricing(pricing_data)

    def update_pricing(self, pricing_id: int, update_data: dict):
        """Fiyatlandırma güncelle"""
        return self.pricing_repo.update_pricing(pricing_id, update_data)

    def delete_pricing(self, pricing_id: int):
        """Fiyatlandırma sil"""
        return self.pricing_repo.delete_pricing(pricing_id)

    def toggle_active(self, pricing_id: int):
        """Fiyatlandırmayı aktif/pasif yap"""
        return self.pricing_repo.toggle_active(pricing_id)

    def get_room_types(self) -> List[str]:
        """Oda tiplerini getir"""
        return self.ROOM_TYPES

    def get_capacities(self) -> List[str]:
        """Kapasite seçeneklerini getir"""
        return self.CAPACITIES

    def get_pricing_matrix(self) -> List[Dict]:
        """Fiyatlandırma matrisini getir (oda tipi x kapasite)"""
        active_pricing = self.pricing_repo.get_active_pricing()
        matrix = []

        for room_type in self.ROOM_TYPES:
            row = {"room_type": room_type, "prices": {}}
            for capacity in self.CAPACITIES:
                pricing = self.pricing_repo.get_price_by_room_type_and_capacity(room_type, capacity)
                row["prices"][capacity] = pricing.price_per_night if pricing else None
            matrix.append(row)

        return matrix

    def get_or_create_price(self, room_type: str, capacity: str) -> float:
        """Fiyat varsa getir, yoksa varsayılan değer döndür"""
        pricing = self.pricing_repo.get_price_by_room_type_and_capacity(room_type, capacity)
        if pricing:
            return pricing.price_per_night
        # Varsayılan fiyatlar
        default_prices = {
            "Standard": 500,
            "Deluxe": 800,
            "Suite": 1200
        }
        return default_prices.get(room_type, 500)

