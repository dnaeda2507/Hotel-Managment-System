from sqlalchemy.orm import Session
from app.models.review import Review
from typing import List
from datetime import datetime


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_reviews_since(self, cutoff: datetime) -> List[Review]:
        return self.db.query(Review).filter(Review.created_at >= cutoff).all()

    def get_reviews_for_room(self, room_id: int) -> List[Review]:
        return self.db.query(Review).filter(Review.room_id == room_id).order_by(Review.created_at.desc()).all()

    def create_review(self, review_data: dict) -> Review:
        rev = Review(**review_data)
        self.db.add(rev)
        self.db.commit()
        self.db.refresh(rev)
        return rev
