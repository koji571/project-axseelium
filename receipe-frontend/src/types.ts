// Mirrors the backend RecipeResponse schema (receipe-backend/app/models.py).
export interface Nutrition {
  calories: number;
  protein: string;
  carbs: string;
}

export interface Recipe {
  name: string;
  ingredients: string[];
  instructions: string[];
  cookingTime: string;
  difficulty: string;
  nutrition: Nutrition;
}

export interface RecipeResponse {
  recipes: Recipe[];
}
