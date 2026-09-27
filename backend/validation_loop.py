"""Validation + retry loop for Scenario 1. Logs attempts, feeds failures back."""
import json
from agent_graph import agent_graph
from tools import get_available_budget, get_storage_capacity, get_supplier_info, create_purchase_order, modify_purchase_order


def validate_po(purchase: dict) -> dict:
    """Check PO against budget/storage/min-order. Returns {ok: bool, reasons: list}."""
    sk = purchase.get("sku")
    qty = purchase.get("qty", 0)
    supplier = purchase.get("supplier_id", "SUP-A")
    reasons = []
    # Budget
    bud = get_available_budget()
    if qty * 100 > bud.get("remaining", 0):  # rough unit cost assumption
        reasons.append(f"Budget exceeded: needed ~{qty*100}, remaining {bud.get('remaining')}")
    # Storage (representative node)
    stor = get_storage_capacity("node_east")
    if stor.get("capacity", {}).get("available", 999) < qty:
        reasons.append(f"Storage tight: available {stor['capacity'].get('available')}, needed {qty}")
    # Supplier MOQ
    sup = get_supplier_info(supplier)
    min_qty = sup.get("info", {}).get("min_order_qty", 0)
    if qty < min_qty:
        reasons.append(f"Below supplier MOQ ({min_qty})")
    return {"ok": len(reasons) == 0, "reasons": reasons}


def run_with_validation(rec: dict, max_retries: int = 2) -> dict:
    history = []
    current_decision = None
    for attempt in range(max_retries + 1):
        # Run agent
        result = agent_graph.invoke(
            {"recommendation": rec, "messages": [], "reasoning_trace": [], "decision": ""},
            config={"configurable": {"thread_id": f"t_{rec['sku']}_{attempt}"}}
        )
        decision = result.get("decision", "INVESTIGATE FURTHER")
        current_decision = decision
        trace = result.get("reasoning_trace", [])
        attempt_log = {
            "attempt": attempt + 1,
            "decision": decision,
            "reasoning_trace": trace,
            "actions": []
        }
        # If ACCEPT/MODIFY, try action
        if decision in ("ACCEPT", "MODIFY"):
            if decision == "ACCEPT":
                po_result = create_purchase_order(rec["sku"], rec["qty"], rec.get("supplier_id", "SUP-A"))
                attempt_log["actions"].append({"create_purchase_order": po_result})
                # Validate the created PO
                val = validate_po({"sku": rec["sku"], "qty": rec["qty"], "supplier_id": rec.get("supplier_id")})
                attempt_log["validation"] = val
                if not val["ok"]:
                    history.append(attempt_log)
                    # Feed failure back: revise recommendation or force INVESTIGATE
                    rec["qty"] = max(1, rec["qty"] - 10)  # simple reduction for retry
                    continue  # retry with revised rec
            elif decision == "MODIFY":
                # Find open PO for SKU and modify
                # Simple: create then modify (for demo)
                po_result = create_purchase_order(rec["sku"], rec["qty"], rec.get("supplier_id", "SUP-A"))
                attempt_log["actions"].append({"create_purchase_order": po_result})
                val = validate_po({"sku": rec["sku"], "qty": rec["qty"], "supplier_id": rec.get("supplier_id")})
                attempt_log["validation"] = val
                if val["ok"]:
                    attempt_log["actions"].append({"modify_purchase_order": "skipped (new PO)"})
                else:
                    # Try to fix by reducing qty and modifying
                    new_qty = max(1, rec["qty"] - 10)
                    modify_purchase_order(po_result["po_id"], new_qty)
                    attempt_log["actions"].append({"modify_purchase_order": {"po_id": po_result["po_id"], "new_qty": new_qty}})
                    val2 = validate_po({"sku": rec["sku"], "qty": new_qty, "supplier_id": rec.get("supplier_id")})
                    attempt_log["validation_after_modify"] = val2
                    if not val2["ok"]:
                        history.append(attempt_log)
                        rec["qty"] = new_qty
                        continue
        else:
            attempt_log["actions"] = []
            attempt_log["validation"] = {"skipped": True, "reason": "No PO created (REJECT/INVESTIGATE)"}
        history.append(attempt_log)
        # If accepted and passed validation, break
        if decision in ("ACCEPT", "MODIFY") and attempt_log.get("validation", {}).get("ok"):
            break
    return {
        "final_decision": current_decision,
        "final_recommendation": rec,
        "validation_history": history,
        "retries_used": len(history) - 1
    }
