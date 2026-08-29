# Research Protocol: Voice-Interactive Data Storytelling for Rural/Low-Literacy Populations

**Version:** 1.0  
**Date:** 2026-08-29  
**Status:** FROZEN — Engineering implementation complete. This document defines the research protocol only.  
**Branch:** research/personas-scope-mvrs  
**Dataset:** agriculture.csv (600 rows, 8 states, 8 crops, 2022-2024)  

---

## 1. Research Objective

Evaluate how different interaction modalities (conventional GUI vs. voice-based interaction) affect participants' ability to comprehend agricultural data insights and complete information-seeking tasks using an interactive dashboard.

The study compares four experimental conditions that progressively add voice, icon, and narrative features to a baseline chart-and-filter dashboard.

---

## 2. Research Questions

1. Does voice interaction improve task completion efficiency compared to conventional GUI-only interaction?
2. Does the addition of icon legends (C3) or narrative storytelling (C4) change comprehension scores relative to voice-only (C2)?
3. Is voice usage associated with higher trust in the system's recommendations?
4. Does the multimodal condition (C4) produce different SUS usability scores than simpler conditions?
5. Are there measurable differences in how participants interact with the dashboard across conditions?

---

## 3. Hypotheses

These hypotheses are derived from the existing experimental design and are not invented.

**H1 (Efficiency):** Participants in voice conditions (C2, C3, C4) will complete tasks faster than C1 for tasks amenable to voice query.

**H2 (Comprehension):** C4 (Voice+Icons+Story) will show higher comprehension scores than C1 due to the combination of modalities.

**H3 (Trust):** Higher-condition participants (C3, C4) will report higher trust scores than C1 and C2.

**H4 (Usability):** C1 will have higher SUS scores than voice conditions due to lower learning curve, OR C4 will have equivalent/better scores if multimodal integration reduces cognitive load.

**H5 (Voice adoption):** In voice conditions, participants who actually use voice will complete tasks faster than those who do not, despite identical underlying data.

---

## 4. Experimental Conditions

| Condition | Value | Available UI Elements | Data Source |
|-----------|-------|----------------------|-------------|
| C1 | `conventional` | Filters, charts, KPIs, insights, tasks | Same backend `/api/v1/dashboard`, `/api/v1/insights` |
| C2 | `voice-only` | C1 + VoiceControls (mic, language selector, transcript) | Same |
| C3 | `voice-icons` | C2 + IconLegend (icon legend, simple/standard toggle, read aloud) | Same |
| C4 | `voice-story` | C3 + StoryPanel + RecommendationsPanel | Same |

**Critical invariant:** All conditions use the identical dataset, identical backend analytics, identical filters, identical task definitions, and identical factual values. Only presentation/interaction modality differs.

---

## 5. Participant Assignment Procedure

**Current implementation:** Condition is selected manually via the `ConditionSwitcher` component in the UI. There is no automated randomization or assignment system in the current codebase.

**Researcher responsibility:**
- Assign participants to conditions before they open the application.
- Communicate the assigned condition to the participant.
- Set the condition in the UI before the participant begins tasks.
- Do NOT allow participants to switch conditions during the session.

**Recommended assignment:** Between-subjects design. Each participant experiences exactly one condition for the entire session.

**Sample size:** The repository does not specify participant counts. Determine sample size based on statistical power requirements for your analysis.

---

## 6. Participant Session Procedure

1. **Welcome** (researcher-led)
   - Explain the study purpose at a high level.
   - Explain the assigned condition.
   - For C2/C3/C4: demonstrate the voice control button and microphone permission flow.
   - For C3/C4: explain the icon legend and/or story panel.

2. **Launch**
   - Open the application at the assigned condition.
   - Ensure browser supports SpeechRecognition for voice conditions (see Section 16).
   - Log the participant ID from the browser localStorage.

3. **Task Phase**
   - Participant completes research tasks in the task palette.
   - Tasks auto-complete after 3 seconds when clicked.
   - Do NOT instruct participants to wait for auto-complete; let them proceed naturally.
   - Record all task logs automatically via the backend.

4. **Survey Trigger**
   - After exactly 3 completed tasks, the survey modal appears automatically.
   - Participant completes the 4-step survey.
   - Survey can be skipped using the "Skip survey" button (see Section 14 for implications).

5. **Debrief**
   - Thank the participant.
   - Record any qualitative observations.
   - Do NOT reveal the other conditions to avoid demand characteristics.

---

## 7. Task Sequence

Tasks are presented in a palette (not a fixed sequence). Participants may choose any available task. All 8 tasks are available in all conditions.

| Task ID | Label | Voice-Specific | Description |
|---------|-------|----------------|-------------|
| `weather_outlook` | Weather outlook (3-day forecast) | No | Ask about expected weather conditions |
| `rainfall_trend` | Rainfall trend analysis (30 days) | No | Ask about rainfall patterns |
| `soil_moisture` | Soil moisture status | No | Ask about soil moisture levels |
| `sowing_suitability` | Sowing/harvesting suitability | No | Ask about planting/harvesting recommendations |
| `yield_insight` | Crop-specific yield insight | No | Ask about crop yield information |
| `voice_exploration` | Voice-driven data exploration | Yes | Use voice controls to explore data |
| `story_review` | Automated story review | C4 only | Review and understand the generated story |
| `recommendation_review` | Recommendation review | C4 only | Review system recommendations |

**Note:** The `voice_exploration` task is labeled as voice-specific but is available in all conditions. Participants in C1 may complete it via filters instead of voice. This is by design — it measures whether participants naturally choose voice when available.

---

## 8. Voice-Use Expectations

| Condition | Voice Available | Expected Voice Use |
|-----------|----------------|-------------------|
| C1 | No | `voice_used = false` for all tasks |
| C2 | Yes | Variable — depends on participant choice |
| C3 | Yes | Variable — depends on participant choice |
| C4 | Yes | Variable — depends on participant choice |

**Important:** `voice_used` records actual voice interaction, not condition assignment. A participant in C2 who never speaks will have `voice_used = false` for all tasks. This is intentional and analyzable.

---

## 9. Survey Procedure

The survey appears automatically after 3 completed tasks. It has 4 steps:

1. **Comprehension** (3 questions) — multiple choice about dashboard content
2. **Trust** (4 Likert items, 1-5) — trust in the system
3. **SUS** (10 Likert items, 1-5) — system usability
4. **Feedback** (open text) — optional qualitative comments

All steps except feedback are required. The "Skip survey" button allows participants to bypass the entire survey.

**Known limitation:** SUS scoring currently treats all items as positive. Items 2, 4, 6, 8, 10 are negative statements and require reverse-coding for valid SUS scores. See Section 14.

---

## 10. Data Recorded Per Task

| Field | Type | Source | Backend Column |
|-------|------|--------|----------------|
| `task_id` | string | Task definition | `task_logs.task_id` |
| `condition` | string | React state at completion | `task_logs.condition` |
| `user_id` | string | `crypto.randomUUID()` + localStorage | `task_logs.user_id` |
| `completed` | bool | Task completion status | `task_logs.completed` |
| `duration_ms` | int | `Date.now()` delta from start to complete | `task_logs.duration_ms` |
| `voice_used` | bool | `markVoiceUsed()` when transcript sent to backend | `task_logs.voice_used` |
| `error` | string \| null | Error state if task interrupted/failed | `task_logs.error` |

---

## 11. Data Recorded Per Participant/Condition

| Field | Type | Backend Column |
|-------|------|----------------|
| `task_id` | string \| null | `survey_responses.task_id` |
| `condition` | string | `survey_responses.condition` |
| `user_id` | string \| null | `survey_responses.user_id` |
| `comprehension_score` | int | `survey_responses.comprehension_score` |
| `trust_score` | int | `survey_responses.trust_score` |
| `sus_score` | int | `survey_responses.sus_score` |
| `feedback` | string | `survey_responses.feedback` |

**Joinability:** Task logs and survey responses can be joined on `user_id` + `condition`. Task-level join is possible via `task_id` when present in survey responses.

---

## 12. Participant Identifiers and Privacy

| Aspect | Implementation |
|--------|---------------|
| ID generation | `crypto.randomUUID()` on first visit |
| ID persistence | `localStorage` key: `agristory_user_id` |
| ID stability | Same ID reused across sessions on same browser |
| ID randomness | UUID v4 — no personal information encoded |
| Backend storage | Stored as plain text in `task_logs.user_id` and `survey_responses.user_id` |
| IP logging | Backend logs client IP in request logs (see security) |

**Privacy considerations:**
- No demographic data is collected.
- No personally identifiable information beyond the browser-generated UUID.
- IP addresses are logged by the backend request logger.
- Feedback text may contain identifying information if participants include names.

**Recommendation:** Add a consent screen before condition assignment to document voluntary participation and data collection scope.

---

## 13. Handling Incomplete Sessions

| Scenario | Frontend Behavior | Backend Behavior |
|----------|-------------------|------------------|
| Participant closes tab during active task | `useEffect` cleanup → `completeTask(taskId, false, "interrupted")` | Inserts record with `completed=false`, `error="interrupted"` |
| Participant closes tab during survey | Survey modal closed; no explicit handling | No survey record created |
| Browser crash | Same as tab close | Same as tab close |
| Network failure during task log | `fetch(...).catch(() => {})` — silently swallows error | No record created |
| Network failure during survey | `await fetch(...)` without catch — error thrown | No record created |

**Gap:** Network failures during task logging are silently swallowed. Researchers should verify that the expected number of task records exist for each participant after the session.

---

## 14. Handling Technical Failures

| Failure | Frontend Handling | Participant Action |
|---------|-------------------|-------------------|
| Microphone permission denied | Displays "Microphone access denied." | Participant must grant permission or switch to C1 |
| No speech detected | Stops listening, no error shown | Participant can retry |
| Recognition error | Displays "Speech error: {error}" | Participant can retry |
| Backend 500 error | Displays error message in red | Participant can retry or continue with filters |
| Unsupported browser | VoiceControls returns `null` | Participant must use C1 |
| Unsupported language | No validation; recognition may use default language | Participant should select a supported language |

**Known gaps:**
- No browser language capability validation before offering language selector.
- No fallback to text input if voice fails in voice conditions.
- No retry limit or escalation path for persistent failures.

---

## 15. Handling Unsupported Browser/Language Situations

| Situation | Current Behavior | Recommended Action |
|-----------|-----------------|-------------------|
| Browser without SpeechRecognition | VoiceControls hidden (`isSupported` check) | Assign participant to C1 |
| Browser with SpeechRecognition but without selected language pack | Recognition may silently use default language or fail | Researcher should test browser compatibility before session |
| Participant selects unsupported language | Frontend accepts any of the 7 languages; backend processes text regardless | No explicit error; NLU may misdetect language |

**Recommendation:** Test browser compatibility on the actual participant device before starting the session. Chrome with Google voice packs is recommended for all 7 languages.

---

## 16. Pilot Procedure

1. **Recruit 2-4 participants per condition** (total 8-16 participants).
2. **Use the same device/browser** for all pilot participants to control for technical variability.
3. **Researcher observes but does not intervene** during task completion, except to resolve technical blockers.
4. **Record session notes** for each participant:
   - Time to first task completion
   - Voice usage observed
   - Errors encountered
   - Survey completion status
   - Qualitative observations
5. **Verify backend records** after each session:
   - Expected number of task logs exist
   - Survey record exists (if completed)
   - `voice_used` values match observed behavior
6. **Debrief** each participant with open-ended questions about usability.

---

## 17. Criteria for Participant-Blocking Defects

A defect is participant-blocking if it prevents a participant from completing the workflow without researcher intervention.

| Criterion | Blocking? | Examples |
|-----------|-----------|---------|
| Cannot load dashboard | Yes | Backend down, dataset missing |
| Cannot see assigned condition UI | Yes | ConditionSwitcher broken |
| Voice controls visible in C1 | Yes | Condition leakage |
| Mock data shown instead of real data | Yes | API returning demo values |
| Task completion not recorded | Yes | Backend endpoint failing |
| Survey not triggered after 3 tasks | Yes | Trigger logic broken |
| Cannot submit survey | Yes | Backend endpoint failing |
| Browser crashes on voice button | Yes | SpeechRecognition error |
| Participant sees other participants' data | Yes | User ID collision |
| Numerical values change between conditions | Yes | Data source divergence |

**Non-blocking:** SUS scoring error, Marathi language detection, task auto-complete timing, survey skip button.

---

## 18. Data-Freeze Procedure After Collection

1. **Stop the backend server** to prevent new writes.
2. **Export the SQLite database:**
   ```bash
   cp agri.db agri.db.frozen.<timestamp>
   ```
3. **Export task logs:**
   ```sql
   .output task_logs.csv
   SELECT * FROM task_logs;
   ```
4. **Export survey responses:**
   ```sql
   .output survey_responses.csv
   SELECT * FROM survey_responses;
   ```
5. **Verify counts:** Ensure expected number of records per participant × condition.
6. **Checksum the exports** and store with the frozen database.
7. **Do NOT modify the frozen database.** Create copies for analysis.

---

## 19. Researcher Checklist Before Starting Pilot

- [ ] Backend deployed and `/api/v1/health` returns 200
- [ ] Frontend deployed and loads without errors
- [ ] Dataset file (`agriculture.csv`) present in deployment
- [ ] Database initialized (`dataset_meta` table exists)
- [ ] CORS configured for frontend origin
- [ ] `TTS_PROVIDER=edge` and `TTS_ALLOW_MOCK=false` in production
- [ ] Browser tested with all 7 language options
- [ ] Microphone permission flow tested for voice conditions
- [ ] Condition assignment plan documented
- [ ] Consent process prepared (not yet implemented in code)
- [ ] Data export procedure tested
- [ ] Backup storage location identified
- [ ] Pilot observation template prepared
- [ ] Known limitations documented and accepted

---

## 20. Known Limitations Affecting Research Validity

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| SUS reverse-coding missing | Invalid SUS scores | Fix in post-processing or re-score after collection |
| Marathi detected as Hindi | Misattributed language for Marathi queries | Note in analysis; does not affect task completion |
| No browser language validation | Participants may select unsupported languages | Test browsers before session |
| Survey can be skipped | Missing survey data | Encourage completion; document skip rate |
| ConditionSwitcher visible | Risk of condition switching during session | Researcher instruction; consider UI lock in pilot |
| Task auto-complete after 3s | Duration may not reflect actual task time | Use duration as "time to initiate completion" |
| No randomization | Potential experimenter bias | Use fixed assignment order; document condition order |

---

## Appendix A: Files Inspected

| File | Purpose |
|------|---------|
| `frontend/src/hooks/use-task-logger.ts` | Task logging implementation |
| `frontend/src/components/survey-modal.tsx` | Survey UI and scoring |
| `frontend/src/components/condition-switcher.tsx` | Condition selection UI |
| `frontend/src/pages/dashboard-page.tsx` | Main dashboard and workflow |
| `backend/database/db.py` | Task log and survey persistence |
| `backend/models/schemas.py` | Pydantic models for research data |
| `backend/core/config.py` | Environment configuration |
| `backend/database/migrations/001_initial_schema.sql` | Database schema |
| `frontend/src/components/voice-controls.tsx` | Voice UI |
| `frontend/src/components/icon-legend.tsx` | Icon legend UI |
| `frontend/src/components/story-panel.tsx` | Story panel UI |
| `frontend/src/lib/voice-intents.ts` | Client-side intent parsing |
| `backend/nlu/engine.py` | Backend NLU |
| `backend/text_to_speech/languages.py` | TTS language config |
| `backend/speech_to_text/languages.py` | STT language config |
| `README.md` | Project overview |
| `plan.md` | Product requirements |
| `backend/MODULE2_VALIDATION_REPORT.md` | Prior validation report |

---

## Appendix B: Files Created/Modified

| File | Action | Purpose |
|------|--------|---------|
| `docs/research-protocol.md` | Created | This document |

No production code was modified.

---

## Appendix C: Final Protocol Summary

This protocol defines a between-subjects experiment with 4 conditions comparing conventional GUI interaction against progressively enriched voice-based multimodal interaction. All conditions share identical data, analytics, and task definitions. The system automatically records task-level metrics (completion, duration, voice usage) and condition-level survey data (comprehension, trust, SUS, feedback). The engineering implementation is frozen. Data collection can proceed after pilot validation confirms no participant-blocking defects.

---

## Appendix D: Research-Design Ambiguities

The following items must be resolved by the research team before participant recruitment:

1. **Participant sampling:** No target population, sample size, or recruitment strategy is specified in the repository.
2. **Condition assignment:** No randomization or balancing mechanism exists in the code. Researchers must implement assignment externally.
3. **Consent process:** No consent screen or ethics documentation is implemented.
4. **SUS scoring:** Current implementation is mathematically incorrect for standard SUS. Decide whether to fix before collection or apply correction post-hoc.
5. **Survey skip policy:** Decide whether skipping should be allowed, logged separately, or prevented.
6. **Language/browser testing:** No pre-session compatibility check exists. Researchers must verify participant devices manually.
7. **Debrief procedure:** Not implemented. Researchers must conduct debriefing externally.

---

## Appendix E: Pilot Readiness Verdict

**CONDITIONAL GO**

The engineering implementation is complete and tested. The system can support a pilot study. However, pilot success depends on researcher discipline (manual condition assignment, browser testing, observation) because some research-control features (condition locking, randomization, consent) are not implemented in the application.

**Recommended pilot sequence:**
1. Test all 4 conditions on the same device/browser.
2. Complete 1 full session per condition with a team member acting as participant.
3. Verify backend records match expected counts and values.
4. Resolve Appendix D ambiguities.
5. Begin controlled pilot with external participants.
