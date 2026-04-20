from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from datetime import date as date_type
from app.database import SessionLocal


class OccupancyToolInput(BaseModel):
    start_date: str = Field(..., description="Start date YYYY-MM-DD")
    end_date: str = Field(..., description="End date YYYY-MM-DD")


class OccupancyTool(BaseTool):
    name: str = "OccupancyTool"
    description: str = (
        "Fetches hotel occupancy data from the database for demand analysis."
        "Returns total rooms, reserved rooms, occupancy rate, and whether dates are on a weekend."
    )
    args_schema: Type[BaseModel] = OccupancyToolInput

    # DB session injected at runtime — set before kickoff
    db_session: object = None

    class Config:
        arbitrary_types_allowed = True

    def _run(self, start_date: str, end_date: str) -> str:
        # If a DB session was injected before kickoff use it; otherwise create a local session.
        local_session = None
        db = self.db_session
        if db is None:
            try:
                local_session = SessionLocal()
                db = local_session
            except Exception as e:
                return f"Database Error: Could not create local DB session: {e}"

        try:
            from app.repositories.room_repository import RoomRepository
            from app.repositories.reservation_repository import ReservationRepository

            start = date_type.fromisoformat(start_date)
            end = date_type.fromisoformat(end_date)

            room_repo = RoomRepository(db)
            res_repo = ReservationRepository(db)

            rooms = room_repo.get_all_rooms()
            total = len(rooms)

            if total == 0:
                return "No rooms found in database."

            reserved = 0
            for room in rooms:
                is_available = res_repo.check_room_availability(room.id, start, end)
                if not is_available:
                    reserved += 1

            rate = reserved / total
            # Determine whether any date in the requested range falls on a weekend (Sat/Sun)
            try:
                from datetime import timedelta
                days = (end - start).days
                if days < 0:
                    days = 0
                is_weekend = any(((start + timedelta(days=i)).weekday() in (5, 6)) for i in range(days + 1))
            except Exception:
                # Fallback in case of unexpected date arithmetic issues
                is_weekend = start.weekday() in (5, 6)

            # Interpret occupancy
            if rate >= 0.85:
                interpretation = "Very high occupancy — strong demand, significant price increase recommended."
            elif rate >= 0.65:
                interpretation = "High occupancy — good demand, moderate price increase recommended."
            elif rate >= 0.40:
                interpretation = "Medium occupancy — normal demand, minor adjustments recommended."
            else:
                interpretation = "Low occupancy — weak demand, consider competitive pricing to fill rooms."

            return (
                f"Occupancy Report for {start_date} to {end_date}:\n"
                f"  Total rooms: {total}\n"
                f"  Reserved rooms: {reserved}\n"
                f"  Occupancy rate: {rate:.1%}\n"
                f"  Is weekend: {is_weekend}\n"
                f"  Interpretation: {interpretation}"
            )

        except Exception as e:
            return f"Error fetching occupancy data: {str(e)}"
        finally:
            if local_session is not None:
                try:
                    local_session.close()
                except Exception:
                    pass
