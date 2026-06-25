"""FastAPI app: validate input -> call LLM -> return structured recipes."""

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .llm import generate_recipes
from .models import RecipeRequest, RecipeResponse

load_dotenv()

app = FastAPI(title="Smart Recipe Analyzer")


@app.exception_handler(RequestValidationError)
async def on_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Surface a single clean message (e.g. "Ingredients list must not be empty")
    # instead of FastAPI's raw error array with Pydantic's "Value error," prefix.
    msg = exc.errors()[0].get("msg", "Invalid request").removeprefix("Value error, ")
    return JSONResponse(status_code=422, content={"detail": msg})

origins = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_methods=["POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/recipes", response_model=RecipeResponse)
def recipes(req: RecipeRequest) -> RecipeResponse:
    # Pydantic already rejected empty ingredients (422). Here we guard the LLM call.
    try:
        return generate_recipes(req.ingredients, req.diet)
    except KeyError:
        raise HTTPException(500, "Server is missing DEEPSEEK_API_KEY")
    except Exception as e:  # network error, malformed model output, etc.
        raise HTTPException(502, f"Failed to generate recipes: {e}")
