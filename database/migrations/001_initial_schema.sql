-- =============================================================================
-- Migration 001: Initial Relational Schema for DAV
-- =============================================================================

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    phone VARCHAR(20) UNIQUE,
    google_id VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS profiles (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL DEFAULT 'Raj Patil',
    location VARCHAR(100) NOT NULL DEFAULT 'Pune, MH',
    age INTEGER NOT NULL DEFAULT 42,
    avatar_url VARCHAR(255),
    land_location VARCHAR(200) DEFAULT 'Plot No. 124/2, Kothrud',
    primary_crop VARCHAR(50) NOT NULL DEFAULT 'Cotton',
    land_size VARCHAR(50) NOT NULL DEFAULT '20 acres',
    irrigation_type VARCHAR(50) NOT NULL DEFAULT 'Rain Fed',
    livestock VARCHAR(150) DEFAULT 'Cow, Goat, Buffalo',
    crops_grown TEXT NOT NULL DEFAULT '["Cotton", "Wheat", "Ragi"]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS onboarding_preferences (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    preferred_language VARCHAR(10) NOT NULL DEFAULT 'mr',
    voice_confirmed BOOLEAN NOT NULL DEFAULT 0,
    onboarding_completed BOOLEAN NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS crops (
    id VARCHAR(36) PRIMARY KEY,
    name_en VARCHAR(50) NOT NULL,
    name_hi VARCHAR(50) NOT NULL,
    name_mr VARCHAR(50) NOT NULL,
    season VARCHAR(50),
    is_default BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS production_records (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    crop_id VARCHAR(36) NOT NULL REFERENCES crops(id),
    year INTEGER NOT NULL,
    month INTEGER,
    quantity_quintals NUMERIC(10, 2) NOT NULL,
    revenue_inr NUMERIC(12, 2) NOT NULL DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS expense_records (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    crop_id VARCHAR(36) REFERENCES crops(id),
    category VARCHAR(50) NOT NULL,
    amount_inr NUMERIC(12, 2) NOT NULL,
    expense_date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS query_history (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    query_text TEXT NOT NULL,
    query_language VARCHAR(10) NOT NULL,
    intent VARCHAR(50),
    answer_text TEXT NOT NULL,
    visualization_data TEXT,
    audio_url VARCHAR(255),
    is_saved BOOLEAN DEFAULT 0,
    share_token VARCHAR(64) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS weather_cache (
    id VARCHAR(36) PRIMARY KEY,
    location_key VARCHAR(100) NOT NULL UNIQUE,
    cached_data TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL
);

-- Indices for rapid querying and user isolation
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_production_user_year ON production_records(user_id, year);
CREATE INDEX IF NOT EXISTS idx_expense_user_cat ON expense_records(user_id, category);
CREATE INDEX IF NOT EXISTS idx_query_user_created ON query_history(user_id, created_at);
