from fastapi import APIRouter, Body, HTTPException
from app.database import SessionLocal

router = APIRouter(prefix="/agents/mcp", tags=["MCP AI"])


# ── Chat ──────────────────────────────────────────────────────────────────────

@router.post("/chat")
async def mcp_chat(
    message:    str = Body(..., embed=True),
    session_id: str = Body(None, embed=True),
):
    """
    Otel yönetim asistanına mesaj gönder.
    İki MCP server'a (reviews + ops) erişimi olan agent yanıt üretir.
    session_id ile aynı konuşma devam ettirilebilir.
    """
    try:
        from app.agents.mcp.hotel_mcp_agent import chat
        return await chat(user_message=message, session_id=session_id)
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}\n{traceback.format_exc()}")


@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Bir session'ın konuşma geçmişini getir."""
    try:
        from app.agents.mcp.hotel_mcp_agent import get_history
        return {"session_id": session_id, "messages": get_history(session_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat/session/{session_id}")
async def clear_chat_session(session_id: str):
    """Bir session'ın konuşma geçmişini temizle."""
    try:
        from app.agents.mcp.hotel_mcp_agent import clear_session
        clear_session(session_id)
        return {"cleared": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Dashboard (direkt DB — hızlı status bar için) ─────────────────────────────

@router.get("/dashboard")
async def mcp_dashboard():
    """
    Günlük otel özeti: doluluk, giriş/çıkış, ortalama puan, bekleyen görevler.
    Frontend status bar için kullanılır.
    """
    from sqlalchemy import text
    from datetime import date

    db = SessionLocal()
    try:
        today = date.today().isoformat()

        with db.bind.connect() as conn:
            occ = conn.execute(text("""
                SELECT COUNT(*) AS total,
                       SUM(CASE WHEN is_occupied THEN 1 ELSE 0 END) AS occupied
                FROM rooms WHERE status = 'Aktif'
            """)).fetchone()

            checkins = conn.execute(text("""
                SELECT COUNT(*) FROM reservations
                WHERE check_in_date = :today AND status != 'iptal_edildi'
            """), {"today": today}).fetchone()

            checkouts = conn.execute(text("""
                SELECT COUNT(*) FROM reservations
                WHERE check_out_date = :today
                  AND status IN ('onaylandı', 'giriş_yapıldı')
            """), {"today": today}).fetchone()

            avg_rating = conn.execute(text("""
                SELECT ROUND(AVG(rating)::numeric, 1) FROM reviews
                WHERE created_at > NOW() - INTERVAL '30 days'
            """)).fetchone()

            pending_clean = conn.execute(text("""
                SELECT COUNT(*) FROM housekeeping_tasks WHERE status = 'beklemede'
            """)).fetchone()

            open_maint = conn.execute(text("""
                SELECT COUNT(*) FROM maintenance_tickets WHERE status = 'açık'
            """)).fetchone()

        total    = occ[0] or 0
        occupied = occ[1] or 0

        return {
            "date":          today,
            "total_rooms":   total,
            "occupied":      occupied,
            "available":     total - occupied,
            "occupancy_pct": round(occupied / total * 100) if total else 0,
            "checkins_today":  checkins[0],
            "checkouts_today": checkouts[0],
            "avg_rating":    float(avg_rating[0]) if avg_rating[0] else None,
            "pending_housekeeping": pending_clean[0],
            "open_maintenance":     open_maint[0],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


# ── Servers info ──────────────────────────────────────────────────────────────

@router.get("/servers")
async def mcp_servers_info():
    """Aktif MCP server'ların bilgisini döndür."""
    return {
        "servers": [
            {
                "name":  "Hotel Review Server",
                "port":  8001,
                "tools": [
                    "get_recent_reviews",
                    "search_reviews",
                    "get_reviews_by_room",
                    "get_reviews_by_rating",
                    "get_all_reviews_for_analysis",
                    "get_review_trends",
                ],
                "resources": ["hotel://reviews/summary"],
            },
            {
                "name":  "Hotel Operations Server",
                "port":  8002,
                "tools": [
                    "get_room_availability",
                    "make_reservation",
                    "get_upcoming_checkouts",
                    "get_pending_housekeeping",
                    "get_open_maintenance",
                    "suggest_room_price",
                ],
                "resources": [
                    "hotel://dashboard/today",
                    "hotel://rooms/available",
                ],
            },
        ]
    }
