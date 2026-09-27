# AI Purchasing Agent — Assignment Completion

Repo (public): https://github.com/ashishjaiswar21/AI_Purchasing_Agent
Branch: main (23 commits, attribution preserved)
Date: 2026-09-27

---

## 1. Scenario Implemented (End-to-End)
**Scenario 1 — Purchase Recommendation Review** fully implemented.
- Agent receives a purchase recommendation (SKU + qty + supplier).
- Investigates: inventory, demand forecast, open POs, supplier info, budget, storage.
- Decides: ACCEPT / MODIFY / REJECT / INVESTIGATE FURTHER.
- Explains decision with exact numbers cited from mock data (e.g., 65 total vs 800 requested).
- Validates result; retries with corrected quantity if constraints fail.

Files: `backend/agent_graph.py`, `backend/validation_loop.py`, `backend/main.py`, `tests/test_scenarios.py`

---

## 2. Architecture & Design
- **Diagram**: `README.md` contains mermaid flow (Gather → Reason → Validate → Retry → Response).
- **Approach**: `README.md` §3 explains why split gather/reason/validate/retry.
- **Design decisions**: `README.md` §4 covers validation retry with qty correction, grounding in real JSON, graceful 503 on 429.
- **Technology stack**: FastAPI (backend), React/Vite (frontend), LangGraph + ChatGroq (agent), pytest (tests).

---

## 3. Agent Tools & Interaction
- 8 JSON-based tools (`backend/tools.py`): `get_inventory`, `get_demand_forecast`, `get_open_purchase_orders`, `get_supplier_info`, `get_available_budget`, `get_storage_capacity` + save/modify.
- Agent uses direct data injection into prompt (Groq `bind_tools` fails — documented and resolved).
- Memory: `MemorySaver` via LangGraph checkpointer.

---

## 4. Mock Data (Created / Used)
`mock_data/` (7 JSON files): `inventory.json`, `demand_forecast.json`, `purchase_orders.json`, `suppliers.json`, `budget.json`, `storage.json`, `products.json`

---

## 5. Validation / Feedback Loop (Key Rubric Focus)
- `validation_loop.py`: validates PO against budget, storage, MOQ.
- If fails: reduces qty (e.g., qty - 10), writes corrected order via `modify_purchase_order`, logs to `retry_history`, retries (max 2).
- Test proof: `tests/test_scenarios.py` `test_sku101_qty500_reject_after_retry` asserts `len(history) > 1`.
- Endpoint (`main.py` `/evaluate-purchase`) catches 429 and returns 503 with retry info — no crash.

---

## 6. Tests & Evaluation (5 Cases)
File: `tests/test_scenarios.py`
| Case | SKU / Qty | Expected | Verified |
|---|---|---|---|
| Accept | SKU-105 / 50 | ACCEPT | 200 available; trace with real numbers |
| Reject | SKU-104 / 1000 | REJECT | only 120 exist |
| Retry | SKU-101 / 500 | REJECT after retry | `retry_history` > 1 attempt; qty corrected |
| Investigate | SKU-103 / 200 | INVESTIGATE FURTHER / MODIFY | sparse data handled |
| Failure handling | mock 429 | 503 clean | `test_rate_limit_handled` |

---

## 7. Security / Commit Hygiene
- `.env` sanitized (placeholder only, not committed): verified.
- `.gitignore`: excludes `.env`, `.venv`, `node_modules`, `__pycache__`.
- `.env.example`: `GROQ_API_KEY=` placeholder + model override.
- No secrets in repo history.
- All commits end with: `Co-Authored-By: Claude Code <noreply@anthropic.com>`
- PR descriptions include (if created): `🤖 Generated with [Claude Code](https://claude.com/claude-code)`

---

## 8. Demo / Run
```bash
# Backend
cd backend && source .venv/bin/activate && uvicorn main:app --reload --port 8000
# Frontend
cd ../frontend && npm install && npm run dev  # http://localhost:5173
# Tests
.venv/bin/python tests/test_scenarios.py
```

---

## 9. What Was Not Required / Not Built
- Scenario 2 (Supplier Cannot Fulfil), 3 (Forecast Change), 4 (Purchasing Constraint) are referenced in structure but not fully implemented (scope per rubric: one scenario end-to-end sufficient; quality over breadth).
- No production-grade infrastructure; mock APIs/JSON only, per rubric.

---

## 10. Submission Checklist (Per Rubric)
- [x] Complete source code (backend / frontend / mock_data / tests)
- [x] README.md with setup, run, architecture diagram, approach, design decisions, evaluation, limitations
- [x] Test scenarios demonstrating behavior + validation approach
- [x] Mock APIs / datasets included
- [x] Explanation of validation / feedback loop included
- [x] Working demo (local run instructions; frontend at localhost:5173)
- [x] `.env.example` present; secrets excluded from commits
- [x] Git history intact; public repo URL provided

