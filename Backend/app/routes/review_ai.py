
from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import List
from pydantic import BaseModel
from app.agents.review_langgraph.langgraph_agentic_review import build_agentic_review_graph, AgenticState  # type: ignore[attr-defined]
from app.agents.review_langgraph.langgraph_review_task import create_checkout_cleaning_task
from app.dependencies import get_db
from app.repositories.review_repository import ReviewRepository
from app.services.housekeeping_service import HousekeepingService
from app.services.maintenance_service import MaintenanceService
from app.repositories.housekeeping_repository import HousekeepingRepository
from app.repositories.maintenance_repository import MaintenanceRepository
from app.repositories.room_repository import RoomRepository


class IssueIn(BaseModel):
    room_id: int
    type: str
    desc: str
    date: str | None = None

router = APIRouter(tags=["AI"])

# DB'deki yorumları al, agentic analiz et, rapor döndür
@router.get("/auto-report")
def auto_report(
    period: str = Query("daily", enum=["daily", "weekly"]),
    db: Session = Depends(get_db),
):
    repo = ReviewRepository(db)
    cutoff = datetime.utcnow() - (timedelta(days=1) if period == "daily" else timedelta(days=7))
    reviews = repo.get_reviews_since(cutoff)
    review_texts = [f"Oda {r.room_id}: {r.text}" for r in reviews]
    if not review_texts:
        return {"report": "Bu dönemde yorum bulunamadı.", "detected_issues": [], "generated_tasks": []}
    graph = build_agentic_review_graph(db)
    state: AgenticState = {
        "messages": [{"role": "user", "content": t} for t in review_texts],
        "cleaning_issues": [],
        "maintenance_issues": [],
        "cleaning_tasks_created": [],
        "maintenance_tasks_created": [],
        "report": None,
        "eval_result": None,
        "eval_feedback": None,
        "iteration": 0,
    }
    result = graph.invoke(state)

    cleaning_tasks = result.get("cleaning_tasks_created") or []
    maintenance_tasks = result.get("maintenance_tasks_created") or []
    cleaning_issues = result.get("cleaning_issues") or []
    maintenance_issues = result.get("maintenance_issues") or []

    # Classifier'ın tespit ettiği sorunlar — oluşturulan görevler auto_assigned
    assigned_cleaning_rooms = {t["room_id"] for t in cleaning_tasks}
    assigned_maintenance_rooms = {t["room_id"] for t in maintenance_tasks}

    detected_issues = []
    for issue in cleaning_issues:
        detected_issues.append({
            "room_id": issue.get("room_id"),
            "type": "cleaning",
            "desc": issue.get("description", ""),
            "date": datetime.now(timezone.utc).isoformat(),
            "auto_assigned": issue.get("room_id") in assigned_cleaning_rooms,
        })
    for issue in maintenance_issues:
        detected_issues.append({
            "room_id": issue.get("room_id"),
            "type": "maintenance",
            "desc": issue.get("description", ""),
            "date": datetime.now(timezone.utc).isoformat(),
            "auto_assigned": issue.get("room_id") in assigned_maintenance_rooms,
        })

    generated_tasks = [
        {"task_type": t["type"], "room_id": t["room_id"], "desc": t["description"], "date": t["date"]}
        for t in cleaning_tasks + maintenance_tasks
    ]

    return {
        "report": result.get("report") or "Analiz tamamlandı.",
        "detected_issues": detected_issues,
        "generated_tasks": generated_tasks,
    }

# Agentic (LLM+tools+evaluator+loop) tek akış endpointi
@router.post("/analyze-reviews")
def agentic_analyze_reviews(
    reviews: list[str] = Body(...),
    db: Session = Depends(get_db),
):

    graph = build_agentic_review_graph(db)
    state: AgenticState = {
        "messages": [{"role": "user", "content": r} for r in reviews],
        "cleaning_issues": [],
        "maintenance_issues": [],
        "cleaning_tasks_created": [],
        "maintenance_tasks_created": [],
        "report": None,
        "eval_result": None,
        "eval_feedback": None,
        "iteration": 0,
    }
    result = graph.invoke(state)
    return result

# Seçili maddeler için görev ata
@router.post("/assign-selected-tasks")
def assign_selected_tasks(
    issues: List[IssueIn] = Body(...),
    db: Session = Depends(get_db),
):
    housekeeping_repo = HousekeepingRepository(db)
    maintenance_repo = MaintenanceRepository(db)
    room_repo = RoomRepository(db)
    housekeeping_svc = HousekeepingService(housekeeping_repo, room_repo)
    maintenance_svc = MaintenanceService(maintenance_repo, room_repo)
    created_tasks = []
    # --- Detected issues state güncellemesi için ---
    # Varsayım: detected_issues state'i bir şekilde erişilebilir olmalı (ör. DB, cache, dosya, vs.)
    # Burada örnek olarak global bir değişken gibi simüle edelim (gerçek uygulamada uygun şekilde entegre edilmeli)
    try:
        from app.agents.review_langgraph.langgraph_agentic_review import _issues_buffer
    except ImportError:
        _issues_buffer = None

    for issue in issues:
        if issue.type in ("cleaning", "temizlik"):
            task = housekeeping_svc.create_task({
                "room_id": issue.room_id,
                "notes": issue.desc,
                "status": "beklemede",
            })
            created_tasks.append({
                "task_type": "cleaning",
                "room_id": issue.room_id,
                "desc": issue.desc,
                "date": str(datetime.utcnow().date()),
                "task_id": getattr(task, "id", None),
            })
        else:
            # Oda numarasını DB'den al
            room = room_repo.get_room_by_id(issue.room_id)
            room_label = room.room_number if room else str(issue.room_id)
            task = maintenance_svc.create_ticket({
                "room_id": issue.room_id,
                "title": f"Oda {room_label} - {issue.type}",
                "description": issue.desc,
                "status": "açık",
            })
            created_tasks.append({
                "task_type": "maintenance",
                "room_id": issue.room_id,
                "desc": issue.desc,
                "date": str(datetime.utcnow().date()),
                "task_id": getattr(task, "id", None),
            })
        # --- assigned flag'ini güncelle ---
        # Eğer _issues_buffer erişilebiliyorsa, ilgili sorunun assigned alanını True yap
        if _issues_buffer is not None:
            for buf_issue in _issues_buffer:
                if (
                    buf_issue["room_id"] == issue.room_id and
                    buf_issue["type"] == issue.type and
                    buf_issue["desc"] == issue.desc
                ):
                    buf_issue["assigned"] = True
    return {"created_tasks": created_tasks}


# Checkout sonrası temizlik görevi
@router.post("/checkout-cleaning-task")
def checkout_cleaning_task(
    room_id: int = Body(...),
    db: Session = Depends(get_db),
):
    task = create_checkout_cleaning_task(room_id, db)
    return {"created_task": task}