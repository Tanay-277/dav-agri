# Implementation Plan: AgriStory Dashboard — Finish + Voice Layer (Option A)

**Decision:** Use **Web Speech API (browser-native)** for voice interaction.
Rationale: No backend dependency, works offline in supported browsers (Chrome/Edge/Safari), simplest path to finishing the project. Acknowledged limitations: language support depends on browser, requires user permission, no custom model training. Backend-driven STT/TTS is deferred as future novelty.

---

## Current State (verified from codebase)

- Backend: FastAPI with complete analytics, insights, story, recommendations, and export pipelines.
- Frontend: React + Vite + TypeScript + Tailwind + Plotly dashboard with filters, 5 chart types, KPI cards, insights panel, story panel, recommendations panel, PDF/JSON export.
- Dataset: Minimal 10-row CSV (placeholder). Data loader has column aliasing and filter support.
- Status: Functional prototype. Not yet "finished" — needs robustness, error handling, responsive polish, and voice layer.

---

## Phase 1: Finish the Project (Make It Production-Ready)

### 1.1 Dataset & Backend Hardening
- [ ] Expand `dataset/agriculture.csv` to a realistic dataset (at least 500 rows, multiple crops/states/districts/seasons).
- [ ] Add dataset validation on load (missing values, date parsing, column normalization).
- [ ] Add pagination or sampling for large datasets in chart responses.
- [ ] Add rate limiting and request validation on FastAPI routes.
- [ ] Ensure all endpoints return consistent error shapes with HTTP status codes.
- [ ] Add integration tests for backend (pytest + httpx).

### 1.2 Frontend Robustness
- [ ] Add global error boundary and user-friendly error states.
- [ ] Add empty states for all panels (no data, no insights, etc.).
- [ ] Implement responsive design audit (mobile, tablet, desktop breakpoints).
- [ ] Add loading skeletons for all async sections.
- [ ] Replace `console.log` with proper logging or remove.
- [ ] Add form validation on filter inputs (date ranges, dropdown clears).
- [ ] Accessibility pass: ARIA labels, keyboard navigation, focus management.

### 1.3 Deployment Readiness
- [ ] Create `backend/Dockerfile` and `frontend/Dockerfile`.
- [ ] Add `docker-compose.yml` for one-command local deployment.
- [ ] Add environment variable validation on startup (fail fast if missing).
- [ ] Configure Vercel (`vercel.json`) and Render (`render.yaml`) deployment configs.
- [ ] Add health check endpoint with dependency checks (DB, dataset file).

### 1.4 Documentation
- [ ] Update `README.md` with setup, deployment, and API docs.
- [ ] Add `CONTRIBUTING.md` with development workflow.
- [ ] Document dataset schema and expected CSV format.

---

## Phase 2: Voice Layer (Web Speech API)

**Architecture:** Frontend-only voice module. No backend changes required.

### 2.1 Voice Input (Speech-to-Text)
- [ ] Add `useVoiceInput` hook wrapping `webkitSpeechRecognition` / `SpeechRecognition`.
- [ ] Support continuous recognition with interim results.
- [ ] Map recognized intents to dashboard filter actions (e.g., "show wheat in Karnataka" → set crop + state filters).
- [ ] Add visual feedback: pulsing microphone icon, transcript display, error states.
- [ ] Fallback: if STT unavailable or unsupported language, show text input fallback.

### 2.2 Voice Output (Text-to-Speech)
- [ ] Add `useVoiceOutput` hook wrapping `speechSynthesis`.
- [ ] Auto-read story panel content when filters change (user-toggleable).
- [ ] Auto-read recommendations panel (user-toggleable).
- [ ] Highlight current sentence/paragraph being read.
- [ ] Play/pause/stop controls.
- [ ] Respect `prefers-reduced-motion` and `prefers-reduced-sound` media queries.

### 2.3 Multilingual Support
- [ ] Add language selector (browser-supported languages: en, hi, ta, te, kn, mr, bn, etc.).
- [ ] Set `SpeechRecognition.lang` and `speechSynthesis.lang` from selector.
- [ ] Fallback message if selected language is not supported by browser.
- [ ] Store preference in `localStorage`.

### 2.4 Icon-Based Visual Anchors
- [ ] Add icon column to KPI cards (rain, temperature, yield, etc. using lucide-react or custom SVGs).
- [ ] Add icon legend/cheat sheet for chart types.
- [ ] Highlight icon when corresponding voice segment is being read (synchronize TTS with icon state).
- [ ] Add "simple mode" toggle: reduces chart complexity, enlarges icons, hides advanced filters.

### 2.5 Voice-Driven Filters
- [ ] Intent parsing (lightweight, regex + keyword matching, no NLP dependency):
  - "show [crop] in [state]"
  - "filter by [district]"
  - "from [date] to [date]"
  - "reset filters"
- [ ] Confirmation step: "Did you mean to show Wheat in Karnataka?" with yes/no buttons.
- [ ] Undo last voice action.

---

## Phase 3: Novelty & Research Extensions (After Project Is Finished)

Only start these after Phase 1 + Phase 2 are validated and stable.

### 3.1 A/B Testing Framework
- [ ] Add experimental condition toggles (voice-only, voice+icons, voice+icons+story, conventional).
- [ ] Log user interactions, task completion, time-on-task to backend.
- [ ] Add post-task survey component (comprehension quiz, trust scale, SUS).

### 3.2 Data Literacy Assessment
- [ ] Integrate visualization literacy quiz (adapted from Galesic & Garcia-Ramero, or Alper et al.).
- [ ] Pre- and post-intervention assessment to measure literacy change.

### 3.3 Advanced Novelty (Deferred)
- [ ] Backend-driven STT/TTS (Whisper + pyttsx3/mimic3) for offline support beyond browser capabilities.
- [ ] Culturally co-designed icon set (participatory design with target community).
- [ ] Longitudinal study tracking data literacy over repeated use.

---

## File Changes Required

| File | Change |
|---|---|
| `frontend/src/hooks/use-dashboard.ts` | Add voice state management, filter synchronization |
| `frontend/src/components/voice-controls.tsx` | New: mic button, language selector, transcript |
| `frontend/src/components/icon-legend.tsx` | New: simple mode toggle + icon cheat sheet |
| `frontend/src/components/ui/button.tsx` | May need voice-specific button variant |
| `frontend/src/lib/voice-intents.ts` | New: intent parsing logic |
| `dataset/agriculture.csv` | Expand dataset |
| `backend/requirements.txt` | Add test dependencies |
| `backend/tests/` | New: integration tests |

---

## Validation & Testing

1. **Unit tests:** Backend analytics engine, insight engine, recommendations engine.
2. **Integration tests:** API endpoints with expanded dataset.
3. **Frontend tests:** Component rendering, filter state, chart data binding.
4. **Manual validation:**
   - Open dashboard in Chrome, verify all charts render with expanded dataset.
   - Toggle filters, verify KPIs, charts, insights, story, and recommendations update.
   - Test voice input: speak filter commands, verify transcript and filter application.
   - Test voice output: toggle story reading, verify TTS fires and highlights sync.
   - Test on mobile viewport.
   - Test with `prefers-reduced-motion` / `prefers-reduced-sound`.

---

## Out of Scope (Explicitly Deferred)

- Authentication / authorization.
- Real-time data ingestion (APIs, IoT).
- LLM-based storytelling (Gemini) — keep rule-based for now to ensure offline-like behavior.
- User accounts and history.
- Advanced analytics (ML predictions).
- Mobile native apps (PWA is sufficient).

---

## Execution Order

1. Expand dataset and harden backend (Phase 1.1).
2. Frontend robustness pass (Phase 1.2).
3. Deployment configs (Phase 1.3).
4. Documentation (Phase 1.4).
5. Voice input hook + visual controls (Phase 2.1).
6. Voice output hook + TTS controls (Phase 2.2).
7. Multilingual selector (Phase 2.3).
8. Icon anchors + simple mode (Phase 2.4).
9. Voice-driven filters (Phase 2.5).
10. Manual validation and bug fixes.
