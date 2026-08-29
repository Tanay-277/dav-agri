# Database / Data-Storage Layer — Implementation Plan

## 1. Design Decisions

### 1.1 Storage Strategy

| Data Type | Storage | Rationale |
|---|---|---|
| Locations | SQLite table `locations` | Static reference data, queryable by API |
| Weather observations | SQLite table `weather_observations` | Persisted normalized data from CSV + providers |
| Forecasts | SQLite table `forecasts` | Short-term forecasts (3–7 days) |
| Historical weather | SQLite table `weather_observations` (partitioned by date) | Same table; `data_classification` distinguishes historical |
| Agricultural context | SQLite table `agricultural_records` | Preprocessed CSV data joined with weather |
| Data sources | SQLite table `data_sources` | Provider metadata, lineage |
| User/query records | SQLite table `query_logs` | Dashboard filter history for evaluation |
| System insights | SQLite table `insights` | Structured insights (replaces JSON blob in `insight_history`) |

### 1.2 ORM vs Raw SQL

**Decision:** Continue with **raw SQLite** + **repository pattern**. Do NOT introduce SQLAlchemy.

**Rationale:**
- Existing codebase uses raw `sqlite3` exclusively.
- Project is a research prototype (Module 1 MVP), not a long-lived service.
- SQLAlchemy would add ~2MB dependency and require rewriting `db.py`, `cache.py`, all tests, and migration system.
- Repository pattern provides the requested separation without ORM overhead.

### 1.3 Migration System

**Decision:** Custom migration system using versioned SQL files in `backend/database/migrations/`.

**Rationale:**
- No Alembic (no SQLAlchemy).
- Lightweight: each migration is a `.sql` file with `UP` and `DOWN` sections.
- Applied automatically on startup via `init_db()` checking a `schema_version` table.
- Human-readable, auditable, and version-controllable.

---

## 2. Schema Definition

### 2.1 `locations`

```sql
CREATE TABLE IF NOT EXISTS locations (
    location_id TEXT PRIMARY KEY,           -- e.g. 'punjab_ludhiana'
    state TEXT NOT NULL,                    -- normalized state name
    district TEXT NOT NULL,                 -- normalized district name
    latitude REAL,                          -- decimal degrees, +N
    longitude REAL,                         -- decimal degrees, +E
    timezone TEXT DEFAULT 'Asia/Kolkata',   -- IANA timezone
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_locations_state ON locations(state);
CREATE INDEX idx_locations_district ON locations(district);
```

### 2.2 `data_sources`

```sql
CREATE TABLE IF NOT EXISTS data_sources (
    source_id TEXT PRIMARY KEY,             -- e.g. 'csv', 'open-meteo', 'nasa-power'
    name TEXT NOT NULL,                     -- human-readable name
    provider_type TEXT NOT NULL,            -- 'csv' | 'api' | 'model'
    configuration TEXT,                     -- JSON: API keys, file paths, etc.
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

### 2.3 `weather_observations`

```sql
CREATE TABLE IF NOT EXISTS weather_observations (
    observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id TEXT NOT NULL,              -- FK -> locations.location_id
    source_id TEXT NOT NULL,                -- FK -> data_sources.source_id
    timestamp TEXT NOT NULL,                -- ISO8601 UTC datetime
    record_date TEXT NOT NULL,              -- DATE only (for partitioning)
    data_classification TEXT NOT NULL,      -- 'historical' | 'current' | 'forecast'
    -- Weather variables (nullable = missing data, not imputed)
    rainfall_mm REAL,
    temperature_c REAL,
    humidity_pct REAL,
    soil_moisture_pct REAL,
    wind_speed_kmh REAL,
    cloud_cover_okta REAL,
    precipitation_probability_pct REAL,
    -- Metadata
    is_duplicate INTEGER NOT NULL DEFAULT 0,
    is_outlier INTEGER NOT NULL DEFAULT 0,
    is_invalid INTEGER NOT NULL DEFAULT 0,
    validation_flags TEXT,                  -- JSON array of flag strings
    raw_payload TEXT,                       -- JSON: original provider response
    source_row_id INTEGER,                  -- Original CSV row or API record ID
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES data_sources(source_id) ON DELETE RESTRICT
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_weather_unique
    ON weather_observations (location_id, source_id, timestamp, data_classification);
CREATE INDEX idx_weather_location_date ON weather_observations (location_id, record_date);
CREATE INDEX idx_weather_source ON weather_observations (source_id);
CREATE INDEX idx_weather_classification ON weather_observations (data_classification);
CREATE INDEX idx_weather_timestamp ON weather_observations (timestamp);
```

**Note:** Forecasts and historical weather share this table, distinguished by `data_classification`. This avoids data duplication and simplifies queries like "show me the last 30 days plus the 3-day forecast."

### 2.4 `agricultural_records`

```sql
CREATE TABLE IF NOT EXISTS agricultural_records (
    ag_record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id TEXT NOT NULL,              -- FK -> locations.location_id
    source_id TEXT NOT NULL,                -- FK -> data_sources.source_id
    record_date TEXT NOT NULL,              -- DATE
    crop TEXT NOT NULL,                     -- normalized crop name
    -- Agricultural variables
    yield_kg_per_ha REAL,
    production_tonnes REAL,
    area_ha REAL,
    fertilizer_kg REAL,
    irrigation_pct REAL,
    -- Metadata
    source_row_id INTEGER,                  -- Original CSV row ID
    is_duplicate INTEGER NOT NULL DEFAULT 0,
    is_outlier INTEGER NOT NULL DEFAULT 0,
    is_invalid INTEGER NOT NULL DEFAULT 0,
    validation_flags TEXT,                  -- JSON array
    raw_payload TEXT,                       -- JSON original
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES data_sources(source_id) ON DELETE RESTRICT
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_ag_unique
    ON agricultural_records (location_id, crop, record_date, source_id);
CREATE INDEX idx_ag_location_date ON agricultural_records (location_id, record_date);
CREATE INDEX idx_ag_crop ON agricultural_records (crop);
```

### 2.5 `query_logs`

```sql
CREATE TABLE IF NOT EXISTS query_logs (
    query_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,                        -- Browser session / user session
    user_id TEXT,                           -- Research participant ID (nullable)
    filters_json TEXT NOT NULL,             -- JSON of DashboardFilters
    result_summary TEXT,                    -- JSON: KPI summary, insight count
    response_time_ms INTEGER,               -- API response time
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_query_session ON query_logs (session_id);
CREATE INDEX idx_query_user ON query_logs (user_id);
CREATE INDEX idx_query_created ON query_logs (created_at);
```

### 2.6 `insights` (replaces JSON blob in `insight_history`)

```sql
CREATE TABLE IF NOT EXISTS insights (
    insight_id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_id INTEGER,                       -- FK -> query_logs.query_id (nullable)
    location_id TEXT,                       -- FK -> locations.location_id (nullable)
    crop TEXT,                              -- Filtered crop (nullable)
    insight_type TEXT NOT NULL,             -- 'trend' | 'anomaly' | 'comparison' | 'recommendation'
    metric TEXT NOT NULL,                   -- e.g. 'rainfall_mm', 'yield_kg_per_ha'
    severity TEXT NOT NULL DEFAULT 'info',  -- 'info' | 'warning' | 'critical'
    magnitude REAL,                         -- Numeric magnitude of the insight
    message TEXT NOT NULL,                  -- Human-readable insight text
    context_json TEXT,                      -- JSON: supporting data for the insight
    source TEXT NOT NULL DEFAULT 'rule',    -- 'rule' | 'ai'
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (query_id) REFERENCES query_logs(query_id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE SET NULL
);
CREATE INDEX idx_insights_query ON insights (query_id);
CREATE INDEX idx_insights_location ON insights (location_id);
CREATE INDEX idx_insights_type ON insights (insight_type);
CREATE INDEX idx_insights_created ON insights (created_at);
```

### 2.7 Retained Tables (no schema change)

- `task_logs` — MVRS research task logs (keep as-is)
- `survey_responses` — MVRS research survey responses (keep as-is)
- `dataset_meta` — key-value dataset metadata (keep as-is)

---

## 3. Repository / Data-Access Layer

### 3.1 Architecture

```
backend/database/
├── __init__.py
├── connection.py      # get_connection(), connection context manager
├── schema.py          # CREATE TABLE statements (idempotent)
├── migrations/        # Versioned SQL migrations
│   ├── 001_initial_schema.sql
│   ├── 002_add_forecasts.sql
│   └── ...
├── repositories/
│   ├── __init__.py
│   ├── base.py        # BaseRepository with common CRUD
│   ├── locations.py   # LocationRepository
│   ├── weather.py     # WeatherRepository
│   ├── agricultural.py # AgriculturalRepository
│   ├── sources.py     # DataSourceRepository
│   ├── queries.py     # QueryLogRepository
│   ├── insights.py    # InsightRepository
│   └── research.py    # TaskLog + SurveyRepository (existing)
├── models.py          # Pydantic models for DB entities (optional, for typing)
└── db.py              # init_db(), migration runner, legacy functions (deprecated)
```

### 3.2 Base Repository

```python
class BaseRepository:
    def __init__(self, table_name: str):
        self.table_name = table_name

    def _execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        conn = get_connection()
        try:
            cur = conn.execute(sql, params)
            conn.commit()
            return cur
        finally:
            conn.close()

    def find_by_id(self, pk_value) -> dict | None: ...
    def find_all(self, limit: int = 100) -> list[dict]: ...
    def insert(self, data: dict) -> int: ...
    def update(self, pk_value, data: dict) -> bool: ...
    def delete(self, pk_value) -> bool: ...
```

### 3.3 Specialized Repositories

Each repository provides typed methods for its domain:

```python
class WeatherRepository(BaseRepository):
    def get_current(self, location_id: str) -> dict | None:
        """Latest observation for a location."""
        sql = """SELECT * FROM weather_observations
                 WHERE location_id = ? AND data_classification IN ('current', 'historical')
                 ORDER BY timestamp DESC LIMIT 1"""
        ...

    def get_forecast(self, location_id: str, days: int = 3) -> list[dict]:
        """Forecast observations for a location."""
        sql = """SELECT * FROM weather_observations
                 WHERE location_id = ? AND data_classification = 'forecast'
                 ORDER BY timestamp ASC LIMIT ?"""
        ...

    def get_historical(self, location_id: str, start: str, end: str) -> list[dict]:
        """Historical observations in date range."""
        sql = """SELECT * FROM weather_observations
                 WHERE location_id = ? AND data_classification = 'historical'
                 AND record_date BETWEEN ? AND ?
                 ORDER BY record_date ASC"""
        ...

    def get_rainfall_trends(self, location_id: str, start: str, end: str) -> list[dict]:
        """Daily rainfall aggregation."""
        sql = """SELECT record_date, SUM(rainfall_mm) as total_rainfall,
                         AVG(rainfall_mm) as avg_rainfall
                 FROM weather_observations
                 WHERE location_id = ? AND record_date BETWEEN ? AND ?
                 GROUP BY record_date ORDER BY record_date ASC"""
        ...

    def get_temperature_trends(self, location_id: str, start: str, end: str) -> list[dict]:
        """Daily temperature aggregation."""
        sql = """SELECT record_date, AVG(temperature_c) as avg_temp,
                         MIN(temperature_c) as min_temp, MAX(temperature_c) as max_temp
                 FROM weather_observations
                 WHERE location_id = ? AND record_date BETWEEN ? AND ?
                 GROUP BY record_date ORDER BY record_date ASC"""
        ...

    def bulk_insert(self, records: list[dict]) -> int:
        """Batch insert with INSERT OR IGNORE to handle duplicates."""
        ...
```

### 3.4 CRUD Operations

All repositories implement:
- `create(data: dict) -> int` — insert and return new PK
- `get_by_id(pk: int) -> dict | None` — single row by PK
- `get_all(filters: dict, limit: int, offset: int) -> tuple[list[dict], int]` — paginated list + total count
- `update(pk: int, data: dict) -> bool` — partial update
- `delete(pk: int) -> bool` — soft or hard delete
- `exists(pk: int) -> bool` — existence check

---

## 4. Database Migrations

### 4.1 Migration File Format

```sql
-- migrations/001_initial_schema.sql
-- Description: Create initial tables for Module 1 MVP
-- Created: 2026-08-21

-- UP
CREATE TABLE IF NOT EXISTS locations (...);
CREATE TABLE IF NOT EXISTS data_sources (...);
CREATE TABLE IF NOT EXISTS weather_observations (...);
CREATE TABLE IF NOT EXISTS agricultural_records (...);
CREATE TABLE IF NOT EXISTS query_logs (...);
CREATE TABLE IF NOT EXISTS insights (...);

INSERT INTO data_sources (source_id, name, provider_type) VALUES ('csv', 'Local CSV', 'csv');

-- DOWN
DROP TABLE IF EXISTS insights;
DROP TABLE IF EXISTS query_logs;
DROP TABLE IF EXISTS agricultural_records;
DROP TABLE IF EXISTS weather_observations;
DROP TABLE IF EXISTS data_sources;
DROP TABLE IF EXISTS locations;
```

### 4.2 Migration Runner

```python
# backend/database/db.py
def run_migrations(conn: sqlite3.Connection) -> None:
    """Apply pending migrations in order."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    applied = {row[0] for row in conn.execute("SELECT version FROM schema_migrations").fetchall()}
    migration_dir = Path(__file__).parent / "migrations"
    for file in sorted(migration_dir.glob("*.sql")):
        version = int(file.stem.split("_")[0])
        if version not in applied:
            sql = file.read_text()
            up_section = sql.split("-- UP")[1].split("-- DOWN")[0].strip()
            conn.executescript(up_section)
            conn.execute("INSERT INTO schema_migrations (version) VALUES (?)", (version,))
            conn.commit()
```

---

## 5. Query Functions for Analytics

These go in `backend/database/repositories/weather.py` and `backend/database/repositories/agricultural.py`:

| Function | Purpose | Optimization |
|---|---|---|
| `get_current(location_id)` | Latest weather record | Index on `(location_id, timestamp DESC)` |
| `get_forecast(location_id, days)` | Upcoming forecast | Filter by `data_classification = 'forecast'` |
| `get_historical(location_id, start, end)` | Date-range history | Index on `(location_id, record_date)` |
| `get_rainfall_trends(location_id, start, end)` | Daily rainfall sums | `GROUP BY record_date`, use index |
| `get_temperature_trends(location_id, start, end)` | Daily min/avg/max temp | `GROUP BY record_date`, use index |
| `compare_locations(loc_ids, metric, start, end)` | Multi-location comparison | Single query with `IN` clause |
| `get_crop_summary(crop, start, end)` | Yield/production by crop | Join `agricultural_records` + `weather_observations` |

---

## 6. Connection Management

### 6.1 Connection Helper

```python
# backend/database/connection.py
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

_DB_PATH = Path(get_settings().DATABASE_URL.replace("sqlite:///", ""))

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")       # Better concurrency
    conn.execute("PRAGMA foreign_keys=ON")        # Enforce FK constraints
    conn.execute("PRAGMA cache_size=-64000")      # 64MB cache
    return conn

@contextmanager
def get_cursor() -> Generator[sqlite3.Cursor, None, None]:
    conn = get_connection()
    try:
        yield conn.cursor()
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
```

### 6.2 Test Database

```python
# backend/tests/conftest.py
@pytest.fixture
def test_db(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide an isolated test database."""
    db_path = tmp_path / "test.db"
    original = get_settings().DATABASE_URL
    get_settings().DATABASE_URL = f"sqlite:///{db_path}"
    init_db()  # Create schema
    yield db_path
    get_settings().DATABASE_URL = original
    if db_path.exists():
        db_path.unlink()
```

---

## 7. Error Handling

### 7.1 Custom Exceptions

```python
# backend/database/exceptions.py
class DatabaseError(Exception): ...
class RecordNotFound(DatabaseError): ...
class DuplicateRecord(DatabaseError): ...
class ConstraintViolation(DatabaseError): ...
class MigrationError(DatabaseError): ...
```

### 7.2 Error Handling Pattern

All repository methods:
1. Wrap SQLite errors in custom exceptions
2. Never expose raw SQL errors to API layer
3. Log full error with `logger.exception()`
4. Return safe sentinel values (`None`, `[]`) for "not found" cases

---

## 8. Implementation Steps (Ordered)

1. **Create `backend/database/connection.py`** — connection helper, WAL mode, pragmas
2. **Create `backend/database/exceptions.py`** — custom exception hierarchy
3. **Create `backend/database/models.py`** — Pydantic models for DB entities (optional but useful for typing)
4. **Create `backend/database/repositories/base.py`** — BaseRepository with CRUD
5. **Create migration `001_initial_schema.sql`** — all 6 new tables
6. **Create `backend/database/migrations/__init__.py`** — empty
7. **Update `backend/database/db.py`** — replace inline schema with migration runner; keep legacy functions but mark deprecated
8. **Create `backend/database/repositories/locations.py`** — LocationRepository
9. **Create `backend/database/repositories/sources.py`** — DataSourceRepository
10. **Create `backend/database/repositories/weather.py`** — WeatherRepository with trend queries
11. **Create `backend/database/repositories/agricultural.py`** — AgriculturalRepository
12. **Create `backend/database/repositories/queries.py`** — QueryLogRepository
13. **Create `backend/database/repositories/insights.py`** — InsightRepository
14. **Update `backend/database/repositories/research.py`** — move existing task_log/survey functions here
15. **Update `backend/tests/conftest.py`** — add `test_db` fixture
16. **Create `backend/tests/test_repositories.py`** — CRUD tests for each repository
17. **Update `backend/database/__init__.py`** — export key functions
18. **Update API routes** to use repositories instead of direct SQL (separate plan step)

---

## 9. Testing Strategy

### 9.1 Unit Tests (`backend/tests/test_repositories.py`)

| Test | Coverage |
|---|---|
| `test_location_crud` | Create, read, update, delete location |
| `test_source_crud` | Create, read, update, deactivate source |
| `test_weather_insert_and_query` | Insert observation, query by location/date |
| `test_weather_current_lookup` | Verify `get_current` returns latest |
| `test_weather_forecast_lookup` | Verify `get_forecast` filters by classification |
| `test_weather_historical_range` | Verify date range filtering |
| `test_rainfall_trends` | Verify daily aggregation |
| `test_temperature_trends` | Verify min/avg/max aggregation |
| `test_agricultural_crud` | Insert crop record, query by crop/date |
| `test_insight_crud` | Insert insight, query by query_id |
| `test_query_log_crud` | Insert query log, query by session |
| `test_duplicate_prevention` | Verify unique constraint on `(location_id, source_id, timestamp)` |
| `test_foreign_key_cascade` | Deleting location cascades to weather observations |
| `test_migration_runner` | Apply migrations, verify schema_version table |

### 9.2 Integration Tests

- Test full pipeline: preprocessor → repository → query functions
- Test API routes using repositories (in `test_api.py`)
- Verify WAL mode and connection pooling under concurrent access

---

## 10. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| SQLite concurrency limits | Write conflicts under concurrent API requests | WAL mode + short transactions; acceptable for research prototype |
| Schema evolution without migrations | Data loss or inconsistency | Versioned SQL migrations enforced on startup |
| Large dataset inserts slow | CSV → DB import takes seconds | `executemany()` + `PRAGMA cache_size`; acceptable for initial load |
| Test isolation | Tests interfere via shared DB | `test_db` fixture creates isolated temp file per test |

---

## 11. Out of Scope (Module 2+)

- PostgreSQL / MySQL migration
- SQLAlchemy ORM adoption
- Connection pooling (e.g., `DBUtils`)
- Read replicas
- Time-series partitioning (e.g., by month)
- Full-text search on insights

---

## 12. Validation Checklist

- [ ] `pytest tests/test_repositories.py -v` — all repository tests pass
- [ ] `pytest tests/ -v` — all existing tests still pass
- [ ] `make preprocess && make run` — app starts, migrations apply, dashboard loads
- [ ] `sqlite3 agri.db ".schema"` — all tables created with correct indexes
- [ ] `sqlite3 agri.db "SELECT COUNT(*) FROM schema_migrations"` — returns 1
- [ ] `ruff check database/` — lint passes
- [ ] `black --check database/` — format passes
- [ ] `mypy database/` — typecheck passes
