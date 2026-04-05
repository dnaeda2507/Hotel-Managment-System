from app.repositories.review_repository import ReviewRepository
from typing import List


class ReviewService:
    def __init__(self, repo: ReviewRepository):
        self.repo = repo

    def get_reviews_for_room(self, room_id: int):
        return self.repo.get_reviews_for_room(room_id)

    def create_review(self, review_data: dict):
        return self.repo.create_review(review_data)
