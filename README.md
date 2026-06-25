# Smart Recipe Analyzer

Enter the ingredients you have → get 2-3 AI-generated recipes with instructions,
cooking time, difficulty, and nutrition estimates.

- **`receipe-frontend/`** — React + TypeScript (Vite)
- **`receipe-backend/`** — FastAPI + Anthropic

## Quick start

```bash
# 1. Backend
cd receipe-backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # add your ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000

# 2. Frontend (new terminal)
cd receipe-frontend
npm install && npm run dev    # http://localhost:5173
```

## How it works

Frontend posts `{ ingredients, diet }` to `POST /api/recipes`. The backend
validates input (Pydantic), then asks an Anthropic model for recipes using a
**forced tool call** whose schema is the response schema — so the model returns
structured data instead of free-form JSON we'd have to parse defensively. See
`receipe-backend/README.md` for the why.
