from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.agents.review_langgraph.langgraph_review_task import create_checkout_cleaning_task

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/checkout-cleaning-task")
def checkout_cleaning_task(room_id: int = Body(...), db: Session = Depends(get_db)):
    task = create_checkout_cleaning_task(room_id, db)
    return {"created_task": task}
