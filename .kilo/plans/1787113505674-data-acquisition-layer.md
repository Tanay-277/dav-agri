# Data Acquisition Layer — Implementation Plan

## 1. Current State

| Component | Status |
|---|---|
| `database/data.py` | Loads single CSV via `_load_dataset()` (lru_cache). No external APIs. |
| `database/db.py` | SQLite for research logs only. No weather API response cache. |
| `core/config.py` | Has `DATASET_FILE`, `DATASET_DIR`. No weather provider settings. |
| `analytics/engine.py` | Consumes DataFrame from `database.data`. No source awareness. |
| `insights/engine.py` | Consumes DataFrame. No source awareness. |
| `recommendations/engine.py` | Consumes DataFrame. No source awareness. |
| `api/routes.py` | All endpoints call `data.get_filtered()`. Single source. |

## 2. Design Decisions

### 2.1 Provider Selection

| Provider | Role | Rationale |
|---|---|---|
| **CSV (existing)** | Primary source (MVRS) | Zero dependencies, deterministic, offline-capable |
| **Open-Meteo** | Historical weather API | Free, no API key, global coverage, historical data (1950–present), permissive license (CC-BY). Single-step geocoding + weather. |
| **NASA POWER** | Alternative/fallback | Public domain, agricultural-specific variables (soil moisture, humidity), but requires API key and has more complex response format. |

**Decision:** Use Open-Meteo as the primary API provider. NASA POWER is a documented alternative but not implemented in this batch.

### 2.2 Internal Schema

All providers normalize to this canonical schema:

```python
WeatherRecord:
    timestamp: datetime       # UTC
    location_id: str          # e.g. "punjab_ludhiana"
    latitude: float | None
    longitude: float | None
    rainfall_mm: float | None
    temperature_c: float | None
    humidity_pct: float | None
    soil_moisture_pct: float | None
    wind_speed_kmh: float | None
    cloud_cover_okta: float | None
    precipitation_probability_pct: float | None
    source: str               # "csv", "open-meteo", "nasa-power"
    raw: dict | None          # Original provider response for debugging
```

Agricultural data (crop, yield, production, etc.) remains CSV-only for now.

### 2.3 Architecture

```
backend/
  data_ingestion/
    __init__.py
    base.py              # Abstract base provider + WeatherRecord schema
    csv_provider.py      # Existing CSV loader (refactored)
    openmeteo_provider.py # Open-Meteo API client
    normalizer.py        # Provider response → WeatherRecord
    cache.py             # SQLite-backed response cache
    errors.py            # Custom exception hierarchy
    settings.py          # Provider selection + API keys
  database/
    data.py              # Updated to use provider abstraction
    db.py                # Add API cache tables
```

### 2.4 Caching Strategy

- **CSV data:** Existing `lru_cache` on `_load_dataset()` is sufficient.
- **API responses:** SQLite table `weather_api_cache` keyed by `(provider, location_id, date)`.
  - TTL: 24 hours for historical, 3 hours for forecast.
  - On cache hit: return cached record.
  - On cache miss: fetch from API, store, return.
  - On API failure: return cached data if available, else raise.

### 2.5 Error Handling

| Failure Mode | Behavior |
|---|---|
| API timeout (>10s) | Return cached data or empty DataFrame; log warning |
| API 429 rate limit | Back off exponentially (1s, 2s, 4s); return cached data |
| API 401/403 | Log error; disable provider for session; fall back to CSV |
| Network unreachable | Return cached data or empty DataFrame; log warning |
| Malformed response | Log raw response; return empty DataFrame for that source |
| Missing values in response | Leave as `None`; do NOT fabricate or impute |

### 2.6 Settings

Add to `core/config.py`:

```python
WEATHER_PROVIDER: str = os.getenv("WEATHER_PROVIDER", "csv")  # "csv" | "open-meteo"
OPEN_METEO_URL: str = os.getenv("OPEN_METEO_URL", "https://api.open-meteo.com/v1")
OPEN_METEO_TIMEOUT_S: int = int(os.getenv("OPEN_METEO_TIMEOUT_S", "10"))
WEATHER_CACHE_TTL_HOURS: int = int(os.getenv("WEATHER_CACHE_TTL_HOURS", "24"))
```

### 2.7 Provider Activation

- Default: `WEATHER_PROVIDER=csv` (no change to existing behavior).
- To enable API: set `WEATHER_PROVIDER=open-meteo` in `.env`.
- When API is active, the system fetches weather data for the requested location/date range and **merges** it with agricultural data from CSV by `date` and `location_id`.
- When API is inactive or fails, the system falls back to CSV data silently.

## 3. Implementation Tasks

### Task 1: Create `data_ingestion` package structure

Create files:
- `backend/data_ingestion/__init__.py`
- `backend/data_ingestion/base.py`
- `backend/data_ingestion/csv_provider.py`
- `backend/data_ingestion/openmeteo_provider.py`
- `backend/data_ingestion/normalizer.py`
- `backend/data_ingestion/cache.py`
- `backend/data_ingestion/errors.py`
- `backend/data_ingestion/settings.py`

### Task 2: Implement base provider and WeatherRecord

- `base.py`: `WeatherRecord` dataclass/Pydantic model, `BaseProvider` abstract class with methods:
  - `fetch_historical(lat, lon, start_date, end_date) -> list[WeatherRecord]`
  - `fetch_current(lat, lon) -> WeatherRecord | None`
  - `fetch_forecast(lat, lon, days) -> list[WeatherRecord]` (stub, raises `NotImplementedError` for MVRS)

### Task 3: Implement CSV provider

- Refactor existing `_load_dataset()` logic into `CSVProvider`.
- Map CSV columns to `WeatherRecord` fields.
- Return `list[WeatherRecord]` for weather columns, preserve full DataFrame for agricultural columns.
- This is the **only active provider** for MVRS.

### Task 4: Implement Open-Meteo provider

- Endpoint: `https://archive-api.open-meteo.com/v1/archive` (historical) and `https://api.open-meteo.com/v1/forecast` (forecast, stub).
- Geocoding: Use Open-Meteo's geocoding API to resolve `state/district` → `(lat, lon)`.
- Request: `daily=temperature_2m_mean,precipitation_sum,relative_humidity_2m_mean,wind_speed_10m_max,cloud_cover_mean`
- Normalize response to `WeatherRecord`.
- Implement retry with exponential backoff (max 3 retries).
- Respect rate limits: Open-Meteo free tier allows ~10,000 calls/day.

### Task 5: Implement cache layer

- Add table `weather_api_cache` to `database/db.py`:
  ```sql
  CREATE TABLE IF NOT EXISTS weather_api_cache (
      provider TEXT NOT NULL,
      location_id TEXT NOT NULL,
      date TEXT NOT NULL,
      payload TEXT NOT NULL,
      fetched_at TEXT NOT NULL DEFAULT (datetime('now')),
      PRIMARY KEY (provider, location_id, date)
  )
  ```
- `cache.py`: `get_cached()`, `set_cached()`, `is_fresh()` based on TTL.
- Cache key: `(provider, location_id, date_str)`.

### Task 6: Implement normalizer

- `normalizer.py`: Convert provider-specific JSON to `WeatherRecord`.
- Handle missing fields (set to `None`).
- Validate ranges (rainfall >= 0, temperature [-10, 60], humidity [0, 100]).
- Record `source` and `raw` fields.

### Task 7: Update `database/data.py`

- Add `get_weather_data(filters: dict) -> pd.DataFrame` that:
  1. Checks `WEATHER_PROVIDER` setting.
  2. If `csv`: returns weather columns from existing CSV (current behavior).
  3. If `open-meteo`: fetches via provider, normalizes, caches, returns DataFrame.
  4. Merges weather DataFrame with agricultural DataFrame on `date` and `location_id`.
- Keep existing `get_filtered()` signature unchanged for backward compatibility.
- Add `get_weather_source()` -> `str` to indicate active source.

### Task 8: Update settings

- Add weather provider settings to `core/config.py`.
- Update `backend/.env.example` with new variables.

### Task 9: Update requirements

- Add `httpx` (already present) and `tenacity` (retry logic) to `backend/pyproject.toml` and `requirements.txt`.

### Task 10: Add unit tests

- `backend/tests/test_data_ingestion.py`:
  - `test_csv_provider_loads_records`
  - `test_openmeteo_provider_normalizes_response` (mocked)
  - `test_openmeteo_provider_handles_api_failure` (mocked 500)
  - `test_openmeteo_provider_retries_on_429` (mocked rate limit)
  - `test_cache_stores_and_retrieves`
  - `test_cache_respects_ttl`
  - `test_normalizer_validates_ranges`
  - `test_normalizer_handles_missing_fields`
  - `test_get_weather_data_falls_back_to_csv_on_api_failure`
  - `test_get_weather_data_merges_weather_and_agricultural`

### Task 11: Documentation

- Update `README.md` with provider setup instructions.
- Add `docs/data-providers.md` documenting:
  - Provider choice rationale
  - Field mapping
  - Units
  - Rate limits
  - Licensing
  - Setup procedure

## 4. Out of Scope (Module 1 Postponements Respected)

- Forecast API integration (stub only, not wired up)
- NASA POWER provider implementation
- Agricultural context data ingestion (crop handbooks, soil types)
- Voice/query dataset ingestion
- Real-time IoT/satellite data
- Geocoding beyond state/district → lat/lon

## 5. Validation

| Check | Method |
|---|---|
| CSV provider unchanged | Run existing `pytest tests/` — all 14 tests must pass |
| API provider mocked tests | `pytest tests/test_data_ingestion.py -v` |
| Integration | `GET /api/v1/dataset/status` returns correct rows/source |
| Error handling | Simulate API failure; verify fallback to CSV |
| Cache | Verify SQLite cache table populated and TTL respected |

## 6. Open Questions

1. **Geocoding resolution:** Open-Meteo's geocoding is city-based. For `state/district` queries, do we need a lookup table mapping Indian districts to lat/lon, or should we geocode on-the-fly? **Recommendation:** Add a static lookup table (`data_ingestion/locations.py`) for the 8 states/5 districts in the current dataset. Expand later.

2. **Merge strategy:** When API weather data is merged with CSV agricultural data, how do we handle date mismatches? **Recommendation:** Left-join on `date`; if API returns fewer days, fill missing weather rows with `None` (do not impute).

3. **Soil moisture source:** Open-Meteo does not provide soil moisture in the free tier. NASA POWER does. **Recommendation:** For the API provider, leave `soil_moisture_pct` as `None` unless NASA POWER is explicitly enabled. The CSV provider retains synthetic soil moisture for MVRS.
