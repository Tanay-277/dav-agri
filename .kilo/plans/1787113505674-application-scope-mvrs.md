# Application Scope and Minimum Viable Research System (MVRS)

## Branch

All research deliverables are tracked on `research/personas-scope-mvrs`.

---

## 1. Primary Domain

**Agricultural and weather data storytelling for smallholder farmers.**

The system focuses on the intersection of:
- Weather information (rainfall, temperature, humidity, soil moisture)
- Agricultural decision-making (sowing, irrigation, harvesting, pest management)
- Low-literacy, rural, multilingual user contexts

---

## 2. Primary User

**Rural smallholder farmers with low to functional literacy, limited digital fluency, and intermittent internet connectivity.**

Secondary users (out of scope for initial research, but acknowledged):
- Agricultural extension workers
- Government policy analysts
- Agronomists

---

## 3. Primary Decision-Support Problem

**"Given current and forecasted weather and agricultural conditions, what action should I take this week on my farm?"**

This is a *weekly tactical* decision problem, not a strategic planning problem. The system reduces the cognitive and literacy burden of interpreting raw charts and tables by translating data into a multimodal narrative (voice + icon + story) that leads to a concrete recommendation.

---

## 4. Core Use Cases (5–8)

1. **Weather outlook (3-day forecast):** Understand expected rain, temperature, and wind for the next 72 hours.
2. **Rainfall trend analysis (past 30 days):** Know whether the monsoon is delayed, on schedule, or excessive.
3. **Soil moisture status:** Determine whether irrigation is needed now or can be deferred.
4. **Sowing/harvesting suitability:** Get a go/no-go recommendation based on soil + forecast conditions.
5. **Crop-specific yield insight:** Compare current crop performance against historical averages for the same period.
6. **Voice-driven data exploration:** Filter dashboard by crop, state, district, and date range using voice commands.
7. **Automated story generation:** Receive a plain-language narrative summarizing current conditions and recommended actions.
8. **Recommendation delivery:** Get prioritized, actionable recommendations (e.g., "irrigate tomorrow morning").

---

## 5. Secondary Use Cases (5–10)

1. **Historical yield comparison:** Compare yield across multiple past seasons for a specific crop/region.
2. **Correlation exploration:** Understand relationships (e.g., rainfall vs. yield) via heatmap.
3. **Market price context:** View commodity production trends (not real-time mandi prices).
4. **Pest/disease risk indication:** Rule-based alerts when humidity + temperature thresholds suggest risk.
5. **Export/share report:** Download PDF/JSON summary for offline reference or sharing with extension workers.
6. **Multilingual voice interaction:** Interact in local language (Hindi, Kannada, Tamil, Telugu, Marathi, Bengali) via Web Speech API.
7. **Simple mode:** Reduced-chart interface with enlarged icons for users with severe literacy barriers.
8. **Icon-anchored narration:** Voice output synchronized with on-screen icon highlighting.
9. **Data literacy micro-assessment:** Pre/post-intervention quiz to measure comprehension improvement.
10. **A/B condition toggle:** Switch between conventional, voice-only, voice+icons, and voice+story conditions (for research evaluation).

---

## 6. Explicitly Excluded Use Cases

- Real-time IoT sensor integration (soil probes, weather stations)
- Satellite imagery or NDVI analysis
- ML-based yield prediction or pest detection
- User accounts, authentication, or personalization beyond localStorage preferences
- E-commerce (input ordering, mandi price negotiation)
- Government scheme enrollment or subsidy processing
- SMS/USSD delivery (voice is the primary channel; SMS is deferred)
- Offline-first architecture beyond browser caching (no PWA service worker in MVP)
- Multi-user collaboration or shared dashboards

---

## 7. Required Weather/Agricultural Variables

### Weather Variables
| Variable | Unit | Source in Current Dataset |
|---|---|---|
| Rainfall | mm | `rainfall` |
| Temperature | °C | `temperature` |
| Humidity | % | `humidity` |
| Soil Moisture | % | `soil_moisture` |

### Agricultural Variables
| Variable | Unit | Source in Current Dataset |
|---|---|---|
| Crop type | categorical | `crop` |
| State | categorical | `state` |
| District | categorical | `district` |
| Date | YYYY-MM-DD | `date` |
| Yield | kg/ha | `yield` |
| Production | tonnes | `production` |
| Area | ha | `area` |
| Fertilizer usage | kg | `fertilizer` |
| Irrigation | % | `irrigation` |

---

## 8. Required Historical Data

- **Daily/monthly aggregated weather data:** Minimum 2 years of historical records to establish trends and detect anomalies.
- **Crop-wise yield and production records:** Minimum 2 years, aligned by district/season.
- **Soil moisture records:** Aligned with weather data for correlation.
- **Input data (fertilizer, irrigation):** Optional but recommended for generating recommendations.

*Current implementation:* 600-row synthetic dataset (8 crops, 8 states, 5 districts, 2022–2024).

---

## 9. Required Forecast Data

**NOT included in the current dataset.** The MVRS operates on *historical* data only.

Forecast data (3-day and 7-day) would require:
- External weather API integration (e.g., OpenWeatherMap, IMD, or local meteorological service)
- API key management and fallback for offline operation
- Geocoding to map user location to forecast grid

**Decision:** Forecast integration is **postponed** to Phase 3 (post-MVRS). The MVRS research hypothesis can be tested using historical trends and rule-based recommendations without live forecast data.

---

## 10. Data Update Frequency

| Data Type | Update Frequency | Rationale |
|---|---|---|
| Historical weather/agriculture | Static (CSV reload) | Research dataset; no live ingestion needed |
| Insights/story/recommendations | Real-time on filter change | Computed from loaded dataset |
| Forecast (postponed) | 3-hourly or daily | Would require API integration |

---

## 11. Minimum Viable Research System (MVRS)

The MVRS is the **smallest possible system that can test our core research hypothesis:**

> *"A voice-interactive, icon-anchored data storytelling interface improves agricultural data comprehension and decision confidence among low-literacy users compared to a conventional text-and-chart dashboard."*

### MVRS Must Include

| Component | Implementation |
|---|---|
| **Conventional dashboard condition** | Existing Plotly.js charts + filters (already built) |
| **Voice input (STT)** | Web Speech API with multilingual selector (already built) |
| **Voice output (TTS)** | `speechSynthesis` for story narration (already built) |
| **Icon-based visual anchors** | Icon legend + simple mode toggle (already built) |
| **Data storytelling engine** | Rule-based narrative generation from insights + recommendations (already built) |
| **A/B condition switcher** | Toggle between conventional / voice-only / voice+icons / voice+story (needs implementation) |
| **Task completion logger** | Record which use case was attempted, success/failure, time-on-task (needs implementation) |
| **Post-task survey** | Comprehension quiz + trust scale + SUS (needs implementation) |
| **Expanded dataset** | 600+ rows with realistic correlations (already built) |

### MVRS Must NOT Include

- LLM-based storytelling (Gemini) — use rule-based to ensure deterministic, offline-capable behavior
- Real-time forecast data — historical data is sufficient for hypothesis testing
- Authentication or user accounts — single-device, single-user research tool
- Advanced analytics (ML predictions) — rule-based thresholds are sufficient

---

## 12. MVP Features (Included in MVRS)

| Feature | Rationale |
|---|---|
| Conventional dashboard (5 charts, KPIs, filters) | Baseline condition for A/B comparison |
| Voice input with intent parsing | Primary independent variable (voice interaction) |
| Voice output (story narration) | Primary independent variable (storytelling) |
| Icon legend + simple mode | Primary independent variable (icon anchoring) |
| A/B condition switcher | Research methodology — enables within-subjects or between-subjects design |
| Task completion + time-on-task logging | Dependent variable measurement |
| Post-task comprehension quiz | Dependent variable measurement (data literacy) |
| Trust/SUS survey | Dependent variable measurement (user experience) |
| 600-row realistic dataset | Provides sufficient data variation for meaningful tasks |
| Multilingual selector (8 languages) | Supports target user population |
| PDF/JSON export | Utility for participants and researchers |
| Responsive design + accessibility (ARIA, reduced-motion) | Ethical requirement for inclusive research |

---

## 13. Optional Features (Post-MVRS, Pre-Production)

| Feature | Rationale |
|---|---|
| Backend-driven STT/TTS (Whisper + mimic3) | Better offline support and custom model training, but adds deployment complexity |
| Forecast API integration | Increases real-world relevance, but requires API keys, geocoding, and error handling |
| Culturally co-designed icon set | Improves icon comprehension, but requires participatory design sessions with target users |
| Longitudinal data literacy tracking | Measures learning over time, but requires multi-session study design |
| User accounts and history | Enables longitudinal analysis, but adds auth and database complexity |
| PWA service worker | Enables true offline mode, but adds maintenance burden |
| Advanced analytics (yield prediction, pest risk) | Increases system utility, but requires domain expertise and validation |

---

## 14. Features Explicitly Postponed

| Feature | Reason for Postponement |
|---|---|
| LLM-based storytelling (Gemini API) | Cloud dependency, cost, non-deterministic output complicates research measurement; rule-based engine is sufficient for hypothesis testing |
| Real-time IoT/satellite data | Infrastructure cost, data pipeline complexity, not needed for MVRS hypothesis |
| Government scheme integration | Domain expansion beyond weather/agriculture analytics; requires legal/policy review |
| E-commerce/mandi price integration | Requires third-party APIs, payment processing, and regulatory compliance |
| Multi-language dialect support | 8 languages is sufficient for initial research; dialect-specific fine-tuning requires additional ASR/TTS models |
| Mobile native apps (iOS/Android) | Web app is sufficient for research; native apps require separate codebases and store approval |
| Collaborative/shared dashboards | Multi-user architecture is out of scope for single-user decision-support research |

---

## 15. Research Hypothesis Alignment

The MVRS is tightly scoped to test the hypothesis. Every feature in the MVP directly serves one of three purposes:

1. **Deliver the intervention** (voice input, voice output, icons, storytelling)
2. **Provide the baseline** (conventional dashboard)
3. **Measure the outcome** (task logging, surveys, comprehension quiz)

Features outside the MVP are explicitly deferred because they do not contribute to hypothesis testing in the initial study phase.

---

## 16. Next Steps

1. Implement A/B condition switcher in `dashboard-page.tsx`
2. Implement task completion logger (frontend state + backend endpoint)
3. Implement post-task survey component (quiz + trust scale + SUS)
4. Integrate survey trigger into dashboard flow (e.g., after 3 tasks or explicit "Finish Study" button)
5. Validate dataset realism with domain expert
6. Conduct Wizard-of-Oz validation with 3–5 users before full deployment
