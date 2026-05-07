# LangGraph — Yorum Analizi Çok-Ajan Mimarisi

## Akış Şeması

```
                    ┌─────────────────────────────────────────┐
                    │  Misafir Yorumları (DB'den)              │
                    │  "Oda 3: klima bozuk"                    │
                    │  "Oda 7: banyo kirli"                    │
                    └──────────────────┬──────────────────────┘
                                       │
                                       ▼
                    ┌─────────────────────────────────────────┐
                    │  Node 1: classifier                      │
                    │  LLM — yorumları kategorize eder         │
                    │                                          │
                    │  cleaning_issues:                        │
                    │    [{room_id: 7, description: "..."}]    │
                    │  maintenance_issues:                     │
                    │    [{room_id: 3, description: "..."}]    │
                    └────────────┬────────────────┬───────────┘
                                 │                │
                    ┌────────────▼───┐    ┌───────▼────────────┐
                    │ Node 2:        │    │ Node 3:             │
                    │ cleaning_agent │    │ maintenance_agent   │
                    │ LLM            │    │ LLM                 │
                    │                │    │                     │
                    │ • Önceliklendir│    │ • Önceliklendir     │
                    │ • DB'de açık   │    │ • DB'de açık        │
                    │   görev var mı?│    │   bilet var mı?     │
                    │ • create_      │    │ • create_           │
                    │   cleaning_    │    │   maintenance_      │
                    │   task() → DB  │    │   task() → DB       │
                    └────────────┬───┘    └───────┬────────────┘
                                 │   PARALEL      │
                                 └───────┬────────┘
                                         │ (her ikisi bitince)
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │  Node 4: coordinator                     │
                    │  LLM — iki ajanın çıktısını sentezler    │
                    │                                          │
                    │  "3 temizlik, 1 bakım görevi oluşturuldu.│
                    │   Kritik: Oda 3 klima arızası..."        │
                    └──────────────────┬──────────────────────┘
                                       │
                                       ▼
                    ┌─────────────────────────────────────────┐
                    │  Node 5: evaluator                       │
                    │  LLM — raporu değerlendirir              │
                    │                                          │
                    │  "Sorunlar kategorize edilmiş mi?        │
                    │   Öncelik sırası var mı?"                │
                    │                                          │
                    │  → success: END                          │
                    │  → retry:   coordinator'a geri dön       │
                    └──────────────────┬──────────────────────┘
                                       │
                              success  │  retry (max 3)
                        ┌──────────────┴──────────────┐
                        ▼                             ▼
                       END                      coordinator
```

---

## Node Detayları

| Node | Tür | Girdi | Çıktı |
|---|---|---|---|
| `classifier` | LLM | Yorum metinleri | `cleaning_issues`, `maintenance_issues` |
| `cleaning_agent` | LLM + DB yazma | `cleaning_issues` | `cleaning_tasks_created` |
| `maintenance_agent` | LLM + DB yazma | `maintenance_issues` | `maintenance_tasks_created` |
| `coordinator` | LLM | Her iki task listesi | `report` |
| `evaluator` | LLM | `report` | `eval_result`: success / retry |

---

## Paralel Çalışma

`cleaning_agent` ve `maintenance_agent` aynı anda çalışır — birbirini beklemez.

```
classifier biter
    │
    ├──► cleaning_agent   (Oda 7 temizlik → DB)
    └──► maintenance_agent (Oda 3 klima → DB)
              ↓ (her ikisi tamamlandığında)
         coordinator
```

LangGraph bunu StateGraph fan-out/fan-in ile yönetir:
```python
gb.add_edge("classifier", "cleaning_agent")
gb.add_edge("classifier", "maintenance_agent")
gb.add_edge("cleaning_agent", "coordinator")
gb.add_edge("maintenance_agent", "coordinator")
```

---

## State

```python
class AgenticState(TypedDict):
    messages: List[Any]               # Yorum metinleri (girdi)
    cleaning_issues: List[Dict]        # classifier çıktısı
    maintenance_issues: List[Dict]     # classifier çıktısı
    cleaning_tasks_created: List[Dict] # cleaning_agent çıktısı
    maintenance_tasks_created: List[Dict] # maintenance_agent çıktısı
    report: Optional[str]              # coordinator çıktısı
    eval_result: Optional[str]         # "success" | "retry"
    eval_feedback: Optional[str]       # evaluator açıklaması
    iteration: int                     # retry sayacı (max 3)
```

---

## Tetikleme

```
GET  /agents/review-ai/auto-report?period=daily|weekly
POST /agents/review-ai/analyze-reviews
```

"Rapor Ver" butonuna basıldığında:
1. Yorumlar DB'den çekilir
2. LangGraph graph'ı çalışır
3. Görevler **otomatik olarak** DB'ye yazılır
4. Rapor + oluşturulan görevler frontend'e döner

---

## Önceki Mimariden Fark

| | Eski | Yeni |
|---|---|---|
| Ajan sayısı | 1 LLM (her şey yapar) | 4 LLM çağrısı (uzmanlaşmış) |
| Paralel çalışma | Yok | `cleaning_agent` ∥ `maintenance_agent` |
| Evaluator | if/else Python | Gerçek LLM değerlendirmesi |
| Görev oluşturma | Manuel seçim gerekiyordu | Otomatik, elle onay yok |
| DB kontrolü | Buffer'da kontrol | Her agent kendi alanını kontrol eder |
