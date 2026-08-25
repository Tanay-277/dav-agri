# Implementation Plan: Technical Architecture — Executable Tasks

## Goal

Provide a step-by-step, file-level implementation plan for the architecture defined in `1787113505674-technical-architecture.md`. Each task includes exact file paths, code changes, and validation steps.

**NOTE:** The current permission configuration restricts file edits to `.kilo/plans/*.md` only. The tasks below are documented for future execution when full edit access is available, or for handoff to an execution-capable agent.

---

## Phase 1: Backend Observability

### Task 1.1: Create Request Logging Middleware

**File to create:** `backend/core/middleware.py`

**Content:**
```python
from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger("agristory.request")


def _generate_request_id() -> str:
    return uuid.uuid4().hex[:8]


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Structured request logging middleware.

    Logs each request with method, path, status, duration, and request ID.
    Skips logging for health check endpoints to reduce noise.
    """

    def __init__(self, app, skip_paths: list[str] | None = None) -> None:
        super().__init__(app)
        self.skip_paths = set(skip_paths or ["/api/health", "/favicon.ico"])

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        if request.url.path in self.skip_paths:
            return await call_next(request)

        request_id = _generate_request_id()
        start = time.perf_counter()

        log_extra = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query": dict(request.query_params),
            "client_ip": request.client.host if request.client else "unknown",
        }

        logger.info("request_start", extra=log_extra)

        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = int((time.perf_counter() - start) * 1000)
            logger.error(
                "request_error",
                extra={
                    **log_extra,
                    "status": 500,
                    "duration_ms": duration_ms,
                    "error": str(exc),
                },
            )
            raise

        duration_ms = int((time.perf_counter() - start) * 1000)
        logger.info(
            "request_complete",
            extra={
                **log_extra,
                "status": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        response.headers["X-Request-ID"] = request_id
        return response
```

**Validation:**
- `pytest tests/test_api.py -v` — all 14 tests pass
- Manual: start backend, make requests, verify JSON logs appear
- Verify health endpoint `/api/health` is excluded from logs
- Verify `X-Request-ID` header appears in responses

---

### Task 1.2: Update Logging Configuration

**File to modify:** `backend/core/logging.py`

**Changes:**
1. Import `json` module
2. Replace `logging.Formatter` with a custom `JSONFormatter` class
3. Add request ID propagation via `logging.LoggerAdapter` or `extra` dict
4. Ensure all loggers use the JSON formatter

**Validation:**
- All log output is valid JSON
- Log levels are correctly set (DEBUG in dev, INFO in prod)
- No duplicate handlers

---

### Task 1.3: Register Middleware in main.py

**File to modify:** `backend/main.py`

**Changes:**
1. Import `RequestLoggingMiddleware` from `core.middleware`
2. Add `app.add_middleware(RequestLoggingMiddleware)` after `RateLimitMiddleware`
3. Ensure middleware order: CORS → RateLimit → RequestLogging → Routes

**Validation:**
- `pytest tests/test_api.py -v` — all 14 tests pass
- Backend starts without errors
- Request logs appear in correct order

---

## Phase 2: Frontend Error Reporting

### Task 2.1: Create Error Log Endpoint

**Files to modify:**
- `backend/models/schemas.py` — add `ErrorLog` schema
- `backend/api/routes.py` — add `POST /api/research/error-log`
- `backend/database/db.py` — add `record_error_log()` function + table

**Validation:**
- `pytest tests/test_api.py -v` — all tests pass
- POST to `/api/research/error-log` returns 200
- Error appears in SQLite `error_logs` table

---

### Task 2.2: Update ErrorBoundary Component

**File to modify:** `frontend/src/components/error-boundary.tsx`

**Changes:**
1. Add `onError?: (error: { message: string; componentStack: string; url: string }) => void` prop
2. In `componentDidCatch`, call `onError` with sanitized error info
3. Scrub PII from component stack (remove file paths, keep component names)
4. In `App.tsx`, pass error handler that POSTs to `/api/research/error-log`

**Validation:**
- Trigger error in development
- Verify error appears in backend logs
- Verify UI shows fallback (no crash loop)

---

## Phase 3: API Versioning

### Task 3.1: Update Route Prefix

**Files to modify:**
- `backend/main.py` — change `prefix="/api"` to `prefix="/api/v1"`
- `frontend/src/services/api.ts` — update `baseURL` to include `/api/v1`
- `frontend/src/services/dashboard.ts` — verify all endpoints use `/api/v1`

**Validation:**
- All existing API calls work
- Old `/api/` paths return 404
- Full regression test

---

## Phase 4: Frontend Automated Tests

### Task 4.1: Install Vitest

**Command:**
```bash
cd frontend
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

### Task 4.2: Create Vitest Config

**File to create:** `frontend/vitest.config.ts`

**Content:**
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/__tests__/setup.ts'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

### Task 4.3: Create Test Files

**Files to create:**
- `frontend/src/__tests__/setup.ts` — test setup
- `frontend/src/__tests__/use-voice-input.test.ts` — hook tests
- `frontend/src/__tests__/use-voice-output.test.ts` — hook tests
- `frontend/src/__tests__/voice-intents.test.ts` — parser tests
- `frontend/src/__tests__/kpi-card.test.tsx` — component test
- `frontend/src/__tests__/icon-legend.test.tsx` — component test

**Validation:**
- `npm run test` passes
- Coverage ≥ 60% for hooks

---

## Phase 5: Performance Profiling

### Task 5.1: Create Profiling Script

**File to create:** `backend/scripts/profile.py`

**Content:**
```python
import time
import json
from pathlib import Path
from database.data import get_filtered
from analytics.engine import compute_kpis
from analytics.charts import line_chart, bar_chart

DATASETS = {
    "10k": "dataset/profiling/agriculture_10k.csv",
    "50k": "dataset/profiling/agriculture_50k.csv",
    "100k": "dataset/profiling/agriculture_100k.csv",
}

def profile_dataset(name: str, path: str):
    # ... benchmark load, filter, KPI, chart times
    pass

if __name__ == "__main__":
    results = {}
    for name, path in DATASETS.items():
        results[name] = profile_dataset(name, path)
    print(json.dumps(results, indent=2))
```

### Task 5.2: Generate Profiling Datasets

**Command:**
```bash
python -c "
import pandas as pd
# Generate 10k, 50k, 100k row datasets
# Save to dataset/profiling/
"
```

**Validation:**
- Script runs without errors
- Output shows p50, p95, p99 latencies
- NFR-01 targets met or exceptions documented

---

## Phase 6: Icon Validation (Post-MVRS)

### Task 6.1: Create Icon Recognition Test

**Deliverable:** Printable/testable icon sheet with all 13 icons

**Protocol:**
1. Show icon to user without label
2. Ask user to describe what it means
3. Record accuracy
4. Target: ≥90% recognition per icon

### Task 6.2: Wizard-of-Oz Protocol

**Deliverable:** Script for voice + icon testing with 5 users

**Steps:**
1. Show icon + speak description
2. Ask user to confirm meaning
3. Iterate on confusing icons
4. Document findings

---

## 8. Integration Checkpoints

| Checkpoint | When | Criteria |
|---|---|---|
| CP1 | After Phase 1 | Request logs in JSON; health endpoint excluded; tests pass |
| CP2 | After Phase 2 | ErrorBoundary sends errors; backend stores them |
| CP3 | After Phase 3 | All routes use `/api/v1`; frontend updated |
| CP4 | After Phase 4 | `npm run test` passes; coverage ≥60% |
| CP5 | After Phase 5 | Profiling report generated; NFR targets met |
| CP6 | After Phase 6 | Icon recognition ≥90%; findings documented |

---

## 9. Validation Commands

```bash
# Backend tests
cd backend && .venv/bin/pytest tests/test_api.py -v

# Frontend build
cd frontend && npm run build

# Frontend tests (Phase 4+)
cd frontend && npm run test

# Performance profiling (Phase 5)
cd backend && python scripts/profile.py

# Type checking
cd frontend && npx tsc --noEmit
```

---

## 10. Out of Scope

- Service Worker / PWA
- User authentication
- Real-time data ingestion
- Mobile native apps
- LLM-based NLU replacement
- GraphQL
- OpenTelemetry distributed tracing
- CI/CD changes
