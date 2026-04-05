
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db
from app.services.pricing_service import PricingService
from app.repositories.pricing_repository import PricingRepository
from app.schemas.pricing import (
    RoomPricing, 
    RoomPricingCreate, 
    RoomPricingUpdate,
    RoomPricingResponse
)

router = APIRouter(prefix="/pricing", tags=["Pricing"])


@router.get("/", response_model=List[RoomPricing])
def get_all_pricing(db: Session = Depends(get_db)):
    """Tüm fiyatlandırma kayıtlarını getir"""
    repo = PricingRepository(db)
    service = PricingService(repo)
    return service.get_all_pricing()


@router.get("/active", response_model=List[RoomPricing])
def get_active_pricing(db: Session = Depends(get_db)):
    """Aktif fiyatlandırma kayıtlarını getir"""
    repo = PricingRepository(db)
    service = PricingService(repo)
    return service.get_active_pricing()


@router.get("/matrix", response_model=List[dict])
def get_pricing_matrix(db: Session = Depends(get_db)):
    """Fiyatlandırma matrisini getir"""
    repo = PricingRepository(db)
    service = PricingService(repo)
    return service.get_pricing_matrix()


@router.get("/room-types")
def get_room_types(db: Session = Depends(get_db)):
    """Oda tiplerini getir"""
    repo = PricingRepository(db)
    service = PricingService(repo)
    return {"room_types": service.get_room_types()}


@router.get("/capacities")
def get_capacities(db: Session = Depends(get_db)):
    """Kapasite seçeneklerini getir"""
    repo = PricingRepository(db)
    service = PricingService(repo)
    return {"capacities": service.get_capacities()}


@router.get("/price/{room_type}/{capacity}")
def get_price(room_type: str, capacity: str, db: Session = Depends(get_db)):
    """Oda tipi ve kapasiteye göre fiyat getir"""
    repo = PricingRepository(db)
    service = PricingService(repo)
    price = service.get_price_for_room(room_type, capacity)
    if price is None:
        raise HTTPException(status_code=404, detail="Bu kombinasyon için fiyat bulunamadı")
    return {"room_type": room_type, "capacity": capacity, "price_per_night": price}


@router.post("/", response_model=RoomPricing, status_code=201)
def create_pricing(pricing_data: RoomPricingCreate, db: Session = Depends(get_db)):
    """Yeni fiyatlandırma oluştur"""
    repo = PricingRepository(db)
    service = PricingService(repo)
    return service.create_pricing(pricing_data.model_dump())


@router.put("/{pricing_id}", response_model=RoomPricing)
def update_pricing(pricing_id: int, update_data: RoomPricingUpdate, db: Session = Depends(get_db)):
    """Fiyatlandırma güncelle"""
    repo = PricingRepository(db)
    service = PricingService(repo)
    
    updated = service.update_pricing(pricing_id, update_data.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Fiyatlandırma bulunamadı")
    return updated


@router.delete("/{pricing_id}")
def delete_pricing(pricing_id: int, db: Session = Depends(get_db)):
    """Fiyatlandırma sil"""
    repo = PricingRepository(db)
    service = PricingService(repo)
    
    deleted = service.delete_pricing(pricing_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Fiyatlandırma bulunamadı")
    return {"message": "Fiyatlandırma silindi"}


@router.patch("/{pricing_id}/toggle", response_model=RoomPricing)
def toggle_pricing_active(pricing_id: int, db: Session = Depends(get_db)):
    """Fiyatlandırmayı aktif/pasif yap"""
    repo = PricingRepository(db)
    service = PricingService(repo)
    
    updated = service.toggle_active(pricing_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Fiyatlandırma bulunamadı")
    return updated


@router.get("/{pricing_id}", response_model=RoomPricing)
def get_pricing_by_id(pricing_id: int, db: Session = Depends(get_db)):
    """ID'ye göre fiyatlandırma getir"""
    repo = PricingRepository(db)
    service = PricingService(repo)
    
    pricing = service.get_pricing(pricing_id)
    if not pricing:
        raise HTTPException(status_code=404, detail="Fiyatlandırma bulunamadı")
    return pricing


@router.get("/type/{room_type}/capacity/{capacity}", response_model=RoomPricing)
def get_pricing_by_type_and_capacity(room_type: str, capacity: str, db: Session = Depends(get_db)):
    """Oda tipi ve kapasiteye göre fiyatlandırma getir"""
    repo = PricingRepository(db)
    service = PricingService(repo)
    # Return the full RoomPricing record (ORM) so response_model=RoomPricing can serialize it
    pricing = repo.get_price_by_room_type_and_capacity(room_type, capacity)
    if not pricing:
        raise HTTPException(status_code=404, detail="Fiyatlandırma bulunamadı")
    return pricing


@router.get("/options")
def get_pricing_options(db: Session = Depends(get_db)):
    """Fiyatlandırma seçeneklerini getir"""
    repo = PricingRepository(db)
    service = PricingService(repo)
    return {
        "room_types": service.get_room_types(),
        "capacities": service.get_capacities()
    }


@router.post("/bulk", response_model=List[RoomPricing])
def bulk_update_pricing(pricing_list: List[RoomPricingCreate], db: Session = Depends(get_db)):
    """Toplu fiyat güncelleme"""
    repo = PricingRepository(db)
    service = PricingService(repo)
    
    results = []
    for pricing_data in pricing_list:
        result = service.create_pricing(pricing_data.model_dump())
        results.append(result)
    return results

