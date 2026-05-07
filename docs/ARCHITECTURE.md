# Sistem Mimarisi — AI Hotel PMS

## Genel Bakış

Bu proje üç farklı AI framework'ünü farklı problemler için kullanır:

| Framework | Modül | Amaç |
|---|---|---|
| **LangGraph** | Yorum Analizi | Yorumlardan sorun tespiti + otomatik görev |
| **CrewAI** | Dinamik Fiyatlama | Piyasa araştırması + fiyat önerisi |
| **MCP + OpenAI Agents SDK** | Chat Asistanı | Admin yorum sorgulama chat'i |

---

## 1. LangGraph — Yorum Analizi ve Görev Yönetimi

### Ne Yapar?
DB'deki misafir yorumlarını okur, sorunları tespit eder, kategorize eder ve otomatik görev oluşturur.

### Dosyalar
```
Backend/app/agents/review_langgraph/
├── langgraph_agentic_review.py   ← Graph tanımı, state, node'lar
└── langgraph_review_tools.py     ← create_cleaning_task, create_maintenance_task
```

### Tetikleme
```
GET  /ai/auto-report?period=daily|weekly
POST /ai/analyze-reviews
```

### State
```python
AgenticState:
  messages        # yorumlar + konuşma geçmişi
  detected_issues # tespit edilen sorunlar
  generated_tasks # oluşturulan görevler
  report          # Türkçe yönetici raporu
  iteration       # döngü sayacı (max 5)
  eval_result     # "success" | "retry"
```

### Tool'lar
| Tool | Açıklama |
|---|---|
| `log_issue(room_id, issue_type, desc)` | Sorunu buffer'a kaydet (DB kontrolü yapar) |
| `create_cleaning_task(room_id, desc)` | HousekeepingService → DB |
| `create_maintenance_task(room_id, desc)` | MaintenanceService → DB |

### Akış (State Diagram)
```
START → agent_node → [tool_calls var?]
                          │ evet          │ hayır
                          ▼               ▼
                     tools_node     finalize_node
                          │               │
                          └──► agent_node  ▼
                          (iteration++)  report_node
                                            │
                                       evaluator_node
                                       │ success → END
                                       │ retry   → agent_node
```

---

## 2. CrewAI — Dinamik Fiyatlama

### Ne Yapar?
Otel doluluk oranını, Antalya'daki etkinlikleri ve hava durumunu analiz ederek oda tipi bazında fiyat önerisi üretir.

### Dosyalar
```
Backend/app/agents/hotel_pricing/
├── crew.py                  ← Agent ve Task tanımları
├── config/agents.yaml       ← Agent rolleri ve backstory
├── config/tasks.yaml        ← Görev açıklamaları
└── tools/
    ├── occupancy_tool.py    ← DB'den doluluk hesapla
    ├── event_search_tool.py ← Brave Search API
    └── weather_tool.py      ← Open-Meteo API
```

### Tetikleme
```
POST /ai/pricing/suggest
Body: { "date_range": "2025-07-10 to 2025-07-15" }
```

### Agent'lar ve Tool'lar
```
occupancy_analyst  ──► OccupancyTool (DB → doluluk oranı)
                                              │
                                              ├── paralel ──►
market_researcher  ──► EventSearchTool (Brave API)
                   ──► WeatherTool (Open-Meteo API)
                                              │
                                              ▼
pricing_strategist ──► Tool yok (LLM sentezi)
                       → JSON fiyat önerisi
                       → output/price_suggestions.json
```

### Process
`Process.sequential` — Task 1 ve 2 `async_execution=True` ile paralel başlar, her ikisi bitince Task 3 başlar.

---

## 3. MCP + OpenAI Agents SDK — Chat Asistanı

### Ne Yapar?
Yöneticinin yorumlar hakkında serbest dilde soru sorabildiği, session hafızalı bir chat asistanı.

### Dosyalar
```
Backend/
├── hotel_mcp_server.py              ← FastMCP server (port 8001, 6 tool)
└── app/agents/mcp/
    ├── hotel_mcp_agent.py           ← OpenAI Agents SDK client
    └── review_analysis.py           ← 3-agent analiz sistemi (opsiyonel)

Backend/app/routes/
└── mcp_ai.py                        ← API endpoint'leri
```

### Tetikleme
```
POST   /agents/mcp/chat
GET    /agents/mcp/chat/history/{session_id}
DELETE /agents/mcp/chat/session/{session_id}
```

Detaylı dokümantasyon: [MCP.md](./MCP.md)

---

## 4. Backend — FastAPI

```
Backend/
├── run.py                    ← MCP server başlat → uvicorn başlat
├── hotel_mcp_server.py       ← MCP server (FastMCP)
└── app/
    ├── main.py               ← FastAPI app, lifespan (init_db)
    ├── init_db.py            ← Tablo oluşturma + seed data
    ├── database.py           ← SQLAlchemy engine
    ├── models/               ← ORM modelleri
    ├── repositories/         ← DB erişim katmanı
    ├── services/             ← İş mantığı
    ├── routes/               ← API endpoint'leri
    └── agents/
        ├── review_langgraph/ ← LangGraph
        ├── hotel_pricing/    ← CrewAI
        └── mcp/              ← MCP client
```

### Başlatma Sırası (`run.py`)
```
1. subprocess.Popen(hotel_mcp_server.py) → port 8001
2. time.sleep(2)
3. uvicorn app.main:app → port 8000
4. lifespan: init_db() → PostgreSQL seed
```

---

## 5. Frontend — React + TypeScript

```
Frontend/src/
├── pages/admin/
│   ├── MCPDemoPage.tsx          ← MCP chat arayüzü
│   ├── ReviewAnalysisPanel.tsx  ← LangGraph arayüzü
│   └── ...
├── api/
│   └── authApi.ts               ← Axios instance (timeout: 120s)
└── types/
    └── aiReview.ts              ← AI tip tanımları
```

---

## 6. Veritabanı

**PostgreSQL** — Docker Compose ile çalışır (host port: 5500)

Temel tablolar:
```
users          rooms         reservations
reviews        housekeeping_tasks
maintenance_tickets          pricing
```

---

## 7. Ortam Değişkenleri

```env
# Backend/.env
DATABASE_URL=postgresql://postgres:password@localhost:5500/hotel_db
SECRET_KEY=...
OPENAI_API_KEY=sk-...
MCP_PORT=8001

# Opsiyonel
BRAVE_API_KEY=...        # CrewAI market araştırması
```

---

## 8. Tek Komutla Başlatma

```bash
# Windows — proje kök dizininde
start.bat
```

`start.bat` sırası:
1. `docker compose up -d` → PostgreSQL
2. Backend terminal → `python run.py` (MCP + FastAPI)
3. Frontend terminal → `npm run dev`
