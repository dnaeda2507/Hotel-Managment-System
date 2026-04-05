import json
import re
import os
import sys
from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.dependencies import get_db, require_role
from app.models.user import RoleEnum
from app.repositories.pricing_repository import PricingRepository
from app.services.pricing_service import PricingService

router = APIRouter(prefix="", tags=["Pricing AI"])

# --- Schemas ---
class SuggestRequest(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class PriceSuggestionItem(BaseModel):
    room_type: str
    capacity: str
    base_price: float
    suggested_price: float
    change_percent: float
    # Make justification optional and allow empty string so missing AI text won't break validation
    justification: Optional[str] = ""
    # Backwards-compatible field: some frontends expect `reason`
    reason: Optional[str] = ""
    # Frontend legacy: some UI expects `reasons` (plural)
    reasons: Optional[str] = ""
    # Multiplier for suggested/base shown in UI
    multiplier: Optional[float] = 0.0

class SuggestResponse(BaseModel):
    suggestions: List[PriceSuggestionItem]
    overall_strategy: str
    demand_level: str
    date_range: str

class ApplyRequest(BaseModel):
    suggestions: List[PriceSuggestionItem]

# --- Routes ---
@router.post("/suggest", response_model=SuggestResponse)
def get_price_suggestions(
    db: Session = Depends(get_db),
    body: Optional[SuggestRequest] = None, # Hem body hem query desteği için
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    _=Depends(require_role(RoleEnum.MODERATOR)),
):
    # Path Ayarı (Hata almamak için şart)
    current_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
    if project_root not in sys.path: sys.path.insert(0, project_root)

    try:
        from app.agents.hotel_pricing.crew import HotelPricingCrew
        
        # Tarih Karar Mekanizması
        start = (body.start_date if body else None) or start_date or (date.today() + timedelta(days=1)).isoformat()
        end = (body.end_date if body else None) or end_date or (date.today() + timedelta(days=7)).isoformat()

        # DB'den fiyatları çek
        pricing_repo = PricingRepository(db)
        base_prices = {f"{p.room_type} {p.capacity}": p.price_per_night for p in pricing_repo.get_active_pricing()}

        if not base_prices:
            raise HTTPException(status_code=400, detail="Fiyat tablosu boş.")

        # Crew Çalıştır
        crew_instance = HotelPricingCrew()
        crew_instance.set_db_session(db)
        # Provide start_date/end_date as separate variables so task templates can use them
        inputs = {
            "start_date": start,
            "end_date": end,
            "date_range": f"{start} to {end}",
            "base_prices": json.dumps(base_prices, ensure_ascii=False),
        }
        result = crew_instance.crew().kickoff(inputs=inputs)

        # JSON Parse
        raw = result.raw
        try:
            data = json.loads(raw)
        except:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            data = json.loads(match.group(0)) if match else None

        if not data or "suggestions" not in data:
            raise HTTPException(status_code=500, detail="AI çıktı üretemedi.")

        # Ensure each suggestion contains required fields (capacity may be missing from AI).
        # Try to infer missing `capacity` from DB active pricing if possible.
        suggestions = data.get("suggestions", [])
        # Build room_type -> capacities map from DB
        pricing_rows = pricing_repo.get_active_pricing()
        room_type_map: dict = {}
        capacities_set = set()
        for p in pricing_rows:
            room_type_map.setdefault(p.room_type, set()).add(p.capacity)
            capacities_set.add(p.capacity)
        # Prepare capacities sorted by length so longer matches (e.g. '2+1 kişilik') match first
        capacities_sorted = sorted(list(capacities_set), key=lambda x: len(x), reverse=True)

        cleaned_suggestions = []
        for idx, s in enumerate(suggestions):
            # s is expected to be a dict
            if not isinstance(s, dict):
                raise HTTPException(status_code=500, detail=f"Invalid suggestion format at index {idx}: expected object")

            room_type = s.get("room_type")
            capacity = s.get("capacity")

            if not room_type:
                raise HTTPException(status_code=500, detail=f"Suggestion at index {idx} missing 'room_type' field")

            # If capacity missing, try to parse it out from room_type (AI sometimes combines them)
            if not capacity:
                found = None
                rt_lower = room_type.lower()
                for cap in capacities_sorted:
                    if cap.lower() in rt_lower:
                        found = cap
                        break

                if found:
                    # remove capacity substring from room_type
                    pattern = re.escape(found)
                    new_rt = re.sub(pattern, '', room_type, flags=re.IGNORECASE).strip() or room_type
                    room_type = new_rt
                    s["room_type"] = room_type
                    capacity = found
                    s["capacity"] = capacity
                else:
                    # Try DB-inference by exact room_type match
                    caps = list(room_type_map.get(room_type, []))
                    if len(caps) == 1:
                        capacity = caps[0]
                        s["capacity"] = capacity
                    elif len(caps) == 0:
                        raise HTTPException(status_code=500, detail=f"Suggestion for room_type '{room_type}' missing 'capacity' and no pricing entries exist to infer it. Add pricing for this room type in DB or ensure AI returns capacity.")
                    else:
                        raise HTTPException(status_code=500, detail=f"Suggestion for room_type '{room_type}' missing 'capacity' and multiple capacities exist in DB {caps}; cannot infer. Please ensure AI returns 'capacity'.")
                # end if found
            else:
                # capacity provided — but sometimes AI stuck capacity inside room_type; normalize
                rt_lower = room_type.lower()
                for cap in capacities_sorted:
                    if cap.lower() in rt_lower and cap != capacity:
                        # split out the capacity from room_type
                        pattern = re.escape(cap)
                        new_rt = re.sub(pattern, '', room_type, flags=re.IGNORECASE).strip() or room_type
                        room_type = new_rt
                        s["room_type"] = room_type
                        break

            # Normalize numeric fields
            try:
                s["base_price"] = float(s.get("base_price", 0))
            except Exception:
                s["base_price"] = 0.0
            try:
                s["suggested_price"] = float(s.get("suggested_price", s["base_price"]))
            except Exception:
                s["suggested_price"] = s["base_price"]

            # compute change_percent if missing
            if s.get("change_percent") is None:
                try:
                    bp = s["base_price"] or 1.0
                    s["change_percent"] = round((s["suggested_price"] - bp) / bp * 100, 2)
                except Exception:
                    s["change_percent"] = 0.0

            # compute multiplier for frontend (suggested/base)
            try:
                bp = s["base_price"] or 1.0
                s["multiplier"] = round(s["suggested_price"] / bp, 2)
            except Exception:
                s["multiplier"] = 0.0

            # Ensure a `reason` key exists for frontends that expect it
            # Normalize justification from common alternate keys if AI used a different name
            just = s.get("justification") or s.get("reason") or s.get("explanation") or s.get("why") or data.get("overall_strategy") or ""
            s["justification"] = just
            if not s.get("reason"):
                s["reason"] = just
            # ensure plural `reasons` for frontend compatibility
            s["reasons"] = s.get("reason") or s.get("justification") or ""

            cleaned_suggestions.append(s)

        # replace with cleaned list
        data["suggestions"] = cleaned_suggestions

        return SuggestResponse(
            suggestions=data["suggestions"],
            
            overall_strategy=data.get("overall_strategy", ""),
            demand_level=data.get("demand_level", "MEDIUM"),
            date_range=f"{start} to {end}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/apply")
def apply_price_suggestions(
    payload: object = Body(...),
    db: Session = Depends(get_db),
    _=Depends(require_role(RoleEnum.MODERATOR)),
):
    """Accept either an array body ([...]) or an object with `suggestions` key.
    Normalize to a list of dicts and apply suggested_price for matching room_type+capacity.
    """
    pricing_repo = PricingRepository(db)
    pricing_service = PricingService(pricing_repo)
    applied, failed = [], []

    items = []
    try:
        if isinstance(payload, list):
            items = payload
        elif isinstance(payload, dict):
            if "suggestions" in payload and isinstance(payload["suggestions"], list):
                items = payload["suggestions"]
            else:
                # Maybe frontend sent { room_type, capacity, suggested_price } directly
                # or an object wrapper — try to coerce
                # If it's a dict with keys of a single suggestion
                if all(k in payload for k in ("room_type", "capacity", "suggested_price")):
                    items = [payload]
                else:
                    raise HTTPException(status_code=400, detail="Unrecognized payload structure")
        else:
            raise HTTPException(status_code=400, detail="Invalid payload type")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    for item in items:
        if not isinstance(item, dict):
            failed.append("invalid_item")
            continue
        room_type = item.get("room_type")
        capacity = item.get("capacity")
        suggested_price = item.get("suggested_price")
        if room_type is None or capacity is None or suggested_price is None:
            failed.append(f"invalid:{room_type}:{capacity}")
            continue

        existing = pricing_repo.get_price_by_room_type_and_capacity(room_type, capacity)
        if existing:
            try:
                pricing_service.update_pricing(existing.id, {"price_per_night": float(suggested_price)})
                applied.append(f"{room_type} {capacity}")
            except Exception:
                failed.append(f"{room_type} {capacity}")
        else:
            failed.append(f"{room_type} {capacity}")

    return {"applied": applied, "failed": failed, "message": f"{len(applied)} güncellendi."}