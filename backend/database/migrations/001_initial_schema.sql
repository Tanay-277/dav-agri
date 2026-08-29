-- Description: Create initial tables for Module 1 MVP
-- Created: 2026-08-21

-- UP
CREATE TABLE IF NOT EXISTS locations (
    location_id TEXT PRIMARY KEY,
    state TEXT NOT NULL,
    district TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    timezone TEXT DEFAULT 'Asia/Kolkata',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS data_sources (
    source_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    provider_type TEXT NOT NULL,
    configuration TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS weather_observations (
    observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    record_date TEXT NOT NULL,
    data_classification TEXT NOT NULL DEFAULT 'historical',
    rainfall_mm REAL,
    temperature_c REAL,
    humidity_pct REAL,
    soil_moisture_pct REAL,
    wind_speed_kmh REAL,
    cloud_cover_okta REAL,
    precipitation_probability_pct REAL,
    is_duplicate INTEGER NOT NULL DEFAULT 0,
    is_outlier INTEGER NOT NULL DEFAULT 0,
    is_invalid INTEGER NOT NULL DEFAULT 0,
    validation_flags TEXT,
    raw_payload TEXT,
    source_row_id INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES data_sources(source_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS agricultural_records (
    ag_record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    record_date TEXT NOT NULL,
    crop TEXT NOT NULL,
    yield_kg_per_ha REAL,
    production_tonnes REAL,
    area_ha REAL,
    fertilizer_kg REAL,
    irrigation_pct REAL,
    source_row_id INTEGER,
    is_duplicate INTEGER NOT NULL DEFAULT 0,
    is_outlier INTEGER NOT NULL DEFAULT 0,
    is_invalid INTEGER NOT NULL DEFAULT 0,
    validation_flags TEXT,
    raw_payload TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES data_sources(source_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS query_logs (
    query_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    user_id TEXT,
    filters_json TEXT NOT NULL,
    result_summary TEXT,
    response_time_ms INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS insights (
    insight_id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_id INTEGER,
    location_id TEXT,
    crop TEXT,
    insight_type TEXT NOT NULL,
    metric TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'info',
    magnitude REAL,
    message TEXT NOT NULL,
    context_json TEXT,
    source TEXT NOT NULL DEFAULT 'rule',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (query_id) REFERENCES query_logs(query_id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS dataset_meta (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_weather_unique
    ON weather_observations (location_id, source_id, timestamp, data_classification);
CREATE INDEX IF NOT EXISTS idx_weather_location_date
    ON weather_observations (location_id, record_date);
CREATE INDEX IF NOT EXISTS idx_weather_source
    ON weather_observations (source_id);
CREATE INDEX IF NOT EXISTS idx_weather_classification
    ON weather_observations (data_classification);
CREATE INDEX IF NOT EXISTS idx_weather_timestamp
    ON weather_observations (timestamp);

CREATE UNIQUE INDEX IF NOT EXISTS idx_ag_unique
    ON agricultural_records (location_id, crop, record_date, source_id);
CREATE INDEX IF NOT EXISTS idx_ag_location_date
    ON agricultural_records (location_id, record_date);
CREATE INDEX IF NOT EXISTS idx_ag_crop
    ON agricultural_records (crop);

CREATE INDEX IF NOT EXISTS idx_locations_state
    ON locations(state);
CREATE INDEX IF NOT EXISTS idx_locations_district
    ON locations(district);

CREATE INDEX IF NOT EXISTS idx_query_session
    ON query_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_query_user
    ON query_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_query_created
    ON query_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_insights_query
    ON insights(query_id);
CREATE INDEX IF NOT EXISTS idx_insights_location
    ON insights(location_id);
CREATE INDEX IF NOT EXISTS idx_insights_type
    ON insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_insights_created
    ON insights(created_at);

INSERT OR IGNORE INTO data_sources (source_id, name, provider_type)
VALUES ('csv', 'Local CSV Dataset', 'csv');

-- DOWN
DROP TABLE IF EXISTS insights;
DROP TABLE IF EXISTS query_logs;
DROP TABLE IF EXISTS agricultural_records;
DROP TABLE IF EXISTS weather_observations;
DROP TABLE IF EXISTS data_sources;
DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS schema_migrations;
