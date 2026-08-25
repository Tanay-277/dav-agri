# Data Strategy and Experimental Evaluation Methodology

## Branch

All research deliverables are tracked on `research/personas-scope-mvrs`.

---

## 1. Data Strategy

### 1.1 Dataset Inventory

| Dataset | Purpose | MVRS Status |
|---|---|---|
| Weather data | Current conditions, trends, forecasts | Synthetic placeholder (600 rows) |
| Historical data | Trend analysis, season comparison | Synthetic placeholder (600 rows) |
| Forecast data | Future-looking queries | **Postponed** — not in MVRS |
| Agricultural context data | Crop-specific recommendations | Synthetic placeholder (600 rows) |
| Voice/query dataset | NLU training, intent coverage | Collected during evaluation |
| Evaluation tasks | Structured user study protocol | Designed in Section 3 |

### 1.2 Weather Data

| Property | Specification |
|---|---|
| **Required fields** | timestamp, location (state, district), rainfall_mm, temperature_c, humidity_pct, soil_moisture_pct, wind_speed_kmh, cloud_cover_okta |
| **Source requirements** | Station-level or gridded reanalysis data. For MVRS: synthetic data with realistic seasonal correlations. For production: IMD (India Meteorological Department) open data, or NASA POWER API. |
| **Data format** | CSV or Parquet with datetime index. Columns normalized to snake_case. |
| **Update frequency** | Daily for operational use. Static for MVRS research dataset. |
| **Licensing** | IMD data: Open Government Data — generally CC-BY or public domain. Verify specific dataset license before publication. NASA POWER: public domain. Synthetic data: no restrictions. |
| **Preprocessing** | - Parse dates to datetime[ns, UTC]  - Normalize column names via alias map  - Handle missing values: forward-fill for weather stations, interpolation for reanalysis  - Aggregate to daily resolution if source is hourly  - Validate: rainfall >= 0, temperature within [-10, 60]°C, humidity in [0, 100] |

### 1.3 Historical Data

| Property | Specification |
|---|---|
| **Required fields** | date, state, district, crop, yield_kg_per_ha, production_tonnes, area_ha, fertilizer_kg, irrigation_pct |
| **Source requirements** | Ministry of Agriculture & Farmers Welfare (India) — "Agriculture Statistics at a Glance" or state agricultural departments. For MVRS: synthetic data modeled on published averages. |
| **Data format** | CSV with one row per (date, state, district, crop) tuple. |
| **Update frequency** | Annual for yield/production. Seasonal for crop-specific records. |
| **Licensing** | Government of India data: typically public domain. Verify specific state-level datasets. |
| **Preprocessing** | - Align dates to financial/agricultural year (April–March) or calendar year  - Normalize crop names to controlled vocabulary (8 crops in MVRS)  - Validate: yield > 0, production <= yield * area (sanity check)  - Impute missing fertilizer/irrigation with district-level medians |

### 1.4 Forecast Data

| Property | Specification |
|---|---|
| **Required fields** | forecast_date, location, rainfall_probability_pct, temperature_min_c, temperature_max_c, wind_speed_kmh, humidity_pct, precipitation_mm |
| **Source requirements** | OpenWeatherMap Forecast API, IMD forecast API, or local meteorological service. **Postponed post-MVRS.** |
| **Data format** | JSON from API, normalized to same schema as historical weather. |
| **Update frequency** | 3-hourly or daily. |
| **Licensing** | API-specific. OpenWeatherMap: commercial license, free tier available. IMD: check current terms. |
| **Preprocessing** | - Convert probability from categorical (rain/no rain) to percentage  - Smooth noisy daily forecasts with moving average  - Align forecast horizon to system-supported range (3-day, 7-day) |

### 1.5 Agricultural Context Data

| Property | Specification |
|---|---|
| **Required fields** | crop, state, district, season (Kharif/Rabi/Zaid), soil_type, optimal_rainfall_mm, optimal_temperature_c, pest_risk_thresholds |
| **Source requirements** | ICAR (Indian Council of Agricultural Research) crop handbooks, state agricultural universities, extension service bulletins. |
| **Data format** | Reference tables (CSV or YAML). Static, rarely updated. |
| **Update frequency** | As-needed when crop varieties or recommendations change. Typically every 3–5 years. |
| **Licensing** | Government publications: public domain. Verify ICAR data policies. |
| **Preprocessing** | - Normalize crop/state/district names to match weather/historical datasets  - Encode thresholds as structured rules (if-else or JSON rules)  - Translate agronomic jargon to plain language for storytelling engine |

### 1.6 Voice/Query Dataset

| Property | Specification |
|---|---|
| **Required fields** | transcript, language, intent, entities, confidence, condition, user_id, timestamp, success |
| **Source requirements** | Collected during user evaluation. No pre-existing dataset. |
| **Data format** | JSONL or CSV. One record per voice interaction turn. |
| **Update frequency** | Continuous during study. Batch-export after each session. |
| **Licensing** | Participant consent required. Anonymized storage. No voice recordings stored (transcripts only). |
| **Preprocessing** | - Strip PII from transcripts  - Normalize language codes to BCP-47  - Map intents to canonical taxonomy  - Calculate WER (Word Error Rate) against manual transcription if needed |

### 1.7 Evaluation Tasks

| Property | Specification |
|---|---|
| **Required fields** | task_id, task_label, required_data, correct_answer, success_criteria, estimated_duration_s |
| **Source requirements** | Designed by research team based on user personas and use cases. |
| **Data format** | YAML or JSON. Version-controlled in repository. |
| **Update frequency** | Static for study. Iterate between pilot and full deployment. |
| **Licensing** | N/A — internal research artifact. |
| **Preprocessing** | - Validate that each task can be answered with available dataset  - Pilot with 3–5 users to calibrate difficulty  - Ensure tasks cover all core use cases (weather, rainfall, soil moisture, yield, recommendation) |

---

## 2. Experimental Evaluation Design

### 2.1 Research Questions and Hypotheses Mapping

| ID | Research Question / Hypothesis | Evaluation Metric(s) |
|---|---|---|
| RQ1 | Does voice + icon + storytelling improve comprehension vs. conventional dashboard? | Comprehension score, task completion rate |
| H1 | Voice + icon + story users will have significantly higher comprehension scores than conventional users. | Comprehension score (quiz), decision accuracy |
| H2 | Voice + icon + story condition will yield higher trust and decision confidence than other conditions. | Trust score, SUS score |
| H3 | Narrative form leads to better agricultural decisions than isolated statistics. | Decision accuracy, task completion rate |
| H4 | System effectiveness is moderated by literacy level. | Comprehension score stratified by literacy |

### 2.2 Conditions (Independent Variable)

| Condition | Description | Research Purpose |
|---|---|---|
| **A: Conventional** | Text-and-chart dashboard only. No voice, no icons beyond default chart legends, no story panel. | Baseline |
| **B: Voice-only** | Voice input + TTS output. No icon legend, no story panel. | Isolate voice effect |
| **C: Voice + Icons** | Voice input + TTS + icon legend + simple mode. No story panel. | Isolate icon effect |
| **D: Voice + Icons + Story** | Voice input + TTS + icon legend + story panel + recommendations. **Full proposed system.** | Full intervention |

**Primary comparison:** A vs. D (conventional vs. proposed system)
**Secondary comparisons:** B vs. C vs. D (decompose multimodal effects)

### 2.3 Measurable Metrics (Dependent Variables)

| Metric | Definition | Measurement Method | RQ / Hypothesis |
|---|---|---|---|
| **Task completion rate** | Proportion of tasks completed successfully | Binary success/failure per task | RQ1, H1 |
| **Comprehension score** | % correct on post-task quiz (3–5 multiple-choice questions per task) | Quiz administered after each task block | RQ1, H1, H4 |
| **Decision accuracy** | Agreement between user's decision and agronomist-validated correct answer | Expert rubric scoring of open-ended or multiple-choice decisions | H3 |
| **Time to answer** | Seconds from task presentation to user response | Automated timer in UI | RQ1 |
| **Number of interaction steps** | Count of user actions (voice turns, button taps, filter changes) to complete task | Automated event logging | RQ1 |
| **Error rate** | Proportion of failed interactions (misrecognitions, wrong filters, abandoned tasks) | Automated logging + manual annotation | RQ1 |
| **User satisfaction (SUS)** | System Usability Scale score (0–100) | Post-study questionnaire | H2 |
| **Trust score** | Mean of 4 Likert items (1–5) on trust, reliance, explainability, confidence | Post-study questionnaire | H2 |
| **Cognitive burden (NASA-TLX)** | 6-item NASA Task Load Index (mental demand, physical demand, time pressure, performance, effort, frustration) | Post-task questionnaire | RQ1 (optional) |
| **Voice recognition accuracy** | Word Error Rate (WER) of STT transcripts vs. manual transcription | Manual transcription of subset + automated WER calculation | N/A — voice quality diagnostic |
| **Data literacy change** | Pre/post difference in visualization literacy quiz score | Pre- and post-study quiz | RQ5 |
| **Condition preference** | Which condition did the user prefer and why? | Exit interview | H2 |

### 2.4 Control Variables

| Variable | Control Method |
|---|---|
| **Dataset** | All conditions use the same filtered dataset for each task. |
| **Task order** | Counterbalanced using Latin square design to minimize learning/fatigue effects. |
| **Device type** | Fixed: Android smartphone or desktop (consistent within study). |
| **Browser** | Chrome or Edge (Web Speech API support required). |
| **Language** | Fixed per participant based on preference; same language across all conditions. |
| **Session duration** | Maximum 60 minutes per participant to limit fatigue. |
| **Facilitator** | Same facilitator for all sessions; standardized script. |
| **Environment** | Quiet room, consistent lighting, no distractions. |

### 2.5 Experimental Tasks

Tasks are designed to cover the 8 core use cases and map directly to RQs.

| Task ID | Use Case | Required Data | Correct Answer | Success Criterion |
|---|---|---|---|---|
| T1 | Weather outlook (3-day forecast) | Forecast data (postponed; use historical trend) | Identify dominant condition (rain/sun/cloud) | Correct condition selected |
| T2 | Rainfall trend (30 days) | Past 30 days rainfall | "Below normal" / "Above normal" / "Normal" | Correct classification |
| T3 | Soil moisture status | Current soil moisture | "Irrigate" or "Do not irrigate" | Correct action |
| T4 | Sowing/harvesting suitability | Soil + forecast | "Sow" / "Wait" / "Harvest" | Correct action |
| T5 | Crop-specific yield insight | Yield for selected crop/period | Above/below/same as average | Correct classification |
| T6 | Voice-driven data exploration | Filters (crop, state, date) | Correct crop/state/date selected | Filters match intent |
| T7 | Automated story review | Story panel | Summarize main recommendation in 1 sentence | Key recommendation present |
| T8 | Recommendation review | Recommendations panel | Select top priority action | Correct action selected |

**Note:** For MVRS, T1 uses historical trend instead of forecast (forecast data postponed).

### 2.6 Participant Groups

| Group | Description | Inclusion Criteria | Exclusion Criteria |
|---|---|---|---|
| **P1: Low-literacy farmers** | Primary user group. 0–6 years formal education. | Age 18–65, rural residence, agriculture as primary income, owns or uses smartphone. | Literate beyond functional level (>10 years education). |
| **P2: Semi-literate farmers** | Secondary user group. 7–12 years formal education. | Same as P1, but with some secondary education. | None specific. |
| **P3: Extension workers** | Tertiary user group. Intermediate literacy, tech-comfortable. | Agricultural extension background, smartphone user. | None specific. |

**Primary analysis:** P1 only (low-literacy farmers).
**Secondary analysis:** P1 + P2 + P3 (moderation by literacy level, H4).

### 2.7 Sample Size Considerations

| Analysis | Required N | Justification |
|---|---|---|
| **Primary (A vs. D, P1 only)** | 40 per condition (80 total) | Medium effect size (Cohen's d = 0.5), α = 0.05, power = 0.80, two-tailed t-test. |
| **Secondary (4 conditions, P1 only)** | 30 per condition (120 total) | ANOVA with 4 groups, medium effect size (f = 0.25), α = 0.05, power = 0.80. |
| **Full factorial (4 conditions × 3 groups)** | 20 per cell (240 total) | 4 × 3 ANOVA. Minimum 15–20 per cell for ANOVA robustness. |
| **Pilot** | 5–8 per condition | Detect major usability issues, calibrate task difficulty. |

**Recruitment strategy:**
- Partner with local agricultural NGOs, self-help groups, or extension offices.
- Screen for literacy using a 3-item literacy checklist (read a sentence, interpret a chart, write a sentence).
- Offer modest incentive (mobile data voucher, seeds, or cash equivalent ~₹200–₹500 per session).

### 2.8 Experimental Procedure

**Total session duration:** 45–60 minutes per participant.

```
1. INFORMED CONSENT (5 min)
   - Explain purpose, risks, benefits
   - Audio recording consent (if any)
   - Right to withdraw at any time

2. PRE-SESSION QUESTIONNAIRE (5 min)
   - Demographics: age, education, occupation
   - Literacy self-assessment
   - Smartphone/voice experience
   - Pre-study data literacy quiz (5 items)

3. BASELINE CONDITION (10 min)
   - Randomly assign to Condition A, B, C, or D
   - Brief tutorial on condition interface (1–2 min)
   - Participant completes 4 tasks from the task set

4. POST-BASELINE SURVEY (5 min)
   - NASA-TLX (cognitive burden)
   - Condition-specific SUS and trust items
   - Short open-ended feedback

5. CROSSOVER / SECOND CONDITION (10 min) [optional — within-subjects design]
   - If within-subjects: participant uses second condition
   - Counterbalance condition order (A→D or D→A)
   - Different task set to minimize learning transfer

6. POST-SESSION SURVEY (5 min)
   - Full SUS, trust scale
   - Preference ranking (which condition preferred?)
   - Exit interview (3–5 open-ended questions)

7. DEBRIEF (5 min)
   - Explain study purpose
   - Answer questions
   - Provide contact information
```

**Design choice:**
- **Between-subjects** is preferred for naive participants to avoid learning transfer.
- **Within-subjects** can be used for experienced users or in a follow-up study.
- **Mixed design:** Between-subjects for primary comparison (A vs. D), within-subjects for secondary (B, C, D decomposition).

### 2.9 Baseline System

**Condition A (Conventional Dashboard):**
- Existing Plotly.js charts (line, bar, scatter, heatmap, pie)
- Filter dropdowns (crop, state, district, date range)
- KPI cards with numeric values and change percentages
- Insights panel with text-only insights
- No voice interaction, no icon legend, no story panel, no recommendations panel
- Responsive design, accessible via keyboard

This is the **exact current dashboard** minus voice/story/icon components.

### 2.10 Statistical Analysis Plan

#### Primary Analysis

| Hypothesis | Test | Variables |
|---|---|---|
| H1: Comprehension improvement | Independent samples t-test (A vs. D) or ANCOVA (controlling for pre-literacy) | IV: Condition (A vs. D). DV: Comprehension score. Covariate: Pre-study literacy score. |
| H2: Trust/SUS improvement | Independent samples t-test (A vs. D) | IV: Condition. DV: Trust score, SUS score. |
| H3: Narrative decisions better than statistics | Independent samples t-test (D vs. A) on decision accuracy | IV: Condition. DV: Decision accuracy (% correct). |
| H4: Literacy moderation | Moderation analysis (PROCESS or linear regression) | IV: Condition. Moderator: Literacy level. DV: Comprehension score. |

#### Secondary Analysis

| Analysis | Test | Variables |
|---|---|---|
| Multimodal decomposition | One-way ANOVA (A vs. B vs. C vs. D) | IV: Condition (4 levels). DV: Comprehension, trust, SUS. Post-hoc: Tukey HSD. |
| Task difficulty effects | Mixed ANOVA | Within-subjects: Task (8 levels). Between-subjects: Condition. DV: Completion rate, time. |
| Voice accuracy impact | Correlation / regression | IV: WER. DV: Comprehension, task completion. |
| Literacy group differences | One-way ANOVA | IV: Literacy group (P1, P2, P3). DV: Comprehension, SUS. |
| Time-to-answer | Survival analysis or ANOVA | IV: Condition. DV: Time to answer (seconds). Censor: abandoned tasks. |

#### Assumptions and Checks

- **Normality:** Shapiro-Wilk test on continuous DVs. Transform or use non-parametric tests if violated.
- **Homogeneity of variance:** Levene's test. Use Welch's t-test if violated.
- **Outliers:** Winsorize at 5th/95th percentiles or use robust regression.
- **Multiple comparisons:** Bonferroni or FDR correction for secondary analyses.

#### Missing Data

- **Participant dropouts:** Intention-to-treat principle. Replace missing with condition mean (conservative) or use multiple imputation.
- **Missing task responses:** Exclude from task-level analysis; include in condition-level if >50% tasks completed.
- **Incomplete surveys:** Exclude from SUS/trust analysis; include in task analysis.

#### Software

- **Analysis:** R (tidyverse, lme4, emmeans) or Python (scipy, statsmodels, pingouin).
- **Visualization:** ggplot2 or matplotlib.
- **Reproducibility:** R Markdown / Jupyter notebook with fixed random seeds.

---

## 3. Dataset Specifications for MVRS

### 3.1 Current Synthetic Dataset (`dataset/agriculture.csv`)

| Field | Type | Range | Notes |
|---|---|---|---|
| date | date | 2022-01-01 to 2024-12-31 | Generated with seasonal patterns |
| state | categorical | 8 states | |
| district | categorical | 5 districts per state | |
| crop | categorical | 8 crops | |
| rainfall | float | 0–250 mm | Seasonal: higher in monsoon |
| temperature | float | 15–40 °C | Seasonal: higher in summer |
| humidity | float | 30–90 % | Correlated with rainfall |
| soil_moisture | float | 10–50 % | Derived from humidity + rainfall |
| yield | int | 150–700 kg/ha | Correlated with rainfall |
| production | int | 200–5000 tonnes | Derived from yield × area |
| area | float | 50–500 ha | Random uniform |
| fertilizer | float | 80–250 kg | Random uniform |
| irrigation | float | 30–90 % | Random uniform |

**Limitations:** Synthetic data lacks real-world noise, measurement error, and agronomic complexity. **Must be replaced or supplemented with real data before publication.**

### 3.2 Evaluation Task Dataset (`dataset/evaluation-tasks.yaml`)

```yaml
tasks:
  - id: T1_weather_outlook
    label: "Weather outlook"
    use_case: "weather_outlook"
    required_data: ["rainfall", "temperature", "humidity"]
    correct_answer: "rain"
    success_criterion: "user_identifies_dominant_condition"
    estimated_duration_s: 60

  - id: T2_rainfall_trend
    label: "Rainfall trend"
    use_case: "rainfall_trend"
    required_data: ["rainfall"]
    correct_answer: "below_normal"
    success_criterion: "correct_classification"
    estimated_duration_s: 90

  # ... 6 more tasks
```

---

## 4. Data Governance and Ethics

### 4.1 Consent

- Written informed consent required for all participants.
- Consent form must specify: data collected (transcripts, survey responses, interaction logs), retention period (6 months), deletion procedure, no-voice-recording policy.
- For low-literacy participants: verbal consent with witness signature; use simplified consent form with icons.

### 4.2 Anonymization

- **User ID:** Random UUID stored in `localStorage`. No PII linked.
- **Transcripts:** Strip names, village names, phone numbers before storage.
- **Logs:** No IP addresses stored (backend already excludes them).
- **Surveys:** No name, age, or exact village recorded. Age range only.

### 4.3 Data Retention

- Research data retained for 6 months post-study.
- Deletion via SQLite `DELETE` + `VACUUM`.
- Participants can request deletion at any time via facilitator.

### 4.4 Data Sharing

- Aggregate statistics only in publications. No individual-level data.
- Code and synthetic datasets released under MIT license.
- Real datasets (if used) released under original license with attribution.

---

## 5. Validation and Pilot Testing

### 5.1 Pilot Study (n = 5–8 per condition)

**Purpose:** Detect major usability issues, calibrate task difficulty, estimate variance.

**Procedure:**
1. Run 2–3 participants per condition.
2. Record: completion rate, time, errors, verbal feedback.
3. Adjust:
   - Tasks that are too hard (>80% failure) → simplify
   - Tasks that are too easy (<20% failure) → increase difficulty
   - Voice commands not recognized → add synonyms to intent parser
   - Icons not recognized → redesign

### 5.2 Inter-Rater Reliability

- For open-ended decision tasks: 2 independent raters score 20% of responses.
- Calculate Cohen's kappa. Target: κ ≥ 0.75.
- If κ < 0.75, refine rubric and rater training.

### 5.3 Manipulation Check

- After each session, ask: "Which features did you notice?" (multiple choice: voice, icons, story, charts, none).
- Verify participants in Condition D actually used voice + icons + story.
- Exclude participants who did not engage with their assigned condition.

---

## 6. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Low literacy participants cannot complete tasks | Medium | High | Simplify tasks; add facilitator assistance; pilot extensively. |
| Voice recognition accuracy too low for analysis | Medium | High | Select Chrome/Edge; test WER in pilot; add clarification prompts. |
| Recruitment delays | High | Medium | Partner with multiple NGOs; offer incentives; recruit from extension offices. |
| Dataset not representative of target region | Medium | Medium | Document limitations; supplement with expert validation; avoid overgeneralization. |
| Learning transfer in within-subjects design | Medium | Medium | Use between-subjects for primary analysis; counterbalance order. |
| Attrition bias | Low | Medium | Keep sessions short (<60 min); offer flexible scheduling; track dropouts by condition. |
| COVID / field access restrictions | Low | High | Have remote/phone-based backup protocol. |

---

## 7. Deliverables

| Deliverable | Format | Timeline |
|---|---|---|
| Evaluation protocol document | PDF | Before pilot |
| Task dataset (YAML) | Code file | Before pilot |
| Consent forms (plain language + icon versions) | PDF | Before pilot |
| Raw data (anonymized) | JSONL / CSV | After study |
| Analysis code | R Markdown / Jupyter | After study |
| Statistical results | Tables + plots | After study |
| Research report | PDF / conference paper | After analysis |
| Synthetic dataset release | CSV + documentation | With publication |

---

## 8. Next Steps

1. **Finalize evaluation tasks** with domain expert review (agronomist).
2. **Pilot test** with 5–8 users per condition.
3. **Refine** tasks, icons, and voice commands based on pilot feedback.
4. **Power analysis** using pilot variance estimates.
5. **IRB / ethics approval** — secure before full deployment.
6. **Recruit** participants through local partners.
7. **Run** full study with monitoring for protocol deviations.
8. **Analyze** and report.
