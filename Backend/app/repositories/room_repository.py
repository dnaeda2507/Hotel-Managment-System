from sqlalchemy.orm import Session
from app.models.room import Room
from app.models.room_feature import RoomFeature


class RoomRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_rooms(self):
        return self.db.query(Room).all()

    def get_room_by_id(self, room_id: int):
        return self.db.query(Room).filter(Room.id == room_id).first()

    def get_room_by_number(self, room_number: str):
        return self.db.query(Room).filter(Room.room_number == room_number).first()

    def create_room(self, room_data):
        db_room = Room(**room_data)
        self.db.add(db_room)
        self.db.commit()
        self.db.refresh(db_room)
        return db_room

    def update_room(self, room_id: int, update_data: dict):
        room = self.db.query(Room).filter(Room.id == room_id).first()
        if room:
            for key, value in update_data.items():
                setattr(room, key, value)
            self.db.commit()
            self.db.refresh(room)
        return room

    def check_out(self, room_id: int):
        """Check-out: Oda boşaltılır, otomatik kirli olarak işaretlenir"""
        room = self.db.query(Room).filter(Room.id == room_id).first()
        if room:
            room.is_occupied = False
            room.is_clean = False  # Otomatik kirli
            self.db.commit()
            self.db.refresh(room)
        return room

    def check_in(self, room_id: int):
        """Check-in: Oda dolu olarak işaretlenir"""
        room = self.db.query(Room).filter(Room.id == room_id).first()
        if room:
            room.is_occupied = True
            self.db.commit()
            self.db.refresh(room)
        return room

    def mark_clean(self, room_id: int):
        """Oda temizlendi olarak işaretlenir"""
        room = self.db.query(Room).filter(Room.id == room_id).first()
        if room:
            room.is_clean = True
            self.db.commit()
            self.db.refresh(room)
        return room

    def mark_dirty(self, room_id: int):
        """Oda kirli olarak işaretlenir"""
        room = self.db.query(Room).filter(Room.id == room_id).first()
        if room:
            room.is_clean = False
            self.db.commit()
            self.db.refresh(room)
        return room

    # FIX: Metot class dışındaydı, içine alındı
    def get_features_by_type(self, room_type: str):
        return self.db.query(RoomFeature).filter(RoomFeature.room_type == room_type).first()