"""Offline self-checks: input validation + schema parsing. No network/API key needed.

Run: python test_app.py
"""

from contextlib import contextmanager

from pydantic import ValidationError

from app.models import RecipeRequest, RecipeResponse


@contextmanager
def raises(exc):
    try:
        yield
    except exc:
        return
    raise AssertionError(f"expected {exc.__name__}")

EXAMPLE = {
    "recipes": [{
        "name": "Garlic Butter Pasta",
        "ingredients": ["pasta", "garlic", "butter", "parmesan"],
        "instructions": ["Boil pasta...", "Sauté garlic..."],
        "cookingTime": "20 minutes",
        "difficulty": "Easy",
        "nutrition": {"calories": 450, "protein": "12g", "carbs": "60g"},
    }]
}


def test_empty_ingredients_rejected():
    for bad in ["", "   "]:
        with raises(ValidationError):
            RecipeRequest(ingredients=bad)


def test_ingredients_trimmed():
    assert RecipeRequest(ingredients="  eggs, flour  ").ingredients == "eggs, flour"


def test_example_response_parses():
    parsed = RecipeResponse(**EXAMPLE)
    assert parsed.recipes[0].nutrition.calories == 450


if __name__ == "__main__":
    test_empty_ingredients_rejected()
    test_ingredients_trimmed()
    test_example_response_parses()
    print("ok")
