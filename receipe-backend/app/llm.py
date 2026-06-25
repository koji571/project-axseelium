"""DeepSeek integration (OpenAI-compatible API).

The one genuinely hard part of this app is making the LLM return JSON we can
parse reliably. We use DeepSeek's JSON output mode (`response_format`), which
constrains the model to emit a single valid JSON object. Per DeepSeek's docs
this requires (1) the word "json" in the prompt and (2) an example of the
desired shape — both are in the prompt below. Pydantic then validates the
parsed object against our schema as a final guard.

(deepseek-v4-flash is a thinking model and rejects forced tool_choice, so JSON
mode — not function calling — is the right structured-output path here.)

DeepSeek speaks the OpenAI API format, so we use the OpenAI SDK pointed at
DeepSeek's base URL.
"""

import json
import os

from openai import OpenAI

from .models import RecipeResponse

DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_BASE_URL = "https://api.deepseek.com"

# Shown to the model so it knows the exact JSON shape to return.
EXAMPLE_JSON = """{
  "recipes": [
    {
      "name": "Garlic Butter Pasta",
      "ingredients": ["pasta", "garlic", "butter", "parmesan"],
      "instructions": ["Boil pasta...", "Saute garlic..."],
      "cookingTime": "20 minutes",
      "difficulty": "Easy",
      "nutrition": { "calories": 450, "protein": "12g", "carbs": "60g" }
    }
  ]
}"""


def build_messages(ingredients: str, diet: str | None) -> list[dict]:
    diet_line = f"\nDietary restriction: all recipes must be {diet}." if diet else ""
    system = (
        "You are a helpful cooking assistant. You reply ONLY with a single valid "
        "JSON object matching this exact shape (no markdown, no prose):\n"
        f"{EXAMPLE_JSON}\n"
        "difficulty is one of Easy, Medium, Hard. calories is an integer; protein "
        "and carbs are strings like \"12g\". Nutrition values are rough per-serving "
        "estimates, not exact."
    )
    user = (
        "Generate 2-3 recipe suggestions that primarily use these ingredients "
        "(common pantry staples like salt, pepper, oil, water may be assumed): "
        f"{ingredients}.{diet_line}\n"
        "Return the result as the json object described above."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def generate_recipes(ingredients: str, diet: str | None = None) -> RecipeResponse:
    client = OpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url=os.environ.get("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL),
    )
    model = os.environ.get("DEEPSEEK_MODEL", DEFAULT_MODEL)

    resp = client.chat.completions.create(
        model=model,
        max_tokens=2048,
        response_format={"type": "json_object"},
        messages=build_messages(ingredients, diet),
    )

    content = resp.choices[0].message.content
    if not content or not content.strip():
        # DeepSeek docs note JSON mode may occasionally return empty content.
        raise ValueError("Model returned empty content")
    return RecipeResponse(**json.loads(content))
