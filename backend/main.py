from fastapi import FastAPI
from config import ANTHROPIC_API_KEY

app = FastAPI(title="ai-purchasing-agent")

@app.get("/")
def root():
    return {"status": "ok", "api_key_set": bool(ANTHROPIC_API_KEY)}
