# Module 5 — Batch 6: Research Dataset Freeze & Analysis Dataset

**Generated:** 2026-08-29T05:24:31.304257
**Database:** `/workspaces/dav-agri/backend/agri.db`

---

## 1. Raw Data Record Counts

| Layer | Table | Count |
|-------|-------|-------|
| RAW | task_logs | 119 |
| RAW | survey_responses | 61 |
| RAW | **Total** | **180** |

Raw data has been exported to `/tmp/frozen_raw_data/` and is **not modified**.

## 2. Analysis Dataset Record Count

**Analysis dataset records:** 87
**Unique participants:** 20
**Conditions:** conventional, voice-icons, voice-only, voice-story
**Tasks:** rainfall_trend, soil_moisture, sowing_suitability, voice_exploration, weather_outlook, yield_insight

Analysis dataset exported to: `/tmp/analysis_dataset/analysis_dataset.csv`
MD5 checksum: `4cf8d8739456ad85cd6e540fe0ec5ebc`

## 3. Exclusions

### Test/dev user
- **Affected user IDs:** test-user, test-user-1, user_123
- **Task logs excluded:** 32
- **Survey responses excluded:** 32

**Total excluded task logs:** 32
**Total excluded survey responses:** 32
**Total excluded raw records:** 64

### Pilot Data Decision

Pilot participants (4 users) retained in analysis dataset with is_pilot flag. They completed 3 tasks each across 4 conditions. Can be excluded via `is_pilot == False` for main analysis.
- Pilot users: pilot-c1-001, pilot-c2-001, pilot-c3-001, pilot-c4-001
- Pilot participants: 4

## 4. Missing Data

- **Records without survey:** 0
- **Language field:** Not recorded in database (`NULL` for all records)
- **Records with errors:** 0
- **Duration implausible:** 0 (outside 1s–10min range)

## 5. SUS Handling

### 5.1 Frontend Implementation (Current)

The frontend (`survey-modal.tsx`) computes SUS as:
```javascript
const susSum = susRatings.reduce((a, b) => a + b, 0)
const susScore = Math.round(((susSum - 10) / 40) * 100)
```

This formula **does NOT perform standard SUS reverse-coding**.

### 5.2 Standard SUS Transformation (Required)

| Step | Odd items (1,3,5,7,9) | Even items (2,4,6,8,10) |
|------|----------------------|------------------------|
| Transform | response - 1 | 5 - response |
| Range after transform | 0–4 | 0–4 |

Final score: `sum(transformed responses) * 2.5` → range 0–100

### 5.3 Impact Assessment

- **Stored values are non-standard:** Stored sus_score uses non-standard formula: ((raw_sum - 10) / 40) * 100. No reverse-coding applied. Individual SUS item responses not stored; standard SUS score cannot be reconstructed from existing data.
- **Cannot reconstruct standard SUS:** Individual item responses are not stored in the database.
- **Recommendation:** Future data collection must store all 10 individual SUS item responses to enable proper scoring.
- **Analysis use:** Existing `sus_score` values can be used as a relative indicator within this dataset, but should NOT be treated as standard SUS scores.

## 6. Participant × Condition × Task Verification

### 6.1 Expected vs Actual Task Coverage

| Condition | Expected Tasks | Actual Tasks | Missing | Unexpected |
|-----------|---------------|--------------|---------|------------|
| conventional | 5 | 6 | — | voice_exploration |
| voice-icons | 6 | 6 | — | — |
| voice-only | 6 | 6 | — | — |
| voice-story | 5 | 5 | — | — |

### 6.2 Anomalies

- conventional: unexpected ['voice_exploration']

### 6.3 Integrity Issues

| User ID | Condition | Task ID | Issue |
|---------|-----------|---------|-------|
| p-con-002 | conventional | voice_exploration | Task voice_exploration not in expected set for conventional |
| p-con-004 | conventional | voice_exploration | Task voice_exploration not in expected set for conventional |

## 7. Final Data Dictionary

| Field | Type | Description | Source | Missing Handling |
|-------|------|-------------|--------|------------------|
| participant_id | string | Anonymized user identifier | task_logs.user_id | Never missing (excluded if test) |
| condition | string | Experimental condition | task_logs.condition | Never missing |
| task_id | string | Task identifier | task_logs.task_id | Never missing |
| completed | integer | 1 if task completed, 0 otherwise | task_logs.completed | Never missing |
| duration_ms | integer | Task duration in milliseconds | task_logs.duration_ms | Missing = NULL |
| voice_used | integer | 1 if voice was used, 0 otherwise | task_logs.voice_used | Never missing |
| error | string | Error message if any | task_logs.error | NULL if no error |
| session_timestamp | datetime | Record creation timestamp | task_logs.created_at | Never missing |
| comprehension_score | integer | 0–3 correct answers | survey_responses.comprehension_score | NULL if no survey |
| trust_score | integer | Mean trust rating (1–5) | survey_responses.trust_score | NULL if no survey |
| sus_score | integer | SUS score (0–100, non-standard) | survey_responses.sus_score | NULL if no survey |
| language | string | Interface language used | **NOT RECORDED** | Always NULL |
| feedback | string | Open-ended participant feedback | survey_responses.feedback | NULL if no survey |
| is_pilot | boolean | True for pilot participants | Derived from user_id prefix | Never missing |
| duration_plausible | boolean | True if 1s ≤ duration ≤ 10min | Derived | False if outside range |
| has_error | boolean | True if error is not NULL | Derived | False if error is NULL |
| has_survey | boolean | True if survey data present | Derived | False if no survey |

## 8. Transformations Log

| Step | Transformation | Rationale |
|------|----------------|-----------|
| 1 | Excluded `user_123`, `test-user`, `test-user-1` | Automated test/dev data; `user_123` has 29 identical duplicate records |
| 2 | Merged condition-level surveys | `survey_responses` with `task_id IS NULL` joined on `(user_id, condition)` |
| 3 | Added `is_pilot` flag | Users with ID prefix `pilot-` identified as pilot participants |
| 4 | Added `duration_plausible` flag | Values outside 1,000–600,000 ms flagged as implausible |
| 5 | Added `has_error` flag | Derived from non-NULL `error` field |
| 6 | Added `has_survey` flag | Derived from non-NULL `comprehension_score` |
| 7 | Set `language = NULL` | Language not recorded in backend database |
| 8 | Renamed `created_at` → `session_timestamp` | Align with requested field name |

## 9. DATA FREEZE VERDICT

| Criterion | Status |
|-----------|--------|
| Raw records frozen | PASS — 180 records exported unmodified |
| Test/dev data excluded | PASS — 64 records excluded |
| Analysis dataset built | PASS — 87 records, 20 participants |
| Participant × Condition × Task verified | CONDITIONAL — see §6 anomalies |
| SUS reverse-coding verified | FAIL — application does not perform standard SUS reverse-coding |
| Missing data documented | PASS — see §4 |
| Traceability preserved | PASS — raw exports retained; exclusions logged |

**Overall Verdict: CONDITIONAL PASS**

The dataset is fit for analysis with documented caveats:
1. SUS scores are not standard SUS. Use as relative indicator only.
2. `language` field is missing and must be added manually if needed.
3. Two conventional-condition records contain `voice_exploration` task (data entry anomaly).
4. Pilot data is included and flagged; exclude via `is_pilot == False` for main analysis.
