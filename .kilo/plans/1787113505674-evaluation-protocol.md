# Evaluation Protocol: Voice-Interactive Data Storytelling System

## Document Control

| Version | Date | Author | Status |
|---|---|---|---|
| 0.1 | 2026-08-19 | Research Team | Draft |

## Branch

All research deliverables are tracked on `research/personas-scope-mvrs`.

---

## 1. Purpose

This document defines the step-by-step procedure for evaluating the Voice-Interactive Data Storytelling System against a conventional dashboard baseline. It is designed for use by facilitators conducting field or lab-based user studies with rural, low-literacy participants.

---

## 2. Equipment and Setup

### 2.1 Required Equipment

- Android smartphone (minimum 4GB RAM, Chrome browser) OR desktop computer with Chrome/Edge
- Quiet, well-lit room with minimal distractions
- Backup power source (if in field)
- Mobile data voucher or Wi-Fi for internet-dependent features
- Consent forms (paper + digital)
- Incentive items (data vouchers, seeds, or cash equivalent)

### 2.2 Software Setup

1. Open browser to study URL (e.g., `https://agristory.vercel.app` or local `http://localhost:5173`)
2. Clear browser cache and localStorage
3. Set device language to participant's preferred language
4. Test microphone permissions in browser settings
5. Verify dataset loads correctly (600+ rows visible)
6. Test voice input/output functionality

### 2.3 Facilitator Checklist

- [ ] Consent form ready (plain language + icon version)
- [ ] Demographics questionnaire loaded
- [ ] Task sheets printed (one per condition)
- [ ] Stopwatch/timer available
- [ ] Audio recording device (if consented)
- [ ] Backup device available
- [ ] Participant ID log ready

---

## 3. Participant Screening

### 3.1 Literacy Screening

Use the following 3-item checklist to categorize participants:

1. **Reading:** "Please read this sentence: 'Today the rain will come.'"
   - Can read independently: **literate**
   - Needs help or cannot read: **low-literate**

2. **Chart interpretation:** Show a simple bar chart with 2 bars. Ask: "Which bar is taller?"
   - Correct answer: **semi-literate or higher**
   - Incorrect answer or no response: **low-literate**

3. **Writing:** "Please write your name and your village name."
   - Can write both: **literate**
   - Can write name only: **semi-literate**
   - Cannot write either: **low-literate**

**Classification:**
- **P1 (Low-literate):** Cannot read sentence or interpret chart
- **P2 (Semi-literate):** Can read sentence but not chart, or vice versa
- **P3 (Extension worker):** Can do both + has agricultural background

### 3.2 Inclusion Criteria

- Age 18–65
- Rural residence
- Agriculture as primary or significant income source
- Owns or regularly uses a smartphone
- Speaks one of the supported languages (English, Hindi, Tamil, Telugu, Kannada, Marathi, Bengali)

### 3.3 Exclusion Criteria

- Formal education beyond 12th grade (for P1/P2 groups)
- No smartphone experience
- Cognitive impairment affecting task completion
- Prior exposure to the AgriStory system (to avoid learning bias)

---

## 4. Session Procedure

### 4.1 Welcome and Consent (5 minutes)

**Facilitator script:**

"Hello. My name is [facilitator]. I am working with a team that is building a new tool to help farmers get weather and crop information easily. We would like your help in testing this tool. The session will take about 45 minutes. You will receive [incentive] for your time. Your responses are anonymous. You can stop at any time. Do you have any questions?"

**Consent steps:**
1. Explain study purpose in simple language
2. Explain what data is collected (transcripts, survey responses, interaction logs)
3. Explain that voice is not recorded, only text transcripts are stored
4. Explain retention period (6 months) and deletion procedure
5. Obtain verbal consent for low-literate participants (witness signature)
6. Obtain written consent for literate participants

### 4.2 Pre-Session Questionnaire (5 minutes)

Administer via tablet/paper:

**Demographics:**
- Age range: 18–25 / 26–35 / 36–45 / 46–55 / 56+
- Education: None / Primary / Secondary / Higher secondary / Graduate
- Occupation: Farmer / Agricultural labor / Extension worker / Other
- Smartphone experience: <1 year / 1–3 years / 3+ years
- Voice assistant experience: Yes / No

**Pre-literacy quiz (5 items):**
1. "What does this chart show?" [show simple bar chart]
2. "Which number is larger: 50 or 100?"
3. "What is the main idea of this sentence?" [show simple sentence]
4. "Look at these two bars. Which one is taller?"
5. "If it rains 20mm today and 30mm tomorrow, which day had more rain?"

Score: 0–5. Used as covariate in analysis.

### 4.3 Condition Assignment

Randomize participant to one of four conditions:

- **Condition A:** Conventional dashboard
- **Condition B:** Voice-only
- **Condition C:** Voice + Icons
- **Condition D:** Voice + Icons + Story

**Randomization method:** Use sealed envelope or random number generator. Ensure equal allocation within each literacy group.

### 4.4 Tutorial (2 minutes)

**Condition A (Conventional):**
"Here is the dashboard. You can use the filters at the top to select crop, state, and date. The charts show different views of the data. You can ask me questions if you get stuck."

**Condition B (Voice-only):**
"Here is the dashboard. You can speak to it using the microphone button. Try saying 'show wheat in Punjab'. You can also ask questions like 'how is the weather?'"

**Condition C (Voice + Icons):**
"Here is the dashboard. You can use voice commands, and you will see icons at the top that show the main weather conditions. Use the Simple View button to make the icons bigger."

**Condition D (Voice + Icons + Story):**
"Here is the dashboard. You can use voice commands, see icons, and read or listen to a story that explains the data. Try the Read Aloud button."

**Important:** Do not demonstrate specific tasks. Let participants discover functionality.

### 4.5 Task Block (10 minutes)

Present 4 tasks from the evaluation dataset (see `dataset/evaluation-tasks.yaml`). Task order counterbalanced using Latin square.

**Facilitator script per task:**

"Now I will show you a task. Read the question on the screen [or I will read it to you]. Use the dashboard to find the answer. Tell me when you are done. I will note how long it takes. Do you have any questions?"

**Task presentation rules:**
- Read task aloud for low-literate participants
- Do not provide hints or guidance unless participant is completely stuck (log as "facilitator-assisted")
- If participant fails after 3 minutes, move to next task and log as "incomplete"
- Record: start time, end time, success/failure, number of interaction steps, errors encountered

**Interaction logging:**
The system automatically logs:
- Voice commands and transcripts
- Filter changes
- Chart interactions
- Error messages
- Task completion events

Facilitator additionally records:
- Facilitator assistance (yes/no)
- Participant verbalizations (think-aloud protocol, optional)
- Observed frustration or confusion

### 4.6 Post-Task Survey (5 minutes)

Administer after each condition block:

**NASA-TLX (6 items, 0–100 scale):**
1. Mental demand: "How mentally demanding was the task?"
2. Physical demand: "How physically demanding was the task?"
3. Time pressure: "How hurried or rushed was the pace?"
4. Performance: "How successful were you in completing the task?"
5. Effort: "How hard did you have to work?"
6. Frustration: "How insecure, discouraged, or stressed did you feel?"

**Condition-specific questions:**
1. "Did you use the voice feature?" (Condition B/C/D only)
2. "Did you use the icons?" (Condition C/D only)
3. "Did you read or listen to the story?" (Condition D only)
4. "What did you like most about this system?"
5. "What did you find difficult or confusing?"

### 4.7 Post-Session Survey (5 minutes)

**System Usability Scale (SUS) — 10 items:**
1. "I would like to use this system frequently."
2. "I found the system unnecessarily complex."
3. "I think the system is easy to use."
4. "I would need technical support to use this system."
5. "I found the various functions in this system were well integrated."
6. "I thought there was too much inconsistency in this system."
7. "I would imagine that most people would learn to use this system very quickly."
8. "I found the system very cumbersome to use."
9. "I felt very confident using the system."
10. "I needed to learn a lot of things before I could get going with this system."

**Trust scale (4 items, 1–5 Likert):**
1. "I trust the information provided by the system."
2. "I would rely on this system for farming decisions."
3. "The system's explanations are clear and understandable."
4. "I feel confident using this system."

**Preference ranking:**
"Which system did you prefer? Why?"

**Exit interview (3–5 open-ended questions):**
1. "What was the easiest part of using the system?"
2. "What was the hardest part?"
3. "What would you change about the system?"
4. "Would you use this system on your farm? Why or why not?"

### 4.8 Debrief (5 minutes)

- Explain the purpose of the study (without revealing hypotheses)
- Answer participant questions
- Provide contact information for follow-up
- Distribute incentive
- Thank participant

---

## 5. Data Collection and Management

### 5.1 Data Collected

| Data Type | Source | Storage | Retention |
|---|---|---|---|
| Demographics | Facilitator entry | SQLite `survey_responses` | 6 months |
| Pre-literacy quiz | Facilitator entry | SQLite `survey_responses` | 6 months |
| Task completion logs | Automated | SQLite `task_logs` | 6 months |
| Voice transcripts | Automated | Not stored (transient only) | N/A |
| Interaction logs | Automated | SQLite `insight_history` | 6 months |
| Post-task surveys | Facilitator entry | SQLite `survey_responses` | 6 months |
| Post-session surveys | Facilitator entry | SQLite `survey_responses` | 6 months |
| Audio recordings | Optional | Encrypted local drive | 6 months |

### 5.2 Data Entry

- Facilitator enters paper surveys into database within 24 hours of session.
- Automated logs are exported after each session.
- Cross-check 10% of entries for data entry errors.

### 5.3 Data Quality Checks

- **Missing data:** Flag if >20% of tasks missing for a participant.
- **Outliers:** Flag if task time > 3× IQR above Q3.
- **Speeders:** Flag if entire survey completed in <5 minutes.
- **Straight-lining:** Flag if all Likert items have same response.

---

## 6. Safety and Ethics

### 6.1 Risks

- **Fatigue:** Limit session to 60 minutes. Offer breaks.
- **Frustration:** Have facilitator trained to provide encouragement without guidance.
- **Privacy:** Conduct sessions in private. Do not share individual data.
- **Agricultural advice:** System provides general information only. Include disclaimer: "This is not a substitute for professional agricultural advice."

### 6.2 Ethical Approvals

- Obtain IRB approval before recruitment.
- Register study protocol if required by institution.
- Follow Declaration of Helsinki principles.

---

## 7. Pilot Testing

### 7.1 Pilot Protocol

- Recruit 5–8 participants per condition (total 20–32).
- Use same procedure as full study.
- Collect: completion rates, times, errors, qualitative feedback.

### 7.2 Pilot Adjustments

| Issue | Adjustment |
|---|---|
| Task completion < 30% | Simplify task instructions or reduce difficulty |
| Task completion > 90% | Increase difficulty or add distractor options |
| Voice recognition WER > 30% | Add clarification prompts, improve intent parser |
| Icon recognition < 70% | Redesign confusing icons |
| Session duration > 60 min | Reduce number of tasks or shorten survey |
| Participant confusion | Rewrite instructions, add visual aids |

### 7.3 Power Analysis

After pilot, estimate effect sizes from pilot data. Adjust sample size if needed:

```r
# R code for power analysis
library(pwr)
pwr.t.test(d = 0.5, power = 0.80, sig.level = 0.05, type = "two.sample")
# Expected output: n = 64 (32 per condition)
```

---

## 8. Facilitator Training

### 8.1 Training Topics

- Study purpose and hypotheses
- Participant screening procedure
- Consent process
- Task administration script
- Neutral probing (how to help without guiding)
- Data entry procedures
- Safety and ethics

### 8.2 Certification

- Facilitators must practice with 2–3 pilot participants before certification.
- Supervisor observes at least one full session before independent facilitation.

---

## 9. Timeline

| Phase | Duration | Activities |
|---|---|---|
| Preparation | 2 weeks | Finalize tasks, consent forms, facilitator training |
| Pilot | 2 weeks | 20–32 participants, refine materials |
| Full study | 4–8 weeks | 80–240 participants, data collection |
| Data cleaning | 1 week | Export, verify, clean data |
| Analysis | 2 weeks | Statistical analysis, visualization |
| Reporting | 2 weeks | Write results, prepare presentation |

---

## 10. Contact Information

**Principal Investigator:** [Name, email, phone]
**Facilitator Supervisor:** [Name, email, phone]
**Institution:** [Name, IRB number]
**Emergency Contact:** [Name, phone]
