"""
Hotel Review Chat Agent
========================
Admin yorumlar hakkında soru sorar, agent DB'den okuyup cevap üretir.
Her session kendi konuşma geçmişini hatırlar (in-process memory).
"""

import os
import uuid
from datetime import datetime
from typing import Dict, List, Any

from agents import Agent, Runner
from agents.mcp import MCPServerSse
from dotenv import load_dotenv

load_dotenv()

MCP_PORT  = int(os.getenv("MCP_PORT", "8001"))
_MCP_URL  = f"http://127.0.0.1:{MCP_PORT}/sse"
_SSE_PARAMS = {"url": _MCP_URL, "timeout": 30, "sse_read_timeout": 600}

# ── In-process conversation memory ───────────────────────────────────────────
# { session_id: [ {"role": "user"|"assistant", "content": str, "ts": str} ] }
_sessions: Dict[str, List[Dict[str, str]]] = {}
_MAX_HISTORY = 20          # Her session'da en fazla 20 mesaj tut


def _build_context(session_id: str) -> str:
    history = _sessions.get(session_id, [])
    if not history:
        return ""
    lines = ["[Önceki Konuşma]"]
    for m in history[-10:]:          # Son 10 mesajı bağlama ekle
        role = "Admin" if m["role"] == "user" else "Asistan"
        lines.append(f"{role}: {m['content'][:300]}")
    return "\n".join(lines)


def _save_messages(session_id: str, user_msg: str, assistant_msg: str):
    if session_id not in _sessions:
        _sessions[session_id] = []
    ts = datetime.now().strftime("%H:%M")
    _sessions[session_id].append({"role": "user",      "content": user_msg,       "ts": ts})
    _sessions[session_id].append({"role": "assistant",  "content": assistant_msg,  "ts": ts})
    if len(_sessions[session_id]) > _MAX_HISTORY:
        _sessions[session_id] = _sessions[session_id][-_MAX_HISTORY:]


_SYSTEM_PROMPT = """\
Sen bir otel yöneticisinin danışmanısın. Gerçek misafir yorumlarını okuyup yöneticiye net, akıllıca değerlendirmeler sunarsın.

Elinde 6 araç var:
1. get_recent_reviews(days)               – Son N günün yorumları (özet liste)
2. search_reviews(keyword, days)          – DB'de substring ara (LIKE sorgusu; yazım hatalarını yakalamaz)
3. get_reviews_by_room(room_number)       – Belirli odanın yorumları
4. get_reviews_by_rating(min, max, days)  – Puana göre filtrele
5. get_all_reviews_for_analysis(days)     – Tüm yorum metinlerini ham olarak getir; sen analiz et
6. get_review_trends(weeks)              – Haftalık trend

Araç seçimi:
- Genel durum / kategori analizi → get_all_reviews_for_analysis + get_review_trends çağır, tüm metni kendin oku ve kategorize et
- Belirli konu arama → önce search_reviews dene (kısa kelimeyle); 0 sonuç gelirse get_all_reviews_for_analysis çağır ve ilgili yorumları kendin bul (yazım farklılıklarını sen anlarsın, DB anlamaz)
- Oda numarası → get_reviews_by_room
- Puan filtresi → get_reviews_by_rating

Nasıl cevap vereceğin:
- Sadece sorulan konuyu yanıtla. Yemek sorulduysa sadece yemek; resepsiyon gibi başka konular aynı yorumda geçse bile getirme.
- Misafirin söylediklerini doğru temsil et:
    • Yorumda açıkça varsa → direkt söyle ("Misafir tatlıları çok beğendiğini belirtiyor.")
    • Yorumda net değilse → makul çıkarım yap ama belli et ("Çeşitten bahsediyor, genel memnuniyetten bu türleri takdir ettiği anlaşılıyor.")
    • Yorumda hiç yoksa → "Bu konuda net bir ifade yok." de, uydurma.
- Follow-up sorular ("net miydi?", "öneri var mıydı?") için yeni araç çağırma, konuşma hafızandakini değerlendir.
- Somut ol: hangi oda, kaç yıldız, misafirin ifadesi.
- Birden fazla yorumda aynı şikayet tekrarlıyorsa özellikle vurgula.
- Veri yoksa "Bu konuda yorum yok" de.
- Türkçe yaz. "Başka bir konuda yardımcı olabilir miyim?" hiçbir zaman yazma.

{conversation_context}
"""


async def chat(user_message: str, session_id: str | None = None) -> Dict[str, Any]:
    """
    Admin mesajına yanıt ver. Yorumları MCP üzerinden okur ve analiz eder.

    Returns:
        session_id, response, is_new_session
    """
    if not session_id:
        session_id = str(uuid.uuid4())[:8]

    is_new = session_id not in _sessions
    ctx    = _build_context(session_id)
    prompt = _SYSTEM_PROMPT.format(conversation_context=ctx)

    async with MCPServerSse(params=_SSE_PARAMS, client_session_timeout_seconds=120) as mcp_server:
        agent = Agent(
            name="review_analyst",
            instructions=prompt,
            model="gpt-4o-mini",
            mcp_servers=[mcp_server],
        )
        result = await Runner.run(agent, user_message, max_turns=6)

    response = result.final_output or "Yanıt alınamadı."
    _save_messages(session_id, user_message, response)

    return {
        "session_id":  session_id,
        "response":    response,
        "is_new_session": is_new,
        "message_count": len(_sessions.get(session_id, [])),
    }


def get_history(session_id: str) -> List[Dict[str, str]]:
    return _sessions.get(session_id, [])


def clear_session(session_id: str):
    _sessions.pop(session_id, None)


def list_sessions() -> List[str]:
    return list(_sessions.keys())
