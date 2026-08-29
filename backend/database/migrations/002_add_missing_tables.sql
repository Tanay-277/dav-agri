-- Description: Add missing metadata and research logging tables
-- Created: 2026-08-28

-- UP
CREATE TABLE IF NOT EXISTS dataset_meta (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS insight_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    filters_json TEXT NOT NULL,
    insights_json TEXT NOT NULL,
    story TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS task_logs (
    task_id TEXT,
    condition TEXT,
    user_id TEXT,
    completed INTEGER NOT NULL DEFAULT 0,
    duration_ms INTEGER,
    voice_used INTEGER NOT NULL DEFAULT 0,
    error TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS survey_responses (
    response_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT,
    condition TEXT,
    user_id TEXT,
    comprehension_score INTEGER,
    trust_score INTEGER,
    sus_score INTEGER,
    feedback TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_task_logs_condition
    ON task_logs(condition);
CREATE INDEX IF NOT EXISTS idx_task_logs_user
    ON task_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_task_logs_created
    ON task_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_survey_condition
    ON survey_responses(condition);
CREATE INDEX IF NOT EXISTS idx_survey_user
    ON survey_responses(user_id);
CREATE INDEX IF NOT EXISTS idx_survey_created
    ON survey_responses(created_at);

-- DOWN
DROP TABLE IF EXISTS survey_responses;
DROP TABLE IF EXISTS task_logs;
DROP TABLE IF EXISTS insight_history;
DROP TABLE IF EXISTS dataset_meta;
