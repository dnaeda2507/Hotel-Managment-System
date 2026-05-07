# MCP (Model Context Protocol) — Teknik Dokümantasyon

## Hotel Management System · Yorum Analizi Modülü

---

## 1. MCP Nedir?

**Model Context Protocol (MCP)**, Anthropic tarafından 2024 yılında geliştirilen açık kaynaklı bir standarttır.
LLM'lerin harici araçlara, veri kaynaklarına ve servislere **standart ve güvenli bir protokol** üzerinden bağlanmasını sağlar.

Geleneksel yaklaşımda her tool doğrudan koda gömülürken, MCP'de tool'lar bağımsız bir serviste çalışır ve agent bunları protokol üzerinden **otomatik olarak keşfeder**.

### Temel Bileşenler

| Bileşen | Açıklama |
|---|---|
| **MCP Server** | Tool'ları barındıran bağımsız HTTP servisi |
| **MCP Client** | Agent'ın tool'lara bağlandığı katman |
| **Transport** | Server–client iletişim yöntemi (stdio / SSE) |
| **Tool** | `@mcp.tool()` ile tanımlı, agent'ın çağırabileceği fonksiyon |

---

## 2. Neden MCP?

Bu projede otel yöneticisinin misafir yorumları hakkında serbest dilde soru sorabildiği hafızalı bir chat asistanı geliştirilmiştir.

MCP tercih edilme nedenleri:

- **LLM özerkliği** — Hangi tool'un ne zaman çağrılacağına LLM kendi karar verir; if/else kodu yoktur
- **Otomatik keşif** — Agent başlarken `tools/list` ile tool listesini öğrenir; manuel tanım gerekmez
- **Servis izolasyonu** — MCP server (port 8001) ve backend (port 8000) bağımsız process'lerde çalışır
- **Genişletilebilirlik** — Yeni tool eklemek için sadece `@mcp.tool()` ile fonksiyon yazmak yeterli
- **Standart protokol** — Farklı LLM client'ları aynı server'a bağlanabilir

---

## 3. Transport: SSE (Server-Sent Events)

MCP iki transport destekler:

```
stdio Transport:
  Agent ──subprocess.spawn()──► MCP Server (pipe üzerinden)
  ❌ Windows'ta asyncio event loop çakışması

SSE Transport:
  Agent ──HTTP GET :8001/sse──► MCP Server
  ✅ Tüm platformlarda çalışır
```

Windows ortamında `MCPServerStdio` kullanıldığında `asyncio.create_subprocess_exec`
ile uvicorn'un ProactorEventLoop'u çakışmaktadır.
Bu nedenle **SSE transport** tercih edilmiştir.
Transport katmanı dışında MCP protokolü (mesaj formatı, tool keşfi, tool çağrısı) tamamen aynıdır.

---

## 4. Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────┐
│  Admin (Tarayıcı)  —  MCPDemoPage.tsx                       │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP POST /agents/mcp/chat
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  FastAPI Backend  (port 8000)                               │
│  mcp_ai.py  ──►  hotel_mcp_agent.py                        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  OpenAI Agents SDK                                  │    │
│  │  Agent(model="gpt-4o-mini", mcp_servers=[...])     │    │
│  │  Runner.run(agent, message, max_turns=6)            │    │
│  └──────────────────────┬──────────────────────────────┘    │
└─────────────────────────┼───────────────────────────────────┘
                          │ SSE — HTTP port 8001
                          │
                 ┌────────┴────────┐
                 │  tools/list     │  → 6 tool keşfedilir
                 │  tools/call     │  → tool çağrılır, sonuç döner
                 └────────┬────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│  MCP Server  (port 8001)  —  hotel_mcp_server.py            │
│  FastMCP · mcp.run(transport="sse")                         │
│                                                             │
│  @mcp.tool() get_recent_reviews                             │
│  @mcp.tool() search_reviews                                 │
│  @mcp.tool() get_reviews_by_room                            │
│  @mcp.tool() get_reviews_by_rating                          │
│  @mcp.tool() get_all_reviews_for_analysis                   │
│  @mcp.tool() get_review_trends                              │
│                                                             │
│  Her tool → SQLAlchemy → PostgreSQL (port 5500)            │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. MCP Server — `hotel_mcp_server.py`

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Hotel Review Server")

@mcp.tool()
def search_reviews(keyword: str, days: int = 90) -> str:
    """
    Belirtilen anahtar kelimeyi içeren yorumları ara.
    Belirli bir konuya (klima, temizlik, yemek vb.) odaklanmak için kullan.
    """
    # PostgreSQL: WHERE LOWER(text) LIKE LOWER(:pattern)
    ...

if __name__ == "__main__":
    mcp.settings.host = "127.0.0.1"
    mcp.settings.port = MCP_PORT        # 8001
    mcp.run(transport="sse")
```

### Tool Listesi

| # | Tool | Parametreler | SQL / İşlem |
|---|---|---|---|
| 1 | `get_recent_reviews` | `days=30` | `WHERE created_at > cutoff ORDER BY created_at DESC LIMIT 50` |
| 2 | `search_reviews` | `keyword, days=90` | `WHERE LOWER(text) LIKE LOWER('%keyword%')` |
| 3 | `get_reviews_by_room` | `room_number` | `JOIN rooms WHERE room_number = :rnum` |
| 4 | `get_reviews_by_rating` | `min, max, days=90` | `WHERE rating BETWEEN :min AND :max` |
| 5 | `get_all_reviews_for_analysis` | `days=30` | Ham veri — LLM analiz eder |
| 6 | `get_review_trends` | `weeks=4` | `COUNT(*) + AVG(rating)` haftalık döngü |

---

## 6. MCP Client — `hotel_mcp_agent.py`

```python
from agents import Agent, Runner
from agents.mcp import MCPServerSse

_SSE_PARAMS = {
    "url": "http://127.0.0.1:8001/sse",
    "timeout": 30,
    "sse_read_timeout": 600,
}

async def chat(user_message: str, session_id: str | None = None):
    ctx    = _build_context(session_id)          # önceki 10 mesaj
    prompt = _SYSTEM_PROMPT.format(conversation_context=ctx)

    async with MCPServerSse(params=_SSE_PARAMS,
                            client_session_timeout_seconds=120) as mcp_server:
        agent = Agent(
            name="review_analyst",
            instructions=prompt,
            model="gpt-4o-mini",
            mcp_servers=[mcp_server],
        )
        result = await Runner.run(agent, user_message, max_turns=6)

    _save_messages(session_id, user_message, result.final_output)
    return { "session_id": session_id, "response": result.final_output, ... }
```

---

## 7. MCP Protokol Mesajları

### tools/list — Tool Keşfi

Agent bağlandığında otomatik çalışır:

```json
→ İstek:
{ "jsonrpc": "2.0", "method": "tools/list", "id": 1 }

← Yanıt:
{
  "result": {
    "tools": [
      {
        "name": "search_reviews",
        "description": "Belirtilen anahtar kelimeyi içeren yorumları ara...",
        "inputSchema": {
          "type": "object",
          "properties": {
            "keyword": { "type": "string" },
            "days":    { "type": "integer", "default": 90 }
          },
          "required": ["keyword"]
        }
      },
      ...
    ]
  }
}
```

### tools/call — Tool Çağrısı

LLM "yemek sorunları" sorusunu alınca:

```json
→ İstek:
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "search_reviews",
    "arguments": { "keyword": "yemek", "days": 90 }
  }
}

← Yanıt:
{
  "result": {
    "content": [{
      "type": "text",
      "text": "'yemek' içeren yorumlar (2 adet):\n  [Oda 102] ⭐4/5: ..."
    }]
  }
}
```

---

## 8. Çoklu Tool Çağrısı

`max_turns=6` sayesinde agent tek kullanıcı mesajında birden fazla tool çağırabilir.

**Örnek:** `"otelin genel durumu nedir?"`

```
Tur 1: get_all_reviews_for_analysis(days=30)  çağrıldı
        → 5 yorum ham verisi döndü

Tur 2: get_review_trends(weeks=4)  çağrıldı
        → Haftalık trend verisi döndü

Tur 3: LLM her iki kaynaktan sentez yapıp Türkçe yanıt yazdı
```

---

## 9. Oturum Hafızası

MCP protokolü session hafızası sağlamaz; hafıza uygulama katmanında implemente edilmiştir.

```python
# hotel_mcp_agent.py
_sessions: Dict[str, List[Dict[str, str]]] = {}
_MAX_HISTORY = 20

def _build_context(session_id: str) -> str:
    history = _sessions.get(session_id, [])
    lines = ["[Önceki Konuşma]"]
    for m in history[-10:]:          # Son 10 mesaj context'e eklenir
        role = "Admin" if m["role"] == "user" else "Asistan"
        lines.append(f"{role}: {m['content'][:300]}")
    return "\n".join(lines)
```

| Özellik | Değer |
|---|---|
| Depolama | In-process Python dict (RAM) |
| Session başına max mesaj | 20 |
| Context'e eklenen mesaj | Son 10 |
| Session silme | `DELETE /agents/mcp/chat/session/{id}` |
| Backend restart | Tüm session'lar sıfırlanır |

---

## 10. API Endpoint'leri

| Method | URL | Açıklama |
|---|---|---|
| `POST` | `/agents/mcp/chat` | Mesaj gönder, yanıt al |
| `GET` | `/agents/mcp/chat/history/{session_id}` | Session geçmişi |
| `DELETE` | `/agents/mcp/chat/session/{session_id}` | Session temizle |

**POST /agents/mcp/chat**
```json
// İstek
{ "message": "yemek sorunları neler?", "session_id": "a3f2b1" }

// Yanıt
{
  "session_id": "a3f2b1",
  "response": "Yemek hakkında 2 yorum bulundu...",
  "is_new_session": false,
  "message_count": 4
}
```

---

## 11. Başlatma

```bash
# Tüm sistem (Windows)
start.bat

# Sadece backend + MCP
cd Backend
python run.py
```

`run.py` başlatma sırası:

```
1. subprocess.Popen(["python", "hotel_mcp_server.py"])
   → MCP server port 8001'de başlar
   → Windows güvenli: senkron Popen, asyncio yok

2. time.sleep(2)
   → Server'ın SSE endpoint'ini dinlemeye başlaması beklenir

3. uvicorn.run("app.main:app", port=8000)
   → FastAPI başlar
   → lifespan: init_db() → tablolar + seed data
```

---

## 12. Sonuç

| MCP'nin Sağladığı | Açıklama |
|---|---|
| Standart protokol | JSON-RPC · `tools/list` + `tools/call` |
| LLM özerkliği | Hangi tool çağrılacağına LLM karar verir |
| Servis izolasyonu | MCP server ve backend bağımsız process |
| Otomatik keşif | Tool listesi runtime'da öğrenilir |
| Genişletilebilirlik | Yeni tool = sadece `@mcp.tool()` fonksiyon |
| Platform uyumu | SSE transport — Windows dahil her platform |
