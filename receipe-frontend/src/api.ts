import type { RecipeResponse } from "./types";

const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function fetchRecipes(
  ingredients: string,
  diet?: string,
): Promise<RecipeResponse> {
  const res = await fetch(`${BASE}/api/recipes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ingredients, diet: diet || null }),
  });

  if (!res.ok) {
    // FastAPI puts the message in `detail` (string, or array for 422 validation).
    const body = await res.json().catch(() => null);
    const detail = body?.detail;
    const msg = Array.isArray(detail) ? detail[0]?.msg : detail;
    throw new Error(msg || `Request failed (${res.status})`);
  }
  return res.json();
}
