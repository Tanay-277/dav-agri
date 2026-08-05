# Interactive Data Storytelling Dashboard for Agricultural Analytics

A modern web application that transforms raw agricultural datasets into interactive
visualizations, automated insights, and narrative-style data stories.

See [plan.md](plan.md) for the full PRD.

## Tech Stack

| Layer | Stack |
|---|---|
| Frontend | React (Vite), TypeScript, Tailwind CSS, Plotly.js, React Router, Axios |
| Backend | FastAPI, Python 3.12+ |
| Analytics | Pandas, NumPy |
| AI | Gemini API (fallback: Rule-based Insight Engine) |
| Database | SQLite |
| Deployment | Frontend → Vercel, Backend → Render |

## Project Structure

```
project/
├── frontend/          # React (Vite) dashboard
├── backend/           # FastAPI service
│   ├── api/           # HTTP routes
│   ├── analytics/     # KPIs + chart data
│   ├── insights/      # insight detection + Gemini storytelling
│   ├── recommendations/# rule-based recommendations
│   ├── models/        # Pydantic schemas
│   ├── database/      # SQLite + dataset loading
│   └── core/          # config + logging
├── dataset/           # CSV datasets (agriculture.csv)
├── docs/
└── paper/
```

## Prerequisites

- Node.js 18+ / Bun
- Python 3.12+

## Backend Setup

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate        # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
cp .env.example .env            # then edit if needed
```

Run the server:

```bash
uvicorn main:app --reload --port 8000
```

- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

### Dataset

Place your CSV at `dataset/agriculture.csv` (configurable via `DATASET_FILE`).
The loader auto-detects common column names (crop, state, district, date,
rainfall, temperature, yield, production, humidity, soil_moisture, ...).

### AI (optional)

Set `GEMINI_API_KEY` in `backend/.env` to enable AI-powered storytelling. Without
it, the app transparently falls back to the rule-based engine.

## Frontend Setup

```bash
cd frontend
bun install        # or npm install
cp .env.example .env
```

Run the dev server (proxies `/api` to the backend):

```bash
bun run dev        # or npm run dev
```

Production build:

```bash
bun run build
```

## Backend APIs

| Endpoint | Description |
|---|---|
| `GET /api/dashboard` | KPIs + all chart data + filter options |
| `GET /api/insights` | Auto-generated insights |
| `GET /api/story` | Narrative story (AI or rule-based) |
| `GET /api/recommendations` | Rule-based recommendations |
| `GET /api/filters` | Available filter values |
| `POST /api/export` | Export dashboard as PDF / JSON |

All data endpoints accept the optional query filters:
`crop`, `state`, `district`, `start_date`, `end_date`.

## Deployment

- **Backend (Render):** command `uvicorn main:app --host 0.0.0.0 --port $PORT`,
  set `CORS_ORIGINS` to your Vercel URL.
- **Frontend (Vercel):** build command `bun run build`, output `dist`,
  set `VITE_API_BASE_URL` to the deployed backend origin.
