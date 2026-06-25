# Smart Recipe Analyzer

Enter the ingredients you have → get 2-3 AI-generated recipes with instructions,
cooking time, difficulty, and nutrition estimates.

- **`receipe-frontend/`** — React + TypeScript (Vite)
- **`receipe-backend/`** — FastAPI + DeepSeek (`deepseek-v4-flash`)

## Quick start

```bash
# 1. Backend
cd receipe-backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # add your DEEPSEEK_API_KEY
uvicorn app.main:app --reload --port 8000

# 2. Frontend (new terminal)
cd receipe-frontend
npm install && npm run dev    # http://localhost:5173
```

## How it works

Frontend posts `{ ingredients, diet }` to `POST /api/recipes`. The backend
validates input (Pydantic), then asks DeepSeek (`deepseek-v4-flash`) for recipes
using **JSON output mode** (`response_format`) — so the model returns one valid
JSON object instead of free-form text we'd have to parse defensively. See
`receipe-backend/README.md` for the why.
