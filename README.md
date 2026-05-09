# AI Hotel PMS — Otel Yönetim Sistemi

[![React](https://img.shields.io/badge/React-19.2-61DAFB?logo=react&logoColor=white)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Docker-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-purple)](https://langchain-ai.github.io/langgraph/)
[![CrewAI](https://img.shields.io/badge/CrewAI-latest-FF6B35)](https://crewai.com/)
[![MCP](https://img.shields.io/badge/MCP-SSE-red)](https://modelcontextprotocol.io/)

Üç farklı AI framework ile donatılmış tam kapsamlı otel yönetim sistemi. Rezervasyon, oda yönetimi, misafir yorumları ve otomatik fiyatlandırmayı tek platformda birleştirir.

---

## Özellikler

**Otel Operasyonları**
- Oda yönetimi (CRUD, özellikler, fotoğraflar)
- Rezervasyon sistemi (oluşturma, düzenleme, iptal)
- Misafir yorumları ve derecelendirmeler
- Temizlik (housekeeping) görev takibi
- Bakım (maintenance) talep yönetimi
- Dinamik fiyat yönetimi

**AI Destekli Modüller**
- Yorumlardan otomatik görev oluşturma (LangGraph)
- Piyasa verisiyle dinamik fiyat önerisi (CrewAI)
- Admin için hafızalı chat asistanı (MCP + OpenAI Agents SDK)

**Teknik Altyapı**
- JWT tabanlı kimlik doğrulama (admin/kullanıcı rolleri)
- Repository pattern ile katmanlı mimari
- Docker ile izole PostgreSQL
- Swagger UI ile canlı API dokümantasyonu

---

## AI Modüller

| Modül | Framework | Ne Yapar |
|---|---|---|
| **Yorum Analizi** | LangGraph | Misafir yorumlarını sınıflandırır, temizlik/bakım görevlerini otomatik oluşturur, admin raporu üretir |
| **Dinamik Fiyatlama** | CrewAI | Doluluk oranı + hava durumu + yerel etkinlik verisini birleştirerek fiyat önerisi sunar |
| **Chat Asistanı** | MCP + OpenAI Agents SDK | Admin sorgularını anlayan, veritabanı tool'larını çağıran ve hafıza tutan konuşma arayüzü |

### LangGraph — Yorum Analizi

5 düğümlü yönlendirilmiş bir durum grafiği:

```
Yorumlar → [Classifier] → [CleaningAgent] → [Coordinator] → [Evaluator] → Rapor
                       ↘ [MaintenanceAgent] ↗
```

- **Classifier:** Yorumları temizlik/bakım kategorisine ayırır
- **CleaningAgent / MaintenanceAgent:** ReAct döngüsüyle DB'ye görev yazar (paralel)
- **Coordinator:** Yönetici raporu üretir
- **Evaluator:** Kalite kontrolü, düşük puanda yeniden döngü (max 3 iterasyon)
  
<img width="655" height="587" alt="image" src="https://github.com/user-attachments/assets/f9cb1b5b-ae1d-423e-b477-35ef3edb92e1" />

### CrewAI — Dinamik Fiyatlama

3 özelleşmiş ajan paralel çalışır, ardından PricingStrategist nihai öneriyi üretir:

```
[OccupancyAnalyst] ──┐
[MarketResearcher]  ──┤→ [PricingStrategist] → JSON fiyat önerisi
                      │    (hava + etkinlik)
```

- **OccupancyTool:** PostgreSQL'den doluluk oranı hesaplar
- **WeatherTool:** Open-Meteo API'dan sıcaklık verisi çeker
- **EventSearchTool:** Brave Search API ile yerel etkinlikleri bulur

<img width="581" height="315" alt="image" src="https://github.com/user-attachments/assets/484dc99a-8631-45ab-949e-01407314418a" />

### MCP — Chat Asistanı

İki MCP sunucusu SSE transport ile çalışır (Windows uyumlu):

```
Frontend Chat → FastAPI → OpenAI Agent → MCP Server (8001 review + 8002 ops)
                                    ↑            ↓
                              Tool seçimi   PostgreSQL
```

- **Review Server (8001):** 6 yorum sorgulama tool'u
- **Ops Server (8002):** 6 operasyon tool'u + 2 resource
- **Hafıza:** Oturum başına max 20 mesaj

<img width="824" height="587" alt="image" src="https://github.com/user-attachments/assets/f51b2cf1-696b-4ac4-b9ef-3cd88a729293" />

---

## Mimari

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React 19)                   │
│  Public: Home · Rooms · Login · Register                │
│  Admin:  Dashboard · Rooms · Reservations · Reviews     │
│          Pricing · Housekeeping · Maintenance · MCP     │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP (Axios)
┌──────────────────────▼──────────────────────────────────┐
│                  FastAPI (port 8000)                     │
│                                                          │
│  Routes: auth · rooms · reservations · reviews          │
│          pricing · housekeeping · maintenance           │
│          pricing_ai · review_ai · mcp_ai                │
│                                                          │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────────┐ │
│  │  CrewAI    │  │  LangGraph   │  │  MCP + OpenAI   │ │
│  │ (Pricing)  │  │  (Reviews)   │  │  Agents SDK     │ │
│  └────────────┘  └──────────────┘  └────────┬────────┘ │
└─────────────────────────────────────────┬────┼──────────┘
                                          │    │ SSE
┌─────────────────────────────────────────▼────▼──────────┐
│              PostgreSQL (Docker, port 5500)               │
│  users · rooms · reservations · reviews                  │
│  housekeeping · maintenance · pricing                    │
└─────────────────────────────────────────────────────────┘
```

---

## Hızlı Başlatma

### Gereksinimler

- Python 3.11+
- Node.js 18+
- Docker Desktop

### Otomatik Başlatma (Windows)

```bat
start.bat
```

Tek komut: Docker PostgreSQL başlatır, Python ortamını kurar, MCP sunucularını açar ve frontend geliştirme sunucusunu başlatır.

### Manuel Kurulum

**1. Depoyu klonla**

```bash
git clone <repo-url>
cd Hotel-Managment-System
```

**2. PostgreSQL başlat**

```bash
cd Backend
docker-compose up -d
```

**3. Python bağımlılıklarını kur**

```bash
cd Backend
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

**4. Ortam değişkenlerini ayarla**

`Backend/.env` dosyasını oluştur:

```env
DATABASE_URL=postgresql://admin:password@localhost:5500/hotel_db
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=sk-...
BRAVE_API_KEY=BSA...
```

**5. Backend'i başlat**

```bash
cd Backend
python run.py
```

> `uvicorn app.main:app` yerine `python run.py` kullan — MCP sunucularını da o başlatır.

**6. Frontend'i başlat**

```bash
cd Frontend
npm install
npm run dev
```

**7. Uygulamaya eriş**

| Servis | URL |
|---|---|
| Frontend | http://localhost:5173 |
| FastAPI | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |

---

## Proje Yapısı

```
Hotel-Managment-System/
├── Backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── hotel_pricing/      # CrewAI ajanları ve tool'ları
│   │   │   ├── review_langgraph/   # LangGraph graf ve tool'ları
│   │   │   └── mcp/                # MCP sunucuları ve ajan istemcisi
│   │   ├── models/                 # SQLAlchemy ORM modelleri
│   │   ├── repositories/           # Veri erişim katmanı
│   │   ├── routes/                 # FastAPI endpoint'leri
│   │   ├── schemas/                # Pydantic request/response modelleri
│   │   ├── services/               # İş mantığı katmanı
│   │   └── main.py                 # FastAPI uygulama girişi
│   ├── docker-compose.yml          # PostgreSQL servisi
│   ├── requirements.txt
│   └── run.py                      # Sistem başlatıcı (MCP + uvicorn)
│
├── Frontend/
│   └── src/
│       ├── api/                    # Axios API istemcileri
│       ├── components/             # Yeniden kullanılabilir bileşenler
│       ├── pages/
│       │   ├── admin/              # Korumalı admin sayfaları
│       │   └── ...                 # Genel sayfalar
│       ├── types/                  # TypeScript arayüzleri
│       └── hooks/                  # Özel React hook'ları
│
├── docs/
│   ├── ARCHITECTURE.md             # Sistem mimarisi detayı
│   ├── LANGGRAPH.md                # LangGraph implementasyonu
│   └── MCP.md                      # MCP protokolü ve araçlar
│
├── MCP_GUIDE.md                    # MCP tam uygulama rehberi
├── AI_AGENTS_RAPOR.md              # AI ajan teknik raporu
└── start.bat                       # Windows tek-tıkla başlatma
```

---

## API Endpoint'leri

| Grup | Prefix | Açıklama |
|---|---|---|
| Auth | `/auth` | Giriş, kayıt, JWT yenileme |
| Rooms | `/rooms` | Oda CRUD, müsaitlik |
| Reservations | `/reservations` | Rezervasyon yönetimi |
| Reviews | `/reviews` | Yorum listeleme |
| Pricing | `/pricing` | Manuel fiyat yönetimi |
| Housekeeping | `/housekeeping` | Temizlik görev takibi |
| Maintenance | `/maintenance` | Bakım talepleri |
| AI Pricing | `/agents/dynamic-pricing` | CrewAI fiyat analizi |
| AI Reviews | `/agents/review-ai` | LangGraph yorum analizi |
| AI Chat | `/agents/mcp` | MCP chat asistanı |

Tüm endpoint detayları: http://localhost:8000/docs

---

## Teknoloji Yığını

| Katman | Teknoloji |
|---|---|
| **Frontend** | React 19 · TypeScript · Vite · React Router · Axios |
| **Backend** | FastAPI · Uvicorn · Pydantic · SQLAlchemy |
| **Veritabanı** | PostgreSQL (Docker) · Alembic |
| **AI — Fiyatlama** | CrewAI · OpenAI GPT-4 |
| **AI — Yorumlar** | LangGraph · LangChain · OpenAI GPT-4 |
| **AI — Chat** | MCP (FastMCP) · OpenAI Agents SDK |
| **Harici API** | Open-Meteo (hava) · Brave Search (etkinlikler) |
| **Kimlik Doğrulama** | JWT (python-jose) · bcrypt |

---

## Varsayılan Kullanıcılar

| Rol | E-posta | Şifre |
|---|---|---|
| Moderatör | moderator@example.com | Dev@12345! |
| Kullanıcı | user@example.com | Dev@12345! |

---

## Port Tablosu

| Servis | Port |
|---|---|
| Frontend (Vite) | 5173 |
| FastAPI | 8000 |
| Swagger UI | 8000/docs |
| MCP Review Server | 8001 |
| MCP Ops Server | 8002 |
| PostgreSQL | 5500 |

---

## Dokümantasyon

| Döküman | İçerik |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Genel sistem mimarisi |
| [docs/LANGGRAPH.md](docs/LANGGRAPH.md) | LangGraph graf implementasyonu |
| [docs/MCP.md](docs/MCP.md) | MCP protokolü, tool'lar, SSE transport |
| [MCP_GUIDE.md](MCP_GUIDE.md) | MCP tam uygulama rehberi (kod + demo) |
| [AI_AGENTS_RAPOR.md](AI_AGENTS_RAPOR.md) | Tüm AI ajan framework'lerinin teknik raporu |
