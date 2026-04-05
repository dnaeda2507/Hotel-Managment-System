import os
from app.database import Base, engine, SessionLocal
from app.repositories.user_repository import UserRepository
from app.models.user import RoleEnum
from app.models.room import Room
from app.models.user import User
from app.models.maintenance import MaintenanceTicket  # EKLE
from app.models.housekeeping import HousekeepingTask  # EKLE
from app.models.pricing import RoomPricing            # EKLE
from app.models.reservation import Reservation
from app.models.room_feature import RoomFeature          # EKLE
from app.models.review import Review

def init_db():
    # 1. Tabloları oluştur
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created.")

    # 2. Seed
    db = SessionLocal()
    try:
        repo = UserRepository(db)

        # FIX: Şifreyi .env'den oku, hardcode etme
        seed_password = os.getenv("SEED_PASSWORD", "Dev@12345!")

        seeds = [
            ("moderator@example.com", seed_password, RoleEnum.MODERATOR),
            ("user@example.com",      seed_password, RoleEnum.USER),
        ]

        for email, password, role in seeds:
            existing_user = repo.get_by_email(email)
            if not existing_user:
                repo.create(email, password, role=role)
                print(f"  🌱 Created → {email}")
            else:
                # Şifre uyuşmazlığı ihtimaline karşı şifreyi güncelle (Force Reset)
                from app.utils.security import get_password_hash
                existing_user.hashed_password = get_password_hash(password)
                db.commit()
                print(f"  🔄 Updated password for → {email}")

                
        print("\n🔑 Test accounts:")
        print(f"   moderator@example.com  /  {seed_password}  → MODERATOR")
        print(f"   user@example.com       /  {seed_password}  → USER")

    finally:
        db.close()


if __name__ == "__main__":
    init_db()