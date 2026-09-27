"""LangGraph agent for Scenario 1: Purchase Recommendation Review."""
from langchain_groq import ChatGroq
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

# Model reads GROQ_API_KEY from .env
import os
import config
model = ChatGroq(model="qwen/qwen3.8-27b", api_key=config.GROQ_API_KEY)

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
    inv = get_inventory(sku)
    dem = get_demand_forecast(sku)
    po = get_open_purchase_orders(sku)
    sup = get_supplier_info(rec.get("supplier_id", "SUP-A"))
    bud = get_available_budget()
    stor = get_storage_capacity("node_east")
    trace += [
        f"Inventory records={len(inv['records'])}",
        f"Forecast={dem['forecast']}",
        f"Open POs={len(po['open_orders'])}",
        f"Supplier={sup['info']['name'] if sup['info'] else 'N/A'}",
        f"Budget remaining={bud.get('remaining')}",
        f"Storage east available={stor['capacity'].get('available') if stor['capacity'] else 'N/A'}"
    ]
    # Build rich context message with actual data
    context = (f"SKU={sku}, qty={rec.get('qty')}. "
               f"Inventory: {inv['records']}. Demand forecast: {dem['forecast']}. "
               f"Open POs: {po['open_orders']}. Supplier info: {sup['info']}. "
               f"Budget remaining: {bud.get('remaining')}. Storage (east): {stor['capacity']}.")
    msg = HumanMessage(content=f"Purchase recommendation review — FINAL DECISION REQUIRED. SKU={sku}, qty={rec.get('qty')}. Data: {context}. You must: (1) state exact numbers checked (inventory total vs qty requested, budget remaining vs estimated cost, storage available, supplier lead time/min order); (2) identify which constraint(s) drove the decision; (3) give a clear one-paragraph justification citing those numbers. Do NOT ask for more data — render the final decision now (ACCEPT / MODIFY / REJECT / INVESTIGATE FURTHER).")
    return {"messages": [msg], "reasoning_trace": trace, "recommendation": rec}

def reason_decide(state: AgentState, config: RunnableConfig):
    model_with_tools = model.bind_tools(tools)
    last_msg = state["messages"][-1]
    response = model_with_tools.invoke([last_msg], config)
    content = response.content or ""
    trace = state.get("reasoning_trace", [])
    # Capture actual model reasoning text (not empty)
    trace.append(f"Model reasoning: {content[:500]}")
    # Extract decision
    decision = "INVESTIGATE FURTHER"
    for d in ["ACCEPT", "MODIFY", "REJECT", "INVESTIGATE FURTHER"]:
        if d in content.upper():
            decision = d
            break
    trace.append(f"Decision: {decision}")
    return {"messages": [AIMessage(content=content)], "reasoning_trace": trace, "decision": decision}

# ---- Build graph ----
builder = StateGraph(AgentState)
builder.add_node("gather", gather_data)
builder.add_node("reason", reason_decide)
builder.set_entry_point("gather")
builder.add_edge("gather", "reason")
builder.add_edge("reason", END)

agent_graph = builder.compile(checkpointer=MemorySaver())
