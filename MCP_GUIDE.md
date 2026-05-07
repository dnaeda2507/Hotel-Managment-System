# MCP (Model Context Protocol) — Proje Kılavuzu

> Bu belge hocanın sınav sorularını yanıtlamak ve sınıfta demo yapmak için hazırlanmıştır.
> Projede MCP'nin nerede başladığını, nasıl ilerlediğini ve ne yaptığını sıfırdan açıklar.

---

## 0. Projeyi Çalıştırma (Baştan Sona)

### Gereksinimler

| Araç | Versiyon | İndirme |
|------|----------|---------|
| Python | 3.11+ | python.org |
| Node.js | 18+ | nodejs.org |
| Docker Desktop | son sürüm | docker.com |
| `uv` (Python pkg yöneticisi) | son sürüm | `pip install uv` |

---

### Adım 1 — PostgreSQL'i Docker ile Başlat

```bash
# Hotel-Managment-System/Backend/ klasöründeyken:
cd Backend
docker compose up -d
```

Başarılı olursa:
```
✔ Container hotel_postgres  Started
```

Kontrol et:
```bash
docker ps
# hotel_postgres   postgres:16   ...   0.0.0.0:5500->5432/tcp
```

Durdurmak için:
```bash
docker compose down          # container'ı durdur (veri korunur)
docker compose down -v       # container + veriyi sil (sıfırdan başlamak için)
```

---

### Adım 2 — Backend .env Dosyası

`Backend/.env` dosyası zaten var. Yoksa oluştur:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5500/hotel_db
SECRET_KEY=fd5f2081639e42e145bf31832570b9000bcce1757f535f10fafd827c6036ec9c
SEED_PASSWORD=Dev@12345!
OPENAI_API_KEY=sk-...        ← kendi anahtarın
BRAVE_API_KEY=...            ← isteğe bağlı (MCP web araması için)
OPENWEATHER_API_KEY=...      ← isteğe bağlı (hava durumu için)
```

---

### Adım 3 — Backend Bağımlılıklarını Kur

```bash
# Backend/ klasöründeyken:
cd Backend
uv venv          # sanal ortam oluştur (.venv/)
uv pip install -r requirements.txt
```

Veya klasik pip ile:
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
```

---

### Adım 4 — Veritabanını Başlat (ilk kez)

```bash
# Backend/ klasöründeyken, .venv aktifken:
python -m app.init_db
```

Tablolar oluşturulur ve seed data eklenir.

---

### Adım 5 — Backend'i Başlat

> **Windows kullanıcıları `python run.py` kullanmalı** — MCP'nin çalışması için zorunlu.

```bash
# Backend/ klasöründeyken:

# Windows (MCP için zorunlu):
python run.py

# Linux / Mac:
python run.py
# veya:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Başarılı olursa:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

API dokümantasyonu: http://localhost:8000/docs

---

### Adım 6 — Frontend'i Başlat

```bash
# Hotel-Managment-System/Frontend/ klasöründeyken:
cd Frontend
npm install        # ilk kurulum
npm run dev
```

Başarılı olursa:
```
  VITE v7.x.x  ready in xxx ms
  ➜  Local:   http://localhost:5173/
```

Tarayıcıda aç: http://localhost:5173

---

### Hızlı Başlatma (Her Seferinde)

```bash
# Terminal 1 — Docker (PostgreSQL)
cd Backend
docker compose up -d

# Terminal 2 — Backend
cd Backend
python run.py

# Terminal 3 — Frontend
cd Frontend
npm run dev
```

---

### Varsayılan Kullanıcılar (seed data)

| Rol | E-posta | Şifre |
|-----|---------|-------|
| Admin/Moderator | admin@hotel.com | Dev@12345! |
| Normal kullanıcı | user@hotel.com | Dev@12345! |

---

### Port Özeti

| Servis | Port | URL |
|--------|------|-----|
| Frontend (Vite) | 5173 | http://localhost:5173 |
| Backend (FastAPI) | 8000 | http://localhost:8000 |
| PostgreSQL (Docker) | 5500 | localhost:5500 |
| API Docs (Swagger) | 8000 | http://localhost:8000/docs |

---

---

## 1. MCP Nedir? (30 saniyede açıklama)

MCP, **AI agent'ların dış araçlara bağlanmasını sağlayan bir protokoldür.**

Normalde bir LLM (ChatGPT gibi) sadece metin üretir — veritabanına bakamaz, rezervasyon yapamaz.
MCP ile LLM'e "bu araçları kullanabilirsin" diyebilirsin.

```
Kullanıcı sorusu
      ↓
   AI Agent  ←──── MCP Server (araçlar burada tanımlı)
      ↓                    ↓
  "Hangi odalar müsait?"   get_room_availability(check_in, check_out)
                                ↓
                         PostgreSQL veritabanı
                                ↓
                         Gerçek veri döner
      ↓
  Agent cevabı oluşturur
```

**Eski yöntem:** LLM → cevap üret (veritabanına erişim yok)  
**MCP ile:** LLM → tool seç → veritabanına git → gerçek veri al → cevap üret

---

## 2. Rezervasyon Nasıl Çalışır?

### Normal Rezervasyon Akışı (MCP olmadan)
```
Kullanıcı → Arayüzden oda seçer → Tarih girer → Form doldurur → Kaydet butonuna basar
```
Bu akış projede zaten var: `/admin/bookings` sayfası → normal rezervasyon formu.

### MCP ile Rezervasyon Akışı (YENİ)
```
Kullanıcı → Agent'a Türkçe yazar:
"101 no'lu odayı 10-15 Temmuz arası Ali Yılmaz için rezerve et, email: ali@mail.com"
          ↓
Agent soruyu anlar
          ↓
make_reservation(room_id=1, guest_name="Ali Yılmaz", check_in="2025-07-10", ...) çağırır
          ↓
hotel_mcp_server.py bu fonksiyonu çalıştırır → DB'ye yazar
          ↓
"Rezervasyon Oluşturuldu! ID=42, 5 gece × 800TL = 4000TL" döner
```

**Fark:** Normal akışta kullanıcı formu elle doldurur.
MCP ile agent doğal dil komutunu anlayıp rezervasyonu otomatik yapar.

### Fiyat Önerisi (CrewAI ile karşılaştırma)

| | CrewAI (Eski) | MCP `suggest_room_price` (Yeni) |
|---|---|---|
| Tetiklenme | Admin "Fiyat Önerileri" sayfasına gider | Agent'a soru sorulur |
| Çalışma | 3 agent (Analist + Araştırmacı + Stratejist) | 1 tool (DB'den hesaplar) |
| Süre | ~30-60 saniye | ~1-2 saniye |
| Onay | Admin onaylar → "Uygula" butonuna basar | Agent öneri döner, admin uygular |
| Veri kaynağı | DB + DuckDuckGo + Open-Meteo API | Sadece DB (doluluk + tarih) |

Her iki sistemde de **admin onayı** gereklidir. MCP sadece önerir, otomatik uygulamaz.

---

## 3. MCP Dosya Haritası — Ne Nerede?

```
Hotel-Managment-System/
│
├── Backend/
│   ├── hotel_mcp_server.py          ← ① MCP SERVER (araçlar burada)
│   │
│   └── app/
│       ├── main.py                  ← ② FastAPI başlangıç noktası
│       ├── routes/
│       │   └── mcp_ai.py            ← ③ HTTP endpoint'leri (/agents/mcp/...)
│       └── agents/
│           └── mcp/
│               ├── hotel_mcp_agent.py  ← ④ AI Agent (server'ı kullanan)
│               ├── review_mcp.py       ← ⑤ Yorum analizi (LLM direkt)
│               ├── pricing_mcp.py      ← ⑥ Fiyat önerisi (LLM direkt)
│               └── servers.py          ← ⑦ MCPManager (yardımcı sınıf)
│
└── Frontend/
    └── src/
        └── pages/admin/
            └── MCPDemoPage.tsx      ← ⑧ Demo arayüzü
```

---

## 4. Her Dosya Ne Yapar?

### ① `hotel_mcp_server.py` — MCP Server (Araç Deposu)

Bu dosya bir **MCP server**'dır. İçindeki her `@mcp.tool()` fonksiyonu bir araçtır.
Agent bu araçları çağırabilir. Server ayrı bir Python process olarak çalışır.

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Hotel Management Server")  # Server oluştur

@mcp.tool()
def get_room_availability(check_in: str, check_out: str) -> str:
    # PostgreSQL'e bağlan, müsait odaları bul, metin olarak döndür
    ...

@mcp.tool()
def make_reservation(room_id: int, guest_name: str, ...) -> str:
    # DB'ye INSERT yap, rezervasyon oluştur
    ...

if __name__ == "__main__":
    mcp.run()  # Server'ı başlat (stdin/stdout üzerinden iletişim)
```

**7 araç içerir:**
1. `get_room_availability` — Müsait oda sorgulama
2. `make_reservation` — Rezervasyon oluşturma ve DB'ye kaydetme
3. `suggest_room_price` — Doluluk oranına göre dinamik fiyat önerisi
4. `get_current_occupancy` — Bugünkü doluluk oranı
5. `get_recent_reviews` — Son müşteri yorumları
6. `get_pricing_summary` — Mevcut baz fiyat listesi
7. `get_pending_tasks` — Bekleyen temizlik/bakım görevleri

**Nasıl çalışır:** Server, `stdin/stdout` (standart giriş/çıkış) üzerinden iletişim kurar.
Agent mesaj gönderir → Server aracı çalıştırır → Sonucu geri gönderir.

---

### ④ `hotel_mcp_agent.py` — AI Agent (Server'ı Kullanan)

Bu dosya **OpenAI Agents SDK** kullanarak bir agent oluşturur.
Agent, hotel_mcp_server.py'yi bir subprocess olarak başlatır ve araçlarına bağlanır.

```python
from agents import Agent, Runner, trace
from agents.mcp import MCPServerStdio

async def run_hotel_mcp_agent(query: str):
    # 1. Server'ı subprocess olarak başlat
    server_params = {"command": "uv", "args": ["run", "hotel_mcp_server.py"]}
    
    async with MCPServerStdio(params=server_params) as mcp_server:
        # 2. Agent oluştur, MCP server'a bağla
        agent = Agent(
            name="hotel_assistant",
            instructions="Sen bir otel yönetim sistemi asistanısın...",
            model="gpt-4o-mini",
            mcp_servers=[mcp_server]   # ← Araçları buradan alır
        )
        
        # 3. Trace (hangi araçlar çağrıldı takip et)
        with trace("hotel_mcp_agent"):
            result = await Runner.run(agent, query, max_turns=10)
        
        return result.final_output
```

**İki fonksiyon içerir:**
- `list_hotel_mcp_tools()` — Server'daki tüm araçları listele
- `run_hotel_mcp_agent(query)` — Sorgu çalıştır, araç çağrılarını takip et

---

### ③ `mcp_ai.py` — HTTP Endpoint'leri

Bu dosya FastAPI **route**'larını tanımlar. Frontend buraya HTTP isteği atar.

```
GET  /agents/mcp/tools       → Mevcut araçları listele
POST /agents/mcp/query       → Agent'a soru sor
POST /agents/mcp/review-analysis → Yorum analizi yap
```

```python
@router.post("/query")
async def mcp_hotel_query(query: str = Body(...)):
    from app.agents.mcp.hotel_mcp_agent import run_hotel_mcp_agent
    result = await run_hotel_mcp_agent(query)
    return result
```

---

### ② `main.py` — Başlangıç Noktası

FastAPI uygulamasının giriş dosyasıdır. Tüm route'ları birbirine bağlar.

```python
from app.routes.mcp_ai import router as mcp_ai_router
app.include_router(mcp_ai_router)   # /agents/mcp/... endpoint'leri aktif
```

---

### ⑧ `MCPDemoPage.tsx` — Frontend Demo

React ile yazılmış admin paneli sayfası. `/admin/mcp-demo` adresinde açılır.

**Gösterdiği şeyler:**
- Mevcut 7 MCP aracının listesi (renk kodlu)
- Agent'a doğal dil ile soru sorma kutusu
- Hangi araçların çağrıldığını terminal gibi gösteren trace ekranı
- Rezervasyon oluşturma formu (`make_reservation` tool'unu tetikler)

---

## 5. MCP Tam Akış Diyagramı

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                         │
│  MCPDemoPage.tsx                                             │
│  Kullanıcı: "Bugün doluluk oranı nedir?"                    │
└──────────────────────┬──────────────────────────────────────┘
                       │ POST /agents/mcp/query
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                          │
│  mcp_ai.py → mcp_hotel_query()                              │
│       ↓ run_hotel_mcp_agent("Bugün doluluk oranı nedir?")   │
│  hotel_mcp_agent.py                                          │
└──────────────────────┬──────────────────────────────────────┘
                       │ subprocess olarak başlatır
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  MCP SERVER (ayrı process)                   │
│  hotel_mcp_server.py                                         │
│  MCPServerStdio ←──────────────────→ hotel_mcp_server.py   │
│  (stdin/stdout iletişimi)                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
  Agent araçları listeler    LLM soruyu analiz eder
  [get_room_availability,    "doluluk" → get_current_occupancy
   make_reservation,          tool'unu seç
   suggest_room_price, ...]
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                   TOOL ÇALIŞIR                               │
│  get_current_occupancy() → PostgreSQL sorgusu               │
│  SELECT COUNT... FROM rooms JOIN reservations...            │
│  Sonuç: "Toplam: 20 oda, Dolu: 14, Doluluk: %70"           │
└──────────────────────┬──────────────────────────────────────┘
                       │ Sonuç agent'a döner
                       ▼
              LLM sonucu Türkçe olarak yazar
              "Bugün otelin doluluk oranı %70'tir..."
                       │
                       ▼
              Frontend'e JSON olarak döner
              {response: "...", tool_calls: [{tool: "get_current_occupancy", ...}]}
                       │
                       ▼
              MCPDemoPage'de gösterilir
```

---

## 6. Hocanın Sorularına Hazır Cevaplar

**S: MCP'yi neden kullandınız? Normal API yeterli değil miydi?**

Normal API'de her soru için ayrı endpoint yazman gerekir. MCP ile agent hangi aracı çağıracağına kendisi karar verir. "Oda müsait mi?" sorusuna `get_room_availability`, "Rezervasyon yap" isteğine `make_reservation` çağrısını **otomatik** seçer.

---

**S: MCP Server ile normal Python fonksiyonu arasındaki fark nedir?**

Normal Python fonksiyonu sadece aynı process içinden çağrılabilir. MCP server ise herhangi bir MCP client (farklı dil, farklı uygulama, Claude, GPT-4) tarafından çağrılabilir. Araçları **paylaşılabilir** hale getirir.

---

**S: make_reservation tool'u gerçekten veritabanına yazıyor mu?**

Evet. `hotel_mcp_server.py` içindeki `make_reservation` fonksiyonu doğrudan `SQLAlchemy` ile PostgreSQL'e `INSERT` yapıyor. `conn.commit()` ile kalıcı olarak kaydediyor. Rezervasyonlar sayfasında görünür.

---

**S: suggest_room_price ile CrewAI fiyat önerisi arasındaki fark nedir?**

CrewAI 3 agent çalıştırır (OccupancyAnalyst → MarketResearcher → PricingStrategist), web araması yapar ve ~60 saniye sürer. MCP tool'u sadece DB'den doluluk oranını alır, hafta sonu ve sezon çarpanı uygular, 1-2 saniyede tamamlanır. Hem daha hızlı hem de yalnızca dahili veriyle çalışır.

---

**S: Tracer ne işe yarıyor?**

`with trace("hotel_mcp_agent"):` bloğu, agent'ın attığı her adımı kaydeder. Hangi tool'un çağrıldığı, ne argüman gönderildiği, ne sonuç döndüğü `result.new_items` listesinde saklanır. Demo sayfasındaki "terminal ekranı" bu veriyi gösterir.

---

**S: MCP Server'ı kim çalıştırıyor?**

`MCPServerStdio` sınıfı `hotel_mcp_server.py`'yi otomatik olarak bir subprocess olarak başlatır:
```python
server_params = {"command": "uv", "args": ["run", "hotel_mcp_server.py"]}
async with MCPServerStdio(params=server_params) as mcp_server:
    ...  # Bu blok bitince server da kapanır
```
Yani ayrıca manuel başlatmana gerek yok.

---

**S: Windows'ta çalışıyor mu?**

MCP'nin Node.js tabanlı server'ları Windows'ta sorun çıkarabilir. Bizim server'ımız Python tabanlı ve `uv run` ile çalıştırılıyor — bu Windows'ta desteklenir. Sorun olursa WSL (Windows Subsystem for Linux) ile çalıştırılabilir.

---

## 7. Backend Başlatma (Windows)

Normal komut **Windows'ta MCPServerStdio'yu bozar:**
```bash
# YANLIŞ — Windows'ta MCP çalışmaz
uvicorn app.main:app --reload
```

**Doğru komut — MCP dahil her şey çalışır:**
```bash
# Backend/ klasöründeyken:
python run.py
```

`run.py` sadece şunu yapar:
```python
asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())  # subprocess desteği
uvicorn.run("app.main:app", ...)
```

Linux/Mac'te `python run.py` ya da `uvicorn app.main:app` ikisi de çalışır.

---

## Demo Adımları (Sınıfta Gösterilecekler)

**Adım 1 — Araçları göster**
1. Admin paneli → "MCP Demo" menüsü
2. "Araçları Yükle" butonuna bas
3. 7 aracın renk kodlu listesi görünür
4. **Anlatım:** "hotel_mcp_server.py içindeki her @mcp.tool() burada görünüyor"

**Adım 2 — Sorgu çalıştır ve tool trace'i göster**
1. "Doluluk oranı" hazır sorgusuna tıkla
2. Agent düşünür → get_current_occupancy tool'unu seçer → DB'den veri çeker
3. Terminal ekranında hangi tool'un çağrıldığı görünür
4. **Anlatım:** "LLM hangi tool'u seçeceğine kendi karar verdi"

**Adım 3 — Fiyat önerisi**
1. "Fiyat önerisi" sorgusuna tıkla (Oda ID = 1)
2. Agent suggest_room_price çağırır
3. Baz fiyat, doluluk, çarpan ve önerilen fiyat görünür
4. **Anlatım:** "Bu CrewAI ile aynı mantık ama MCP tool olarak — anında çalışıyor"

**Adım 4 — Rezervasyon (MCP DB'ye yazıyor)**
1. "Rezervasyon Oluştur" butonuna bas
2. Formu doldur: oda ID, isim, email, tarihler
3. Agent make_reservation tool'unu çağırır
4. "Rezervasyon Oluşturuldu!" mesajı gelir
5. /admin/bookings sayfasına git — rezervasyon orada görünür
6. **Anlatım:** "Agent sadece metin üretmedi, gerçekten veritabanına yazdı"

---

## 8. Kod Özeti (tek sayfada)

```python
# ① SERVER: hotel_mcp_server.py
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Hotel Management Server")

@mcp.tool()
def make_reservation(room_id: int, guest_name: str, ...) -> str:
    # DB'ye yaz
    conn.execute(text("INSERT INTO reservations ..."))
    return "Rezervasyon oluşturuldu!"

if __name__ == "__main__":
    mcp.run()

# ④ AGENT: hotel_mcp_agent.py
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

async def run_hotel_mcp_agent(query: str):
    params = {"command": "uv", "args": ["run", "hotel_mcp_server.py"]}
    async with MCPServerStdio(params=params) as mcp_server:
        agent = Agent(
            name="hotel_assistant",
            instructions="Otel yönetim sistemi asistanısın...",
            model="gpt-4o-mini",
            mcp_servers=[mcp_server]   # ← ARAÇLAR BURADAN GELİYOR
        )
        result = await Runner.run(agent, query)
        return result.final_output

# ③ ROUTE: mcp_ai.py
@router.post("/query")
async def mcp_hotel_query(query: str = Body(...)):
    return await run_hotel_mcp_agent(query)
```

---

*Bu projedeki MCP implementasyonu:*
*hotel_mcp_server.py (7 tool) → hotel_mcp_agent.py (OpenAI Agents SDK) → mcp_ai.py (FastAPI) → MCPDemoPage.tsx (React UI)*
