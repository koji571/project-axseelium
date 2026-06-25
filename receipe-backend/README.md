# Recipe Backend (FastAPI)

Validates an ingredients list, asks an Anthropic model for 2-3 recipes, and
returns them as structured JSON.

## Why it returns reliable JSON

We don't ask the LLM for JSON in prose and parse the result. We define a **tool**
whose input schema is our response schema (`app/llm.py`) and force the model to
call it (`tool_choice`). The reply is already structured; Pydantic validates it as
a final guard. That removes the usual "model wrapped JSON in ```fences```" failure.

## Run

```bash
cd receipe-backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then put your ANTHROPIC_API_KEY in .env
uvicorn app.main:app --reload --port 8000
```

Docs at http://localhost:8000/docs

## Test (no API key needed)

```bash
python test_app.py     # or: pytest
```

## Endpoint

`POST /api/recipes`

```json
{ "ingredients": "pasta, garlic, butter", "diet": "vegetarian" }
```

`diet` is optional (bonus: dietary restrictions). Empty `ingredients` → 422.
