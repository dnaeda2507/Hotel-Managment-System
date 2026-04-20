from app.services.housekeeping_service import HousekeepingService
from app.repositories.housekeeping_repository import HousekeepingRepository
from app.repositories.room_repository import RoomRepository


def create_cleaning_task_for_checkout(room_id: int, db):
    """Oda çıkış (check-out) sonrası temizlik görevi oluşturur."""
    housekeeping_repo = HousekeepingRepository(db)
    room_repo = RoomRepository(db)
    service = HousekeepingService(housekeeping_repo, room_repo)
    task = service.create_task({
        "room_id": room_id,
        "description": "Oda çıkış sonrası temizlik",
        "status": "pending",
    })
    return task