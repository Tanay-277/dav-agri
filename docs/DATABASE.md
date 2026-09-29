# DAV Database Schema & Data Dictionary

This document details the relational database schema, data dictionary, entity relationships, and user isolation guarantees for the DAV platform.

---

## 1. Entity-Relationship Overview

```
 [Users] 1 ──────── 1 [Profiles]
    │    1 ──────── 1 [OnboardingPreferences]
    │    1 ──────── * [ProductionRecords] ── * [Crops]
    │    1 ──────── * [ExpenseRecords]    ── * [Crops]
    └────1 ──────── * [QueryHistory]
```

All primary operational data (`profiles`, `onboarding_preferences`, `production_records`, `expense_records`, `query_history`) are strictly foreign-keyed to `users.id` with `ON DELETE CASCADE`.

---

## 2. Table Specifications

### 2.1 `users`
Represents the authenticated identity of the farmer.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | PRIMARY KEY | UUID v4 user identifier |
| `phone` | VARCHAR(20) | UNIQUE, INDEXED | Farmer mobile phone (E.164 or national format) |
| `google_id` | VARCHAR(100)| UNIQUE, NULLABLE | Google OAuth account identifier |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW | Account creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW | Last record update timestamp |

### 2.2 `profiles`
Stores farmer personal details and agricultural land characteristics matching Figma Screen 16 & 17.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | PRIMARY KEY | UUID v4 profile identifier |
| `user_id` | VARCHAR(36) | NOT NULL, UNIQUE, FK -> users(id) | Owning user ID |
| `name` | VARCHAR(100)| NOT NULL | Farmer name (e.g. "Raj Patil") |
| `location` | VARCHAR(100)| NOT NULL | District/State (e.g. "Pune, MH") |
| `age` | INTEGER | NOT NULL | Age in years (e.g. 42) |
| `avatar_url`| VARCHAR(255)| NULLABLE | Avatar illustration URL |
| `land_location`| VARCHAR(200)| NULLABLE | Land plot / survey no (e.g. "Plot No. 124/2, Kothrud") |
| `primary_crop`| VARCHAR(50)| NOT NULL | Primary cultivated crop (e.g. "Cotton") |
| `land_size` | VARCHAR(50) | NOT NULL | Land acreage (e.g. "20 acres") |
| `irrigation_type`| VARCHAR(50)| NOT NULL | Irrigation ("Rain Fed", "Borewell", "Canal", "Drip") |
| `livestock` | VARCHAR(150)| NULLABLE | Livestock ("Cow, Goat, Buffalo") |
| `crops_grown`| JSON | NOT NULL | Array of active crops (e.g. `["Cotton", "Wheat", "Ragi"]`) |
| `created_at`| TIMESTAMP | NOT NULL | Record creation timestamp |
| `updated_at`| TIMESTAMP | NOT NULL | Last update timestamp |

### 2.3 `onboarding_preferences`
Tracks multi-step onboarding lifecycle matching Figma Screens 5-8.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | PRIMARY KEY | UUID v4 identifier |
| `user_id` | VARCHAR(36) | NOT NULL, UNIQUE, FK -> users(id) | Owning user ID |
| `preferred_language`| VARCHAR(10)| NOT NULL, DEFAULT 'mr' | Standard language code (`en`, `hi`, `mr`) |
| `voice_confirmed` | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether voice audio test passed |
| `onboarding_completed`| BOOLEAN | NOT NULL, DEFAULT FALSE | Whether full onboarding finished |
| `updated_at`| TIMESTAMP | NOT NULL | Last update timestamp |

### 2.4 `crops`
Catalog of supported agricultural crops with multilingual names.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | PRIMARY KEY | UUID v4 identifier |
| `name_en` | VARCHAR(50) | NOT NULL | English name (e.g. "Cotton") |
| `name_hi` | VARCHAR(50) | NOT NULL | Hindi name (e.g. "कपास") |
| `name_mr` | VARCHAR(50) | NOT NULL | Marathi name (e.g. "कापूस") |
| `season` | VARCHAR(50) | NULLABLE | Kharif / Rabi / Zaid |
| `is_default`| BOOLEAN | DEFAULT FALSE | Whether pre-populated in filter pills |

### 2.5 `production_records`
Deterministic crop yield records supporting the Cotton Production Stacked Bar Chart and Income Multi-line chart.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | PRIMARY KEY | UUID v4 record ID |
| `user_id` | VARCHAR(36) | NOT NULL, INDEXED, FK -> users(id) | Owning user ID |
| `crop_id` | VARCHAR(36) | NOT NULL, FK -> crops(id) | Cultivated crop |
| `year` | INTEGER | NOT NULL, INDEXED | Harvest year (e.g. 2021, 2022, 2023, 2024, 2025) |
| `month` | INTEGER | NULLABLE | Harvest month (1-12) |
| `quantity_quintals`| NUMERIC(10,2)| NOT NULL | Quantity in quintals (e.g. 12.0, 15.0, 18.0, 21.0) |
| `revenue_inr` | NUMERIC(12,2)| NOT NULL, DEFAULT 0 | Realized revenue in INR |
| `notes` | TEXT | NULLABLE | Farmer observation |
| `created_at` | TIMESTAMP | NOT NULL | Timestamp |

### 2.6 `expense_records`
Deterministic farm expense records supporting the Donut/Pie Chart breakdown (Labor, Seeds, Fertilizer, Pesticides).
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | PRIMARY KEY | UUID v4 record ID |
| `user_id` | VARCHAR(36) | NOT NULL, INDEXED, FK -> users(id) | Owning user ID |
| `crop_id` | VARCHAR(36) | NULLABLE, FK -> crops(id) | Optional crop allocation |
| `category` | VARCHAR(50) | NOT NULL, INDEXED | `labor`, `seeds`, `fertilizer`, `pesticides`, `other` |
| `amount_inr`| NUMERIC(12,2)| NOT NULL | Expense amount in INR |
| `expense_date`| DATE | NOT NULL | Date incurred |
| `notes` | TEXT | NULLABLE | Description |
| `created_at` | TIMESTAMP | NOT NULL | Timestamp |

### 2.7 `query_history`
Stores farmer voice and text questions, verified analytical calculations, generated AI explanations, and visualizations.
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | PRIMARY KEY | UUID v4 query ID |
| `user_id` | VARCHAR(36) | NOT NULL, INDEXED, FK -> users(id) | Owning user ID |
| `query_text`| TEXT | NOT NULL | Transcribed speech or typed question |
| `query_language`| VARCHAR(10)| NOT NULL | `en`, `hi`, `mr` |
| `intent` | VARCHAR(50) | NULLABLE | Extracted intent (e.g. `production_trend`, `expense_breakdown`) |
| `answer_text`| TEXT | NOT NULL | Localized explanation |
| `visualization_data`| JSON | NULLABLE | Structured JSON for chart rendering |
| `audio_url` | VARCHAR(255)| NULLABLE | Path to synthesized TTS audio |
| `is_saved` | BOOLEAN | DEFAULT FALSE | Saved visualization flag |
| `share_token`| VARCHAR(64) | UNIQUE, NULLABLE | Deep-link sharing token |
| `created_at` | TIMESTAMP | NOT NULL | Creation timestamp |

---

## 3. User Data Isolation Guarantees

Every database query in every service layer is automatically scoped with:
```python
query = select(Model).where(Model.user_id == current_user.id)
```
No user can access, read, update, or delete any record belonging to another user.
