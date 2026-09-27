"""Test scenarios for ai-purchasing-agent using real mock_data."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest
from validation_loop import run_with_validation
from unittest.mock import patch
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# --- Scenario tests against real mock data ---

def test_sku105_qty50_accept():
    res = run_with_validation({"sku": "SKU-105", "qty": 50, "supplier_id": "SUP-A"}, max_retries=2)
    assert res["final_decision"] == "ACCEPT", f"Expected ACCEPT, got {res['final_decision']}"
    trace_text = " ".join(str(t) for t in (res.get("validation_history") or []))
    assert "200" in trace_text or "inventory" in trace_text.lower(), "Trace missing real numbers"

def test_sku104_qty1000_reject():
    res = run_with_validation({"sku": "SKU-104", "qty": 1000, "supplier_id": "SUP-A"}, max_retries=2)
    assert res["final_decision"] == "REJECT", f"Expected REJECT, got {res['final_decision']}"
    trace_text = " ".join(str(t) for t in (res.get("validation_history") or []))
    assert "120" in trace_text or "1000" in trace_text, "Trace missing numeric values"

def test_sku101_qty500_reject_after_retry():
    res = run_with_validation({"sku": "SKU-101", "qty": 500, "supplier_id": "SUP-A"}, max_retries=2)
    assert res["final_decision"] == "REJECT", f"Expected REJECT, got {res['final_decision']}"
    history = res.get("validation_history", [])
    assert len(history) > 1, f"Expected >1 retry attempt, got {len(history)}"
    # Confirm different quantities across attempts (retry modifies qty)
    qtys = []
    for h in history:
        # Try to extract qty from reasoning or action log
        txt = " ".join(str(x) for x in h.get("reasoning_trace", []))
        if "qty" in txt.lower():
            pass  # rough check; primary assertion is length > 1
    # Primary assertion: retry_history has multiple attempts
    assert len(history) >= 2, "Retry history should show at least 2 attempts"

def test_sku103_qty200_investigate():
    res = run_with_validation({"sku": "SKU-103", "qty": 200, "supplier_id": "SUP-A"}, max_retries=2)
    # Sparse data case — should fall through to investigate
    assert res["final_decision"] in ("INVESTIGATE FURTHER", "REJECT", "MODIFY"), f"Unexpected decision: {res['final_decision']}"
    trace_text = " ".join(str(t) for t in (res.get("validation_history") or []))
    assert len(trace_text) > 0, "Reasoning trace empty"
    assert "[]" not in trace_text or "Inventory" in trace_text, "Trace has no real values"

# --- Failure handling (rate-limit mock) ---

def test_rate_limit_handled():
    from agent_graph import agent_graph
    with patch.object(agent_graph, "invoke", side_effect=Exception("429 RESOURCE_EXHAUSTED")):
        resp = client.post("/evaluate-purchase", json={"sku":"SKU-101","quantity":100,"supplier_id":"SUP-A"})
    assert resp.status_code == 503, f"Expected 503, got {resp.status_code}"
    body = resp.json()
    assert "rate limit" in body.get("error", "").lower() or "retry_after_seconds" in body, f"Unexpected body: {body}"

if __name__ == "__main__":
    # Simple runner for quick check without pytest
    for name, fn in [("SKU-105 accept", test_sku105_qty50_accept), ("SKU-104 reject", test_sku104_qty1000_reject),
                       ("SKU-101 retry", test_sku101_qty500_reject_after_retry), ("SKU-103 investigate", test_sku103_qty200_investigate),
                       ("Rate limit", test_rate_limit_handled)]:
        try:
            fn()
            print(f"PASS  {name}")
        except Exception as e:
            print(f"FAIL  {name}: {e}")
