# Recipe Backend (FastAPI)

Validates an ingredients list, asks a DeepSeek model (`deepseek-v4-flash`) for
2-3 recipes, and returns them as structured JSON. DeepSeek's API is
OpenAI-compatible, so we use the OpenAI SDK pointed at `api.deepseek.com`.

## Why it returns reliable JSON

We use DeepSeek's **JSON output mode** (`response_format={"type":"json_object"}`),
which constrains the model to emit one valid JSON object. Per DeepSeek's docs the
prompt includes the word "json" and an example of the target shape (`app/llm.py`).
Pydantic validates the parsed object as a final guard. (deepseek-v4-flash is a
thinking model and rejects forced `tool_choice`, so JSON mode — not function
calling — is the structured-output path here.)

## Run

```bash
cd receipe-backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then put your DEEPSEEK_API_KEY in .env
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
