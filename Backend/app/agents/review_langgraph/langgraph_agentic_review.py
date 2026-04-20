from typing import Annotated, List, Dict, Any, Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import json

# ---------- State ----------
class AgenticState(TypedDict):
    messages: Annotated[List[Any], add_messages]  # add_messages reducer - ders: 1_lab1
    detected_issues: List[Dict]
    generated_tasks: List[Dict]
    report: Optional[str]
    history: List[Dict]
    outcome: Optional[str]
    tool_calls: List[Dict]
    eval_result: Optional[str]
    iteration: int  # sonsuz döngü koruması


# ---------- Graph ----------
def build_agentic_review_graph(db):

    # Her graph build'inde izole buffer — paralel istek güvenli
    _issues_buffer: List[Dict] = []

    # ── @tool dekoratörü (ders: 2_lab2) ───────────────────────────────────────
    @tool
    def log_issue(room_id: int, issue_type: str, description: str) -> str:
        """
        Müşteri yorumundan tespit edilen bir oda sorununu kaydet.

        Args:
            room_id: Sorunun yaşandığı oda ID'si.
            issue_type: 'cleaning' (temizlik) veya 'maintenance' (bakım/teknik arıza).
            description: Sorunun kısa Türkçe açıklaması.
        """
        _issues_buffer.append({
            "room_id": room_id,
            "type": issue_type,
            "desc": description,
        })
        return f"✓ Kaydedildi → Oda {room_id} [{issue_type}]: {description}"

    tools = [log_issue]

    # llm.bind_tools() — LLM'e hangi tool'ların mevcut olduğunu bildir (ders: 2_lab2)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    # ToolNode — tool çağrılarını otomatik execute eder (ders: 2_lab2)
    tool_node = ToolNode(tools)

    # ── Node 1: Agent ──────────────────────────────────────────────────────────
    def agent_node(state: AgenticState) -> dict:
        """LLM sorun bulduğunda log_issue'yu çağırır; bitmişse çağırmaz."""
        messages = state.get("messages", [])
        if not messages:
            return {"outcome": "analyzed", "iteration": 0}

        system = (
            "Sen bir otel yönetim asistanısın. Müşteri yorumlarını analiz et.\n"
            "Her tespit ettiğin sorun için log_issue aracını çağır:\n"
            "  - Temizlik sorunları → issue_type='cleaning'\n"
            "  - Teknik/bakım sorunları → issue_type='maintenance'\n"
            "Zaten kaydettiğin sorunları tekrar kaydetme.\n"
            "Tüm sorunları kaydettikten sonra araç çağırmayı bırak."
        )
        result = llm_with_tools.invoke(
            [{"role": "system", "content": system}] + list(messages)
        )
        return {
            "messages": [result],
            "iteration": state.get("iteration", 0) + 1,
            "outcome": "analyzed",
        }

    # ── Node 2: Finalize (buffer → state) ─────────────────────────────────────
    def finalize_node(state: AgenticState) -> dict:
        """Tool buffer'ındaki sorunları detected_issues state'ine aktar."""
        return {"detected_issues": list(_issues_buffer)}

    # ── Node 3: Report ─────────────────────────────────────────────────────────
    def report_node(state: AgenticState) -> dict:
        """detected_issues listesinden Türkçe yönetici raporu üret."""
        issues = state.get("detected_issues", [])
        if not issues:
            return {
                "report": "Bu dönemde dikkat çeken bir sorun tespit edilmedi.",
                "outcome": "report",
            }
        report_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        issues_text = json.dumps(issues, ensure_ascii=False, indent=2)
        result = report_llm.invoke([
            {
                "role": "system",
                "content": (
                    "Aşağıdaki otel sorunlarını özetle, kısa Türkçe yönetici raporu yaz.\n"
                    "Sorunları kategoriye göre grupla (temizlik / bakım). "
                    "Öncelik sırası öner. 3-5 cümle yeterli."
                ),
            },
            {"role": "user", "content": issues_text},
        ])
        return {"report": result.content, "outcome": "report"}

    # ── Node 4: Evaluator (ders: 3_lab3) ──────────────────────────────────────
    def evaluator_node(state: AgenticState) -> dict:
        """Rapor başarıyla üretildiyse bitir, yoksa retry (max 3 iterasyon)."""
        if state.get("outcome") == "report":
            return {"eval_result": "success"}
        if state.get("iteration", 0) >= 3:
            return {"eval_result": "success"}
        return {"eval_result": "retry"}

    # ── Conditional routing: tool_call var mı? (ders: 2_lab2 tools_condition) ─
    def route_after_agent(state: AgenticState) -> str:
        if state.get("iteration", 0) >= 5:
            return "finalize"
        messages = state.get("messages", [])
        last = messages[-1] if messages else None
        if last and hasattr(last, "tool_calls") and last.tool_calls:
            return "tools"
        return "finalize"

    # ── Graph Assembly ─────────────────────────────────────────────────────────
    gb = StateGraph(AgenticState)

    gb.add_node("agent", agent_node)
    gb.add_node("tools", tool_node)       # ToolNode (ders: 2_lab2)
    gb.add_node("finalize", finalize_node)
    gb.add_node("report", report_node)
    gb.add_node("evaluator", evaluator_node)

    gb.add_edge(START, "agent")
    gb.add_conditional_edges(             # add_conditional_edges (ders: 2_lab2)
        "agent",
        route_after_agent,
        {"tools": "tools", "finalize": "finalize"},
    )
    gb.add_edge("tools", "agent")         # tool sonucu görüldükten sonra agent'a dön
    gb.add_edge("finalize", "report")
    gb.add_edge("report", "evaluator")
    gb.add_conditional_edges(
        "evaluator",
        lambda state: END if state.get("eval_result") == "success" else "agent",
    )
    return gb.compile()

