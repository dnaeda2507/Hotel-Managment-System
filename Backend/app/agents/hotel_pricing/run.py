import json
import re
from datetime import date, timedelta


def run_pricing_crew(start_date: str, end_date: str, db_session) -> dict:
 
    from app.agents.hotel_pricing.crew import HotelPricingCrew
    from app.repositories.pricing_repository import PricingRepository

    pricing_repo = PricingRepository(db_session)
    active_prices = pricing_repo.get_active_pricing()

    if not active_prices:
        raise ValueError("Aktif fiyatlandırma yok. Önce fiyat tablosunu doldurun.")

    base_prices = {
        f"{p.room_type} {p.capacity}": p.price_per_night
        for p in active_prices
    }

    inputs = {
        "start_date" : start_date,
        "end_date"   : end_date,
        "date_range" : f"{start_date} to {end_date}",
        "base_prices": json.dumps(base_prices, ensure_ascii=False),
    }

   
    crew = HotelPricingCrew()
    crew.set_db_session(db_session)
    result = crew.crew().kickoff(inputs=inputs)

    # JSON parse et
    try:
        return json.loads(result.raw)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', result.raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        return {"raw": result.raw}