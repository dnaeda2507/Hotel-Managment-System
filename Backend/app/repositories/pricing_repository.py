from sqlalchemy.orm import Session
from app.models.pricing import RoomPricing
from typing import List, Optional


class PricingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_pricing(self) -> List[RoomPricing]:
        """Tüm fiyatlandırma kayıtlarını getir"""
        return self.db.query(RoomPricing).all()

    def get_active_pricing(self) -> List[RoomPricing]:
        """Aktif fiyatlandırma kayıtlarını getir"""
        return self.db.query(RoomPricing).filter(RoomPricing.is_active == True).all()

    def get_pricing_by_id(self, pricing_id: int) -> Optional[RoomPricing]:
        """ID'ye göre fiyatlandırma getir"""
        return self.db.query(RoomPricing).filter(RoomPricing.id == pricing_id).first()

    def get_price_by_room_type_and_capacity(self, room_type: str, capacity: str) -> Optional[RoomPricing]:
        """Oda tipi ve kapasiteye göre fiyat getir"""
        return self.db.query(RoomPricing).filter(
            RoomPricing.room_type == room_type,
            RoomPricing.capacity == capacity,
            RoomPricing.is_active == True
        ).first()

    def create_pricing(self, pricing_data: dict) -> RoomPricing:
        """Yeni fiyatlandırma oluştur"""
        db_pricing = RoomPricing(**pricing_data)
        self.db.add(db_pricing)
        self.db.commit()
        self.db.refresh(db_pricing)
        return db_pricing

    def update_pricing(self, pricing_id: int, update_data: dict) -> Optional[RoomPricing]:
        """Fiyatlandırma güncelle"""
        pricing = self.db.query(RoomPricing).filter(RoomPricing.id == pricing_id).first()
        if pricing:
            for key, value in update_data.items():
                setattr(pricing, key, value)
            self.db.commit()
            self.db.refresh(pricing)
        return pricing

    def delete_pricing(self, pricing_id: int) -> bool:
        """Fiyatlandırma sil (hard delete)"""
        # FIX: Önceden soft delete (is_active=False) yapıyordu, şimdi gerçekten siliyor
        pricing = self.db.query(RoomPricing).filter(RoomPricing.id == pricing_id).first()
        if pricing:
            self.db.delete(pricing)
            self.db.commit()
            return True
        return False

    def deactivate_pricing(self, pricing_id: int) -> bool:
        """Fiyatlandırmayı pasife al (soft delete)"""
        # FIX: Soft delete ayrı bir metot olarak tanımlandı
        pricing = self.db.query(RoomPricing).filter(RoomPricing.id == pricing_id).first()
        if pricing:
            pricing.is_active = False
            self.db.commit()
            return True
        return False

    def toggle_active(self, pricing_id: int) -> Optional[RoomPricing]:
        """Fiyatlandırmayı aktif/pasif yap"""
        pricing = self.db.query(RoomPricing).filter(RoomPricing.id == pricing_id).first()
        if pricing:
            pricing.is_active = not pricing.is_active
            self.db.commit()
            self.db.refresh(pricing)
        return pricing

    def get_all_room_types(self) -> List[str]:
        """Tüm oda tiplerini getir"""
        return [p.room_type for p in self.db.query(RoomPricing.room_type).distinct().all()]

    def get_all_capacities(self) -> List[str]:
        """Tüm kapasiteleri getir"""
        return [p.capacity for p in self.db.query(RoomPricing.capacity).distinct().all()]