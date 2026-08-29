# Interactive Data Storytelling Dashboard for Agricultural Analytics

A modern web application that transforms raw agricultural datasets into interactive
visualizations, automated insights, and narrative-style data stories.

## Tech Stack

| Layer | Stack |
|---|---|
| **Frontend** | React (Vite), TypeScript, Tailwind CSS, Plotly.js, React Router, Axios |
| **Backend** | FastAPI, Python 3.12+ |
| **Analytics** | Pandas, NumPy |
| **AI** | Rule-based Insight Engine (Gemini API optional) |
| **Database** | SQLite |
| **Deployment** | Frontend → Vercel / Docker, Backend → Render / Docker |

## Project Structure

```
project/
├── frontend/          # React (Vite) dashboard
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── hooks/
│       ├── services/
│       └── lib/
├── backend/           # FastAPI service
│   ├── api/           # HTTP routes
│   ├── analytics/     # KPIs + chart data
│   ├── insights/      # insight detection + storytelling
│   ├── recommendations/# rule-based recommendations
│   ├── models/        # Pydantic schemas
│   ├── database/      # SQLite + dataset loading
│   ├── core/          # config + logging
│   └── tests/         # integration tests
├── dataset/           # CSV datasets (agriculture.csv)
├── docs/
├── paper/
├── Dockerfile.backend
├── Dockerfile.frontend
├── docker-compose.yml
├── vercel.json
├── render.yaml
├── Makefile
└── pyproject.toml     # Backend Python packaging
```

## Prerequisites

- Node.js 20+
- Python 3.12+
- Make (optional, for Makefile commands)
- pre-commit (optional, for git hooks)

## Quickstart (Docker)

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/docs
- Backend health: http://localhost:8000/api/health

## Local Development

### Using Makefile (Recommended)

```bash
# Install all dependencies
make install

# Start backend (in one terminal)
make backend-dev

# Start frontend (in another terminal)
make frontend-dev
```

### Manual Setup

#### Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate     # macOS / Linux
# .\.venv\Scripts\activate    # Windows
cp .env.example .env          # then edit if needed
pip install -e ".[dev]"
```

Run the server:

```bash
cd backend
uvicorn main:app --reload --port 8000
```

- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

#### Backend Commands

```bash
cd backend
make lint      # Run ruff linter
make format    # Format with black
make typecheck # Run mypy
make test      # Run pytest
make run       # Start dev server
make clean     # Remove caches
```

#### Frontend Setup

```bash
cd frontend
cp .env.example .env
npm install
```

Run the dev server (proxies `/api` to the backend):

```bash
cd frontend
npm run dev
```

Production build:

```bash
cd frontend
npm run build
```

#### Frontend Commands

```bash
cd frontend
make lint      # Run ESLint
make format    # Format with Prettier
make typecheck # Run TypeScript compiler
make test      # Run tests
make build     # Production build
make clean     # Remove dist and cache
```

## Dataset

Place your CSV at `dataset/agriculture.csv` (configurable via `DATASET_FILE`).
The loader auto-detects common column names (crop, state, district, date,
rainfall, temperature, yield, production, humidity, soil_moisture, area,
fertilizer, irrigation).

**Expected CSV schema:**

| Column | Description | Type |
|---|---|---|
| `date` | Record date | YYYY-MM-DD |
| `state` | State name | string |
| `district` | District name | string |
| `crop` | Crop type | string |
| `rainfall` | Rainfall in mm | number |
| `temperature` | Temperature in °C | number |
| `humidity` | Humidity % | number |
| `soil_moisture` | Soil moisture % | number |
| `yield` | Yield kg | number |
| `production` | Production tonnes | number |
| `area` | Cropped area ha | number |
| `fertilizer` | Fertilizer kg | number |
| `irrigation` | Irrigation % | number |

## Data Providers

The system supports pluggable weather data providers. By default, it uses the local CSV dataset.

### CSV Provider (Default)

No configuration needed. The system loads `dataset/agriculture.csv`.

### Open-Meteo Provider

To fetch historical weather data from Open-Meteo (no API key required):

1. Edit `backend/.env`:
   ```
   WEATHER_PROVIDER=open-meteo
   ```
2. Ensure `state` and `district` filters are provided for geocoding.
3. Data is cached in SQLite for 24 hours.

See [docs/data-providers.md](docs/data-providers.md) for full documentation.

## AI (optional)

Set `GEMINI_API_KEY` in `backend/.env` to enable AI-powered storytelling. Without
it, the app transparently falls back to the rule-based engine.

## Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | AgriStory Analytics API | Application name |
| `ENV` | development | Environment (development/production) |
| `DEBUG` | false | Enable debug mode |
| `HOST` | 0.0.0.0 | Server host |
| `PORT` | 8000 | Server port |
| `CORS_ORIGINS` | http://localhost:5173 | Comma-separated allowed origins |
| `DATASET_FILE` | agriculture.csv | CSV filename in dataset/ |
| `DATABASE_URL` | sqlite:///agri.db | SQLite database URL |
| `GEMINI_API_KEY` | (empty) | Google Gemini API key |
| `GEMINI_MODEL` | gemini-2.0-flash | Gemini model name |
| `AI_ENABLED` | false | Enable AI storytelling |

### Frontend (`frontend/.env`)

| Variable | Default | Description |
|---|---|---|
| `VITE_API_BASE_URL` | /api | Backend API base URL |
| `VITE_API_PROXY_TARGET` | http://localhost:8000 | Vite dev proxy target |

## Backend APIs

| Endpoint | Description |
|---|---|
| `GET /api/v1/health` | Health check |
| `GET /api/v1/dashboard` | KPIs + all chart data + filter options |
| `GET /api/v1/insights` | Auto-generated insights |
| `GET /api/v1/story` | Narrative story (AI or rule-based) |
| `GET /api/v1/recommendations` | Rule-based recommendations |
| `GET /api/v1/filters` | Available filter values |
| `POST /api/v1/export` | Export dashboard as PDF / JSON |
| `GET /api/v1/dataset/status` | Dataset load status |

All data endpoints accept the optional query filters:
`crop`, `state`, `district`, `start_date`, `end_date`.

## Testing

### Backend

```bash
cd backend
make test
```

### Frontend

```bash
cd frontend
make test
```

## Code Quality

### Linting and Formatting

```bash
# Backend
cd backend
make lint      # ruff
make format    # black

# Frontend
cd frontend
make lint      # eslint
make format    # prettier
```

### Type Checking

```bash
# Backend
cd backend
make typecheck # mypy

# Frontend
cd frontend
make typecheck # tsc
```

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install

# Run on all files
pre-commit run --all-files
```

## Deployment

### Docker

```bash
docker compose up --build -d
```

### Frontend (Vercel)

- Build command: `cd frontend && npm run build`
- Output directory: `frontend/dist`
- Environment variable: `VITE_API_BASE_URL` → your Render backend URL

### Backend (Render)

- Runtime: Python 3.12
- Build command: `pip install -e ".[dev]"` (or `pip install -e ".[ai]"` if using Gemini)
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Environment variables:
  - `CORS_ORIGINS` → your Vercel frontend URL
  - `DATASET_FILE` → `agriculture.csv`
  - `DEBUG` → `false`

## Troubleshooting

### Backend won't start

- Ensure `.env` exists: `cp backend/.env.example backend/.env`
- Check Python version: `python --version` (requires 3.12+)
- Check port 8000 is free: `lsof -i :8000`

### Frontend won't start

- Ensure `.env` exists: `cp frontend/.env.example frontend/.env`
- Check Node version: `node --version` (requires 20+)
- Check port 5173 is free: `lsof -i :5173`

### Docker build fails

- Ensure Docker daemon is running
- Check disk space: `docker system df`
- Rebuild without cache: `docker compose build --no-cache`

## License

[Add license here]
