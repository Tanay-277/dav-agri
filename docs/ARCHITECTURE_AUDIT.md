# DAV Application — Architecture Audit & System Inspection Report

**Date:** 2026-09-29  
**Lead Architect & Senior Full-Stack Engineer:** Antigravity  
**Application Name:** DAV (Voice-First Multilingual Agricultural Intelligence Platform)  
**Target Clients:** Mobile (Android / iOS) and Future Web Application  
**Primary Users:** Farmers (Voice-first, Multilingual: English, Hindi, Marathi)

---

## 1. Executive Summary & Repository Status

### 1.1 Pre-Existing Codebase Audit
A thorough inspection of the development environment and workspace was performed:
* **Existing DAV Frontend:** **None** (Confirmed built from scratch).
* **Existing DAV Backend:** **None** (Confirmed built from scratch).
* **Existing DAV Database:** **None** (Confirmed built from scratch).
* **Existing DAV APIs:** **None** (Confirmed built from scratch).
* **Existing UI/UX Assets:** Figma Design (17 screens, inspected via 5 high-resolution exported design sheets and design specs).

### 1.2 System Environment & Toolchain Inspection
* **Operating System:** Windows 10/11 (PowerShell environment)
* **Node.js Runtime:** `v24.18.0` (Active)
* **Package Manager:** `npm.cmd 11.16.0` (Active)
* **Python Runtime:** `Python 3.13.7` (Active)
* **Python Package Manager:** `pip 25.2` (Active)
* **Version Control:** `git version 2.55.0.windows.3` (Active)
* **Project Location:** `C:\Users\harsh\.gemini\antigravity\scratch\dav`

---

## 2. Technology Stack Selection

To satisfy the strict requirements of:
1. **Platform Independence** (shared backend for Android, iOS, and future Web),
2. **API-First Architecture** (`/api/v1/*`),
3. **Deterministic Numerical Calculations** (AI explains facts, never invents financial/yield numbers),
4. **Multilingual Voice-First Architecture** (`en`, `hi`, `mr`),
5. **Mobile-First Responsive UI** faithful to Figma across 17 screens:

### 2.1 Backend Stack
* **Framework:** **FastAPI** (Python 3.13)
  * High-performance asynchronous ASGI framework with native async/await.
  * Native **Pydantic v2** data validation and automatic OpenAPI / Swagger documentation (`/api/v1/docs`).
  * Direct Python ecosystem integration for AI (Gemini / OpenAI), NLP, and audio processing (speech recognition, synthesis, sound format conversion).
* **Database & ORM:** **SQLAlchemy 2.0 (Async/Sync)** + **SQLite** (local zero-config) with migration-ready architecture compatible with **PostgreSQL**.
* **Database Migrations:** Structured schema versioning and initial migration scripts in `database/migrations/`.
* **Testing:** `pytest` + `httpx.AsyncClient` for automated API, unit, and integration testing with mock providers.

### 2.2 Frontend Stack
* **Framework:** **React 19 + TypeScript + Vite**
  * Mobile-first responsive architecture designed to render flawlessly on phones (Android/iOS viewports), tablets, and desktop browsers.
  * Tailwind CSS for pixel-accurate reproduction of Figma colors, typography, organic textures, rounded pills, and layouts.
  * **Lucide React** for icons matching Figma.
  * **Recharts / SVG** for deterministic, accessible charts (Stacked Bar for Cotton Production, Multi-line for Crop Income, Donut/Pie for Farm Expenses).
  * Centralized Service Layer (`src/services/`) abstracting all HTTP communication via `apiClient`.
  * HTML5 Audio & `MediaRecorder` API for client-side audio recording and playback, streaming standard WAV/WebM to the platform-independent Voice API.

---

## 3. Modular Architecture Breakdown

```
DAV/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── auth.py          # /api/v1/auth/*
│   │   │       │   ├── onboarding.py    # /api/v1/onboarding/*
│   │   │       │   ├── profile.py       # /api/v1/profile/*
│   │   │       │   ├── farm.py          # /api/v1/farm/*
│   │   │       │   ├── weather.py       # /api/v1/weather/*
│   │   │       │   ├── query.py         # /api/v1/query/*
│   │   │       │   └── voice.py         # /api/v1/voice/*
│   │   │       └── router.py            # Main API v1 aggregator
│   │   ├── core/
│   │   │   ├── config.py                # Environment settings & validation
│   │   │   ├── security.py              # JWT, hashing, tokens
│   │   │   └── logging.py               # Structured logging
│   │   ├── database/
│   │   │   ├── session.py               # DB engine & sessionmaker
│   │   │   └── base.py                  # Declarative base
│   │   ├── models/                      # SQLAlchemy ORM entities
│   │   │   ├── user.py
│   │   │   ├── profile.py
│   │   │   ├── farm.py
│   │   │   ├── crop.py
│   │   │   ├── production.py
│   │   │   ├── expense.py
│   │   │   ├── query_history.py
│   │   │   └── onboarding.py
│   │   ├── schemas/                     # Pydantic v2 schemas
│   │   ├── repositories/                # Data access layer
│   │   ├── services/                    # Pure business logic
│   │   │   ├── auth_service.py
│   │   │   ├── profile_service.py
│   │   │   ├── onboarding_service.py
│   │   │   ├── farm_service.py
│   │   │   ├── analytics_service.py     # Deterministic calculations
│   │   │   └── query_service.py
│   │   ├── ai/                          # AI Provider Abstraction
│   │   │   ├── base.py                  # BaseAIProvider
│   │   │   ├── gemini_provider.py       # Google Gemini
│   │   │   ├── mock_provider.py         # Test mock
│   │   │   └── prompt_templates.py      # Multilingual prompts (en, hi, mr)
│   │   ├── voice/                       # Voice STT/TTS Abstraction
│   │   │   ├── base.py                  # BaseSTTProvider, BaseTTSProvider
│   │   │   ├── providers.py             # System / Cloud / Mock providers
│   │   │   └── audio_utils.py           # Audio validation & conversion
│   │   └── integrations/
│   │       └── weather/                 # Weather Provider Abstraction
│   │           ├── base.py
│   │           ├── openmeteo_provider.py# Free, reliable agricultural weather
│   │           └── mock_provider.py
│   ├── tests/                           # Automated pytest suite
│   ├── requirements.txt
│   └── main.py                          # FastAPI ASGI entrypoint
│
├── frontend/
│   ├── src/
│   │   ├── assets/                      # Icons, Figma textures & audio assets
│   │   ├── components/
│   │   │   ├── common/                  # IrisSphere, TopBar, BottomNav, Button
│   │   │   ├── charts/                  # StackedBar, MultiLine, DonutChart
│   │   │   └── voice/                   # MicButton, WaveformVisualizer, AudioPlayer
│   │   ├── screens/                     # All 17 Figma screens
│   │   ├── services/                    # API client and feature services
│   │   ├── state/                       # Auth, Onboarding, Language, Farm stores
│   │   ├── i18n/                        # English, Hindi, Marathi translations
│   │   ├── types/                       # Shared TypeScript interfaces
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── database/
│   └── migrations/                      # SQL schema migration scripts
├── docs/                                # Project documentation
├── .env.example
└── README.md
```

---

## 4. Key Architectural Guarantees

1. **Platform Independence:** The backend contains zero Android/iOS/React Native/browser dependencies. The exact same REST `/api/v1/` endpoints service mobile apps and future web apps alike.
2. **Deterministic Farm Analytics:** All totals, year-over-year percentage growths, and expense breakdown percentages are calculated in `AnalyticsService`. AI only receives verified numerical facts to generate natural language explanations.
3. **Multilingual Architecture:** Standard language codes (`en`, `hi`, `mr`) are enforced throughout the backend, database, AI prompts, and frontend translation dictionaries.
4. **Voice Pipeline Safety:** The voice endpoints accept audio files (multipart/form-data), validate format/size, transcribe to text via STT, process the agricultural query, and return structured text + chart data + synthesized audio stream.
5. **Security & User Isolation:** All farm, profile, visualization, and query records enforce `user_id = current_user.id` foreign key isolation.
