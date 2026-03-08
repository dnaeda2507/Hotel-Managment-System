from sqlalchemy import Column, Integer, String
from app.database import Base


class RoomFeature(Base):
    __tablename__ = "room_features"

    id = Column(Integer, primary_key=True, index=True)  # FIX: primary_base → primary_key
    room_type = Column(String, unique=True, index=True)  # Standard, Deluxe, Suite
    features = Column(String)  # "Klima, TV, WiFi" gibi virgülle ayrılmış metin