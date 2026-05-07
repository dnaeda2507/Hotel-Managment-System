from typing import Annotated, List, Dict, Any, Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import json
from datetime import datetime


class AgenticState(TypedDict):
    messages: Annotated[List[Any], add_messages]
    cleaning_issues: List[Dict]
    maintenance_issues: List[Dict]
    cleaning_tasks_created: List[Dict]
    maintenance_tasks_created: List[Dict]
    report: Optional[str]
    eval_result: Optional[str]
    eval_feedback: Optional[str]
    iteration: int


def build_agentic_review_graph(db):

    # ── Node 1: Classifier ─────────────────────────────────────────────────────
    # Tool yok — sadece sınıflandırma JSON'u üretir
    def classifier_node(state: AgenticState) -> dict:
        messages = state.get("messages", [])
        if not messages:
            return {"cleaning_issues": [], "maintenance_issues": [], "iteration": 0}

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        system = (
            "Otel müşteri yorumlarını oku. Sorunları iki kategoriye ayır ve sadece JSON döndür:\n"
            '{"cleaning_issues": [{"room_id": <int>, "description": "<açıklama>"}], '
            '"maintenance_issues": [{"room_id": <int>, "description": "<açıklama>"}]}\n'
            "cleaning_issues: temizlik, hijyen, çarşaf, banyo\n"
            "maintenance_issues: teknik arıza, klima, tesisat, elektrik, su sızıntısı\n"
            "room_id'yi yorumun başındaki 'Oda X' kısmından al. Sorun yoksa liste boş kalır."
        )

        result = llm.invoke([{"role": "system", "content": system}] + list(messages))

        try:
            text = result.content.strip()
            if "```" in text:
                text = text.split("```")[1].replace("json", "").strip()
            data = json.loads(text)
            cleaning_issues = data.get("cleaning_issues", [])
            maintenance_issues = data.get("maintenance_issues", [])
        except Exception:
            cleaning_issues = []
            maintenance_issues = []

        return {
            "cleaning_issues": cleaning_issues,
            "maintenance_issues": maintenance_issues,
            "iteration": 0,
        }

    # ── Node 2: Cleaning Agent ─────────────────────────────────────────────────
    # LLM → bind_tools → tool_call → ToolNode → LLM (ReAct döngüsü)
    def cleaning_agent_node(state: AgenticState) -> dict:
        from app.agents.review_langgraph.langgraph_review_tools import create_cleaning_task as _create
        from app.repositories.housekeeping_repository import HousekeepingRepository

        issues = state.get("cleaning_issues", [])
        if not issues:
            return {"cleaning_tasks_created": []}

        created = []  # closure ile tool içinden doldurulur

        @tool
        def save_cleaning_task(room_id: int, description: str) -> str:
            """Temizlik görevi oluştur ve DB'ye kaydet."""
            try:
                active = HousekeepingRepository(db).get_active_task_for_room(room_id)
                if active:
                    return f"Oda {room_id} için zaten aktif görev var, atlandı."
            except Exception:
                pass
            _create(room_id, description, db)
            created.append({
                "type": "cleaning",
                "room_id": room_id,
                "description": description,
                "date": datetime.now().isoformat(),
            })
            return f"✓ Oda {room_id}: temizlik görevi oluşturuldu."

        llm_with_tools = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools([save_cleaning_task])
        tool_node = ToolNode([save_cleaning_task])

        system = (
            "Sen bir temizlik uzmanısın. Verilen her temizlik sorunu için "
            "save_cleaning_task tool'unu çağır. "
            "Aynı odayı iki kez çağırma. Tüm sorunları işledikten sonra dur."
        )
        messages: List[Any] = [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(issues, ensure_ascii=False)},
        ]

        # ReAct döngüsü: LLM tool çağırır → ToolNode çalıştırır → LLM devam eder
        for _ in range(6):
            result = llm_with_tools.invoke(messages)
            messages.append(result)
            if not (hasattr(result, "tool_calls") and result.tool_calls):
                break
            tool_results = tool_node.invoke({"messages": messages})
            messages = tool_results["messages"]

        return {"cleaning_tasks_created": created}

    # ── Node 3: Maintenance Agent ──────────────────────────────────────────────
    # LLM → bind_tools → tool_call → ToolNode → LLM (ReAct döngüsü)
    def maintenance_agent_node(state: AgenticState) -> dict:
        from app.agents.review_langgraph.langgraph_review_tools import create_maintenance_task as _create
        from app.repositories.maintenance_repository import MaintenanceRepository
        from app.models.maintenance import MaintenanceStatusEnum

        issues = state.get("maintenance_issues", [])
        if not issues:
            return {"maintenance_tasks_created": []}

        created = []  # closure ile tool içinden doldurulur

        @tool
        def save_maintenance_task(room_id: int, description: str) -> str:
            """Bakım/teknik arıza görevi oluştur ve DB'ye kaydet."""
            try:
                tickets = MaintenanceRepository(db).get_tickets_by_room(room_id)
                open_ticket = next(
                    (t for t in tickets if t.status != MaintenanceStatusEnum.CLOSED), None
                )
                if open_ticket:
                    return f"Oda {room_id} için zaten açık bilet var, atlandı."
            except Exception:
                pass
            _create(room_id, description, db)
            created.append({
                "type": "maintenance",
                "room_id": room_id,
                "description": description,
                "date": datetime.now().isoformat(),
            })
            return f"✓ Oda {room_id}: bakım görevi oluşturuldu."

        llm_with_tools = ChatOpenAI(model="gpt-4o-mini", temperature=0).bind_tools([save_maintenance_task])
        tool_node = ToolNode([save_maintenance_task])

        system = (
            "Sen bir teknik bakım uzmanısın. Verilen her bakım sorunu için "
            "save_maintenance_task tool'unu çağır. "
            "Aynı odayı iki kez çağırma. Tüm sorunları işledikten sonra dur."
        )
        messages: List[Any] = [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(issues, ensure_ascii=False)},
        ]

        # ReAct döngüsü: LLM tool çağırır → ToolNode çalıştırır → LLM devam eder
        for _ in range(6):
            result = llm_with_tools.invoke(messages)
            messages.append(result)
            if not (hasattr(result, "tool_calls") and result.tool_calls):
                break
            tool_results = tool_node.invoke({"messages": messages})
            messages = tool_results["messages"]

        return {"maintenance_tasks_created": created}

    # ── Node 4: Coordinator ────────────────────────────────────────────────────
    # Her iki agent'ın çıktısını alır, yönetici raporu sentezler
    def coordinator_node(state: AgenticState) -> dict:
        cleaning_tasks = state.get("cleaning_tasks_created", [])
        maintenance_tasks = state.get("maintenance_tasks_created", [])
        all_tasks = cleaning_tasks + maintenance_tasks

        if not all_tasks:
            return {
                "report": "Bu dönemde dikkat çeken bir sorun tespit edilmedi.",
                "iteration": state.get("iteration", 0) + 1,
            }

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        summary = {
            "temizlik_gorevleri": cleaning_tasks,
            "bakim_gorevleri": maintenance_tasks,
        }

        result = llm.invoke([
            {
                "role": "system",
                "content": (
                    "Otel yöneticisi için kapsamlı durum raporu yaz.\n"
                    "- Sorunları önceliğe göre grupla: Kritik / Orta / Düşük\n"
                    "- Toplam kaç temizlik, kaç bakım görevi otomatik oluşturulduğunu belirt\n"
                    "- Net, kısa Türkçe rapor (5-7 cümle)"
                ),
            },
            {"role": "user", "content": json.dumps(summary, ensure_ascii=False, indent=2)},
        ])

        return {
            "report": result.content,
            "iteration": state.get("iteration", 0) + 1,
        }

    # ── Node 5: LLM Evaluator ──────────────────────────────────────────────────
    # if/else değil, gerçek LLM değerlendirmesi
    def evaluator_node(state: AgenticState) -> dict:
        if state.get("iteration", 0) >= 3:
            return {"eval_result": "success", "eval_feedback": ""}

        report = state.get("report", "")
        if not report or "sorun tespit edilmedi" in report:
            return {"eval_result": "success", "eval_feedback": ""}

        eval_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        result = eval_llm.invoke([
            {
                "role": "system",
                "content": (
                    "Bu otel durum raporunu değerlendir.\n"
                    "Kriterler: sorunlar kategorize edilmiş mi, öncelik sırası var mı, yöneticiye net bilgi veriyor mu?\n"
                    "Yeterli → sadece 'success' yaz. Yetersiz → 'retry: [eksik olan]' yaz."
                ),
            },
            {"role": "user", "content": report},
        ])

        content = result.content.strip()
        if content.lower().startswith("success"):
            return {"eval_result": "success", "eval_feedback": ""}
        return {"eval_result": "retry", "eval_feedback": content}

    # ── Graph Assembly ─────────────────────────────────────────────────────────
    gb = StateGraph(AgenticState)

    gb.add_node("classifier", classifier_node)
    gb.add_node("cleaning_agent", cleaning_agent_node)
    gb.add_node("maintenance_agent", maintenance_agent_node)
    gb.add_node("coordinator", coordinator_node)
    gb.add_node("evaluator", evaluator_node)

    gb.add_edge(START, "classifier")
    # Fan-out: classifier biter → iki agent paralel çalışır
    gb.add_edge("classifier", "cleaning_agent")
    gb.add_edge("classifier", "maintenance_agent")
    # Fan-in: her iki agent bitince coordinator başlar
    gb.add_edge("cleaning_agent", "coordinator")
    gb.add_edge("maintenance_agent", "coordinator")
    gb.add_edge("coordinator", "evaluator")
    gb.add_conditional_edges(
        "evaluator",
        lambda state: END if state.get("eval_result") == "success" else "coordinator",
    )

    return gb.compile()
