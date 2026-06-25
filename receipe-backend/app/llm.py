"""DeepSeek integration (OpenAI-compatible API).

The one genuinely hard part of this app is making the LLM return JSON we can
parse 100% of the time. We don't ask for JSON in prose and hope — we hand the
model a *tool* whose parameter schema is our Pydantic schema and force it to
call that tool (`tool_choice`). The model then returns its answer as the tool's
JSON arguments, which we validate with Pydantic — no string surgery.

DeepSeek speaks the OpenAI API format, so we use the OpenAI SDK pointed at
DeepSeek's base URL.
"""

import json
import os

from openai import OpenAI

from .models import RecipeResponse

DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_BASE_URL = "https://api.deepseek.com"

# OpenAI function-calling schema. The function's parameters == our response schema.
RECIPE_TOOL = {
    "type": "function",
    "function": {
        "name": "return_recipes",
        "description": "Return the generated recipes in structured form.",
        "parameters": {
            "type": "object",
            "properties": {
                "recipes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "ingredients": {"type": "array", "items": {"type": "string"}},
                            "instructions": {"type": "array", "items": {"type": "string"}},
                            "cookingTime": {"type": "string", "description": "e.g. '20 minutes'"},
                            "difficulty": {"type": "string", "enum": ["Easy", "Medium", "Hard"]},
                            "nutrition": {
                                "type": "object",
                                "properties": {
                                    "calories": {"type": "integer"},
                                    "protein": {"type": "string", "description": "e.g. '12g'"},
                                    "carbs": {"type": "string", "description": "e.g. '60g'"},
                                },
                                "required": ["calories", "protein", "carbs"],
                            },
                        },
                        "required": [
                            "name", "ingredients", "instructions",
                            "cookingTime", "difficulty", "nutrition",
                        ],
                    },
                }
            },
            "required": ["recipes"],
        },
    },
}


def build_prompt(ingredients: str, diet: str | None) -> str:
    diet_line = f"\nDietary restriction: all recipes must be {diet}." if diet else ""
    return (
        "You are a helpful cooking assistant. Generate 2-3 recipe suggestions that "
        "primarily use the ingredients the user has on hand. Common pantry staples "
        "(salt, pepper, oil, water) may be assumed.\n"
        f"Available ingredients: {ingredients}.{diet_line}\n\n"
        "For each recipe include realistic estimated cooking time, a difficulty level, "
        "and rough nutritional estimates per serving (these are approximations, not "
        "lab-measured values). Return your answer via the return_recipes tool."
    )


def generate_recipes(ingredients: str, diet: str | None = None) -> RecipeResponse:
    client = OpenAI(
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url=os.environ.get("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL),
    )
    model = os.environ.get("DEEPSEEK_MODEL", DEFAULT_MODEL)

    resp = client.chat.completions.create(
        model=model,
        max_tokens=2048,
        tools=[RECIPE_TOOL],
        tool_choice={"type": "function", "function": {"name": "return_recipes"}},
        messages=[{"role": "user", "content": build_prompt(ingredients, diet)}],
    )

    # Forced tool call -> arguments is a JSON string. Pydantic validates the shape.
    args = resp.choices[0].message.tool_calls[0].function.arguments
    return RecipeResponse(**json.loads(args))
