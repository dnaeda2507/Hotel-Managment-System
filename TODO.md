# MCP Entegrasyon TODO (Mevcut Kodlar Korunarak)

## ✅ Plan Onaylandı
- Review analizi için MCP ekle
- Opsiyonel: LangGraph'a MCP tool ekle
- Mevcut ajanlar bozulmasın

## 📋 Yapılacak Adımlar (Sıralı)

### 1. Dependencies [✅ TAMAM]
- Backend/requirements.txt → `openai-agents[mcp]` eklendi

### 2. Yeni Klasör & MCP Servers [✅ TAMAM]
```
✅ Backend/app/agents/mcp/__init__.py
✅ Backend/app/agents/mcp/servers.py (Weather, Memory, Brave)
✅ Backend/app/agents/mcp/review_mcp.py (Ana MCP ajan)
```

### 3. Yeni Route (Yeni dosya) [✅ TAMAM]
```
✅ Backend/app/routes/mcp_ai.py → /agents/mcp-review
✅ Backend/app/main.py → router eklendi
```

### 4. Opsiyonel LangGraph Entegrasyon [CURRENT]
```
[ ] langgraph_agentic_review.py → MCP tool bind (opsiyonel toggle)
```

### 5. Frontend [CURRENT]
```
[ ] ReviewAnalysisPanel.tsx → MCP buton
[ ] mcpApi.ts → Yeni API çağrısı
```

### 6. Test & Deploy [✅ Backend Test Edildi]
```
✅ POST /agents/mcp/review-analysis çalışıyor
✅ Hava durumu key eklendi
✅ Event search fix bekleniyor
```

**Tamamlanan**: 5/6 - Frontend buton → Tamam!
```
[ ] smoke test: POST /agents/mcp-review-analysis  
[ ] manuel test: Review page MCP butonu
[ ] production deploy
```

## Progress Tracker
- **Tamamlanan**: 3/6
- **Sonraki**: Frontend + Test
- Backend/requirements.txt → `openai-agents[mcp]` ekle
- `uv pip install openai-agents[mcp]`

### 2. Yeni Klasör & MCP Servers
```
[X] Backend/app/agents/mcp/__init__.py
[X] Backend/app/agents/mcp/servers.py (Weather, Memory, Brave)
[X] Backend/app/agents/mcp/review_mcp.py (Ana MCP ajan)
```

### 3. Yeni Route (Yeni dosya)
```
[X] Backend/app/routes/mcp_ai.py → /agents/mcp-review
[ ] Backend/app/main.py → router ekle
```

### 4. Opsiyonel LangGraph Entegrasyon
```
[ ] langgraph_agentic_review.py → MCP tool bind (opsiyonel toggle)
```

### 5. Frontend
```
[ ] ReviewAnalysisPanel.tsx → MCP buton
[ ] mcpApi.ts → Yeni API çağrısı
```

### 6. Test & Deploy
```
[ ] smoke test: POST /agents/mcp-review-analysis
[ ] manuel test: Review page MCP butonu
[ ] production deploy
```

## Progress Tracker
- **Tamamlanan**: 0/6
- **Sonraki**: requirements.txt güncelle

**Not**: Her adım sonrası TODO güncellenecek.
