# Recipe Frontend (React + TS + Vite)

Single-page UI: enter comma-separated ingredients (plus an optional dietary
filter), get AI-generated recipes with nutrition. Has loading, error, and
responsive states.

## Run

```bash
cd receipe-frontend
npm install
npm run dev        # http://localhost:5173
```

Expects the backend on `http://localhost:8000`. To point elsewhere, copy
`.env.example` to `.env` and set `VITE_API_URL`.

## Layout

- `src/App.tsx` — form + results + loading/error state
- `src/api.ts` — backend call, unwraps FastAPI error shapes
- `src/types.ts` — mirror of the backend response schema
