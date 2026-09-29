# DAV — Voice-First Multilingual Agricultural Intelligence Platform

DAV is a voice-first, multilingual platform designed specifically for farmers. Built from scratch based on a comprehensive 17-screen Figma design, DAV combines natural speech interaction, real-time agricultural weather forecasting, deterministic farm financial analytics, and AI-powered agronomic explanations.

---

## 🌟 Key Capabilities

* **17 Figma Screens Recreated with High Fidelity:** From Launch and Phone OTP Onboarding to Interactive Production & Expense Charts, Weather Gauges, Voice Capture, and Profile Management.
* **Voice-First & Multilingual:** Native support for **Marathi (`mr`)**, **Hindi (`hi`)**, and **English (`en`)** across UI, Speech-To-Text (STT), AI responses, and Text-To-Speech (TTS).
* **Deterministic Farm Analytics:** Yield calculations, year-over-year growth percentages, and expense category distributions (Labor 40%, Seeds 25%, Fertilizer 20%, Pesticides 15%) are computed mathematically by backend logic. AI explains verified facts rather than hallucinating numbers.
* **Platform-Independent REST Architecture:** Standard `/api/v1/*` contracts service the mobile application now and will service any future web portal without backend changes.
* **Strict User Isolation:** All farm, profile, and query records enforce `user_id == current_user.id` isolation.

---

## 🛠 Tech Stack

* **Backend:** FastAPI (Python 3.13), SQLAlchemy 2.0, Pydantic v2, SQLite / PostgreSQL.
* **Frontend:** React 19, TypeScript, Vite, Tailwind CSS, Lucide Icons, SVG/Recharts.
* **AI Provider Abstraction:** Google Gemini with intelligent local fallback.
* **Voice Provider Abstraction:** Cloud STT/TTS with pure PCM audio validation and streaming playback.
* **Weather Integration:** Open-Meteo & OpenWeatherMap with agricultural irrigation advisories.

---

## 🚀 Quick Start

### Backend
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# or: python main.py
```
Open API Docs: `http://localhost:8000/docs` (or `http://localhost:8000/api/v1/docs`)

### Frontend
```bash
cd frontend
npm.cmd install
npm.cmd run dev
```
Open App: `http://localhost:5173`

---

## 🧪 Testing

```bash
# Backend pytest suite (16 tests)
cd backend && python -m pytest tests/

# Frontend typecheck & build
cd frontend && npm.cmd run build
```

---

## 📚 Documentation Directory

* [Architecture Audit](docs/ARCHITECTURE_AUDIT.md)
* [Figma 17-Screen Feature Map](docs/FIGMA_FEATURE_MAP.md)
* [System Architecture](docs/ARCHITECTURE.md)
* [REST API Specification](docs/API.md)
* [Database Schema & Data Dictionary](docs/DATABASE.md)
* [Voice Pipeline Design](docs/VOICE.md)
* [Local Setup Guide](docs/SETUP.md)
