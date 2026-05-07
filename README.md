# AI Hotel PMS — Hotel Management System

![React](https://img.shields.io/badge/React-19-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![Python](https://img.shields.io/badge/Python-3.11+-yellow)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2-purple)
![CrewAI](https://img.shields.io/badge/CrewAI-latest-orange)
![MCP](https://img.shields.io/badge/MCP-SSE-red)

AI destekli otel yönetim sistemi. Üç farklı AI framework ile donatılmıştır.

---

## AI Modüller

| Modül | Framework | Açıklama |
|---|---|---|
| **Yorum Analizi** | LangGraph | Yorumlardan sorun tespiti, otomatik görev oluşturma |
| **Dinamik Fiyatlama** | CrewAI | Doluluk + etkinlik + hava verisiyle fiyat önerisi |
| **Chat Asistanı** | MCP + OpenAI Agents SDK | Admin için hafızalı yorum sorgulama chat'i |

---

## Hızlı Başlatma

```bash
# Windows — tüm sistemi tek komutla başlat
start.bat
```

Detaylı kurulum: [docs/SETUP.md](docs/SETUP.md)

---

## Dokümantasyon

| Döküman | İçerik |
|---|---|
| [docs/MCP.md](docs/MCP.md) | MCP implementasyonu — protokol, tool'lar, mimari |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Genel sistem mimarisi |
| [docs/SETUP.md](docs/SETUP.md) | Kurulum ve çalıştırma |
| [docs/API.md](docs/API.md) | API endpoint referansı |

---

## Teknoloji Yığını

**Backend:** FastAPI · SQLAlchemy · PostgreSQL · LangGraph · CrewAI · FastMCP · OpenAI Agents SDK

**Frontend:** React 19 · TypeScript · Vite · Axios

**Altyapı:** Docker (PostgreSQL) · uvicorn

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
| PostgreSQL | 5500 |
| MCP Server | 8001 |
| FastAPI | 8000 |
| Frontend | 5173 |
| Swagger | 8000/docs |
