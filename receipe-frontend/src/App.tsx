import { useState } from "react";
import { fetchRecipes } from "./api";
import type { Recipe } from "./types";
import "./App.css";

export default function App() {
  const [ingredients, setIngredients] = useState("");
  const [diet, setDiet] = useState("");
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!ingredients.trim()) {
      setError("Please enter at least one ingredient.");
      return;
    }
    setLoading(true);
    setError("");
    setRecipes([]);
    try {
      const data = await fetchRecipes(ingredients, diet);
      setRecipes(data.recipes);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app">
      <h1>🍳 Smart Recipe Analyzer</h1>
      <p className="subtitle">
        List what's in your kitchen — get recipes with nutrition.
      </p>

      <form onSubmit={onSubmit} className="form">
        <label htmlFor="ingredients">Ingredients (comma-separated)</label>
        <textarea
          id="ingredients"
          rows={3}
          placeholder="pasta, garlic, butter, parmesan"
          value={ingredients}
          onChange={(e) => {
            setIngredients(e.target.value);
            if (error) setError("");
          }}
        />

        <label htmlFor="diet">Dietary restriction (optional)</label>
        <select id="diet" value={diet} onChange={(e) => setDiet(e.target.value)}>
          <option value="">None</option>
          <option value="vegetarian">Vegetarian</option>
          <option value="vegan">Vegan</option>
          <option value="gluten-free">Gluten-free</option>
          <option value="keto">Keto</option>
        </select>

        <button type="submit" disabled={loading}>
          {loading ? "Cooking up ideas…" : "Get Recipes"}
        </button>
      </form>

      {error && <div className="error" role="alert">{error}</div>}

      {loading && <div className="spinner" aria-label="Loading" />}

      <section className="results">
        {recipes.map((r, i) => (
          <article key={i} className="card">
            <header>
              <h2>{r.name}</h2>
              <div className="meta">
                <span>⏱ {r.cookingTime}</span>
                <span>📊 {r.difficulty}</span>
              </div>
            </header>

            <div className="nutrition">
              <span>{r.nutrition.calories} cal</span>
              <span>{r.nutrition.protein} protein</span>
              <span>{r.nutrition.carbs} carbs</span>
            </div>

            <h3>Ingredients</h3>
            <ul>
              {r.ingredients.map((ing, j) => <li key={j}>{ing}</li>)}
            </ul>

            <h3>Instructions</h3>
            <ol>
              {r.instructions.map((step, j) => <li key={j}>{step}</li>)}
            </ol>
          </article>
        ))}
      </section>

      {recipes.length > 0 && (
        <p className="disclaimer">Nutrition values are AI estimates, not exact.</p>
      )}
    </main>
  );
}
