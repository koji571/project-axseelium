"""Request/response schema. Pydantic gives us validation + a clean contract for free.

The same field shapes are handed to the LLM as a tool schema (see llm.py), so the
model is forced to return exactly this structure instead of free-form JSON we'd
have to defensively parse.
"""

from pydantic import BaseModel, Field, field_validator


class Nutrition(BaseModel):
    calories: int
    protein: str  # e.g. "12g" — kept as string to match the brief's example
    carbs: str


class Recipe(BaseModel):
    name: str
    ingredients: list[str]
    instructions: list[str]
    cookingTime: str
    difficulty: str
    nutrition: Nutrition


class RecipeResponse(BaseModel):
    recipes: list[Recipe]


class RecipeRequest(BaseModel):
    ingredients: str = Field(..., description="Comma-separated ingredients")
    diet: str | None = Field(None, description="Optional dietary restriction, e.g. 'vegan'")

    @field_validator("ingredients")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Ingredients list must not be empty")
        return v.strip()
