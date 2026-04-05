from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user_optional
from app.repositories.review_repository import ReviewRepository
from app.services.review_service import ReviewService
from app.schemas.review import ReviewCreate, ReviewRead

router = APIRouter(prefix="/rooms", tags=["Reviews"])


@router.get("/{room_id}/reviews", response_model=list[ReviewRead])
def get_room_reviews(room_id: int, db: Session = Depends(get_db)):
    repo = ReviewRepository(db)
    service = ReviewService(repo)
    return service.get_reviews_for_room(room_id)


@router.post("/{room_id}/reviews", response_model=ReviewRead, status_code=201)
def create_room_review(room_id: int, payload: ReviewCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user_optional)):
    repo = ReviewRepository(db)
    service = ReviewService(repo)
    review_data = payload.model_dump()
    review_data["room_id"] = room_id
    if current_user:
        review_data["user_id"] = current_user.id
    created = service.create_review(review_data)
    if not created:
        raise HTTPException(status_code=400, detail="Could not create review")
    return created
