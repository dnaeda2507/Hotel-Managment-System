"""
Hotel Manager Agent
====================
İki MCP server'ı aynı anda kullanan otel yönetim asistanı.
Ed Donner Lab 4-5 AsyncExitStack pattern'ı.

Bağlandığı server'lar:
  - Hotel Review Server  (port 8001) — 6 yorum analizi aracı + hotel://reviews/summary
  - Hotel Ops Server     (port 8002) — 6 operasyon aracı + hotel://dashboard/today + hotel://rooms/available
"""

import os
import uuid
from contextlib import AsyncExitStack
from datetime import datetime
from typing import Dict, List, Any

from agents import Agent, Runner
from agents.mcp import MCPServerSse
from dotenv import load_dotenv

load_dotenv()

MCP_PORT     = int(os.getenv("MCP_PORT",     "8001"))
MCP_OPS_PORT = int(os.getenv("MCP_OPS_PORT", "8002"))

_SSE_REVIEW = {"url": f"http://127.0.0.1:{MCP_PORT}/sse",     "timeout": 30, "sse_read_timeout": 600}
_SSE_OPS    = {"url": f"http://127.0.0.1:{MCP_OPS_PORT}/sse", "timeout": 30, "sse_read_timeout": 600}

# ── In-process conversation memory ───────────────────────────────────────────
_sessions: Dict[str, List[Dict[str, str]]] = {}
_MAX_HISTORY = 20


def _build_context(session_id: str) -> str:
    history = _sessions.get(session_id, [])
    if not history:
        return ""
    lines = ["[Önceki Konuşma]"]
    for m in history[-10:]:
        role = "Admin" if m["role"] == "user" else "Asistan"
        lines.append(f"{role}: {m['content'][:300]}")
    return "\n".join(lines)


def _save_messages(session_id: str, user_msg: str, assistant_msg: str):
    if session_id not in _sessions:
        _sessions[session_id] = []
    ts = datetime.now().strftime("%H:%M")
    _sessions[session_id].append({"role": "user",     "content": user_msg,      "ts": ts})
    _sessions[session_id].append({"role": "assistant", "content": assistant_msg, "ts": ts})
    if len(_sessions[session_id]) > _MAX_HISTORY:
        _sessions[session_id] = _sessions[session_id][-_MAX_HISTORY:]


_SYSTEM_PROMPT = """\
Sen bir otel yöneticisinin kişisel asistanısın.
Hem misafir yorumlarını analiz edebilir hem de operasyonel sorulara cevap verirsin.

İki server'dan gelen araçlara erişimin var:

YORUM SERVER'I — 6 araç:
  get_recent_reviews(days)              – Son N günün yorumları
  search_reviews(keyword, days)         – Anahtar kelimeyle ara
  get_reviews_by_room(room_number)      – Oda bazlı yorumlar
  get_reviews_by_rating(min, max, days) – Puana göre filtrele
  get_all_reviews_for_analysis(days)    – Ham yorumlar (kendin analiz et)
  get_review_trends(weeks)              – Haftalık trend

OPERASYONel SERVER — 6 araç:
  get_room_availability(check_in, check_out)              – Müsait odalar
  make_reservation(room_id, guest_name, guest_email, ...) – Rezervasyon oluştur
  get_upcoming_checkouts(days)                            – Yaklaşan check-out'lar
  get_pending_housekeeping()                              – Temizlik bekleyen odalar
  get_open_maintenance()                                  – Açık arıza talepleri
  suggest_room_price(room_id)                             – Dinamik fiyat önerisi

MCP RESOURCE'LARI (otomatik bağlam):
  hotel://reviews/summary    – Son 30 günün yorum özeti
  hotel://dashboard/today    – Günlük doluluk, giriş/çıkış, puan, bekleyen görevler
  hotel://rooms/available    – Şu an müsait odalar

Araç seçimi:
  - Yorum / memnuniyet → yorum araçları
  - Oda müsaitlik → get_room_availability
  - Rezervasyon → önce müsaitliği kontrol et, sonra make_reservation
  - Operasyonel durum → dashboard resource + ilgili araç
  - Fiyat → suggest_room_price

Kurallar:
  - Türkçe yaz
  - Somut ol: oda numarası, ID, tutar, tarih
  - Veri yoksa "Bu konuda bilgi yok" de, uydurma
  - "Başka bir konuda yardımcı olabilir miyim?" yazma

{conversation_context}
"""


async def chat(user_message: str, session_id: str | None = None) -> Dict[str, Any]:
    """
    Admin mesajına yanıt ver.
    İki MCP server'ı AsyncExitStack ile aynı anda yönetir.
    """
    if not session_id:
        session_id = str(uuid.uuid4())[:8]

    is_new = session_id not in _sessions
    ctx    = _build_context(session_id)
    prompt = _SYSTEM_PROMPT.format(conversation_context=ctx)

    # Ed Donner Lab 4-5 pattern: AsyncExitStack ile birden fazla server
    async with AsyncExitStack() as stack:
        review_server = await stack.enter_async_context(
            MCPServerSse(params=_SSE_REVIEW, client_session_timeout_seconds=120)
        )
        ops_server = await stack.enter_async_context(
            MCPServerSse(params=_SSE_OPS, client_session_timeout_seconds=120)
        )

        agent = Agent(
            name="hotel_manager",
            instructions=prompt,
            model="gpt-4o-mini",
            mcp_servers=[review_server, ops_server],
        )
        result = await Runner.run(agent, user_message, max_turns=8)

    response = result.final_output or "Yanıt alınamadı."
    _save_messages(session_id, user_message, response)

    return {
        "session_id":     session_id,
        "response":       response,
        "is_new_session": is_new,
        "message_count":  len(_sessions.get(session_id, [])),
    }


def get_history(session_id: str) -> List[Dict[str, str]]:
    return _sessions.get(session_id, [])


def clear_session(session_id: str):
    _sessions.pop(session_id, None)


def list_sessions() -> List[str]:
    return list(_sessions.keys())
