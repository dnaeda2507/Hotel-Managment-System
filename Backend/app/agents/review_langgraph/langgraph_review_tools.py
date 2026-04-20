from langchain_core.tools import Tool
from app.services.housekeeping_service import HousekeepingService
from app.services.maintenance_service import MaintenanceService
from app.repositories.housekeeping_repository import HousekeepingRepository
from app.repositories.maintenance_repository import MaintenanceRepository
from app.repositories.room_repository import RoomRepository


def create_cleaning_task(room_id: int, desc: str, db):
    housekeeping_repo = HousekeepingRepository(db)
    room_repo = RoomRepository(db)
    service = HousekeepingService(housekeeping_repo, room_repo)
    return service.create_task({
        "room_id": room_id,
        "description": desc,
        "status": "pending",
    })


def create_maintenance_task(room_id: int, desc: str, db):
    maintenance_repo = MaintenanceRepository(db)
    room_repo = RoomRepository(db)
    service = MaintenanceService(maintenance_repo, room_repo)
    return service.create_task({
        "room_id": room_id,
        "description": desc,
        "status": "pending",
    })


def get_review_tools(db):
    """db closure ile Tool'lar oluşturulur. Gereksiz import yok."""
    cleaning_tool = Tool(
        name="create_cleaning_task",
        func=lambda args: create_cleaning_task(args["room_id"], args["desc"], db),
        description="Belirtilen oda için temizlik görevi oluşturur.",
    )
    maintenance_tool = Tool(
        name="create_maintenance_task",
        func=lambda args: create_maintenance_task(args["room_id"], args["desc"], db),
        description="Belirtilen oda için bakım görevi oluşturur.",
    )
    return [cleaning_tool, maintenance_tool]