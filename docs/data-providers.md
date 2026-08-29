# Data Providers

## Overview

The data acquisition layer provides a modular, provider-agnostic interface for obtaining weather and agricultural data. The system supports pluggable providers that normalize external data into a canonical internal schema.

## Provider Selection

| Provider | Role | Status |
|---|---|---|
| **CSV** | Primary source (MVRS) | Active by default |
| **Open-Meteo** | Historical weather API | Implemented, inactive by default |
| **NASA POWER** | Alternative/fallback | Documented, not implemented |

### Why Open-Meteo

| Criterion | Open-Meteo | Notes |
|---|---|---|
| **Availability** | Free tier: 10,000 calls/day | No credit card required |
| **Cost** | Free for non-commercial use | Commercial license available |
| **API limits** | 10,000 calls/day (free) | Sufficient for research use |
| **Historical data** | 1950–present | Covers required 2+ year window |
| **Forecast** | 7-day forecast available | Deferred to post-MVRS |
| **Geographic coverage** | Global | Includes India |
| **Licensing** | CC-BY 4.0 | Attribution required |
| **Reproducibility** | Deterministic responses | Same request = same response |

## Canonical Schema

All providers normalize to `WeatherRecord`:

| Field | Type | Unit | Description |
|---|---|---|---|
| `timestamp` | datetime | UTC | Observation timestamp |
| `location_id` | str | — | Normalized location ID |
| `latitude` | float \| None | degrees | Decimal latitude |
| `longitude` | float \| None | degrees | Decimal longitude |
| `rainfall_mm` | float \| None | mm | Total rainfall |
| `temperature_c` | float \| None | °C | Mean air temperature |
| `humidity_pct` | float \| None | % | Relative humidity |
| `soil_moisture_pct` | float \| None | % | Soil moisture |
| `wind_speed_kmh` | float \| None | km/h | Wind speed |
| `cloud_cover_okta` | float \| None | oktas | Cloud cover [0-8] |
| `precipitation_probability_pct` | float \| None | % | PoP |
| `source` | str | — | Provider name |
| `raw` | dict \| None | — | Original response |

## CSV Provider (Default)

**Purpose:** Loads the local `dataset/agriculture.csv` file.

**Activation:** `WEATHER_PROVIDER=csv` (default)

**Data flow:**
1. `database.data._load_dataset()` loads and caches the CSV.
2. `CSVProvider._load()` wraps the cached DataFrame, adds `location_id`.
3. `fetch_historical()` filters by location and date range.
4. Returns `list[WeatherRecord]`.

**Limitations:**
- Static data (no live updates)
- Synthetic data for MVRS; replace with real dataset for production
- No forecast data
- No soil moisture from API (synthetic only)

## Open-Meteo Provider

**Purpose:** Fetches historical weather data from Open-Meteo Archive API.

**Activation:** Set `WEATHER_PROVIDER=open-meteo` in `backend/.env`.

**Prerequisites:**
- Internet connectivity
- No API key required

**Endpoints used:**
- Geocoding: `https://geocoding-api.open-meteo.com/v1/search`
- Archive: `https://archive-api.open-meteo.com/v1/archive`

**Fields requested:**
- `temperature_2m_mean`
- `precipitation_sum`
- `relative_humidity_2m_mean`
- `wind_speed_10m_max`
- `cloud_cover_mean`

**Data flow:**
1. `OpenMeteoProvider.geocode()` resolves `state/district` → `(lat, lon)`.
2. `fetch_historical()` checks cache → returns cached or fetches from API.
3. API response is cached in `weather_api_cache` SQLite table.
4. Response is normalized to `list[WeatherRecord]`.

**Rate limiting:**
- Free tier: 10,000 calls/day
- Automatic retry with exponential backoff (max 3 retries)
- 429 responses trigger backoff: 1s, 2s, 4s

**Caching:**
- Cache key: `(provider, location_id, date_range)`
- TTL: 24 hours (configurable via `WEATHER_CACHE_TTL_HOURS`)
- Storage: SQLite `weather_api_cache` table

**Error handling:**
- Timeout (>10s): Returns cached data or empty DataFrame; logs warning
- 429 Rate limit: Backs off exponentially; returns cached data
- 401/403: Logs error; falls back to CSV provider
- Network unreachable: Returns cached data or empty DataFrame; logs warning
- Malformed response: Logs raw response; returns empty DataFrame
- Missing values: Left as `None`; never fabricated

**Limitations:**
- No soil moisture in free tier (returns `None`)
- Forecast not implemented (deferred to post-MVRS)
- Geocoding is city-based; may require lookup table for district-level precision
- Internet required

## NASA POWER (Documented, Not Implemented)

**Purpose:** Alternative provider for agricultural-specific variables including soil moisture.

**Activation:** Not yet implemented.

**Rationale for deferral:**
- Requires API key
- More complex response format
- Soil moisture available but requires additional parsing
- Open-Meteo sufficient for MVRS hypothesis testing

## Caching Strategy

| Data Type | Cache Location | TTL | Key |
|---|---|---|---|
| CSV dataset | `lru_cache` in memory | Process lifetime | File path |
| API responses | SQLite `weather_api_cache` | 24 hours | `(provider, location_id, date)` |
| Forecast (future) | SQLite | 3 hours | `(provider, location_id, date)` |

## Configuration

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `WEATHER_PROVIDER` | `csv` | Active provider: `csv` or `open-meteo` |
| `OPEN_METEO_URL` | `https://archive-api.open-meteo.com/v1` | Archive API base URL |
| `OPEN_METEO_FORECAST_URL` | `https://api.open-meteo.com/v1` | Forecast API base URL |
| `OPEN_METEO_GEOCODING_URL` | `https://geocoding-api.open-meteo.com/v1` | Geocoding API base URL |
| `WEATHER_API_TIMEOUT_S` | `10` | Request timeout in seconds |
| `WEATHER_CACHE_TTL_HOURS` | `24` | Cache TTL for historical data |
| `WEATHER_FORECAST_CACHE_TTL_HOURS` | `3` | Cache TTL for forecast data |
| `WEATHER_API_MAX_RETRIES` | `3` | Max retries on transient failures |

### Setup Procedure

1. **Default (CSV):** No setup required. Ensure `dataset/agriculture.csv` exists.

2. **Open-Meteo:**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env:
   WEATHER_PROVIDER=open-meteo
   ```
   No API key required.

3. **Verify:**
   ```bash
   curl http://localhost:8000/api/v1/dataset/status
   # Should show weather_source: "csv" or "open-meteo"
   ```

## Validation

| Check | Method |
|---|---|
| CSV provider loads data | `pytest tests/test_data_ingestion.py -v` |
| API provider mocked | Unit tests with `httpx` mock |
| Cache populated | Inspect `weather_api_cache` table |
| Error handling | Simulate failures in tests |
| Fallback to CSV | Set invalid provider; verify CSV fallback |

## Open Questions

1. **Geocoding precision:** Open-Meteo geocoding is city-based. For district-level accuracy, a static lookup table may be needed.
2. **Soil moisture:** Not available in Open-Meteo free tier. NASA POWER provides it but requires API key.
3. **Merge strategy:** Weather API data is merged with agricultural CSV data on `date`. Date mismatches result in `None` values (no imputation).
