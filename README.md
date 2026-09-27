# ai-purchasing-agent

AI-powered purchasing agent with FastAPI backend and React frontend.

## Setup

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
npm run dev
```

## Environment

Copy `.env.example` to `.env` and add your `ANTHROPIC_API_KEY`. Never commit `.env`.
