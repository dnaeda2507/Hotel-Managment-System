from typing import Annotated, List, Dict, Any, Optional
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from review_langgraph.langgraph_review_tools import get_review_tools
from datetime import datetime
import json

# Agentic State
class AgenticState(TypedDict):
    messages: Annotated[List[Any], add_messages]
    detected_issues: List[Dict]
    generated_tasks: List[Dict]
    report: Optional[str]
    history: List[Dict]
    outcome: Optional[str]
    tool_calls: List[Dict]
    eval_result: Optional[str]

# Worker node: LLM + tool selection
# LLM decides: analyze, create task, or report

def agentic_worker(state: AgenticState, db) -> dict:
    llm = ChatOpenAI(model="gpt-4o-mini")
    tools = get_review_tools(db)
    tool_map = {t.name: t for t in tools}
    messages = state["messages"]
    # LLM prompt: decide what to do
    prompt = (
        "Sen bir otel yönetim asistanısın. Yorumları analiz et, gerekirse temizlik/bakım görevi oluştur, rapor hazırla. "
        "Aşağıdaki formatta karar ver: 'action' (analyze, create_cleaning_task, create_maintenance_task, report), 'args' (gerekirse), 'explanation'.\n"
        "Örnek: {\"action\": \"create_cleaning_task\", \"args\": {\"room_id\": 101, \"desc\": \"Oda kirli\"}, \"explanation\": \"Oda 101 için temizlik gerekli\"}"
    )
    reviews_text = "\n".join([msg["content"] for msg in messages if msg.get("role") == "user"])
    result = llm.invoke([
        {"role": "system", "content": prompt},
        {"role": "user", "content": reviews_text},
    ])
    try:
        decision = json.loads(result.content)
    except Exception:
        decision = {"action": "report", "args": {}, "explanation": "LLM karar veremedi"}
    tool_calls = state.get("tool_calls", [])
    # If tool action, call tool
    if decision["action"] in tool_map:
        tool_result = tool_map[decision["action"]].run(decision.get("args", {}))
        tool_calls.append({"tool": decision["action"], "args": decision.get("args", {}), "result": str(tool_result)})
        return {"tool_calls": tool_calls, "outcome": "tool_called", "messages": messages, "eval_result": None}
    elif decision["action"] == "analyze":
        # Just analyze, extract issues
        analyze_prompt = (
            "Yorumları analiz et, temizlik/bakım sorunlarını JSON olarak çıkar. Sadece JSON döndür."
        )
        analysis = llm.invoke([
            {"role": "system", "content": analyze_prompt},
            {"role": "user", "content": reviews_text},
        ])
        try:
            issues = json.loads(analysis.content)
            if not isinstance(issues, list):
                issues = []
        except Exception:
            issues = []
        return {"detected_issues": issues, "outcome": "analyzed", "messages": messages, "eval_result": None}
    elif decision["action"] == "report":
        return {"outcome": "report", "messages": messages, "eval_result": None}
    else:
        return {"outcome": "unknown", "messages": messages, "eval_result": None}

# Evaluator node: check if outcome is satisfactory

def agentic_evaluator(state: AgenticState) -> dict:
    # For demo: if outcome is 'report', finish; else, loop
    if state.get("outcome") == "report":
        return {"eval_result": "success"}
    return {"eval_result": "retry"}

# Agentic graph factory

def build_agentic_review_graph(db):
    gb = StateGraph(AgenticState)
    gb.add_node("worker", lambda state: agentic_worker(state, db))
    gb.add_node("evaluator", agentic_evaluator)
    gb.add_node("log", lambda state: {"history": state.get("history", []) + ["log eklendi"]})
    # 1. Normal edge: worker -> log
    gb.add_edge("worker", "log")
    # 2. Normal edge: log -> evaluator
    gb.add_edge("log", "evaluator")
    # 3. Conditional edge: evaluator -> END veya worker (loop)
    gb.add_conditional_edges(
        "evaluator",
        lambda state: END if state.get("eval_result") == "success" else "worker"
    )
    # Başlangıç: START -> worker
    gb.add_edge(START, "worker")
    return gb.compile()
