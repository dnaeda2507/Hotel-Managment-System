from fastapi import APIRouter, Body, HTTPException

router = APIRouter(prefix="/agents/mcp", tags=["MCP AI"])


@router.post("/chat")
async def mcp_chat(
    message:    str = Body(..., embed=True),
    session_id: str = Body(None, embed=True),
):
    """
    Yorum analizi chat endpoint'i.
    Admin bir mesaj yazar (örn: 'memnuniyet raporu yaz', 'sorunları listele').
    Agent, DB'deki gerçek yorumları okuyarak yanıt üretir.
    Aynı session_id ile devam edilen konuşmalar hafızada tutulur.
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
