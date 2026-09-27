"""Agent tool functions for quick-commerce purchasing. Each reads/writes mock_data JSON."""
import json, os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "mock_data")

def _load(name):
    with open(os.path.join(DATA_DIR, name)) as f:
        return json.load(f)

def _save(name, data):
    with open(os.path.join(DATA_DIR, name), "w") as f:
        json.dump(data, f, indent=2)

# --- Tools for LLM function-calling ---

def get_inventory(sku: str, node: str = "") -> dict:
    """Get current stock levels for a SKU, optionally filtered by fulfillment node.
    Args:
        sku (str): SKU identifier (e.g., SKU-101).
        node (str): Optional node ID (e.g., node_west). Leave blank for all nodes.
    Returns: dict with inventory entries."""
    data = _load("inventory.json")
    results = [r for r in data.get("inventory", []) if r["sku"] == sku and (not node or r["node_id"] == node)]
    return {"sku": sku, "records": results}

def get_demand_forecast(sku: str) -> dict:
    """Get expected 7-day demand forecast for a SKU.
    Args:
        sku (str): SKU identifier.
    Returns: dict with demand and trend."""
    data = _load("demand_forecast.json")
    item = next((f for f in data.get("forecast", []) if f["sku"] == sku), None)
    return {"sku": sku, "forecast": item}

def get_open_purchase_orders(sku: str) -> dict:
    """List open purchase orders for a SKU.
    Args:
        sku (str): SKU identifier.
    Returns: dict with open POs."""
    data = _load("purchase_orders.json")
    orders = [o for o in data.get("open_purchases", []) if o["sku"] == sku]
    return {"sku": sku, "open_orders": orders}

def get_supplier_info(supplier_id: str) -> dict:
    """Get supplier details including lead time, MOQ, reliability.
    Args:
        supplier_id (str): Supplier identifier (e.g., SUP-A).
    Returns: supplier info dict."""
    data = _load("suppliers.json")
    item = next((s for s in data.get("suppliers", []) if s["supplier_id"] == supplier_id), None)
    return {"supplier_id": supplier_id, "info": item}

def get_available_budget() -> dict:
    """Get current purchasing budget status.
    Args: none.
    Returns: budget summary dict."""
    data = _load("budget.json")
    return data.get("budget", data)

def get_storage_capacity(node: str) -> dict:
    """Get storage capacity and usage for a fulfillment node.
    Args:
        node (str): Node ID (e.g., node_west).
    Returns: capacity info."""
    data = _load("storage.json")
    item = next((c for c in data.get("capacity", []) if c["node_id"] == node), None)
    return {"node": node, "capacity": item}

def create_purchase_order(sku: str, qty: int, supplier_id: str) -> dict:
    """Create a new open purchase order and append to mock data.
    Args:
        sku (str): SKU to order.
        qty (int): Quantity.
        supplier_id (str): Supplier identifier.
    Returns: created PO id and details."""
    data = _load("purchase_orders.json")
    po_id = f"PO-{len(data.get('open_purchases',[]))+1000:03d}"
    new_po = {"po_id": po_id, "sku": sku, "qty_ordered": qty, "status": "open", "supplier": supplier_id}
    data.setdefault("open_purchases", []).append(new_po)
    _save("purchase_orders.json", data)
    return {"po_id": po_id, "po": new_po}

def modify_purchase_order(po_id: str, new_qty: int) -> dict:
    """Modify quantity of an existing open purchase order.
    Args:
        po_id (str): Purchase order ID.
        new_qty (int): New quantity.
    Returns: updated PO."""
    data = _load("purchase_orders.json")
    for o in data.get("open_purchases", []):
        if o["po_id"] == po_id:
            o["qty_ordered"] = new_qty
            _save("purchase_orders.json", data)
            return {"po_id": po_id, "updated": o, "status": "modified"}
    return {"po_id": po_id, "status": "not_found"}
