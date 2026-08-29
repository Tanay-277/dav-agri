# Module 2 Pilot Study and Refinement Plan

## Document Control

| Version | Date | Author | Status |
|---|---|---|---|
| 1.0 | 2026-08-19 | Principal Investigator | Draft for Review |

## Branch

All research deliverables are tracked on `research/personas-scope-mvrs`.

---

## 1. Objectives

1. Resolve all 8 open questions from Module 1 Blueprint
2. Validate system usability with target users
3. Estimate effect sizes for power analysis
4. Identify critical usability issues before full-scale evaluation
5. Finalize evaluation protocol and materials

**Go/No-Go criteria:** Proceed to full study only if:
- WER ≤ 25% for ≥2/3 target languages
- Icon recognition ≥ 70% for ≥10/13 icons
- ≥3/8 tasks completable without facilitator assistance
- No critical usability blockers (session abandonment > 20%)

---

## 2. Participant Recruitment

### 2.1 Sample Size

| Group | N | Rationale |
|---|---|---|
| Pilot participants | 20–24 | 3–4 per condition (A/B/C/D) |
| Icon validation | 10 | Separate from pilot |
| WER testing | 10 | Separate from pilot |

### 2.2 Inclusion Criteria

- Age 25–65
- Primary occupation: farming or agricultural labor
- Maximum formal education: ≤ 8th grade
- Fluent in one of: Hindi, Kannada, Tamil, Telugu, Marathi, Bengali
- Owns or regularly uses a smartphone

### 2.3 Exclusion Criteria

- Visual impairment uncorrectable by glasses
- Hearing impairment uncorrectable by hearing aid
- Prior participation in system design or evaluation

### 2.4 Recruitment Channels

| Channel | Target N | Notes |
|---|---|---|
| Local NGO partner farms | 10–12 | Partner with 2–3 NGOs |
| Agricultural extension offices | 6–8 | Through government programs |
| Farmer producer organizations (FPOs) | 4–6 | FPO meetings as recruitment venues |

---

## 3. Session Protocol

### 3.1 Setup

- Facilitator + 1 participant per session
- Quiet room with table and chair
- Device: Android smartphone or tablet (Chrome browser)
- Screen recording enabled (with consent)
- Audio recording enabled (with consent)

### 3.2 Session Flow (60 minutes)

| Time | Activity | Data Collected |
|---|---|---|
| 0–5 min | Welcome, consent (verbal + signed) | Consent status |
| 5–10 min | Demographic + literacy questionnaire | Age, education, literacy self-rating |
| 10–15 min | Tutorial (condition-specific) | Facilitator notes |
| 15–45 min | Task completion (4 tasks) | Task logs, time, voice usage, screen recording |
| 45–55 min | Survey (comprehension quiz, trust, SUS) | Survey responses |
| 55–60 min | Debrief, open feedback | Qualitative notes |

### 3.3 Task Assignment

Each participant completes **4 tasks** (randomly selected from T1–T8, avoiding duplicates):

| Task ID | Use Case | Difficulty |
|---|---|---|
| T1 | Weather outlook | Low |
| T2 | Rainfall trend | Low |
| T3 | Soil moisture | Medium |
| T4 | Sowing suitability | Medium |
| T5 | Yield insight | High |
| T6 | Filter by crop/state | Low |
| T7 | Story understanding | Medium |
| T8 | Recommendation | High |

**Counterbalancing:** Tasks presented in random order; conditions assigned randomly.

---

## 4. Data Collection Plan

### 4.1 Quantitative Data

| Measure | Source | Format |
|---|---|---|
| Task completion (pass/fail) | Facilitator observation + system log | Binary |
| Time to completion | System log | Seconds |
| Voice usage | System log | Boolean |
| Comprehension score | Quiz responses | 0–4 per task |
| Trust score | Survey | Likert 1–5 |
| SUS score | Survey | 0–100 |
| NASA-TLX | Survey | 0–100 |
| Error rate | Facilitator observation + logs | Count |
| Interaction steps | System log | Count |

### 4.2 Qualitative Data

| Source | Collection Method |
|---|---|
| Facilitator notes | Standardized template after each session |
| Screen recording | Review for usability issues |
| Audio recording | WER analysis, voice interaction quality |
| Post-session interview | 5-minute open-ended debrief |

---

## 5. Open Question Resolution

### 5.1 OQ1: WER for Target Languages

**Method:** Separate testing session with 10 native speakers
**Protocol:** Read 20 standardized agricultural sentences; record via Web Speech API
**Metric:** Word Error Rate (WER) = (S + D + I) / N
**Success criteria:**
- WER ≤ 20% for ≥5/8 languages → proceed with current approach
- WER 20–30% for ≥5/8 languages → add clarification prompts
- WER > 30% for majority → evaluate backend STT (Whisper)

### 5.2 OQ2: Icon Recognition

**Method:** Show each of 13 icons to 10 participants; ask "What does this mean?"
**Metric:** Recognition rate per icon
**Success criteria:**
- ≥80% recognition for ≥10/13 icons → proceed
- <80% for critical icons (rain, temperature, yield) → redesign
- <80% for ≥6 icons → full icon set redesign

### 5.3 OQ3: Synthetic Data Realism

**Method:** Expert validation by 2 agronomists
**Protocol:** Show 20 random rows; ask "Is this realistic?" + specific anomalies
**Metric:** Binary realism rating + qualitative feedback
**Decision:** If >3 critical anomalies found, replace with real data or adjust generation rules

### 5.4 OQ4: Minimal Viable Task Set

**Method:** Track completion rates during pilot
**Success criteria:**
- ≥70% completion for 4 tasks → 4-task set is viable
- <70% completion → reduce to 3 tasks or add facilitator scaffolding

### 5.5 OQ5: Between-Subjects vs. Within-Subjects

**Method:** Compare learning transfer effects
**Analysis:** If within-subjects participants show >15% improvement in second condition, use between-subjects for full study

### 5.6 OQ6: Handling Non-Completers

**Method:** Track reasons for non-completion
**Decision rules:**
- Literacy barrier → pre-screen more strictly
- Technical barrier → fix before full study
- Motivation barrier → shorten session or increase incentives

### 5.7 OQ7: Agronomic Answer Validation

**Method:** Expert review of all 8 task rubrics
**Metric:** Inter-rater reliability (Cohen's κ)
**Success criteria:** κ ≥ 0.75 between 2 agronomists

### 5.8 OQ8: Wake-Word Activation

**Method:** Test both manual button and "Hey AgriStory" wake word
**Metric:** Privacy concerns (qualitative), activation accuracy, false positives
**Decision:** If privacy concerns high OR accuracy < 80%, proceed with manual button only

---

## 6. Success Criteria

### 6.1 System Readiness

| Criterion | Threshold |
|---|---|
| App crashes during session | 0 |
| Critical bugs (data not loading, voice not working) | ≤ 1 |
| Screen recording failures | ≤ 2 |
| Backend errors (500s) | 0 |

### 6.2 Usability

| Criterion | Threshold |
|---|---|
| Task completion rate (any condition) | ≥ 60% |
| Session completion rate | ≥ 80% |
| Average SUS score | ≥ 50 |
| Facilitator-reported frustration episodes | ≤ 3 per session |

### 6.3 Voice Quality

| Criterion | Threshold |
|---|---|
| WER (primary language) | ≤ 25% |
| Users who report voice as "helpful" | ≥ 50% |

---

## 7. Risk Mitigation

| Risk | Mitigation |
|---|---|
| Low recruitment | Partner with 3+ NGOs; offer ₹200–300 incentive per session |
| Device compatibility issues | Test 3 device types before sessions; bring backup tablet |
| Language mismatch | Confirm language preference during screening |
| Facilitator inconsistency | Standardized script; 2 practice sessions; video review |
| Participant dropout | Flexible scheduling; same-day rescheduling option |

---

## 8. Deliverables

| Deliverable | Owner | Due |
|---|---|---|
| Pilot dataset (anonymized) | Evaluation team | After last session |
| WER analysis report | Backend team | Week 2 |
| Icon recognition report | Design team | Week 2 |
| Usability bug list | Frontend team | Week 2 |
| Revised task rubrics | Domain expert | Week 3 |
| Power analysis | Statistician | Week 3 |
| Revised evaluation protocol | PI | Week 4 |
| Go/No-Go recommendation | PI | Week 4 |

---

## 9. Timeline

| Week | Activity |
|---|---|
| 1 | Recruit participants; finalize facilitator training |
| 2 | Conduct pilot sessions (8–10 participants) |
| 3 | Conduct remaining pilot sessions (12–14 participants); begin analysis |
| 4 | Complete analysis; resolve critical issues; decide Go/No-Go |

---

## 10. Dependencies

| Dependency | Owner | Status |
|---|---|---|
| IRB approval (if required for pilot) | PI | Needed before Week 2 |
| Real dataset or validated synthetic data | Data team | Needed before Week 2 |
| Backend deployment for testing | Backend team | Needed before Week 1 |
| Frontend build for devices | Frontend team | Needed before Week 1 |
| Facilitator training materials | Evaluation team | Needed before Week 1 |
| Icon assets finalized | Design team | Needed before Week 1 |

---

## 11. Module 2 → Module 3 Transition Criteria

Proceed to Module 3 (Full-Scale Evaluation) only if:

1. All critical bugs resolved
2. WER acceptable for primary languages
3. Icon recognition ≥ 70% for critical icons
4. Task completion rate ≥ 60%
5. Power analysis confirms feasible sample size
6. IRB approval secured
7. Real dataset acquired or synthetic data limitations documented

---

## 12. Document Index

| Document | Location | Status |
|---|---|---|
| Module 1 Blueprint | `.kilo/plans/1787113505674-module1-blueprint.md` | Final |
| Evaluation Protocol | `.kilo/plans/1787113505674-evaluation-protocol.md` | Final |
| Evaluation Tasks | `dataset/evaluation-tasks.yaml` | Final |
| **Module 2 Pilot Plan (This Document)** | `.kilo/plans/1787113505674-module2-pilot-study-plan.md` | **Draft** |
