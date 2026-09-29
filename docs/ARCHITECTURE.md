# DAV Architecture & Engineering Design

This document details the system architecture, component boundaries, data flows, and design decisions for the **DAV** (Voice-First Multilingual Agricultural Intelligence Platform).

---

## 1. High-Level Architectural Vision

```
                     DAV SYSTEM TOPOLOGY

          ┌───────────────────────────────────────────────┐
          │               CLIENT APPLICATIONS             │
          │                                               │
          │   ┌─────────────────────┐  ┌──────────────┐   │
          │   │   Mobile Browser    │  │  Future Web  │   │
          │   │  Android / iOS PWA  │  │   Desktop    │   │
          │   └──────────┬──────────┘  └──────┬───────┘   │
          └──────────────┼────────────────────┼───────────┘
                         │                    │
                         │   SAME REST APIs   │
                         │    /api/v1/*       │
                         ▼                    ▼
          ┌───────────────────────────────────────────────┐
          │             DAV BACKEND PLATFORM              │
          │             FastAPI (Python 3.13)             │
          │                                               │
          │  ┌─────────────────────────────────────────┐  │
          │  │              API Layer                  │  │
          │  │  Routes · Schemas · Validation · Auth   │  │
          │  └────────────────────┬────────────────────┘  │
          │                       │                       │
          │  ┌────────────────────▼────────────────────┐  │
          │  │            Services Layer               │  │
          │  │  Business Logic · Deterministic Math    │  │
          │  └───────┬────────────┬────────────┬───────┘  │
          │          │            │            │          │
          │  ┌───────▼──────┐ ┌───▼────┐ ┌─────▼───────┐  │
          │  │ Repositories │ │   AI   │ │    Voice    │  │
          │  │  SQLAlchemy  │ │ Engine │ │  (STT/TTS)  │  │
          │  └───────┬──────┘ └───┬────┘ └─────┬───────┘  │
          └──────────┼────────────┼────────────┼──────────┘
                     │            │            │
                     ▼            ▼            ▼
                 Database      Gemini /      Audio
               SQLite / PG      Mock       Validation
```

---

## 2. Platform Independence Guarantees

As mandated by system requirements:
1. **Zero Client-Specific Code in Backend:** The backend has no dependencies on Android APIs, iOS APIs, React Native, browser DOM, screen dimensions, or device storage.
2. **Identical REST Contracts:** Every client (mobile phone, tablet, desktop browser) communicates via the exact same JSON envelopes and multipart audio streams at `/api/v1/*`.
3. **Decoupled Business Logic:** All agricultural formulas, yield metrics, year-over-year growth, and expense category distributions execute strictly in `AnalyticsService`.

---

## 3. Layered Backend Design

* **API Endpoints (`app/api/v1/endpoints/`):**
  * `auth.py`: Passwordless Phone + OTP generation/verification (`/api/v1/auth/*`)
  * `onboarding.py`: Regional language preference and voice setup confirmation (`/api/v1/onboarding/*`)
  * `profile.py`: Farmer details, farm metadata, land plot, crops grown (`/api/v1/profile/*`)
  * `farm.py`: Crops dictionary, production records, expense records, analytics charts (`/api/v1/farm/*`)
  * `weather.py`: Agricultural weather metrics and irrigation advice (`/api/v1/weather/*`)
  * `query.py`: Central voice/text query ingestion, intent routing, structured charts, deep-link sharing (`/api/v1/query/*`)
  * `voice.py`: Audio validation, STT transcription, and TTS speech synthesis (`/api/v1/voice/*`)
* **Schemas (`app/schemas/`):** Pydantic v2 data models with strict input constraints and uniform `APIResponse[T]` serialization.
* **Services (`app/services/`):** Pure, testable business logic modules.
* **Repositories (`app/repositories/`):** Encapsulated data-access objects guaranteeing user ownership isolation (`user_id == current_user.id`).
* **Database Models (`app/models/`):** Normalized SQLAlchemy ORM models.

---

## 4. Deterministic Fact-Grounded AI Architecture

```
 Farmer Question
        │
        ▼
   AI Intent Classification
        │
        ▼
   AnalyticsService (Deterministic Math in Python)
   - Calculates exact growth (e.g. +9 quintals, +75%)
   - Calculates exact expense category percentages (40% labor, 25% seeds, 20% fertilizer, 15% pesticides)
        │
        ▼
   Verified Facts Payload
        │
        ▼
   AIService (Gemini / Mock)
   - Generates natural language explanation in farmer's language (mr, hi, en)
   - NEVER guesses or computes numbers
        │
        ▼
   Structured JSON Data + Chart + Localized Explanation -> Farmer
```

---

## 5. Security & Isolation

* **User Data Isolation:** Every query, farm record, expense, profile, and voice interaction is keyed strictly by authenticated `user_id`. No user can access another farmer's private data.
* **Authentication:** Stateless JWT bearer tokens with standard expiration and secure HMAC signing.
* **CORS:** Configured via environment variable `CORS_ORIGINS`.
* **Zero Hardcoded Secrets:** All secrets, keys, and database paths are loaded via `.env`.
