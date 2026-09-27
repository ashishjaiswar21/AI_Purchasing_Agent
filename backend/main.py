from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import GOOGLE_API_KEY
from pydantic import BaseModel
from validation_loop import run_with_validation

app = FastAPI(title="ai-purchasing-agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PurchaseRequest(BaseModel):
    sku: str
    quantity: int
    supplier_id: str = "SUP-A"

@app.get("/health")
def health():
    return {"status": "healthy", "api_key_set": bool(GOOGLE_API_KEY)}

@app.post("/evaluate-purchase")
def evaluate_purchase(req: PurchaseRequest):
    rec = {"sku": req.sku, "qty": req.quantity, "supplier_id": req.supplier_id}
    result = run_with_validation(rec, max_retries=2)
    return {
        "final_decision": result["final_decision"],
        "reasoning_trace": result["validation_history"][0]["reasoning_trace"] if result["validation_history"] else [],
        "action_taken": result["validation_history"][0]["actions"] if result["validation_history"] else [],
        "validation_result": result["validation_history"][0].get("validation", {}),
        "retry_history": result["validation_history"]
    }

@app.get("/")
def root():
    return {"status": "ok", "api_key_set": bool(GOOGLE_API_KEY)}
