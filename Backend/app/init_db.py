import os
from datetime import datetime, timedelta
from app.database import Base, engine, SessionLocal
from app.repositories.user_repository import UserRepository
from app.models.user import RoleEnum
from app.models.room import Room, RoomStatusEnum
from app.models.user import User
from app.models.maintenance import MaintenanceTicket, MaintenanceStatusEnum, PriorityEnum
from app.models.housekeeping import HousekeepingTask, HousekeepingStatusEnum
from app.models.pricing import RoomPricing
from app.models.reservation import Reservation
from app.models.room_feature import RoomFeature
from app.models.review import Review


def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created.")

    db = SessionLocal()
    try:
        _seed_users(db)
        _seed_hotel_data(db)
    finally:
        db.close()


def _seed_users(db):
    repo = UserRepository(db)
    seed_password = os.getenv("SEED_PASSWORD", "Dev@12345!")

    seeds = [
        ("moderator@example.com", seed_password, RoleEnum.MODERATOR),
        ("user@example.com",      seed_password, RoleEnum.USER),
    ]

    for email, password, role in seeds:
        existing = repo.get_by_email(email)
        if not existing:
            repo.create(email, password, role=role)
            print(f"  Created → {email}")
        else:
            from app.utils.security import get_password_hash
            existing.hashed_password = get_password_hash(password)
            db.commit()
            print(f"  Updated password → {email}")

    print(f"\n  Login: moderator@example.com / {seed_password}  (MODERATOR)")
    print(f"  Login: user@example.com       / {seed_password}  (USER)")


def _seed_hotel_data(db):
    if db.query(Room).count() > 0:
        print("  Hotel data already seeded, skipping.")
        return

    # ── 1. Rooms ──────────────────────────────────────────────────────────────
    rooms_raw = [
        # (room_number, floor, room_type, capacity, price_per_night)
        ("101", 1, "Standard", "1 kişilik",   350.0),
        ("102", 1, "Standard", "2 kişilik",   500.0),
        ("103", 1, "Standard", "2 kişilik",   500.0),
        ("104", 1, "Standard", "2 kişilik",   500.0),
        ("201", 2, "Deluxe",   "2 kişilik",   800.0),
        ("202", 2, "Deluxe",   "2 kişilik",   800.0),
        ("203", 2, "Deluxe",   "3 kişilik",   950.0),
        ("204", 2, "Deluxe",   "2 kişilik",   800.0),
        ("301", 3, "Suite",    "2 kişilik",  1400.0),
        ("302", 3, "Suite",    "2+1 kişilik",1500.0),
        ("303", 3, "Suite",    "4 kişilik",  1800.0),
    ]

    rooms = []
    for num, floor, rtype, cap, price in rooms_raw:
        r = Room(
            room_number=num, floor=floor, room_type=rtype,
            capacity=cap, price_per_night=price,
            status=RoomStatusEnum.ACTIVE, is_clean=True,
        )
        db.add(r)
        rooms.append(r)

    db.commit()
    for r in rooms:
        db.refresh(r)
    print(f"  {len(rooms)} oda oluşturuldu.")

    # ── 2. Room Pricing ───────────────────────────────────────────────────────
    pricing_raw = [
        ("Standard", "1 kişilik",    350.0),
        ("Standard", "2 kişilik",    500.0),
        ("Deluxe",   "2 kişilik",    800.0),
        ("Deluxe",   "3 kişilik",    950.0),
        ("Suite",    "2 kişilik",   1400.0),
        ("Suite",    "2+1 kişilik", 1500.0),
        ("Suite",    "4 kişilik",   1800.0),
    ]
    for rtype, cap, price in pricing_raw:
        db.add(RoomPricing(room_type=rtype, capacity=cap, price_per_night=price, is_active=True))
    db.commit()
    print(f"  {len(pricing_raw)} fiyat kaydı oluşturuldu.")

    # ── 3. Reviews ────────────────────────────────────────────────────────────
    now = datetime.now()
    reviews_raw = [
        (rooms[0].id, "Oda temiz ve bakımlıydı, personel çok yardımsever.", 5, 1),
        (rooms[1].id, "Klima biraz gürültülü çalışıyordu ama genel olarak iyiydi.", 3, 3),
        (rooms[4].id, "Deluxe oda beklentimin çok üzerindeydi, harika manzara!", 5, 2),
        (rooms[6].id, "Banyo fayansında çatlak var, ilgilenilmesi lazım.", 2, 4),
        (rooms[8].id, "Suite çok konforluydu, ailece harika bir tatil geçirdik.", 5, 1),
        (rooms[2].id, "Temizlik iyi fakat yatak biraz sert.", 4, 5),
    ]
    for room_id, text, rating, days_ago in reviews_raw:
        db.add(Review(
            room_id=room_id, text=text, rating=rating,
            created_at=now - timedelta(days=days_ago),
        ))
    db.commit()
    print(f"  {len(reviews_raw)} müşteri yorumu oluşturuldu.")

    # ── 4. Housekeeping Tasks ─────────────────────────────────────────────────
    hk_raw = [
        (rooms[1].id, "Standart temizlik - misafir çıkışı yapıldı"),
        (rooms[5].id, "Derin temizlik gerekli - uzun süreli konaklama"),
        (rooms[7].id, "Yatak çarşafları değiştirilecek"),
    ]
    for room_id, notes in hk_raw:
        db.add(HousekeepingTask(
            room_id=room_id,
            status=HousekeepingStatusEnum.PENDING,
            notes=notes,
        ))
    db.commit()
    print(f"  {len(hk_raw)} temizlik görevi oluşturuldu.")

    # ── 5. Maintenance Tickets ────────────────────────────────────────────────
    mt_raw = [
        (rooms[4].id, "Klima arızası",       "201 no'lu odada klima soğutmuyor",          PriorityEnum.HIGH),
        (rooms[3].id, "Musluk sızıntısı",    "104 no'lu odada banyo musluğu damlatıyor",  PriorityEnum.MEDIUM),
        (rooms[6].id, "Fayans çatlağı",      "203 no'lu odada banyo fayansında çatlak",   PriorityEnum.LOW),
    ]
    for room_id, title, desc, priority in mt_raw:
        db.add(MaintenanceTicket(
            room_id=room_id, title=title, description=desc,
            priority=priority, status=MaintenanceStatusEnum.OPEN,
        ))
    db.commit()
    print(f"  {len(mt_raw)} bakım talebi oluşturuldu.")

    print("\n  Hotel verisi seed tamamlandı.")


if __name__ == "__main__":
    init_db()
