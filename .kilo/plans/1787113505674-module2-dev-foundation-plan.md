# Module 2 Development Foundation Setup Plan

## Current State Assessment

### Existing Infrastructure (Reuse)

| Component | Status | Notes |
|---|---|---|
| Backend FastAPI app | ✅ Complete | `main.py`, `/api/v1` routes, lifespan |
| SQLite database layer | ✅ Complete | `database/db.py`, `database/data.py`, `init_db()` |
| Analytics engine | ✅ Complete | `analytics/engine.py`, `analytics/charts.py` |
| Insights engine | ✅ Complete | `insights/engine.py`, rule-based + optional Gemini |
| Recommendations engine | ✅ Complete | `recommendations/engine.py` |
| Pydantic schemas | ✅ Complete | `models/schemas.py` |
| Structured logging | ✅ Complete | `core/logging.py` (JSON formatter) |
| Request middleware | ✅ Complete | `core/middleware.py` (request ID, rate limit) |
| CORS + error handler | ✅ Complete | `main.py` |
| Research endpoints | ✅ Complete | `/research/task-log`, `/research/survey`, `/research/condition` |
| Frontend React app | ✅ Complete | Vite + TS + Tailwind + Plotly |
| Voice hooks | ✅ Complete | `use-voice-input.ts`, `use-voice-output.ts` |
| Task logger hook | ✅ Complete | `use-task-logger.ts` |
| Survey modal | ✅ Complete | `survey-modal.tsx` |
| Condition switcher | ✅ Complete | `condition-switcher.tsx` |
| Docker setup | ✅ Partial | Dockerfiles exist but reference `pyproject.toml` which is missing |
| CI/CD | ⚠️ Partial | `.github/workflows/` exists but may reference non-existent files |

### Gaps to Fill

| Gap | Severity | Required |
|---|---|---|
| `pyproject.toml` missing | **High** | Dockerfiles reference it; needed for modern Python packaging |
| Backend lint/typecheck commands | **High** | No `ruff`, `black`, `mypy` config |
| Frontend lint errors | **High** | Build succeeds but TS may have errors |
| Pre-commit hooks | Medium | Enforce quality gates |
| Makefile | Medium | Standardize dev commands |
| Secrets scanning | Medium | Prevent accidental secret commits |
| CI workflow validation | Medium | Ensure CI actually runs |
| README completeness | Medium | Missing setup commands, troubleshooting |
| `.env.example` completeness | Low | Backend has one, but some vars undocumented |

---

## Plan

### Phase 1: Backend Foundation

#### 1.1 Create `pyproject.toml`

```toml
[project]
name = "agristory-backend"
version = "0.1.0"
description = "Backend for Voice-Interactive Data Storytelling System"
requires-python = ">=3.12"
dependencies = [
    "fastapi==0.115.12",
    "uvicorn[standard]==0.34.2",
    "python-dotenv==1.1.0",
    "pandas==2.2.3",
    "numpy==2.1.3",
    "pydantic==2.11.1",
    "pydantic-settings==2.8.1",
    "reportlab==4.2.5",
    "httpx==0.28.1",
]

[project.optional-dependencies]
ai = ["google-genai==1.5.0"]
dev = [
    "pytest==8.3.5",
    "pytest-asyncio==0.24.0",
    "ruff==0.8.4",
    "black==24.10.0",
    "mypy==1.13.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]

[tool.black]
line-length = 88
target-version = ["py312"]

[tool.mypy]
python_version = "3.12"
strict = true
ignore_missing_imports = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

**Decision:** Use `hatchling` as build backend. It's modern, fast, and requires no extra build dependencies.

#### 1.2 Update `backend/.gitignore`

Ensure these are excluded:
- `__pycache__/`
- `*.py[cod]`
- `*.egg-info/`
- `.venv/`, `venv/`, `env/`
- `*.log`
- `*.db`, `*.sqlite3`
- `exports/`
- `.env`
- `.mypy_cache/`
- `.ruff_cache/`
- `.pytest_cache/`
- `.coverage`
- `htmlcov/`

#### 1.3 Update `backend/.env.example`

Add missing variables:
```env
APP_NAME=AgriStory Analytics API
ENV=development
DEBUG=false
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DATASET_FILE=agriculture.csv
DATABASE_URL=sqlite:///agri.db
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.0-flash
AI_ENABLED=true
```

#### 1.4 Create `backend/Makefile`

```makefile
.PHONY: install dev lint format typecheck test clean run

install:
	pip install -e ".[dev]"

dev:
	pip install -e ".[dev]"

lint:
	ruff check .

format:
	black .

typecheck:
	mypy .

test:
	pytest tests/ -v

run:
	uvicorn main:app --reload --port 8000

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .mypy_cache/ .ruff_cache/ .pytest_cache/ .coverage htmlcov/
```

#### 1.5 Create `backend/.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: detect-private-key
```

### Phase 2: Frontend Foundation

#### 2.1 Fix TypeScript/Lint Issues

Run `npm run lint` and `npm run typecheck` to identify issues. Fix all errors before proceeding.

#### 2.2 Create `frontend/.env.example` (verify)

Ensure it has:
```env
VITE_API_BASE_URL=/api
VITE_API_PROXY_TARGET=http://localhost:8000
```

#### 2.3 Create `frontend/Makefile`

```makefile
.PHONY: install dev lint format typecheck test build clean

install:
	npm install

dev:
	npm run dev

lint:
	npm run lint

format:
	npm run format

typecheck:
	npm run typecheck

test:
	npm run test

build:
	npm run build

clean:
	rm -rf dist/ node_modules/.cache
```

### Phase 3: Root-Level Configuration

#### 3.1 Create Root `Makefile`

```makefile
.PHONY: install backend-dev frontend-dev lint format typecheck test build clean docker-up docker-down

install:
	cd backend && make install
	cd frontend && make install

backend-dev:
	cd backend && make dev

frontend-dev:
	cd frontend && make dev

lint:
	cd backend && make lint
	cd frontend && make lint

format:
	cd backend && make format
	cd frontend && make format

typecheck:
	cd backend && make typecheck
	cd frontend && make typecheck

test:
	cd backend && make test
	cd frontend && make test

build:
	cd backend && make build
	cd frontend && make build

clean:
	cd backend && make clean
	cd frontend && make clean

docker-up:
	docker compose up --build

docker-down:
	docker compose down
```

#### 3.2 Create `.env.example` at root (optional)

For docker-compose environment variables that apply to both services.

#### 3.3 Update `.gitignore` at root

Add:
```
# Python
.mypy_cache/
.ruff_cache/
.pytest_cache/
.coverage
htmlcov/

# Secrets
*.pem
*.key
.env.local
.env.*.local
```

#### 3.4 Create `.pre-commit-config.yaml` at root

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: detect-private-key
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.4.2
    hooks:
      - id: prettier
        types_or: [typescript, typescriptreact, json, yaml, markdown]
```

### Phase 4: CI/CD

#### 4.1 Create `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install backend
        run: |
          cd backend
          pip install -e ".[dev]"
      - name: Lint
        run: cd backend && ruff check .
      - name: Format check
        run: cd backend && black --check .
      - name: Type check
        run: cd backend && mypy .
      - name: Test
        run: cd backend && pytest tests/ -v

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - name: Install frontend
        run: cd frontend && npm ci
      - name: Lint
        run: cd frontend && npm run lint
      - name: Type check
        run: cd frontend && npm run typecheck
      - name: Build
        run: cd frontend && npm run build
```

### Phase 5: Documentation

#### 5.1 Update `README.md`

Add:
- Setup instructions for local development
- Makefile commands
- Environment variables table
- Troubleshooting section
- Contributing guidelines (brief)

#### 5.2 Create `CONTRIBUTING.md`

Brief guide: fork, branch, commit, push, PR. Mention pre-commit hooks.

### Phase 6: Secrets and Security

#### 6.1 Add `detect-secrets` baseline

```bash
pip install detect-secrets
detect-secrets scan > .secrets.baseline
```

Add `.secrets.baseline` to git (it's a baseline, not actual secrets).

#### 6.2 Add CI secret scan step

```yaml
- name: Secret scan
  uses: trufflesecurity/trufflehog@main
  with:
    path: ./
    base: ${{ github.event.repository.default_branch }}
```

---

## Implementation Order

1. **pyproject.toml** — unblocks Docker and standardizes dependencies
2. **Backend .gitignore + .env.example** — security hygiene
3. **Backend Makefile + pre-commit** — developer experience
4. **Root Makefile + .pre-commit-config.yaml** — unified commands
5. **Frontend lint/typecheck fixes** — ensure clean state
6. **CI workflow** — automated validation
7. **README update** — onboarding
8. **Secrets scanning** — security baseline
9. **Verify clean install** — final validation

---

## Verification Steps

After implementation, verify:

```bash
# 1. Clean clone
git clone <repo-url> /tmp/agristory-clean
cd /tmp/agristory-clean

# 2. Backend
cd backend
cp .env.example .env
make install
make lint
make typecheck
make test

# 3. Frontend
cd ../frontend
cp .env.example .env
make install
make lint
make typecheck
make build

# 4. Docker
cd ..
docker compose up --build -d
curl http://localhost:8000/api/health
curl http://localhost:3000

# 5. Pre-commit
pip install pre-commit
pre-commit run --all-files
```

---

## Architectural Problems Discovered

| Problem | Location | Severity | Recommendation |
|---|---|---|---|
| `pyproject.toml` missing | Root/backend | **High** | Blocks Docker builds using modern Python packaging; creates ambiguity between `requirements.txt` and `pyproject.toml` |
| `main.py` references `pyproject.toml` | `Dockerfile.backend:7` | **High** | Docker build will fail because file doesn't exist |
| Frontend `node_modules` in repo | `.gitignore` missing `node_modules/` at frontend level | Low | Frontend `.gitignore` doesn't explicitly exclude `node_modules/` (though root does) |
| `GEMINI_API_KEY` in `.env.example` without value | `backend/.env.example:19` | Low | Should be empty string, not commented-out placeholder, to avoid confusion |
| No `py.typed` marker | Backend package | Low | Needed for mypy strict mode with package consumers |
| SQLite connection per function | `database/db.py` | Low | Acceptable for research tool; no connection pooling needed |
| Rate limiter in-memory | `main.py:23-44` | Low | Acceptable for single-user research; document for production |
| CORS `allow_credentials=True` with wildcard origins | `main.py:70` | Medium | Should not use `allow_credentials=True` with `*` origins; tighten for production |
| Frontend bundle size warning | Build output | Low | 4.9MB chunk; needs code splitting (already noted) |

---

## Open Questions

| # | Question | Recommendation | Blocking? |
|---|---|---|---|
| 1 | Should we use `requirements.txt` OR `pyproject.toml`? | Use `pyproject.toml` + `pip install -e ".[dev]"`; remove `requirements.txt` or keep as frozen export | Yes |
| 2 | Should Dockerfiles use `requirements.txt` or `pyproject.toml`? | Update Dockerfiles to use `pyproject.toml` | Yes |
| 3 | Should mypy strict mode be enforced now? | Yes — catch type errors early | No |
| 4 | Should we add `node_modules/` to frontend `.gitignore` explicitly? | Yes — defensive | No |
| 5 | Should `CORS_ORIGINS` allow `*` in development? | Yes, but remove `allow_credentials=True` when using `*` | No |
