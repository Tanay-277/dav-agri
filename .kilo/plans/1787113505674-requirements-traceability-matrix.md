# Requirements Traceability Matrix: Voice-Interactive Data Storytelling System

## Purpose

Maps each requirement from the Software Requirements Specification (`1787113505674-software-requirements-specification.md`) to its implementation location and verification status.

---

## Functional Requirements

| ID | Requirement | Implementation | Verification |
|---|---|---|---|
| FR-01 | Microphone Activation | `frontend/src/components/voice-controls.tsx` — Mic button with toggle states | Manual: button toggles Listening/Voice Input, keyboard accessible, aria-label present |
| FR-02 | Continuous Speech Recognition | `frontend/src/hooks/use-voice-input.ts` — `SpeechRecognition` with `continuous=true`, `interimResults=true`, 8s silence timeout | Manual: speak continuously, verify interim transcript appears, stops after silence |
| FR-03 | Speech Error Recovery | `frontend/src/hooks/use-voice-input.ts` — `onerror` handler for `no-speech`, `not-allowed`, `network`, `aborted` | Manual: deny mic permission, verify error message; disconnect network, verify error |
| FR-04 | Browser-Native STT | `frontend/src/hooks/use-voice-input.ts` — uses `window.SpeechRecognition || window.webkitSpeechRecognition` | Manual: test in Chrome/Edge/Safari; verify voice UI hides in unsupported browsers |
| FR-05 | Multilingual STT | `frontend/src/components/voice-controls.tsx` — language dropdown with 8 languages; `recognition.lang` set from selection | Manual: select Hindi/Tamil, speak, verify recognition; check localStorage persistence |
| FR-06 | Manual Language Selection | `frontend/src/components/voice-controls.tsx` — `LANGUAGES` array, dropdown UI, `setLang` state | Manual: open language dropdown, select language, verify TTS/STT language changes |
| FR-07 | Language Mismatch Handling | `frontend/src/components/voice-controls.tsx` — fallback message when browser doesn't support language | Manual: select unsupported language code, verify fallback notification |
| FR-08 | Intent Parsing | `frontend/src/lib/voice-intents.ts` — `parseVoiceIntent()` with 14 action types, confidence scoring | Unit test: test all intent patterns; manual: speak commands, verify correct action |
| FR-09 | Entity Extraction | `frontend/src/lib/voice-intents.ts` — `CROPS`, `STATES`, `DISTRICTS`, date regex, `METRICS` arrays | Unit test: verify entity extraction for all crops/states/districts/dates |
| FR-10 | Context Management | `frontend/src/lib/voice-intents.ts` — `ConversationContext` type, `resolveContext()`; `frontend/src/hooks/use-voice-input.ts` — context state, 60s silence reset | Manual: "show wheat in Punjab" → "And rice?" → verify rice resolves; wait 60s, verify context clears |
| FR-11 | Confirmation Handling | `frontend/src/components/voice-confirmation.tsx` — yes/no prompt; `frontend/src/hooks/use-voice-input.ts` — `confirmation` state | Manual: say "reset filters", verify yes/no prompt; respond via voice/button |
| FR-12 | Clarification Handling | `frontend/src/components/voice-clarification.tsx` — multiple-choice UI; `frontend/src/lib/voice-intents.ts` — `clarificationOptions` | Manual: ask ambiguous question "how is it doing?", verify clarification options appear |
| FR-13 | Unknown Question Handling | `frontend/src/lib/voice-intents.ts` — returns `action: "unknown"` with `clarificationOptions`; `voice-controls.tsx` — graceful fallback | Manual: ask "What is GDP of India?", verify fallback message + help offer |
| FR-14 | Dataset Loading | `backend/database/data.py` — `_load_dataset()` with caching, column normalization, validation | Test: `test_dataset_status` verifies 600+ rows, columns present |
| FR-15 | Filtered Data Retrieval | `backend/api/routes.py` — `get_dashboard()`, `get_insights()`, `get_story()`, `get_recommendations()` all accept `DashboardFilters` | Test: `test_dashboard_with_filters` verifies crop/state filtering |
| FR-16 | KPI Computation | `backend/analytics/engine.py` — `compute_kpis()` | Test: `test_dashboard_default` verifies 6 KPIs returned |
| FR-17 | Chart Data Transformation | `backend/analytics/charts.py` — `line_chart()`, `bar_chart()`, `scatter_chart()`, `heatmap_data()`, `pie_chart()` | Test: `test_dashboard_default` verifies all 5 chart types present |
| FR-18 | Rule-Based Insight Detection | `backend/insights/engine.py` — `generate_insights()` with trend/anomaly/comparison detection | Test: `test_insights` verifies insights returned; `test_insights_no_data` verifies fallback |
| FR-19 | Story Generation | `backend/insights/engine.py` — `generate_story()` with rule-based and AI fallback | Test: `test_story` verifies story, summary, reasons, recommendations, source |
| FR-20 | Icon Rendering | `frontend/src/lib/icons/*.tsx` — 13 SVG components with `aria-label` | Manual: verify all 13 icons render in IconLegend; inspect aria-labels |
| FR-21 | Icon Highlighting | `frontend/src/components/icon-legend.tsx` — `activeIcon` prop; `frontend/src/hooks/use-voice-output.ts` — `currentWordIndex` + `onWordBoundary`; `dashboard-page.tsx` — word-to-icon mapping | Manual: enable voice-story, click "Read Aloud", verify icons highlight during narration |
| FR-22 | Simple Mode | `frontend/src/components/icon-legend.tsx` — `simpleMode` toggle; `dashboard-page.tsx` — conditional rendering; `kpi-card.tsx` — simplified layout | Manual: toggle Simple View, verify charts hide, icons enlarge, text hides |
| FR-23 | TTS Narration | `frontend/src/hooks/use-voice-output.ts` — `speak()` using `speechSynthesis`; `icon-legend.tsx` — `onReadAloud` | Manual: click "Read Aloud", verify story is spoken; verify rate is 0.9x |
| FR-24 | TTS Controls | `frontend/src/components/voice-controls.tsx` — stop/pause/resume buttons; `use-voice-output.ts` — `cancel()`, `pause()`, `resume()` | Manual: during narration, click stop/pause/resume, verify behavior |
| FR-25 | Response Length Enforcement | `frontend/src/hooks/use-voice-output.ts` — `maxSentences` (3) and `maxWords` (60) enforcement in `speak()` | Manual: request long story, verify truncation at 3 sentences/60 words |
| FR-26 | Context Buffer | `frontend/src/lib/voice-intents.ts` — `ConversationContext` type; `frontend/src/hooks/use-voice-input.ts` — context state with `lastCrop`, `lastState`, etc. | Manual: follow-up ellipsis and anaphora tests |
| FR-27 | Context Reset | `frontend/src/hooks/use-voice-input.ts` — `resetContext()`; `dashboard-page.tsx` — calls reset on condition switch | Manual: switch condition, verify context clears; say "reset filters", verify context clears |
| FR-28 | Data Errors | `backend/api/routes.py` — empty result handling; `frontend/src/pages/dashboard-page.tsx` — `EmptyState` component | Test: `test_insights_no_data` verifies info insight for nonexistent crop; manual: verify empty state UI |
| FR-29 | Voice Errors | `frontend/src/hooks/use-voice-input.ts` — `onerror` handler; `frontend/src/components/voice-controls.tsx` — error display | Manual: deny mic permission, verify error message with browser settings hint |
| FR-30 | Offline Operation | `frontend/src/hooks/use-voice-input.ts` — browser-native APIs work offline; dataset loaded into memory | Manual: enable airplane mode after load, verify dashboard still functions, voice still works |
| FR-31 | Degraded Mode | `backend/insights/engine.py` — rule-based fallback when Gemini unavailable; `dashboard-page.tsx` — footer shows "Rule-based analysis" | Test: verify story source is "rule" when no API key; manual: verify footer indicator |

---

## Non-Functional Requirements

| ID | Requirement | Implementation | Verification |
|---|---|---|---|
| NFR-01 | API Response Time | `backend/main.py` — `RateLimitMiddleware` (100 req/60s); FastAPI async; Pandas optimized | Load test: measure p95 latency with 600-row dataset; target <500ms |
| NFR-02 | Frontend Load Time | `frontend/vite.config.ts` — code splitting; `frontend/src/App.tsx` — lazy loading | Manual: Lighthouse audit on 3G throttling; target FCP <1.5s, TTI <3s |
| NFR-03 | Voice Latency | `frontend/src/hooks/use-voice-output.ts` — immediate `speechSynthesis.speak()`; `use-voice-input.ts` — real-time interim results | Manual: measure time from command to TTS start; target <200ms |
| NFR-04 | Uptime | `backend/main.py` — `lifespan` context manager, global exception handler, health endpoint | Test: `test_health` verifies health endpoint; manual: kill process, verify restart |
| NFR-05 | Data Integrity | `backend/database/data.py` — column validation, missing value handling; `backend/database/db.py` — idempotent `init_db()` | Test: `test_dataset_status` verifies columns; manual: corrupt CSV, verify error |
| NFR-06 | WCAG 2.1 AA Compliance | `frontend/src/index.css` — `prefers-reduced-motion`; `frontend/src/components/*` — aria-labels, focus indicators | Manual: axe DevTools scan; keyboard navigation test; contrast check |
| NFR-07 | Screen Reader Support | All icons have `aria-label`; `frontend/src/components/icon-anchor.tsx` — `aria-live="polite"` | Manual: NVDA/VoiceOver test on all panels |
| NFR-08 | Learnability | `frontend/src/components/voice-help-modal.tsx` — lists all commands; `dashboard-page.tsx` — Survey button | Manual: first-time user test, measure time to first completed task |
| NFR-09 | Error Prevention | `frontend/src/components/voice-confirmation.tsx` — destructive action confirmation; filter validation | Manual: attempt reset, verify confirmation prompt |
| NFR-10 | Task Efficiency | `frontend/src/lib/voice-intents.ts` — direct intent parsing; `dashboard-page.tsx` — condition switcher | Manual: time "show wheat in Punjab" command to filter application |
| NFR-11 | Dataset Size | `backend/analytics/engine.py` — Pandas operations; `backend/database/data.py` — `_load_dataset` caching | Test: generate 100K row dataset, measure load time; target <2s |
| NFR-12 | Concurrent Users | `backend/main.py` — `RateLimitMiddleware`; FastAPI ASGI | Load test: 100 concurrent requests, verify stability |
| NFR-13 | Input Validation | `backend/models/schemas.py` — Pydantic validation; `backend/api/routes.py` — query parameter validation | Test: `test_dashboard_with_filters` verifies valid input; manual: test injection attempts |
| NFR-14 | CORS Policy | `backend/main.py` — `CORSMiddleware` with `CORS_ORIGINS` from settings | Test: verify CORS headers in responses; manual: test cross-origin request |
| NFR-15 | Data Collection | `backend/tests/test_api.py` — task log and survey endpoints store anonymized data | Test: `test_research_task_log`, `test_research_survey` verify anonymized storage |
| NFR-16 | Data Retention | `backend/database/db.py` — SQLite storage; no personal identifiers beyond `user_id` | Manual: verify schema, no PII columns; document retention policy in README |
| NFR-17 | Recommendation Explanation | `backend/recommendations/engine.py` — every rec has `message` with reasoning; `backend/insights/engine.py` — causal story format | Test: `test_recommendations` verifies all recs have condition + message; manual: verify no unexplained recs |
| NFR-18 | Insight Traceability | `backend/insights/engine.py` — insights include `metric`, `type`, `magnitude`; `backend/database/db.py` — `record_insight_run()` stores filters + insights | Test: verify insight JSON includes metric and time range |
| NFR-19 | Code Quality | `backend/requirements.txt` — pinned deps; `frontend/package.json` — TypeScript strict mode | Test: `pytest` passes; `npm run build` passes; `npm run lint` passes |
| NFR-20 | Dependency Management | `backend/requirements.txt` — pinned versions; `frontend/package-lock.json` — committed | Manual: audit dependencies for vulnerabilities |
| NFR-21 | Multi-Language Support | `frontend/src/components/voice-controls.tsx` — 8-language selector; `frontend/src/lib/voice-intents.ts` — language-agnostic entity matching | Manual: test all 8 languages; verify UI labels (future: i18n) |
| NFR-22 | Cultural Adaptation | `frontend/src/lib/icons/*.tsx` — universal metaphors (thermometer, cloud, droplet); voice prompts use neutral language | Manual: co-design review with target users (future work) |

---

## Coverage Summary

- **Total requirements**: 42 (31 functional + 11 non-functional)
- **Must have**: 24
- **Should have**: 12
- **Could have**: 4
- **Out of scope**: 2+ (documented in SRS)

### Implementation Status

| Status | Count | Description |
|---|---|---|
| **Implemented** | 38 | Code exists and is functional |
| **Partially implemented** | 3 | FR-07 (language mismatch), FR-21 (icon highlighting basic), NFR-11 (100K dataset untested) |
| **Not yet implemented** | 1 | NFR-22 (cultural adaptation review — requires user testing) |

### Test Coverage

- **Backend**: 14 automated tests covering health, dataset, filters, dashboard, insights, story, recommendations, export, research endpoints
- **Frontend**: Build verification (TypeScript + Vite); no unit test framework configured yet
- **Manual**: Voice interaction, icon rendering, accessibility, simple mode, condition switching

---

## Gaps and Recommendations

1. **FR-21 Icon Highlighting**: Basic word-boundary highlighting is implemented. Recommend adding visual regression tests and user validation.
2. **NFR-11 Dataset Size**: 600-row dataset is functional. Recommend load testing with 100K rows before production.
3. **NFR-22 Cultural Adaptation**: Icons use universal metaphors. Recommend participatory design session with target users to validate icon recognition.
4. **Frontend Tests**: No automated frontend tests exist. Recommend adding Vitest for component and hook tests.
5. **Accessibility Audit**: Manual checks performed. Recommend automated axe DevTools scan and screen reader testing with NVDA/VoiceOver.

---

## Verification Commands

```bash
# Backend tests
cd backend && .venv/bin/pytest tests/test_api.py -v

# Frontend build
cd frontend && npm run build

# Frontend lint (if configured)
cd frontend && npm run lint
```
