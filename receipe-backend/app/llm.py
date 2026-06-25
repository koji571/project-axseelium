"""Anthropic integration.

The one genuinely hard part of this app is making the LLM return JSON we can
parse 100% of the time. We don't ask for JSON in prose and hope — we hand the
model a *tool* whose input schema is our Pydantic schema and force it to call
that tool. The SDK then returns structured input that already matches our shape,
so parsing is `RecipeResponse(**tool_input)` with no string surgery.
"""

import os

from anthropic import Anthropic

from .models import RecipeResponse

DEFAULT_MODEL = "claude-haiku-4-5-20251001"

# The tool schema == our response schema. tool_choice forces the model to use it.
RECIPE_TOOL = {
    "name": "return_recipes",
    "description": "Return the generated recipes in structured form.",
    "input_schema": {
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
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    model = os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL)

    msg = client.messages.create(
        model=model,
        max_tokens=2048,
        tools=[RECIPE_TOOL],
        tool_choice={"type": "tool", "name": "return_recipes"},
        messages=[{"role": "user", "content": build_prompt(ingredients, diet)}],
    )

    tool_use = next(b for b in msg.content if b.type == "tool_use")
    # Pydantic validates the model's output against our schema — last line of defense.
    return RecipeResponse(**tool_use.input)
