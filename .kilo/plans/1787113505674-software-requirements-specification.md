# Software Requirements Specification: Voice-Interactive Data Storytelling System

## Document Control

| Version | Date | Author | Status |
|---|---|---|---|
| 0.1 | 2026-08-19 | Research Team | Draft |

## Branch

All research deliverables are tracked on `research/personas-scope-mvrs`.

---

## 1. Introduction

### 1.1 Purpose

This document defines the software requirements for a voice-interactive data storytelling system that enables rural and low-literacy populations to understand agricultural and weather analytics through multilingual voice interaction, icon-based visual anchors, and narrative data storytelling.

### 1.2 Scope

The system is a web-based frontend (React + Vite) backed by a FastAPI analytics service. It operates on a static agricultural dataset and does not require real-time data ingestion, user authentication, or cloud LLM dependency in its Minimum Viable Research System (MVRS).

### 1.3 Definitions

- **MVRS**: Minimum Viable Research System — smallest system capable of testing the core research hypothesis.
- **Condition**: A research configuration (conventional, voice-only, voice-icons, voice-story).
- **Icon Anchor**: A visual element that highlights during TTS narration to reinforce spoken content.
- **Simple Mode**: Reduced-complexity UI with enlarged icons and minimal text.

---

## 2. Overall Description

### 2.1 User Characteristics

Primary users are rural smallholder farmers with:
- Low to functional literacy
- Limited digital fluency
- Intermittent internet connectivity
- Preference for local-language voice interaction

### 2.2 System Context

The system is a standalone web application. Users access it through a browser on smartphones or desktops. No mobile app, SMS gateway, or IoT integration is included in the MVRS.

---

## 3. Functional Requirements

### 3.1 Voice Input

**FR-01: Microphone Activation**
- **Priority**: Must have
- **Description**: User can start and stop voice input via a microphone button.
- **Acceptance Criteria**:
  - Button toggles between "Listening…" and "Voice Input" states.
  - Button is keyboard accessible with visible focus indicator.
  - Button has `aria-label` describing its action.

**FR-02: Continuous Speech Recognition**
- **Priority**: Must have
- **Description**: System accepts continuous speech input with interim results.
- **Acceptance Criteria**:
  - Interim transcript appears in real-time while user speaks.
  - Final transcript is used for intent parsing.
  - Recognition stops after 8 seconds of silence.

**FR-03: Speech Error Recovery**
- **Priority**: Must have
- **Description**: System handles recognition errors gracefully.
- **Acceptance Criteria**:
  - `no-speech` error: system remains in listening state, no alert shown.
  - `not-allowed` error: system displays "Microphone access denied" message with browser settings hint.
  - `network` error: system displays connectivity error message.
  - `aborted` error: silent recovery, no UI change.

### 3.2 Speech Recognition

**FR-04: Browser-Native STT**
- **Priority**: Must have
- **Description**: System uses Web Speech API (`SpeechRecognition` / `webkitSpeechRecognition`) for speech-to-text.
- **Acceptance Criteria**:
  - Works in Chrome, Edge, and Safari.
  - Gracefully hides voice UI in unsupported browsers.
  - No backend STT dependency in MVRS.

**FR-05: Multilingual STT**
- **Priority**: Should have
- **Description**: System supports speech recognition in multiple languages.
- **Acceptance Criteria**:
  - Supports: English (en-US), Hindi (hi-IN), Tamil (ta-IN), Telugu (te-IN), Kannada (kn-IN), Marathi (mr-IN), Bengali (bn-IN).
  - Language selector persists in `localStorage`.
  - Unsupported language shows fallback message.

### 3.3 Language Detection/Selection

**FR-06: Manual Language Selection**
- **Priority**: Must have
- **Description**: User can manually select input and output language.
- **Acceptance Criteria**:
  - Dropdown shows all supported languages.
  - Selection applies to both STT and TTS.
  - Current selection is visually indicated.

**FR-07: Language Mismatch Handling**
- **Priority**: Should have
- **Description**: System detects when browser does not support selected language.
- **Acceptance Criteria**:
  - Toast notification: "Voice in [language] is not supported by your browser. Using English instead."
  - System continues operation in fallback language.

### 3.4 Natural-Language Understanding

**FR-08: Intent Parsing**
- **Priority**: Must have
- **Description**: System parses voice transcript into structured intents without cloud NLP.
- **Acceptance Criteria**:
  - Recognizes filter intents: `show [crop] in [state]`, `filter by [district]`, `from [date] to [date]`.
  - Recognizes control intents: `reset`, `clear`, `read aloud`, `stop`, `pause`, `resume`, `simple mode`, `standard mode`, `help`, `undo`.
  - Recognizes query intents: weather, rainfall, temperature, soil moisture, yield, trend, comparison.
  - Returns confidence score (0.0–1.0) for every parse.

**FR-09: Entity Extraction**
- **Priority**: Must have
- **Description**: System extracts named entities from transcript.
- **Acceptance Criteria**:
  - Crops: Wheat, Rice, Sugarcane, Cotton, Maize, Pulses, Groundnut, Soybean.
  - States: 8 Indian states.
  - Districts: mapped to parent state.
  - Dates: ISO format (YYYY-MM-DD).

**FR-10: Context Management**
- **Priority**: Should have
- **Description**: System maintains short-term conversation context for follow-up questions.
- **Acceptance Criteria**:
  - Context buffer stores last crop, state, district, metric, and date range.
  - Follow-up queries like "And rice?" resolve context to previous crop.
  - Context clears on filter change, condition switch, or after 60 seconds of silence.

### 3.5 Query Processing

**FR-11: Confirmation Handling**
- **Priority**: Must have
- **Description**: System asks confirmation for destructive or ambiguous actions.
- **Acceptance Criteria**:
  - `reset filters` triggers yes/no confirmation.
  - Partial filter matches trigger confirmation with assumed values.
  - User can respond via voice ("yes"/"no") or button tap.

**FR-12: Clarification Handling**
- **Priority**: Must have
- **Description**: System asks single-shot clarification for ambiguous queries.
- **Acceptance Criteria**:
  - Ambiguous metric: "Do you mean rainfall, temperature, or soil moisture?"
  - Ambiguous crop: "Which crop? Say wheat, rice, or cotton."
  - After clarification, system proceeds with best guess if still unclear.

**FR-13: Unknown Question Handling**
- **Priority**: Must have
- **Description**: System handles unsupported questions gracefully.
- **Acceptance Criteria**:
  - Response: "I don't have that information. I can help with weather, rainfall, soil moisture, yield, and recommendations. Say 'help' for more."
  - Never says "I don't know" without offering alternative path.

### 3.6 Weather-Data Retrieval

**FR-14: Dataset Loading**
- **Priority**: Must have
- **Description**: System loads agricultural dataset from CSV on startup.
- **Acceptance Criteria**:
  - Loads `dataset/agriculture.csv` (configurable path).
  - Validates columns on load: date, state, district, crop, rainfall, temperature, humidity, soil_moisture, yield, production, area, fertilizer, irrigation.
  - Handles missing values with defaults or row exclusion.
  - Returns error if dataset is empty or corrupt.

**FR-15: Filtered Data Retrieval**
- **Priority**: Must have
- **Description**: API returns filtered dataset based on query parameters.
- **Acceptance Criteria**:
  - Accepts: crop, state, district, start_date, end_date.
  - Returns matching rows with computed KPIs.
  - Returns empty result with friendly message if no matches.

### 3.7 Data Transformation

**FR-16: KPI Computation**
- **Priority**: Must have
- **Description**: Backend computes key performance indicators from filtered data.
- **Acceptance Criteria**:
  - Computes: average rainfall, average temperature, average humidity, average soil moisture, average yield, total production.
  - Computes period-over-period change for each KPI.
  - Returns null for KPIs with insufficient data.

**FR-17: Chart Data Transformation**
- **Priority**: Must have
- **Description**: Backend transforms filtered data into chart-ready formats.
- **Acceptance Criteria**:
  - Line chart: time-series with one or more series.
  - Bar chart: categorical aggregation.
  - Scatter chart: x/y pairs with optional size encoding.
  - Heatmap: matrix with row/column labels.
  - Pie chart: categorical proportions.

### 3.8 Insight Generation

**FR-18: Rule-Based Insight Detection**
- **Priority**: Must have
- **Description**: Backend generates insights from data patterns.
- **Acceptance Criteria**:
  - Detects: trends (increasing/decreasing), anomalies (outliers), comparisons (above/below average).
  - Assigns severity: info, warning, critical.
  - Returns at least one insight even for empty/limited data.

**FR-19: Story Generation**
- **Priority**: Must have
- **Description**: Backend generates narrative story from insights and recommendations.
- **Acceptance Criteria**:
  - Produces plain-language summary (max 3 sentences, 60 words).
  - Includes causal reasoning ("rain decreased, so yield dropped").
  - Includes actionable recommendations.
  - Falls back to rule-based engine if AI (Gemini) is unavailable.

### 3.9 Visual Storytelling

**FR-20: Icon Rendering**
- **Priority**: Must have
- **Description**: System renders semantic icons for all supported concepts.
- **Acceptance Criteria**:
  - 13 icons: temperature, rain, rain probability, wind, humidity, cloud cover, sunny, extreme weather, trend up, trend down, comparison, forecast, recommendation.
  - Each icon has `aria-label` text equivalent.
  - Icons are distinguishable by shape alone (color-independent).

**FR-21: Icon Highlighting**
- **Priority**: Should have
- **Description**: System highlights relevant icon during TTS narration.
- **Acceptance Criteria**:
  - Active icon shows visual highlight (ring or background).
  - Highlighting respects `prefers-reduced-motion`.
  - Highlighting clears when narration stops.

**FR-22: Simple Mode**
- **Priority**: Must have
- **Description**: System offers simplified view with reduced visual complexity.
- **Acceptance Criteria**:
  - Hides advanced charts (line, bar, scatter, heatmap).
  - Shows only pie chart or icon summary.
  - Enlarges icons and KPI values.
  - Hides unit/change text in KPI cards.

### 3.10 Text-to-Speech

**FR-23: TTS Narration**
- **Priority**: Must have
- **Description**: System speaks story and recommendation content.
- **Acceptance Criteria**:
  - Reads story panel content on user request ("read aloud").
  - Reads recommendations panel on user request.
  - Uses `speechSynthesis` API.
  - Rate is 0.9x default speed.

**FR-24: TTS Controls**
- **Priority**: Must have
- **Description**: User can control TTS playback.
- **Acceptance Criteria**:
  - Stop button cancels narration immediately.
  - Pause/resume buttons work during narration.
  - Controls are keyboard accessible.

**FR-25: Response Length Enforcement**
- **Priority**: Must have
- **Description**: TTS responses are limited to prevent user overload.
- **Acceptance Criteria**:
  - Max 3 sentences per response.
  - Max 60 words per response.
  - Story mode allows up to 120 words with pause points every 30 words.

### 3.11 Conversation Context

**FR-26: Context Buffer**
- **Priority**: Should have
- **Description**: System maintains in-memory conversation context.
- **Acceptance Criteria**:
  - Stores last crop, state, district, metric, and date range.
  - Resolves pronouns ("it", "that") and ellipsis ("and temperature?") in follow-up queries.
  - Context persists across multiple turns within same session.

**FR-27: Context Reset**
- **Priority**: Must have
- **Description**: Context resets on explicit actions.
- **Acceptance Criteria**:
  - Resets on `reset filters` command.
  - Resets on condition switch.
  - Resets after 60 seconds of silence.

### 3.12 Error Handling

**FR-28: Data Errors**
- **Priority**: Must have
- **Description**: System handles missing or invalid data gracefully.
- **Acceptance Criteria**:
  - Empty dataset: shows "No data available" state with reload hint.
  - Invalid filter: shows "No data found for [filter]. Try another value."
  - API error: shows generic error message with retry button.

**FR-29: Voice Errors**
- **Priority**: Must have
- **Description**: System handles voice subsystem failures.
- **Acceptance Criteria**:
  - Permission denied: shows browser settings hint.
  - Unsupported language: shows fallback notification.
  - Network loss: shows connectivity error.

### 3.13 Offline/Poor-Connectivity Behavior

**FR-30: Offline Operation**
- **Priority**: Should have
- **Description**: System remains functional with intermittent connectivity.
- **Acceptance Criteria**:
  - All core features work without internet after initial load.
  - Dataset is cached in browser memory for the session.
  - Voice APIs work offline in supported browsers (Chrome/Edge).
  - Shows offline indicator when connectivity is lost.

**FR-31: Degraded Mode**
- **Priority**: Could have
- **Description**: System disables non-essential features under poor connectivity.
- **Acceptance Criteria**:
  - Disables AI-powered story generation (Gemini) if unreachable.
  - Falls back to rule-based engine transparently.
  - Shows "Rule-based analysis" indicator in footer.

---

## 4. Non-Functional Requirements

### 4.1 Performance

**NFR-01: API Response Time**
- **Priority**: Must have
- **Target**: 95th percentile < 500ms for all data endpoints.
- **Acceptance Criteria**:
  - `/api/dashboard` responds in < 500ms with 600-row dataset.
  - `/api/insights` responds in < 300ms.
  - `/api/story` responds in < 500ms.

**NFR-02: Frontend Load Time**
- **Priority**: Must have
- **Target**: Initial load < 3 seconds on 3G connection.
- **Acceptance Criteria**:
  - First contentful paint < 1.5s.
  - Time to interactive < 3s.

**NFR-03: Voice Latency**
- **Priority**: Must have
- **Target**: TTS starts within 200ms of command.
- **Acceptance Criteria**:
  - Measured from button tap/voice command to first audio output.
  - STT interim results appear within 100ms of speech.

### 4.2 Reliability

**NFR-04: Uptime**
- **Priority**: Must have
- **Target**: 99.5% availability for backend service.
- **Acceptance Criteria**:
  - Backend restarts automatically on crash.
  - Health check endpoint returns status within 100ms.

**NFR-05: Data Integrity**
- **Priority**: Must have
- **Description**: Dataset loading is idempotent and validated.
- **Acceptance Criteria**:
  - Corrupt CSV shows error message, does not crash server.
  - Missing columns log warning, use defaults where possible.

### 4.3 Accessibility

**NFR-06: WCAG 2.1 AA Compliance**
- **Priority**: Must have
- **Description**: Interface meets WCAG 2.1 AA standards.
- **Acceptance Criteria**:
  - All interactive elements have `aria-label` or visible text.
  - Color contrast ratio ≥ 4.5:1 for normal text, 3:1 for large text.
  - Keyboard navigation works for all features.
  - Focus indicators are visible on all interactive elements.
  - `prefers-reduced-motion` is respected.
  - `prefers-reduced-sound` is respected (visual alternatives provided).

**NFR-07: Screen Reader Support**
- **Priority**: Must have
- **Description**: All information is available via screen reader.
- **Acceptance Criteria**:
  - Charts have accessible descriptions.
  - Icons have `aria-label` text equivalents.
  - Dynamic updates (insights, story) use `aria-live="polite"`.

### 4.4 Usability

**NFR-08: Learnability**
- **Priority**: Must have
- **Target**: New user completes first task within 2 minutes without training.
- **Acceptance Criteria**:
  - Help modal lists all voice commands with examples.
  - First-run tooltip explains voice controls.

**NFR-09: Error Prevention**
- **Priority**: Should have
- **Description**: System prevents user errors where possible.
- **Acceptance Criteria**:
  - Destructive actions (reset) require confirmation.
  - Invalid filter combinations show friendly error.

**NFR-10: Task Efficiency**
- **Priority**: Should have
- **Target**: Expert user completes common task in < 30 seconds.
- **Acceptance Criteria**:
  - Voice command "show wheat in Punjab" applies filters in < 2 seconds.
  - "Read aloud" starts narration within 200ms.

### 4.5 Scalability

**NFR-11: Dataset Size**
- **Priority**: Should have
- **Target**: Supports datasets up to 100,000 rows without UI degradation.
- **Acceptance Criteria**:
  - Dashboard loads within 2s with 100K rows.
  - Charts render without jank.

**NFR-12: Concurrent Users**
- **Priority**: Could have
- **Target**: 100 concurrent users on single backend instance.
- **Acceptance Criteria**:
  - Rate limiting prevents abuse.
  - Memory usage remains stable under load.

### 4.6 Security

**NFR-13: Input Validation**
- **Priority**: Must have
- **Description**: All user inputs are validated server-side.
- **Acceptance Criteria**:
  - SQL injection prevented via parameterized queries.
  - XSS prevented via output encoding.
  - File uploads (if any) restricted to CSV, max 10MB.

**NFR-14: CORS Policy**
- **Priority**: Must have
- **Description**: Backend enforces strict CORS policy.
- **Acceptance Criteria**:
  - Only configured origins allowed.
  - Credentials not exposed to unauthorized origins.

### 4.7 Privacy

**NFR-15: Data Collection**
- **Priority**: Must have
- **Description**: System collects only research-necessary data.
- **Acceptance Criteria**:
  - No personal identifiers beyond anonymous user ID.
  - Voice transcripts are not stored.
  - Task logs and survey responses are anonymized.

**NFR-16: Data Retention**
- **Priority**: Must have
- **Description**: Research data is retained only for study duration.
- **Acceptance Criteria**:
  - Task logs and surveys deleted after 6 months.
  - Users can request data deletion.

### 4.8 Explainability

**NFR-17: Recommendation Explanation**
- **Priority**: Must have
- **Description**: Every recommendation includes reasoning.
- **Acceptance Criteria**:
  - Format: "Action. Because [reason]."
  - Example: "Irrigate tomorrow morning. Soil moisture is 28%, below the 30% threshold."
  - No recommendation without explanation.

**NFR-18: Insight Traceability**
- **Priority**: Should have
- **Description**: Insights reference source data.
- **Acceptance Criteria**:
  - Each insight includes metric name and time range.
  - Hover/tap shows data source details.

### 4.9 Maintainability

**NFR-19: Code Quality**
- **Priority**: Must have
- **Description**: Codebase follows consistent standards.
- **Acceptance Criteria**:
  - TypeScript strict mode enabled.
  - Linting passes with zero errors.
  - Backend tests cover ≥ 80% of endpoints.
  - Frontend builds without warnings.

**NFR-20: Dependency Management**
- **Priority**: Should have
- **Description**: Dependencies are pinned and audited.
- **Acceptance Criteria**:
  - `package-lock.json` and `poetry.lock` committed.
  - No high-severity vulnerabilities in dependencies.

### 4.10 Localization

**NFR-21: Multi-Language Support**
- **Priority**: Must have
- **Description**: UI and voice support 8 languages.
- **Acceptance Criteria**:
  - English, Hindi, Tamil, Telugu, Kannada, Marathi, Bengali.
  - Language selection persists across sessions.
  - Icons and visuals are language-agnostic.

**NFR-22: Cultural Adaptation**
- **Priority**: Should have
- **Description**: System avoids culturally specific metaphors.
- **Acceptance Criteria**:
  - Icons reviewed for cross-cultural recognition.
  - Voice prompts use neutral, respectful tone.

---

## 5. Requirement Prioritization Summary

| ID | Requirement | Priority |
|---|---|---|
| FR-01 | Microphone Activation | Must have |
| FR-02 | Continuous Speech Recognition | Must have |
| FR-03 | Speech Error Recovery | Must have |
| FR-04 | Browser-Native STT | Must have |
| FR-05 | Multilingual STT | Should have |
| FR-06 | Manual Language Selection | Must have |
| FR-07 | Language Mismatch Handling | Should have |
| FR-08 | Intent Parsing | Must have |
| FR-09 | Entity Extraction | Must have |
| FR-10 | Context Management | Should have |
| FR-11 | Confirmation Handling | Must have |
| FR-12 | Clarification Handling | Must have |
| FR-13 | Unknown Question Handling | Must have |
| FR-14 | Dataset Loading | Must have |
| FR-15 | Filtered Data Retrieval | Must have |
| FR-16 | KPI Computation | Must have |
| FR-17 | Chart Data Transformation | Must have |
| FR-18 | Rule-Based Insight Detection | Must have |
| FR-19 | Story Generation | Must have |
| FR-20 | Icon Rendering | Must have |
| FR-21 | Icon Highlighting | Should have |
| FR-22 | Simple Mode | Must have |
| FR-23 | TTS Narration | Must have |
| FR-24 | TTS Controls | Must have |
| FR-25 | Response Length Enforcement | Must have |
| FR-26 | Context Buffer | Should have |
| FR-27 | Context Reset | Must have |
| FR-28 | Data Errors | Must have |
| FR-29 | Voice Errors | Must have |
| FR-30 | Offline Operation | Should have |
| FR-31 | Degraded Mode | Could have |
| NFR-01 | API Response Time | Must have |
| NFR-02 | Frontend Load Time | Must have |
| NFR-03 | Voice Latency | Must have |
| NFR-04 | Uptime | Must have |
| NFR-05 | Data Integrity | Must have |
| NFR-06 | WCAG 2.1 AA Compliance | Must have |
| NFR-07 | Screen Reader Support | Must have |
| NFR-08 | Learnability | Must have |
| NFR-09 | Error Prevention | Should have |
| NFR-10 | Task Efficiency | Should have |
| NFR-11 | Dataset Size | Should have |
| NFR-12 | Concurrent Users | Could have |
| NFR-13 | Input Validation | Must have |
| NFR-14 | CORS Policy | Must have |
| NFR-15 | Data Collection | Must have |
| NFR-16 | Data Retention | Must have |
| NFR-17 | Recommendation Explanation | Must have |
| NFR-18 | Insight Traceability | Should have |
| NFR-19 | Code Quality | Must have |
| NFR-20 | Dependency Management | Should have |
| NFR-21 | Multi-Language Support | Must have |
| NFR-22 | Cultural Adaptation | Should have |

---

## 6. Out of Scope

The following are explicitly excluded from this release:

- Real-time IoT sensor integration
- Satellite imagery or NDVI analysis
- ML-based yield prediction or pest detection
- User accounts, authentication, or personalization beyond localStorage
- E-commerce or mandi price integration
- Government scheme enrollment
- SMS/USSD delivery
- Mobile native apps (iOS/Android)
- Multi-user collaboration
- LLM-based storytelling (Gemini) in MVRS
- Real-time forecast API integration

---

## 7. Verification

| Verification Method | Coverage |
|---|---|
| Automated tests | Backend API endpoints (pytest) |
| TypeScript build | Frontend type safety |
| Manual testing | Voice input/output, icon rendering, accessibility |
| Wizard-of-Oz | Voice interaction patterns with target users |
| Heuristic evaluation | Nielsen's heuristics for low-literacy UI |
