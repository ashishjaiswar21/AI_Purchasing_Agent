"""LangGraph agent for Scenario 1: Purchase Recommendation Review."""
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
import operator

# Import tool functions
from tools import (
    get_inventory, get_demand_forecast, get_open_purchase_orders,
    get_supplier_info, get_available_budget, get_storage_capacity
)

# Model setup — reads GOOGLE_API_KEY from .env via config import
from config import GOOGLE_API_KEY, load_dotenv  # ensures env loaded

model = ChatGoogleGenerativeAI(model="gemini-3.8-flash")

tools = [get_inventory, get_demand_forecast, get_open_purchase_orders,
         get_supplier_info, get_available_budget, get_storage_capacity]

# ---- State ----
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    recommendation: dict  # {sku, qty, supplier_id}
    reasoning_trace: list[str]
    decision: str  # ACCEPT / MODIFY / REJECT / INVESTIGATE FURTHER

# ---- Nodes ----
def gather_data(state: AgentState, config: RunnableConfig):
    rec = state.get("recommendation", {})
    sku = rec.get("sku")
    trace = [f"Gathering data for SKU={sku}, qty={rec.get('qty')}"]
    # Call tools directly (not LLM) to populate context
    inv = get_inventory(sku)
    dem = get_demand_forecast(sku)
    po = get_open_purchase_orders(sku)
    sup = get_supplier_info(rec.get("supplier_id", "SUP-A"))
    bud = get_available_budget()
    stor = get_storage_capacity("node_east")  # representative node
    trace += [
        f"Inventory: {inv['records']}",
        f"Forecast: {dem['forecast']}",
        f"Open POs: {po['open_orders']}",
        f"Supplier: {sup['info']}",
        f"Budget remaining: {bud.get('remaining')}",
        f"Storage (east): {stor['capacity']}"
    ]
    # Build context message
    context = (f"SKU={sku}, qty={rec.get('qty')}. "
               f"Inventory={inv}, Demand={dem}, POs={po}, Supplier={sup}, Budget={bud}, Storage={stor}")
    msg = HumanMessage(content=f"Review purchase recommendation. {context}. Reason step by step and decide: ACCEPT, MODIFY, REJECT, or INVESTIGATE FURTHER.")
    return {"messages": [msg], "reasoning_trace": trace, "recommendation": rec}

def reason_decide(state: AgentState, config: RunnableConfig):
    # Call model with tool-calling capability bound to our tools
    model_with_tools = model.bind_tools(tools)
    # Use last message; model outputs reasoning + tool calls if needed
    last_msg = state["messages"][-1]
    response = model_with_tools.invoke([last_msg], config)
    trace = state.get("reasoning_trace", [])
    trace.append(f"Model reasoning: {response.content}")
    # Extract decision from content (simple heuristic)
    content = response.content or ""
    decision = "INVESTIGATE FURTHER"
    for d in ["ACCEPT", "MODIFY", "REJECT", "INVESTIGATE FURTHER"]:
        if d in content.upper():
            decision = d
            break
    return {"messages": [AIMessage(content=content)], "reasoning_trace": trace + [f"Decision: {decision}"], "decision": decision}

# ---- Build graph ----
builder = StateGraph(AgentState)
builder.add_node("gather", gather_data)
builder.add_node("reason", reason_decide)
builder.set_entry_point("gather")
builder.add_edge("gather", "reason")
builder.add_edge("reason", END)

agent_graph = builder.compile(checkpointer=MemorySaver())
