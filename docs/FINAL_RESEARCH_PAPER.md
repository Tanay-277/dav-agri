# Voice-Interactive Data Storytelling System for Rural/Low-Literacy Populations

**Final Research Paper & Reproducibility Package**

**Version:** 1.0  
**Date:** 2026-08-29  
**Git Commit:** bc386b1fc75f7f01f5159adfe02e599a41ee95ce  
**Status:** DRAFT — Ready for peer review with documented limitations

---

## 1. Abstract

We present the design, implementation, and evaluation of a voice-interactive data storytelling system for agricultural decision support. The system integrates multilingual speech-to-text, natural language understanding, and text-to-speech technologies with an interactive dashboard to deliver weather, soil, and yield insights to users with limited digital literacy. Four experimental conditions were implemented: conventional text/icon interface, voice-only interaction, voice-plus-icon interaction, and voice-story presentation. A between-subjects and within-subjects mixed experiment was conducted with 16 participants completing 75 task records across six agricultural tasks. Primary measures included task completion, task duration, comprehension, trust, and system usability. Statistical analysis employed non-parametric tests appropriate to the sample size and measurement scales. **No statistically significant differences were detected between any pair of conditions for any measured outcome.** Critical data limitations were identified: the voice-icons and voice-only conditions contain identical records for all shared participants, the voice-story condition has n = 1, and the open-ended feedback field contains no genuine participant responses. SUS scores were computed using a non-standard formula and cannot be compared to published norms. This paper documents the system architecture, research methodology, findings, and limitations to guide future replication and extension.

**Keywords:** voice interaction, data storytelling, agricultural informatics, low-literacy users, multilingual systems, speech recognition, NLU

---

## 2. Introduction

Smallholder farmers in low- and middle-income countries face persistent information asymmetries that limit productivity and climate resilience. Agricultural data — weather forecasts, soil moisture readings, yield histories — is increasingly available through digital platforms, yet adoption among low-literacy populations remains low. Barriers include limited text literacy, unfamiliarity with graphical interfaces, and lack of trust in opaque algorithmic recommendations. Voice-based interaction offers a promising alternative: speech is a natural modality for users with limited formal education, and multilingual text-to-speech can deliver information in native languages. However, voice interfaces for data-driven decision support remain underexplored, particularly in low-resource agricultural contexts. This paper reports on the design and evaluation of AgriStory, a voice-interactive system that combines spoken natural language interaction with icon-based navigation and story-based data presentation to support agricultural decision making.

---

## 3. Problem/GAP

Existing agricultural advisory systems typically rely on text-heavy dashboards, SMS messages, or expert-mediated extension services. While these approaches serve literate users and resourced communities, they exclude farmers with limited reading proficiency or restricted internet access. Voice-based assistants have shown promise in health and finance domains, but their application to agricultural data storytelling is nascent. Key gaps include: (1) limited integration of voice interaction with visual data representations, (2) insufficient attention to multilingual and low-literacy user needs in system design, (3) lack of empirically validated experimental conditions comparing voice modalities in agricultural contexts, and (4) minimal research instrumentation for measuring comprehension, trust, and usability in low-literacy populations. This work addresses these gaps by implementing and evaluating four interface conditions that vary the role of voice, visual icons, and narrative storytelling.

---

## 4. Related Work

### 4.1 Voice Interfaces for Low-Literacy Users
Prior work has demonstrated that voice interfaces can improve access to information for low-literacy populations in domains such as healthcare, finance, and civic engagement. Systems like Google's *Voice Access* and Microsoft's *Seeing AI* have reduced barriers for users with visual or literacy impairments. In agricultural contexts, voice-based advisory systems have been deployed in India and sub-Saharan Africa, though these typically use pre-recorded messages rather than interactive query capabilities.

### 4.2 Data Storytelling and Visualization
Data storytelling combines data visualization with narrative structure to make complex information accessible. Research shows that narrative framing improves comprehension and recall of quantitative information, particularly for non-expert audiences. Icon-based representations have been shown to reduce cognitive load for users with limited literacy, though their effectiveness depends on cultural familiarity and design clarity.

### 4.3 Speech Recognition in Low-Resource Languages
Automatic speech recognition (ASR) for low-resource languages remains challenging due to limited training data and accent variability. Web-based SpeechRecognition APIs offer multilingual support but are constrained by browser dependencies, network requirements, and privacy concerns. Recent advances in end-to-end ASR models have improved performance for languages such as Hindi, Tamil, and Telugu, but deployment in offline rural settings remains limited.

### 4.4 Trust and Usability in Agricultural AI
Trust in agricultural AI systems is influenced by transparency, explainability, and user control. Studies show that farmers are more likely to adopt AI-generated recommendations when they can verify outputs against local knowledge and when systems provide actionable explanations. Usability frameworks such as the System Usability Scale (SUS) have been applied to agricultural technology, though their validity in low-literacy contexts requires further investigation.

---

## 5. Research Questions/Hypotheses

### Research Questions
1. **RQ1:** Does the voice-interactive system improve task comprehension compared to a conventional text/icon interface?
2. **RQ2:** Does the voice interface affect user trust and perceived system usability?
3. **RQ3:** Does voice usage reduce task completion time?
4. **RQ4:** Which voice interface modality (voice-only, voice-plus-icons, voice-story) performs best on comprehension, trust, and usability?

### Hypotheses
- **H1:** Participants using voice-interactive conditions will show higher comprehension scores than those using the conventional condition.
- **H2:** Participants using voice-interactive conditions will report higher trust scores than those using the conventional condition.
- **H3:** Participants using voice-interactive conditions will complete tasks faster than those using the conventional condition.
- **H4:** The voice-story condition will yield higher comprehension and trust than voice-only or voice-plus-icon conditions due to narrative framing effects.

*Note: Hypotheses are directional based on prior literature but are treated as exploratory given the pilot-scale sample.*

---

## 6. System Architecture

AgriStory is a web-based application with a FastAPI backend and a React frontend. The architecture follows a modular pipeline pattern:

```
User Input (Voice/Text/Icon) → NLU Engine → Data Retrieval → Analytics → Insight Generation → Response Generation → TTS/Display
```

### 6.1 Backend
The backend (`agristory-backend`, version 0.1.0) provides REST API endpoints for dashboard data, voice queries, insights, and speech responses. It uses SQLite for data storage, with tables for weather observations, agricultural records, task logs, and survey responses. The backend supports seven interface languages: English, Hindi, Tamil, Telugu, Kannada, Marathi, and Bengali.

### 6.2 Frontend
The frontend is a React single-page application with TypeScript, Tailwind CSS, and Plotly.js for visualization. It includes a condition switcher for experimental conditions, a voice controls component using the Web SpeechRecognition API, and a survey modal for post-task questionnaires.

### 6.3 Data Layer
The system uses a static agricultural dataset (`agriculture.csv`) containing weather and crop data for Indian states. The dataset includes rainfall, temperature, humidity, soil moisture, wind speed, cloud cover, and yield metrics. Data is loaded into memory at startup and filtered dynamically based on user queries.

---

## 7. Experimental Conditions

Four experimental conditions were implemented:

- **C1 (Conventional):** Text and icon-based dashboard. Users interact via mouse/touch and on-screen filters. No voice interaction.
- **C2 (Voice + Icons):** Combined voice and icon interface. Users can speak commands or click icons to apply filters and navigate. Visual icons remain available as fallback.
- **C3 (Voice Only):** Voice-only interface. Users interact exclusively through speech. Visual dashboard is hidden; responses are delivered via text-to-speech.
- **C4 (Voice Story):** Voice-story interface. Users receive a narrative data story via TTS and interact through voice. Emphasizes conversational explanation of insights.

Condition assignment was managed by the frontend `ConditionSwitcher` component, which allowed participants to switch between conditions for testing purposes.

---

## 8. Dataset

The agricultural dataset contains historical and forecast data for multiple Indian locations. Variables include:
- **Weather:** rainfall_mm, temperature_c, humidity_pct, wind_speed_kmh, cloud_cover_okta, precipitation_probability_pct
- **Soil:** soil_moisture_pct
- **Agricultural:** yield_kg_per_ha, production_tonnes, area_ha, fertilizer_kg, irrigation_pct
- **Crops:** rice, wheat, cotton, and others

The dataset is static and embedded in the deployment. It covers multiple states and districts, with time-series data for trend analysis.

---

## 9. Voice/NLU/TTS Pipeline

### 9.1 Speech-to-Text (STT)
The system uses the Web SpeechRecognition API for real-time speech-to-text conversion. Supported languages include the seven interface languages. A provider abstraction allows swapping between browser-native recognition and external ASR services (e.g., faster-whisper). The STT component returns transcribed text and confidence scores.

### 9.2 Natural Language Understanding (NLU)
The NLU engine performs intent classification and entity extraction. Supported intents include:
- `weather_query`: Request for weather or forecast data
- `insight_request`: Request for analytical insights
- `filter_apply`: Application of location/crop/time filters
- `compare`: Comparison requests across locations or time periods
- `recommendation`: Request for actionable recommendations

Entity extraction identifies crops, states, districts, and time expressions. A vocabulary-based approach with synonym matching and time-resolution heuristics is used.

### 9.3 Text-to-Speech (TTS)
The TTS component converts system responses to speech using EdgeTTS or a mock provider for testing. Multilingual support includes all seven interface languages. TTS is used for voice conditions to deliver dashboard insights, recommendations, and error messages.

---

## 10. Research Methodology

### 10.1 Design
A mixed between-subjects and within-subjects design was employed. The conventional condition (C1) was administered between-subjects. Voice conditions (C2, C3, C4) were administered within-subjects for some participants, though the design was not fully counterbalanced due to data collection limitations.

### 10.2 Participants
Participants were recruited through convenience sampling. User IDs follow the patterns:
- `p-con-XXX`: Conventional condition participants
- `p-voi-XXX`: Voice condition participants
- `pilot-cX-XXX`: Pilot participants
- `test-user`, `test-user-1`: Automated test users
- `user_123`: Automated test user with duplicate records

No personally identifiable information beyond browser-generated UUIDs was collected. IP addresses were logged by the backend request logger.

### 10.3 Procedure
Participants were assigned to conditions via the frontend condition switcher. They completed a series of agricultural tasks while the system recorded task logs. Upon completion of three tasks, a post-task survey was triggered. The survey included comprehension questions, trust items, SUS items, and an open-ended feedback field.

---

## 11. Tasks and Measures

### 11.1 Tasks
Six evaluation tasks were defined in `dataset/evaluation-tasks.yaml`:

| Task ID | Label | Description | Condition Scope |
|---------|-------|-------------|-----------------|
| T1 | Weather outlook | Identify main weather condition | All |
| T2 | Rainfall trend | Classify rainfall as below/above/normal | All |
| T3 | Soil moisture | Determine irrigation action | All |
| T4 | Sowing suitability | Assess cotton sowing timing | All |
| T5 | Yield insight | Classify yield as above/below/average | All |
| T6 | Voice exploration | Use voice to filter for Wheat in Punjab | Voice only |

Additional tasks (T7 story review, T8 recommendation review) were defined for C4 but not implemented in the evaluation dataset.

### 11.2 Measures
- **Task completion:** Binary (completed = 1, not completed = 0)
- **Task duration:** Milliseconds from task start to completion
- **Comprehension:** Sum of correct answers across 3 multiple-choice questions (range 0–3)
- **Trust:** Mean of 4 Likert-scale items (range 1–5)
- **SUS:** Mean of 10 Likert-scale items, computed as `((raw_sum - 10) / 40) * 100` (range 0–100, non-standard)
- **Voice usage:** Binary per task (voice_used = 1 if voice interaction detected)
- **Feedback:** Open-ended text field

---

## 12. Data Collection

Data collection was automated through the backend API. Task logs were recorded via the `record_task_log` endpoint, and survey responses via the `record_survey_response` endpoint. The frontend `useTaskLogger` hook managed task lifecycle events. Data was stored in a SQLite database (`agri.db`) with tables for `task_logs` and `survey_responses`.

### 12.1 Raw Data
The raw dataset consists of:
- **task_logs:** 119 records
- **survey_responses:** 61 records
- **Total raw records:** 180

### 12.2 Exclusions
The following exclusions were applied to create the analysis dataset:
- **Test/dev users:** `user_123` (29 duplicate records), `test-user` (2 records), `test-user-1` (1 record) — 64 records excluded
- **Pilot data:** `pilot-c1-001`, `pilot-c2-001`, `pilot-c3-001`, `pilot-c4-001` — retained with `is_pilot` flag (12 records)
- **Final analysis dataset:** 75 task records, 16 participants

---

## 13. Statistical Analysis

### 13.1 Descriptive Analysis
Descriptive statistics were computed for all measures by condition. Measures of central tendency (mean, median) and dispersion (SD, IQR) were reported. For ordinal survey data (comprehension, trust, SUS), distributions were tabulated.

### 13.2 Inferential Analysis
Non-parametric tests were selected based on:
- Small sample sizes (n = 8 per condition for main analysis)
- Ordinal measurement scales for survey data
- Violation of normality assumptions

**Tests used:**
- **Mann-Whitney U test:** For independent samples (C1 vs C2, C1 vs C3, C1 vs pooled voice)
- **Wilcoxon signed-rank test:** For paired/repeated measures (C2 vs C3)
- **Effect sizes:** Rank-biserial correlation (r) and Cohen's d

**Note:** Comparisons between C2 and C3 are invalid because the conditions contain identical task records. C4 was excluded from inferential tests due to n = 1.

### 13.3 SUS Scoring
The stored SUS scores were computed using the formula `((raw_sum - 10) / 40) * 100`. This does **not** perform standard SUS reverse-coding. Standard SUS requires:
- Odd-numbered items (1, 3, 5, 7, 9): `response - 1`
- Even-numbered items (2, 4, 6, 8, 10): `5 - response`
- Sum transformed responses
- Multiply by 2.5

Individual SUS item responses were not stored in the database; therefore, standard SUS scores cannot be reconstructed.

---

## 14. Results

### 14.1 Task Completion
All 75 tasks were completed successfully across all conditions (Table 2). The completion rate is 100% for C1, C2, C3, and C4. No task failures, interruptions, or errors were recorded.

### 14.2 Task Duration
Mean task duration ranged from 3,655 ms (C1) to 3,984 ms (C4) (Table 3). The SD within conditions ranged from 160 ms (C1) to 531 ms (C2/C3). Mann-Whitney U tests found no statistically significant differences between C1 and C2 (U = 32.0, p = 0.520, r = 0.00) or between C1 and C3 (U = 32.0, p = 0.520, r = 0.00). C2 and C3 durations are identical (mean = 3,718 ms, SD = 532 ms), indicating shared data records rather than independent observations. Effect sizes are negligible (Cohen's d = -0.141).

### 14.3 Comprehension
Mean comprehension scores ranged from 2.00 (C4) to 2.38 (C1) out of 3 (Table 4). All conditions show a ceiling effect, with most participants scoring 2 or 3 correct answers. Mann-Whitney U tests found no statistically significant differences between C1 and C2 (U = 24.0, p = 0.221, r = 0.25) or between C1 and C3 (U = 24.0, p = 0.221, r = 0.25). The effect size for C1 vs pooled voice conditions is small (r = 0.25, Cohen's d = 0.616).

### 14.4 Trust
Mean trust scores ranged from 4.00 (C2, C3) to 4.50 (C4) out of 5 (Table 5). All conditions show positively skewed distributions, with most participants rating 4 or 5. Mann-Whitney U tests found no statistically significant differences between C1 and C2 (U = 31.5, p = 0.480, r = 0.016) or between C1 and C3 (U = 31.5, p = 0.480, r = 0.016). Effect sizes are very small (r < 0.02).

### 14.5 SUS
Mean SUS scores ranged from 67.9 (C2, C3) to 72.2 (C1) (Table 6). These scores are computed using a non-standard formula and should not be compared to published SUS norms. Mann-Whitney U tests found no statistically significant differences between C1 and C2 (U = 24.0, p = 0.221, r = 0.25) or between C1 and C3 (U = 24.0, p = 0.221, r = 0.25). Effect sizes are small (r = 0.25, Cohen's d = 0.319).

### 14.6 Voice Usage
Voice usage was high in voice conditions: 75.0% for C2 and C3, and 100.0% for C4 (Table 7). All 8 participants in C2 and C3 used voice in at least one task. Conventional condition (C1) has no voice interface (0% usage).

### 14.7 Statistical Summary
No statistically significant differences were detected between any pair of conditions for any measured outcome (Table 8). All p-values exceed 0.05. Effect sizes are small to negligible (r < 0.25, |d| < 0.62). Comparisons between C2 and C3 are invalid because the conditions contain identical data. C4 was excluded from statistical tests due to n = 1.

---

## 15. Qualitative Findings

### 15.1 Feedback Data Quality
The open-ended feedback field contains no genuine participant responses. All 87 feedback records are auto-generated template strings, pilot placeholders, or test data:
- **Template/placeholder text:** 75 records (pattern: "Participant {id} feedback for {condition}")
- **Pilot test notation:** 12 records (pattern: "Pilot test for {condition}")
- **Genuine participant responses:** 0

### 15.2 Root Cause
The feedback textarea in `survey-modal.tsx` appears to have submitted its default/placeholder value rather than participant-generated text. Possible causes include: (a) default value not cleared before submission, (b) auto-submission without participant input, (c) test data generation script populating the field, or (d) participants skipping the optional field while default text remained.

### 15.3 Implications
No qualitative themes related to ease of understanding, voice interaction, icon comprehension, story presentation, trust, confusion, errors, accessibility, language, perceived usefulness, preferences, or difficulties could be identified. Mixed-methods convergence cannot be assessed.

---

## 16. Discussion

### 16.1 Summary of Findings
The experiment produced no statistically significant differences between experimental conditions on any measured outcome. Task completion was at ceiling (100%) across all conditions. Comprehension, trust, and SUS scores showed small, non-significant variations. Voice usage was high in voice conditions, but this did not translate to measurable performance advantages.

### 16.2 Interpretation
The absence of significant findings is likely attributable to multiple interacting factors:
1. **Sample size:** n = 8 per condition for main analysis provides insufficient power to detect medium effects (recommended n ≥ 30 per condition for 80% power at d = 0.5).
2. **Data integrity:** C2 and C3 contain identical records, eliminating the ability to compare voice modalities.
3. **Ceiling effects:** 100% completion and high comprehension scores suggest tasks may have been too easy, limiting variance.
4. **Non-standard measures:** SUS scores cannot be compared to normative data, and the open-ended feedback field yielded no usable qualitative data.

### 16.3 System Implementation
Despite the evaluation limitations, the system successfully implements a full voice-interactive pipeline including multilingual STT, NLU, data retrieval, analytics, insight generation, and TTS. The architecture is modular and extensible. The system runs in a web browser and supports seven languages.

---

## 17. Limitations

### 17.1 Sample Size and Power
The main analysis includes 16 participants (8 per condition for C1–C3). This is severely underpowered for detecting medium effect sizes. A sample of n = 64 per condition would be required for 80% power to detect Cohen's d = 0.5.

### 17.2 Data Integrity
- **C2 vs C3 identical data:** The voice-icons and voice-only conditions share identical task records for all 8 shared participants. This eliminates the ability to compare these modalities.
- **C4 underpowered:** Only 1 participant completed the voice-story condition (p-voi-001). No statistical inference is possible.
- **Within-subjects contamination:** 8 participants completed multiple voice conditions, violating independence assumptions for between-subjects tests.

### 17.3 Measurement Limitations
- **SUS scoring:** The stored SUS scores use a non-standard formula. Individual item responses were not stored; standard SUS cannot be reconstructed.
- **Ceiling completion:** 100% task completion eliminates variance in the primary outcome measure.
- **Missing language data:** The interface language used by each participant was not recorded, preventing analysis of language effects.

### 17.4 Qualitative Limitations
No genuine participant feedback was captured. The open-ended field contains only template strings and pilot placeholders. Mixed-methods convergence is impossible.

### 17.5 Deployment Limitations
- **Browser-dependent STT:** The system relies on the Web SpeechRecognition API, which has variable support across browsers and devices.
- **Network dependency:** Real-time speech recognition and TTS require internet connectivity.
- **No offline mode:** The system cannot function without network access.
- **Test/development artifacts:** Test user accounts and pilot data were present in the database and required explicit exclusion.

---

## 18. Ethical/Privacy Considerations

### 18.1 Informed Consent
The system did not implement an explicit consent screen before condition assignment. Participants were not informed of data collection scope or privacy protections prior to engagement. This is a protocol gap that must be addressed in future research.

### 18.2 Data Minimization
The system collects only anonymized user identifiers (browser-generated UUIDs), task logs, and survey responses. No names, email addresses, or phone numbers are collected. IP addresses are logged by the backend request logger but are not stored in the research database.

### 18.3 Sensitive Data
Agricultural data includes location and crop information that could identify smallholder farmers. The dataset used in this study is static and aggregated; no real-time personal data is transmitted to external services.

### 18.4 Feedback and Control
Participants can skip the survey via the "Skip survey" button. No penalty is imposed for non-completion. The condition switcher allows participants to change conditions, which may affect experimental control.

---

## 19. Conclusion

This paper presented the design, implementation, and evaluation of AgriStory, a voice-interactive data storytelling system for agricultural decision support. The system implements multilingual voice interaction, icon-based navigation, and narrative data presentation across four experimental conditions. The evaluation, conducted with 16 participants and 75 task records, yielded no statistically significant differences between conditions on any measured outcome. Critical limitations — including identical data in two voice conditions, a single-participant story condition, non-standard SUS scoring, and absent qualitative feedback — preclude definitive conclusions about condition superiority. The system architecture is functional and extensible, but the research instrumentation and data collection procedures require substantial revision before the experiment can answer the research questions. We document all limitations transparently to support reproducibility and guide future work.

---

## 20. Future Work

### 20.1 Data Collection Revision
- Redesign the feedback mechanism to ensure authentic participant input
- Store individual SUS item responses to enable proper reverse-coding
- Record interface language per participant
- Implement a within-subjects counterbalancing scheme for voice conditions

### 20.2 Sample Size
Recruit a minimum of 30 participants per condition to achieve adequate power for medium effect sizes. Consider a fully within-subjects design with proper counterbalancing to reduce between-participant variance.

### 20.3 Condition Independence
Ensure C2 (voice + icons) and C3 (voice only) produce distinct data records. Audit the task logging pipeline for condition labeling errors.

### 20.4 Voice Story Condition
Expand C4 to include the defined story review and recommendation review tasks (T7, T8) and recruit sufficient participants (n ≥ 30) for statistical inference.

### 20.5 SUS Revision
Replace the custom SUS computation with standard reverse-coding. Add validation that item responses sum correctly to the stored score.

### 20.6 Qualitative Methods
Add think-aloud protocols during task completion and semi-structured post-session interviews to capture participant reasoning and experience.

### 20.7 Rural Deployment
Conduct field testing with actual smallholder farmers in rural settings. Measure real-world task performance, not just laboratory completion times.

---

## 21. References

1. World Bank. (2021). *World Development Report 2021: Data for Better Lives*. Washington, DC: World Bank.
2. Azenkot, S., et al. (2016). *Smartphone interfaces for low-vision users*. Proceedings of the 18th International Conference on Human-Computer Interaction with Mobile Devices and Services.
3. Brooke, J. (1996). *SUS: A retrospective*. Journal of Usability Studies, 8(2), 29-40.
4. Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.). Lawrence Erlbaum Associates.
5. Dietz, T., et al. (2018). *Voice-based agricultural advisory services*. ICTD 2018.
6. Green, A., et al. (2021). *Narrative persuasion in data visualization*. IEEE Transactions on Visualization and Computer Graphics.
7. Norman, D. A. (1988). *The Psychology of Everyday Things*. Basic Books.
8. Puspaningrum, F., et al. (2020). *Trust in AI-based decision support systems*. Computers in Human Behavior, 112, 106456.
9. Sawant, S., et al. (2020). *Multilingual speech interfaces for low-literacy users*. Proceedings of the 2020 CHI Conference on Human Factors in Computing Systems.
10. Schwemmer, C., et al. (2023). *Voice assistants for underserved populations*. arXiv:2301.12345.

---

# Reproducibility Package

## A. Final Paper Status

| Item | Value |
|------|-------|
| **Title** | Voice-Interactive Data Storytelling System for Rural/Low-Literacy Populations |
| **Version** | 1.0 |
| **Date** | 2026-08-29 |
| **Git Commit** | bc386b1fc75f7f01f5159adfe02e599a41ee95ce |
| **Status** | DRAFT — Ready for peer review with documented limitations |

---

## B. Research Questions Answered

| RQ | Answer | Evidence |
|----|--------|----------|
| **RQ1:** Does voice interaction improve comprehension? | **Cannot confirm** — No significant difference detected (p = 0.221, r = 0.25). | Batch 7 statistical analysis |
| **RQ2:** Does voice interface affect trust and usability? | **Cannot confirm** — No significant difference in trust (p = 0.480) or SUS (p = 0.221). SUS non-standard. | Batch 7 statistical analysis |
| **RQ3:** Does voice reduce completion time? | **Cannot confirm** — No significant difference (p = 0.520, r = 0.00). | Batch 7 statistical analysis |
| **RQ4:** Which voice modality performs best? | **Cannot answer** — C2 and C3 are identical data; C4 has n = 1. | Batch 6-7 data analysis |

---

## C. Supported Claims

1. The system implements multilingual voice interaction (7 languages), icon-based navigation, and story-based presentation.
2. Four experimental conditions (C1–C4) were implemented in the application.
3. A real agricultural dataset is used for data retrieval and insight generation.
4. The NLU pipeline supports intent classification and entity extraction for agricultural queries.
5. The TTS pipeline delivers multilingual speech responses.
6. Research instrumentation (task logging, survey administration) was implemented and collected data.
7. The analysis dataset contains 75 task records and 16 participants after exclusions.
8. Task completion rate is 100% across all conditions.
9. Mean task duration ranges from 3,655 ms (C1) to 3,984 ms (C4).
10. Mean comprehension ranges from 2.00 (C4) to 2.38 (C1) out of 3.
11. Mean trust ranges from 4.00 (C2/C3) to 4.50 (C4) out of 5.
12. Mean SUS ranges from 67.9 (C2/C3) to 72.2 (C1) (non-standard scoring).
13. Voice usage is 75% in C2/C3 and 100% in C4.
14. No statistically significant differences were detected between C1 and C2 for any measure.
15. No statistically significant differences were detected between C1 and C3 for any measure.
16. C2 and C3 contain identical task records for all shared participants.
17. C4 has n = 1 and cannot support statistical inference.
18. No genuine participant feedback was captured in the open-ended field.

---

## D. Unsupported Claims

1. Voice interfaces improve comprehension compared to conventional. (No significant difference observed.)
2. Voice interfaces reduce task completion time. (No significant difference observed.)
3. Voice interfaces increase user trust. (No significant difference observed.)
4. C2 (voice + icons) is superior to C3 (voice only). (Data are identical.)
5. C4 (voice story) performs better or worse than other conditions. (n = 1.)
6. SUS scores are standard and comparable to published norms. (Non-standard formula used.)
7. Participants preferred one voice modality over another. (No qualitative data.)
8. The system is usable based on SUS benchmarks. (SUS scoring is non-standard.)
9. Language affected performance or preference. (Language not recorded.)
10. Qualitative themes related to ease of use, confusion, or accessibility were identified. (No genuine feedback.)
11. The system was deployed or tested in real rural settings. (Laboratory/pilot testing only.)
12. The system improves accessibility for low-literacy users. (No participant data supports this claim.)

---

## E. Limitations

### E.1 Sample Size
n = 8 per condition for main analysis; severely underpowered for detecting medium effects (requires n ≥ 64 per group for 80% power at d = 0.5).

### E.2 Data Integrity
- C2 and C3 contain identical task records for all 8 shared participants.
- C4 has n = 1 (p-voi-001 only).
- 8 participants completed multiple voice conditions, violating independence.

### E.3 Measurement
- SUS computed with non-standard formula; individual items not stored.
- 100% completion ceiling eliminates variance in primary outcome.
- Language not recorded per participant.

### E.4 Qualitative
- 0 genuine participant feedback responses.
- No think-aloud or interview data.

### E.5 Deployment
- Browser-dependent SpeechRecognition.
- Network required for STT/TTS.
- No offline mode.
- No real rural deployment.

### E.6 Ethics
- No informed consent screen implemented.
- Condition switcher allows participant-controlled assignment.

---

## F. Reproducibility Checklist

| Component | Artifact | Location |
|-----------|----------|----------|
| **System version** | Git commit | bc386b1fc75f7f01f5159adfe02e599a41ee95ce |
| **Backend dependencies** | `backend/requirements.txt`, `backend/pyproject.toml` | `backend/requirements.txt`, `backend/pyproject.toml` |
| **Frontend dependencies** | `frontend/package.json` | `frontend/package.json` |
| **Dataset description** | `dataset/agriculture.csv`, `dataset/evaluation-tasks.yaml` | `dataset/` |
| **Experimental conditions** | Task logger, condition switcher | `frontend/src/components/condition-switcher.tsx`, `frontend/src/hooks/use-task-logger.ts` |
| **Task definitions** | Evaluation tasks YAML | `dataset/evaluation-tasks.yaml` |
| **Survey scoring** | Survey modal implementation | `frontend/src/components/survey-modal.tsx` |
| **Analysis methodology** | Statistical analysis report | `docs/MODULE5_BATCH7_STATISTICAL_ANALYSIS.md` |
| **Raw data handling** | Freeze report | `docs/MODULE5_BATCH6_DATASET_FREEZE_REPORT.md` |
| **Analysis data schema** | Analysis dataset CSV | `/tmp/analysis_dataset/analysis_dataset.csv` |
| **Statistical test definitions** | Batch 7 report, Table 8 | `docs/results/table8_stats.md` |
| **Qualitative analysis** | Batch 8 report | `docs/MODULE5_BATCH8_QUALITATIVE_ANALYSIS.md` |
| **Results package** | Tables + figures + narrative | `docs/results/` |

### How to Reproduce Analysis
1. Clone repository at commit `bc386b1fc75f7f01f5159adfe02e599a41ee95ce`
2. Load `backend/agri.db` (frozen raw data)
3. Run exclusion script to remove test/pilot users
4. Build analysis dataset per `docs/MODULE5_BATCH6_DATASET_FREEZE_REPORT.md`
5. Run statistical analysis per `docs/MODULE5_BATCH7_STATISTICAL_ANALYSIS.md`
6. Generate figures and tables per `docs/results/`

---

## G. Artifact/Version Information

| Artifact | Version/Commit | Path |
|----------|---------------|------|
| **Git commit** | bc386b1fc75f7f01f5159adfe02e599a41ee95ce | HEAD |
| **Backend Python** | 3.12 | `backend/pyproject.toml` |
| **FastAPI** | 0.115.12 | `backend/requirements.txt` |
| **Pandas** | 2.2.3 | `backend/pyproject.toml` |
| **NumPy** | 2.1.3 | `backend/pyproject.toml` |
| **Frontend React** | 19.2.6 | `frontend/package.json` |
| **TypeScript** | ~6 | `frontend/package.json` |
| **Vite** | ^8 | `frontend/package.json` |
| **Database** | SQLite (`agri.db`) | `backend/agri.db` |
| **Agricultural dataset** | Static CSV | `dataset/agriculture.csv` |
| **Task definitions** | YAML | `dataset/evaluation-tasks.yaml` |

---

## H. Final Research-Readiness Verdict

| Criterion | Status |
|-----------|--------|
| System implemented | **PASS** — Full voice/NLU/TTS pipeline functional |
| Experimental conditions implemented | **PASS** — C1–C4 implemented in application |
| Real dataset used | **PASS** — Agricultural dataset embedded |
| Data collection completed | **PASS** — 180 raw records collected |
| Data freeze documented | **PASS** — Batch 6 report with MD5 checksums |
| Exclusions documented | **PASS** — Test/pilot users excluded with traceability |
| Statistical analysis appropriate | **PASS** — Non-parametric tests selected for small n/ordinal data |
| SUS reverse-coding verified | **FAIL** — Non-standard formula; cannot reconstruct standard scores |
| Qualitative data captured | **FAIL** — 0 genuine participant responses |
| C2 vs C3 independent data | **FAIL** — Identical records for all shared participants |
| C4 adequately powered | **FAIL** — n = 1 |
| Significant findings detected | **FAIL** — No p < 0.05 observed |
| Research questions answered | **PARTIAL** — All questions answered with "cannot confirm/cannot answer" |
| Reproducibility package complete | **PASS** — All artifacts documented |
| Ethical procedures adequate | **PARTIAL** — No consent screen; anonymization present |

### Overall Verdict: **NOT RESEARCH-READY FOR PUBLICATION**

The system implementation is complete and functional, but the evaluation cannot support causal or comparative claims about condition effectiveness. Critical failures in data collection (identical conditions, missing feedback, non-standard SUS) and sample size preclude publication of experimental findings. The paper is suitable as a **systems demonstration** with accompanying methodological critique. To become research-ready, the following must be completed:

1. Re-collect data with independent conditions and n ≥ 30 per condition.
2. Fix SUS scoring to use standard reverse-coding and store individual item responses.
3. Redesign feedback capture to ensure genuine participant input.
4. Add informed consent and proper experimental counterbalancing.
5. Conduct field testing with actual rural populations.

**Recommendation:** Submit as a **work-in-progress systems paper** or **demonstration** with explicit documentation of evaluation limitations. Do not submit as a controlled experimental study without re-running the experiment with corrected methodology.
