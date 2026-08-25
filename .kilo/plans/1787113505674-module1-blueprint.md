# Module 1 Research Blueprint — PI Review and Integration

## Document Control

| Version | Date | Author | Status |
|---|---|---|---|
| 1.0 | 2026-08-19 | Principal Investigator | Final — Ready for Module 2 |

## Branch

All research deliverables are tracked on `research/personas-scope-mvrs`.

---

## Executive Summary

This document integrates all Module 1 deliverables into a single coherent research blueprint. It verifies internal consistency across problem statement, research gap, questions, hypotheses, literature, users, use cases, MVP, architecture, data, and evaluation. It identifies contradictions, unsupported claims, missing requirements, and risks. It then produces the **final** Module 1 artifacts and defines Module 2 prerequisites.

**Bottom line:** The project is **feasible** and **methodologically sound** for a student research project, provided that three open questions are resolved before full-scale evaluation. The core contribution is **not** the combination of voice + icons + storytelling, but the **empirical validation of their synergistic effect on comprehension and decision accuracy among low-literacy rural farmers** — a population that has been largely absent from HCI/visualization research.

---

## 1. Consistency Verification

### 1.1 Problem Statement ↔ Research Gap ↔ RQs

| Element | Statement | Consistent? |
|---|---|---|
| Problem | Low-literacy farmers cannot use conventional dashboards | Yes |
| Gap | No system integrates voice + icon + storytelling for agricultural analytics | Yes |
| RQ1 | Comprehension improvement vs. conventional | Directly addresses gap |
| RQ2 | Multimodal configuration effects on trust/usability | Addresses gap |
| RQ3 | Linguistic features for voice | Supports gap but **overly broad** |
| RQ4 | Rule-based storytelling engine | Addresses gap but **may be out of scope** |
| RQ5 | Longitudinal data literacy change | **Postponed** — requires multi-session study |

**Finding:** RQ3 and RQ5 are legitimate research questions but are **not testable in the current MVRS**. RQ3 requires linguistic expertise and dialect-specific ASR models. RQ5 requires a longitudinal design that conflicts with the 45–60 minute session constraint. These should be **explicitly deferred** to Module 2 or a follow-up study.

### 1.2 Hypotheses ↔ Metrics ↔ Evaluation

| Hypothesis | Metric | Experiment | Feasible? |
|---|---|---|---|
| H1: Comprehension improvement | Comprehension score (quiz) | A vs. D comparison | Yes |
| H2: Trust/SUS improvement | Trust score, SUS | A vs. D comparison | Yes |
| H3: Narrative decisions better than statistics | Decision accuracy | A vs. D comparison | Yes |
| H4: Literacy moderation | Comprehension × literacy group | 4-condition ANOVA | Yes |

**Finding:** All four hypotheses are **operationalizable** with the defined metrics and experimental design. No contradictions found.

### 1.3 MVP ↔ Architecture ↔ Evaluation

| MVRS Feature | Architecture Component | Evaluation Use |
|---|---|---|
| Conventional dashboard | Frontend: Plotly charts | Condition A baseline |
| Voice input | `use-voice-input.ts` + Web Speech API | Conditions B/C/D |
| Voice output | `use-voice-output.ts` + `speechSynthesis` | Conditions B/C/D |
| Icon legend | `lib/icons/` + `icon-legend.tsx` | Conditions C/D |
| Story panel | `insights/engine.py` + `story-panel.tsx` | Condition D |
| A/B switcher | `condition-switcher.tsx` | Randomization |
| Task logger | `use-task-logger.ts` + `/research/task-log` | Dependent variable |
| Survey | `survey-modal.tsx` + `/research/survey` | Dependent variable |

**Finding:** Every MVP feature has a clear architecture implementation and evaluation purpose. No orphaned features.

### 1.4 Data Requirements ↔ Dataset ↔ Evaluation Tasks

| Required Variable | Current Dataset | Evaluation Task Coverage |
|---|---|---|
| Rainfall | ✅ Synthetic (600 rows) | T1, T2, T4 |
| Temperature | ✅ Synthetic | T1, T4 |
| Humidity | ✅ Synthetic | T1 |
| Soil moisture | ✅ Synthetic | T3, T4 |
| Yield | ✅ Synthetic | T5 |
| Crop/state/district | ✅ Synthetic | T6 |
| Story/recommendations | ✅ Rule-based engine | T7, T8 |
| Forecast | ❌ Postponed | T1 uses historical trend |

**Finding:** Data requirements are **met for MVRS** except forecast data, which is explicitly postponed. Evaluation tasks align with available data. **Risk:** Synthetic data lacks real-world noise; must be documented as limitation.

---

## 2. Contradictions and Inconsistencies

### 2.1 Identified Contradictions

| # | Contradiction | Severity | Resolution |
|---|---|---|---|
| 1 | **Forecast data**: Use cases T1 ("Weather outlook (3-day forecast)") requires forecast data, but Section 9 of application scope explicitly postpones forecast integration. | High | **Resolved in evaluation protocol:** T1 is redefined to use historical trend instead of forecast. Must be explicit in all documents. |
| 2 | **LLM storytelling**: SRS NFR-17 says "every recommendation must include explanation" but does not require LLM. However, `insights/engine.py` imports `GeminiClient` and the evaluation protocol mentions "AI-powered story generation" as a condition. | Medium | **Resolved:** Remove AI condition from evaluation. Keep Gemini as transparent fallback only. Evaluation tests rule-based engine. |
| 3 | **Offline capability**: Architecture plan claims "offline-capable" but Web Speech API requires internet in some browsers (Safari). Frontend `use-voice-input.ts` does not check connectivity before starting recognition. | Low | **Documented limitation:** Chrome/Edge required for full offline voice. Safari requires internet for STT. |

### 2.2 Unnecessary Features

| Feature | Justification for Removal | Status |
|---|---|---|
| **Pest/disease risk indication** (secondary use case #4) | Not in primary decision problem; requires domain-specific thresholds not in current dataset | **Defer to Module 2** |
| **Market price context** (secondary use case #3) | Explicitly excluded from scope (no mandi integration) | **Remove from use cases list** |
| **Data literacy micro-assessment** (secondary use case #9) | Already covered by pre/post quiz in evaluation | **Consolidate into evaluation** |
| **PDF/JSON export** (MVP feature) | Utility feature, not required for hypothesis testing | **Downgrade to optional** |

### 2.3 Unsupported Claims

| Claim | Source | Issue | Resolution |
|---|---|---|---|
| "Multimodal presentation reduces cognitive load" | Mayer (2009) | General multimedia learning, not specifically tested for low-literacy agricultural contexts | **Caveat already noted** in research analysis. Must not overstate in publications. |
| "Voice interfaces improve accessibility for limited literacy" | Luger & Sellen (2016) | Study focused on blind/visually impaired users, not low-literacy sighted users | **Caveat already noted.** Empirical validation with target users is the project's contribution. |
| "Data storytelling improves comprehension" | Segel & Heer (2010); Chen et al. (2024) | Journalism/education contexts, not agricultural decision-making | **Caveat already noted.** This project tests the claim in the agricultural domain. |

**Finding:** No unsupported claims were found that lack prior caveats. The research analysis document already appropriately flags these as requiring validation.

---

## 3. Missing Requirements

### 3.1 Functional Requirements

| Missing Requirement | Rationale | Priority |
|---|---|---|
| **FR-32: Facilitator override** | During evaluation, facilitator must be able to advance tasks, mark failures, and record qualitative notes without using the system UI. | Must have (for evaluation) |
| **FR-33: Task timer display** | Participants should see a progress indicator (e.g., "Task 2 of 4") to reduce anxiety. | Should have |
| **FR-34: Consent recording** | System must record consent status (yes/no/partial) linked to user ID for audit trail. | Must have (IRB requirement) |
| **FR-35: Facilitator login/dashboard** | Separate interface for facilitator to manage participants, assign conditions, and view live task status. | Should have |
| **FR-36: Data export for research** | Bulk export of task logs and survey responses in anonymized CSV/JSON for analysis. | Must have |

### 3.2 Non-Functional Requirements

| Missing Requirement | Rationale | Priority |
|---|---|---|
| **NFR-23: Browser compatibility matrix** | Explicitly document which browsers/versions are supported and which features degrade. | Must have |
| **NFR-24: Facilitator training materials** | Scripts, checklists, and certification criteria for data collection consistency. | Must have |
| **NFR-25: IRB compliance checklist** | Specific items required by institutional review board (consent, privacy, data handling). | Must have |

---

## 4. Technical Risks

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| **Web Speech API accuracy too low for analysis** | Medium | High | Select Chrome/Edge only; pilot WER testing; add clarification prompts | Backend + Frontend |
| **Synthetic data not representative** | High | Medium | Document limitations; supplement with expert validation; avoid overgeneralization | Data |
| **Frontend bundle size** | High | Low | Code splitting, dynamic imports (already identified) | Frontend |
| **SQLite concurrency** | Low | Low | Single-user research tool; acceptable | Backend |
| **Icon recognition failure** | Medium | Medium | Wizard-of-Oz validation with 5 users before study | Design |
| **Condition leakage** (participants discover other conditions) | Medium | Medium | Between-subjects design; physical separation during study | Evaluation |
| **Facilitator inconsistency** | Medium | Medium | Standardized scripts, training, certification | Evaluation |

### 4.1 Risk Register Update

The architecture implementation plan's risk register is **incomplete**. It omits:
- Participant recruitment risk
- IRB approval delays
- Dataset validity risk
- Voice recognition accuracy risk

**Action:** Update risk register in architecture implementation plan before Module 2.

---

## 5. Research Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Low recruitment** | High | High | Partner with 2–3 NGOs; offer incentives; recruit from extension offices |
| **High attrition** | Medium | Medium | Keep sessions <60 min; flexible scheduling; track dropouts |
| **Learning transfer** (within-subjects) | Medium | Medium | Use between-subjects for primary analysis |
| **Confounding variables** (device, environment, facilitator) | Medium | Medium | Standardize setup; same facilitator; quiet environment |
| **Pilot reveals fundamental usability issue** | Low | High | Pilot with 5–8 per condition; budget 2 weeks for iteration |
| **Effect size smaller than expected** | Medium | High | Increase sample size; use ANCOVA to increase power |

---

## 6. Scope-Creep Risks

| Risk | Trigger | Boundary |
|---|---|---|
| **Adding real forecast data** | "We need realistic tasks" | Postponed to Module 3. Historical trends are sufficient for hypothesis. |
| **Adding LLM-based storytelling** | "Rule-based stories are too simple" | Keep as transparent fallback only. Evaluation tests rule-based engine. |
| **Adding user accounts** | "We need to track progress over time" | Out of scope for MVRS. Single-device, single-session design. |
| **Adding mobile app** | "Users want it on their phones" | Web app is sufficient for research. Native apps deferred to production. |
| **Expanding to additional crops/states** | "We need more generalizability" | Current 8 crops/8 states are sufficient for hypothesis testing. |
| **Adding government schemes/mandi prices** | "Users asked for it" | Explicitly out of scope per SRS Section 6. |

---

## 7. Traceability Matrix

### 7.1 Full Traceability: RQ → Hypothesis → Feature → Experiment → Metric → Evidence

| RQ | Hypothesis | System Feature | Experiment | Metric | Expected Evidence |
|---|---|---|---|---|---|
| **RQ1** | H1 | Conventional dashboard (Condition A) | Between-subjects: A vs. D | Comprehension score (quiz) | Mean score D > A, p < 0.05, Cohen's d ≥ 0.5 |
| **RQ1** | H1 | Voice + icon + story (Condition D) | Between-subjects: A vs. D | Task completion rate | Completion rate D > A by ≥20% |
| **RQ1** | H1 | A/B condition switcher | Within/between-subjects | Time to answer | Median time D ≤ A (faster or equal) |
| **RQ2** | H2 | Voice-only (B), Voice+Icons (C), Voice+Story (D) | ANOVA: A vs. B vs. C vs. D | Trust score, SUS score | Mean D > A, B, C on trust/SUS |
| **RQ2** | H2 | Survey modal (SUS + trust scale) | Post-session questionnaire | SUS score | SUS D ≥ 75 (above average usability) |
| **RQ3** | — | Multilingual selector (8 languages) | Cross-linguistic comparison | WER, comprehension by language | WER < 20% for all supported languages |
| **RQ3** | — | Language-specific voice prompts | Subgroup analysis | Comprehension by language | No significant difference across languages |
| **RQ4** | — | Rule-based story engine | System evaluation | Story quality rubric | ≥80% of stories rated "clear" and "actionable" by experts |
| **RQ5** | — | Pre/post literacy quiz | Paired t-test | Data literacy change | Mean post > pre, p < 0.05 |

**Note:** RQ3 and RQ5 are **not testable in the current MVRS** and are deferred to Module 2.

### 7.2 Feature-to-Requirement Traceability

| Feature | FR | NFR | RQ | Hypothesis |
|---|---|---|---|---|
| Microphone button | FR-01 | NFR-06 | RQ1 | H1 |
| Continuous STT | FR-02 | NFR-03 | RQ1 | — |
| Language selector | FR-06 | NFR-21 | RQ3 | — |
| Intent parser | FR-08 | NFR-01 | RQ1 | — |
| Entity extraction | FR-09 | NFR-01 | RQ1 | — |
| Confirmation handling | FR-11 | NFR-09 | RQ1 | — |
| Clarification handling | FR-12 | NFR-09 | RQ1 | — |
| Unknown question handling | FR-13 | NFR-09 | RQ1 | — |
| Dataset loading | FR-14 | NFR-05 | — | — |
| Filtered data retrieval | FR-15 | NFR-01 | RQ1 | — |
| KPI computation | FR-16 | NFR-01 | RQ1 | — |
| Chart transformation | FR-17 | NFR-06 | RQ1 | — |
| Insight generation | FR-18 | NFR-17 | RQ1 | H3 |
| Story generation | FR-19 | NFR-17 | RQ2 | H3 |
| Icon rendering | FR-20 | NFR-06 | RQ1 | — |
| Icon highlighting | FR-21 | NFR-06 | RQ2 | — |
| Simple mode | FR-22 | NFR-08 | RQ1 | — |
| TTS narration | FR-23 | NFR-03 | RQ1 | H1 |
| TTS controls | FR-24 | NFR-06 | RQ1 | — |
| Response length enforcement | FR-25 | NFR-08 | RQ1 | — |
| Context buffer | FR-26 | NFR-01 | RQ2 | — |
| Context reset | FR-27 | NFR-09 | RQ1 | — |
| Data error handling | FR-28 | NFR-05 | RQ1 | — |
| Voice error handling | FR-29 | NFR-05 | RQ1 | — |
| Offline operation | FR-30 | NFR-01 | RQ1 | — |
| Degraded mode | FR-31 | NFR-04 | RQ1 | — |
| A/B switcher | — | NFR-19 | RQ1, RQ2 | H1, H2 |
| Task logger | — | NFR-15 | RQ1 | H1 |
| Survey modal | — | NFR-15 | RQ2 | H2 |

---

## 8. Final Module 1 Artifacts

### 8.1 Final Problem Statement

Smallholder farmers and rural communities in low- and middle-income countries generate and depend upon agricultural and weather data, yet they remain systematically underserved by conventional data-driven decision-support systems. The barrier is not data availability or analytical accuracy, but **accessibility, comprehension, and actionability**: how can agricultural and weather insights be delivered in a form that low-literacy users can understand, trust, and act upon?

### 8.2 Final Research Gap

No existing system integrates **voice interaction**, **icon-based visual anchoring**, and **narrative data storytelling** into a unified interface specifically designed for agricultural/weather analytics among low-literacy rural users. This absence is critical because each component addresses a distinct barrier, but their synergistic effect has never been empirically tested in this domain.

### 8.3 Final Research Questions

| ID | Question | Status |
|---|---|---|
| **RQ1** | To what extent does voice + icon + storytelling improve comprehension vs. conventional dashboards? | **Primary — Testable in MVRS** |
| **RQ2** | How do multimodal configurations affect trust, usability, and decision confidence? | **Primary — Testable in MVRS** |
| **RQ3** | What linguistic/paralinguistic features maximize comprehension? | **Deferred — Requires Module 2** |
| **RQ4** | Can a rule-based engine generate accurate narratives without cloud LLMs? | **System quality — Not a research question** |
| **RQ5** | How does repeated exposure affect data literacy over time? | **Deferred — Requires longitudinal design** |

**Revised RQ set for MVRS:**
1. **RQ1:** Does the proposed system improve comprehension and decision accuracy compared to a conventional dashboard?
2. **RQ2:** What is the relative contribution of each modality (voice, icons, storytelling) to trust and usability?

### 8.4 Final Hypotheses

| ID | Hypothesis | Test |
|---|---|---|
| **H1** | Low-literacy users using voice + icon + story will have significantly higher comprehension scores than conventional dashboard users. | Independent samples t-test (A vs. D), α = 0.05 |
| **H2** | Voice + icon + story will yield higher trust and SUS scores than conventional. | Independent samples t-test (A vs. D) |
| **H3** | Narrative explanations will lead to more accurate decisions than isolated statistics. | Mediation analysis: narrative → comprehension → decision accuracy |
| **H4** | Literacy level moderates system effectiveness; lowest-literacy users benefit most. | Moderation analysis (PROCESS or regression) |

### 8.5 Final MVP Specification

**In scope (Must have):**
1. Conventional dashboard (Plotly charts, filters, KPIs)
2. Voice input (Web Speech API, 8 languages)
3. Voice output (speechSynthesis, 0.9x rate)
4. Icon legend (13 semantic SVG icons)
5. Story panel (rule-based narrative)
6. Recommendations panel (rule-based actions)
7. A/B condition switcher (4 conditions)
8. Task logger (completion, time, voice usage)
9. Survey modal (comprehension quiz, trust, SUS)
10. 600-row synthetic dataset
11. Simple mode toggle
12. Accessibility (ARIA, reduced-motion)

**Out of scope (Explicitly excluded):**
1. Real-time forecast data
2. LLM-based storytelling (Gemini) in evaluation
3. User authentication
4. Mobile native apps
5. E-commerce/mandi prices
6. Government schemes
7. IoT/satellite data
8. PWA offline mode
9. Longitudinal tracking
10. Dialect-specific models

### 8.6 Final Architecture

**Layers (unchanged from technical architecture plan):**
1. Frontend: React + Vite + TypeScript + Tailwind + Plotly
2. Voice Interface: Web Speech API (STT + TTS)
3. Intent Parser: Client-side TypeScript (regex + token matching)
4. API Layer: FastAPI + `/api/v1` prefix
5. Data Layer: CSV → Pandas DataFrame (in-memory cache)
6. Analytics Layer: Pandas-based KPIs + chart transformation
7. Insights/Story Layer: Rule-based engine + optional Gemini fallback
8. Logging Layer: SQLite (task_logs, survey_responses, insight_history)
9. Visualization Layer: Plotly.js + custom SVG icons + IconAnchor

**Key architectural decisions:**
- **No backend STT/TTS** — browser-native only (simplifies deployment, works offline in Chrome/Edge)
- **Rule-based story engine as primary** — deterministic, explainable, offline-capable
- **SQLite for research logs** — embedded, zero-configuration, sufficient for single-user research
- **API versioning** — `/api/v1` prefix for future compatibility

### 8.7 Final Evaluation Plan

**Design:** Between-subjects randomized controlled trial
**Conditions:** A (conventional), B (voice-only), C (voice+icons), D (voice+icons+story)
**Primary comparison:** A vs. D
**Secondary:** B vs. C vs. D (multimodal decomposition)

**Participants:**
- P1: Low-literacy farmers (primary)
- P2: Semi-literate farmers (secondary)
- P3: Extension workers (secondary)

**Sample size:** 40 per condition for A vs. D (N=80); 30 per condition for 4-condition (N=120)

**Tasks:** 8 tasks from `dataset/evaluation-tasks.yaml` (T1–T8)

**Metrics:**
- Primary: Comprehension score, task completion rate, decision accuracy
- Secondary: Trust score, SUS, time to answer, interaction steps, error rate, NASA-TLX
- Voice quality: WER (diagnostic only)

**Analysis:**
- H1/H2: Independent samples t-test (A vs. D)
- H3: Mediation analysis
- H4: Moderation analysis (condition × literacy)
- Secondary: One-way ANOVA (4 conditions), post-hoc Tukey HSD

---

## 9. Module-2 Prerequisites

These items must be completed before full-scale evaluation can begin:

| # | Prerequisite | Owner | Dependency |
|---|---|---|---|
| 1 | **IRB/ethics approval** | PI | Must be secured before recruitment |
| 2 | **Real dataset acquisition** | Data team | Replace synthetic data with IMD or NASA POWER data |
| 3 | **Icon validation study** | Design team | Wizard-of-Oz with 5–10 target users |
| 4 | **Pilot study** | Evaluation team | 20–32 participants, 2 weeks |
| 5 | **Power analysis with pilot data** | Statistician | Finalize sample size |
| 6 | **Facilitator training and certification** | Evaluation team | 2–3 practice sessions |
| 7 | **Recruitment partnerships** | PI | MOUs with 2–3 local NGOs/extension offices |
| 8 | **Consent forms finalized** | PI + IRB | Plain language + icon versions |
| 9 | **Task rubric validation** | Domain expert + 2 raters | Cohen's κ ≥ 0.75 |
| 10 | **WER baseline measurement** | Backend team | Test STT accuracy with target languages/accent |

---

## 10. Open Questions (Must Be Resolved Before Implementation)

| # | Question | Impact if Unresolved | Recommended Resolution |
|---|---|---|---|
| 1 | **What is the actual WER for Web Speech API in target languages/accents?** | Voice interaction may be unusable, invalidating the entire intervention. | Pilot test with 10 native speakers per language. If WER > 30%, add clarification prompts or switch to backend STT. |
| 2 | **Do target users recognize the proposed icons?** | Icon-anchored narration fails; multimodal benefit disappears. | Wizard-of-Oz validation: show icons to 10 users, ask for labels. Redesign icons with <80% recognition. |
| 3 | **Is the synthetic dataset sufficiently realistic?** | External validity threatened; reviewers may reject findings. | Acquire real historical data OR conduct extensive expert validation of synthetic data. Document limitations transparently. |
| 4 | **What is the minimal viable task set?** | Session too long → fatigue; too short → insufficient data. | Pilot with 8 tasks; if completion < 30%, reduce to 4 tasks. |
| 5 | **Should the study be between-subjects or within-subjects?** | Learning transfer confounds results; recruitment burden differs. | **Decision: Between-subjects for primary analysis.** Within-subjects optional for follow-up. |
| 6 | **How to handle participants who cannot complete any tasks?** | Attrition bias; missing data. | Pre-screen for minimum ability; have "facilitator-assisted" category; use intention-to-treat analysis. |
| 7 | **What is the correct agronomic answer for each task?** | Invalid metrics; meaningless results. | Expert review by 2 agronomists; inter-rater reliability κ ≥ 0.75. |
| 8 | **Should the system support wake-word activation?** | Always-on microphone raises privacy concerns; manual button may be cumbersome. | **Decision: No for MVRS.** Manual button is sufficient and avoids privacy issues. |

---

## 11. Risk Summary for PI Decision

| Category | Risk | Severity | Mitigation Status |
|---|---|---|---|
| **Technical** | STT accuracy too low | **High** | Needs pilot validation (Open Question 1) |
| **Technical** | Synthetic data validity | **Medium** | Document limitations; seek real data |
| **Research** | Icon recognition failure | **Medium** | Wizard-of-Oz validation planned |
| **Research** | Small effect size | **Medium** | Power analysis with pilot data |
| **Research** | Recruitment delays | **High** | Partner with multiple NGOs |
| **Scope** | Feature creep (forecast, LLM) | **Medium** | Explicitly deferred; documented |
| **Ethical** | IRB delays | **High** | Submit early; have contingency timeline |

---

## 12. PI Sign-Off

**Module 1 is approved for progression to Module 2** subject to resolution of Open Questions 1, 2, 3, and 7, and completion of Prerequisites 1 (IRB) and 7 (recruitment partnerships).

The research design is **rigorous, feasible, and appropriately scoped** for a student research project. The experimental contribution — **empirical validation of voice + icon + storytelling synergy for low-literacy agricultural decision-making** — is precisely defined, testable, and non-trivial.

**PI Concerns:**
1. The project has accumulated significant engineering infrastructure (backend, frontend, voice, icons, logging). This is appropriate for a systems-oriented research project, but the **research contribution must be clearly distinguished from the engineering contribution** in all publications.
2. RQ4 (rule-based engine) is a **system quality requirement**, not a research question. It should be reframed as "The system uses a deterministic, explainable rule-based engine to ensure reproducibility and offline capability" rather than a testable hypothesis.
3. RQ5 (longitudinal data literacy) is **postponed**, not answered. Publications must not imply longitudinal findings.

**Next steps:**
1. Resolve open questions via pilot studies (4–6 weeks).
2. Secure IRB approval (2–4 weeks, parallel).
3. Finalize real dataset acquisition (2–4 weeks).
4. Proceed to Module 2: Pilot Study and Refinement.

---

## 13. Document Index

| Document | Location | Status |
|---|---|---|
| Research Analysis | `.kilo/plans/1787113505674-research-analysis.md` | Final |
| Structured Literature Review | `.kilo/plans/1787113505674-structured-literature-review.md` | Final |
| User Personas and Tasks | `.kilo/plans/1787113505674-user-personas-and-tasks.md` | Final |
| Voice Interaction Model | `.kilo/plans/1787113505674-voice-interaction-model.md` | Final |
| Icon Storytelling Language | `.kilo/plans/1787113505674-icon-storytelling-language.md` | Final |
| Software Requirements Specification | `.kilo/plans/1787113505674-software-requirements-specification.md` | Final |
| Requirements Traceability Matrix | `.kilo/plans/1787113505674-requirements-traceability-matrix.md` | Final |
| Technical Architecture | `.kilo/plans/1787113505674-technical-architecture.md` | Final |
| Architecture Implementation Plan | `.kilo/plans/1787113505674-architecture-implementation-plan.md` | Final |
| Application Scope and MVRS | `.kilo/plans/1787113505674-application-scope-mvrs.md` | Final |
| Data Strategy and Evaluation Methodology | `.kilo/plans/1787113505674-data-strategy-evaluation-methodology.md` | Final |
| Evaluation Protocol | `.kilo/plans/1787113505674-evaluation-protocol.md` | Final |
| Consent Form | `.kilo/plans/1787113505674-consent-form.md` | Final |
| Statistical Analysis Template | `.kilo/plans/1787113505674-statistical-analysis-template.Rmd` | Final |
| Evaluation Tasks Dataset | `dataset/evaluation-tasks.yaml` | Final |
| **Module 1 Blueprint (This Document)** | `.kilo/plans/1787113505674-module1-blueprint.md` | **Final** |
