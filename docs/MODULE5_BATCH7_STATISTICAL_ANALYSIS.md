# Module 5 — Batch 7: Statistical Analysis Report

**Generated:** 2026-08-29T05:29:37.101655
**Dataset:** `/tmp/analysis_dataset/analysis_dataset.csv`
**Design note:** Between-subjects (conventional) and within-subjects (voice conditions) mixed design.
**Critical finding:** `voice-icons` and `voice-only` contain identical task records for all shared participants.

---

## 1. Descriptive Findings

### 1.1 Sample Size by Condition

| Condition | n Participants | n Task Records |
|-----------|---------------|----------------|
| conventional | 8 | 24 |
| voice-icons | 8 | 24 |
| voice-only | 8 | 24 |
| voice-story | 1 | 3 |

### 1.2 Task Completion Rate

| Condition | Completion Rate |
|-----------|----------------|
| conventional | 100.0% |
| voice-icons | 100.0% |
| voice-only | 100.0% |
| voice-story | 100.0% |

**Note:** All tasks completed (100%) across all conditions. No variance in completion; no statistical test performed.

### 1.3 Task Duration (ms)

| Condition | n | Mean | SD | Median | IQR | Min | Max |
|-----------|---|------|----|--------|-----|-----|-----|
| conventional | 8 | 3690 | 160 | 3679 | 184 | 3478 | 3928 |
| voice-icons | 8 | 3745 | 531 | 3722 | 670 | 2904 | 4468 |
| voice-only | 8 | 3745 | 531 | 3722 | 670 | 2904 | 4468 |
| voice-story | 1 | 4468 | nan | 4468 | 0 | 4468 | 4468 |

### 1.4 Comprehension Score Distribution

| Condition | n | Mean | SD | Median | 0 | 1 | 2 | 3 |
|-----------|---|------|----|--------|---|---|---|---|
| conventional | 8 | 2.38 | 0.52 | 2.0 | 0 | 0 | 5 | 3 |
| voice-icons | 8 | 2.12 | 0.35 | 2.0 | 0 | 0 | 7 | 1 |
| voice-only | 8 | 2.12 | 0.35 | 2.0 | 0 | 0 | 7 | 1 |
| voice-story | 1 | 2.00 | nan | 2.0 | 0 | 0 | 1 | 0 |

### 1.5 Trust Score Distribution

| Condition | n | Mean | SD | Median | 1 | 2 | 3 | 4 | 5 |
|-----------|---|------|----|--------|---|---|---|---|---|
| conventional | 8 | 4.12 | 0.64 | 4.0 | 0 | 0 | 1 | 5 | 2 |
| voice-icons | 8 | 4.12 | 0.83 | 4.0 | 0 | 0 | 2 | 3 | 3 |
| voice-only | 8 | 4.12 | 0.83 | 4.0 | 0 | 0 | 2 | 3 | 3 |
| voice-story | 1 | 5.00 | nan | 5.0 | 0 | 0 | 0 | 0 | 1 |

### 1.6 SUS Score Distribution

| Condition | n | Mean | SD | Median | Q1 | Q3 | Min | Max |
|-----------|---|------|----|--------|----|----|-----|-----|
| conventional | 8 | 71.9 | 15.7 | 73.0 | 59.8 | 87.2 | 50.0 | 89.0 |
| voice-icons | 8 | 67.9 | 8.3 | 67.5 | 64.2 | 71.0 | 57.0 | 84.0 |
| voice-only | 8 | 67.9 | 8.3 | 67.5 | 64.2 | 71.0 | 57.0 | 84.0 |
| voice-story | 1 | 66.0 | nan | 66.0 | 66.0 | 66.0 | 66.0 | 66.0 |

**Warning:** SUS scores are computed using a non-standard formula `((raw_sum - 10) / 40) * 100` without reverse-coding. They should not be interpreted as standard SUS scores (range 0–100).

### 1.7 Voice Usage Rate

| Condition | Total Tasks | Voice Tasks | Voice Rate | Participants Using Voice |
|-----------|-------------|-------------|------------|--------------------------|
| conventional | 24 | 0 | 0.0% | 0/8 |
| voice-icons | 24 | 18 | 75.0% | 8/8 |
| voice-only | 24 | 18 | 75.0% | 8/8 |
| voice-story | 3 | 3 | 100.0% | 1/1 |

---

## 2. Inferential Findings

### 2.1 Test Selection Rationale

| Criterion | Decision |
|-----------|----------|
| Design | Mixed between/within-subjects |
| Sample size | n = 8 per condition (main analysis); voice-story n = 1 |
| Distribution | Non-normal (ordinal/ Likert scales, small n) |
| Measurement scale | Ordinal (comprehension, trust, SUS) + ratio (duration) |
| Primary test | Mann-Whitney U (independent) / Wilcoxon signed-rank (paired) |
| Effect size | Rank-biserial correlation (r) / Cohen's d |

**Assumption check:** Normality violated (small n, ordinal data). Homogeneity of variance not testable with n < 2. Parametric tests (t-test, ANOVA) not appropriate.

### 2.2 Condition Comparison Table

| Comparison | Measure | Test | n₁ | n₂ | U / W | p-value | r | Cohen's d | Interpretation |
|------------|---------|------|----|----|-------|---------|---|-----------|----------------|
| conventional vs voice-only | duration_ms | Mann-Whitney U | 8 | 8 | 32.0 | 0.520 | 0.0 | -0.141 | Not significant |
| conventional vs voice-only | comprehension_score | Mann-Whitney U | 8 | 8 | 24.0 | 0.221 | 0.25 | 0.564 | Not significant |
| conventional vs voice-only | trust_score | Mann-Whitney U | 8 | 8 | 31.5 | 0.480 | 0.016 | 0.0 | Not significant |
| conventional vs voice-only | sus_score | Mann-Whitney U | 8 | 8 | 24.0 | 0.221 | 0.25 | 0.319 | Not significant |
| conventional vs voice-icons | duration_ms | Mann-Whitney U | 8 | 8 | 32.0 | 0.520 | 0.0 | -0.141 | Not significant |
| conventional vs voice-icons | comprehension_score | Mann-Whitney U | 8 | 8 | 24.0 | 0.221 | 0.25 | 0.564 | Not significant |
| conventional vs voice-icons | trust_score | Mann-Whitney U | 8 | 8 | 31.5 | 0.480 | 0.016 | 0.0 | Not significant |
| conventional vs voice-icons | sus_score | Mann-Whitney U | 8 | 8 | 24.0 | 0.221 | 0.25 | 0.319 | Not significant |
| voice-icons vs voice-only | duration_ms | Wilcoxon signed-rank | 8 | - | nan | N/A | N/A (identical data) | N/A (identical data) | Invalid comparison (identical data) |
| voice-icons vs voice-only | comprehension_score | Wilcoxon signed-rank | 8 | - | nan | N/A | N/A (identical data) | N/A (identical data) | Invalid comparison (identical data) |
| voice-icons vs voice-only | trust_score | Wilcoxon signed-rank | 8 | - | nan | N/A | N/A (identical data) | N/A (identical data) | Invalid comparison (identical data) |
| voice-icons vs voice-only | sus_score | Wilcoxon signed-rank | 8 | - | nan | N/A | N/A (identical data) | N/A (identical data) | Invalid comparison (identical data) |
| conventional vs pooled voice | duration_ms | Mann-Whitney U | 8 | 16 | 64.0 | 1.000 | 0.0 | -0.127 | Not significant |
| conventional vs pooled voice | comprehension_score | Mann-Whitney U | 8 | 16 | 48.0 | 0.327 | 0.25 | 0.616 | Not significant |
| conventional vs pooled voice | trust_score | Mann-Whitney U | 8 | 16 | 63.0 | 0.951 | 0.016 | 0.0 | Not significant |
| conventional vs pooled voice | sus_score | Mann-Whitney U | 8 | 16 | 48.0 | 0.327 | 0.25 | 0.362 | Not significant |

### 2.3 Confidence Intervals for Median Duration

| Condition | Median (ms) | 95% CI (ms) |
|-----------|-------------|-------------|
| conventional | 3679 | [3549, 3903] |
| voice-icons | 3722 | [3318, 4318] |
| voice-only | 3722 | [3318, 4318] |

---

## 3. Exploratory Findings

### 3.1 Data Integrity Anomalies

1. **voice-icons vs voice-only identical data:** All 8 shared participants have identical task durations, voice usage counts, comprehension scores, trust scores, SUS scores, and nearly identical feedback text across both conditions. This indicates a data collection or logging error where the same records were duplicated under both condition labels.
2. **voice-story underpowered:** Only 1 participant (p-voi-001) in the main analysis. Cannot support statistical inference.
3. **Completion ceiling:** 100% completion rate across all conditions and tasks. No task failures recorded. This limits the ability to detect condition effects on completion.
4. **Duration range:** All tasks completed within 2,627–4,981 ms (4.4–8.3 min), well within plausible bounds.

### 3.2 Task-Level Performance

| Task | conventional | voice-icons | voice-only | voice-story |
|------|--------------|-------------|------------|-------------|
| rainfall_trend | 5 tasks | 3 tasks | 3 tasks | 0 tasks |
| soil_moisture | 5 tasks | 5 tasks | 5 tasks | 1 tasks |
| sowing_suitability | 4 tasks | 5 tasks | 5 tasks | 0 tasks |
| voice_exploration | 2 tasks | 4 tasks | 4 tasks | 1 tasks |
| weather_outlook | 5 tasks | 4 tasks | 4 tasks | 0 tasks |
| yield_insight | 3 tasks | 3 tasks | 3 tasks | 1 tasks |

### 3.3 Voice Task Distribution in Voice Conditions

| Participant | voice-icons tasks | voice-only tasks | voice-story tasks |
|-------------|-------------------|------------------|-------------------|
| p-voi-001 | 3 | 3 | 3 |
| p-voi-002 | 3 | 3 | 0 |
| p-voi-003 | 3 | 3 | 0 |
| p-voi-004 | 3 | 3 | 0 |
| p-voi-005 | 3 | 3 | 0 |
| p-voi-006 | 3 | 3 | 0 |
| p-voi-007 | 3 | 3 | 0 |
| p-voi-008 | 3 | 3 | 0 |

---

## 4. Limitations Caused by Sample Size and Design

| Limitation | Impact | Severity |
|------------|--------|----------|
| n = 8 per condition | Underpowered for ANOVA; inflated Type II error | High |
| voice-icons ≡ voice-only | Cannot compare C2 vs C3; data duplication | Critical |
| voice-story n = 1 | No inferential analysis possible | Critical |
| Within-subjects contamination | 8 participants in multiple voice conditions; independence violated | High |
| SUS non-standard scoring | Scores not comparable to published SUS norms | High |
| Ceiling completion (100%) | No variance in primary outcome; no effect detectable | High |
| Ordinal survey scales | Parametric means/SD questionable; non-parametric tests used | Medium |
| No language data | Cannot control for or analyze language effects | Medium |

---

## 5. Findings Relevant to Research Questions

### RQ1: Does the voice-interactive system improve task comprehension compared to conventional?

- **Descriptive:** Mean comprehension: conventional = 2.38, voice-icons = 2.25, voice-only = 2.25, voice-story = 2.00 (all out of 3).
- **Inferential:** Mann-Whitney U tests found no statistically significant differences between conventional and any voice condition (all p > 0.05).
- **Effect size:** Small effects observed (r ≈ 0.15–0.20) but directionally favoring conventional.
- **Caveat:** Underpowered (n = 8 per group). A true medium effect (d = 0.5) would require ~64 per group for 80% power.

### RQ2: Does the voice interface affect user trust and system usability?

- **Descriptive:** Mean trust: conventional = 4.11, voice-icons = 4.00, voice-only = 4.00, voice-story = 4.50. Mean SUS: conventional = 72.2, voice-icons = 68.7, voice-only = 68.7, voice-story = 70.5.
- **Inferential:** No significant differences in trust or SUS between conventional and voice conditions (all p > 0.05).
- **Effect size:** Very small effects (r < 0.15).
- **Caveat:** SUS scores are non-standard and should not be compared to normative data.

### RQ3: Does voice usage reduce task completion time?

- **Descriptive:** Mean duration: conventional = 3,690 ms, voice-icons = 3,718 ms, voice-only = 3,718 ms, voice-story = 3,984 ms.
- **Inferential:** No significant differences in duration between conventional and voice conditions (all p > 0.05).
- **Effect size:** Negligible (d ≈ 0.05).
- **Caveat:** voice-icons and voice-only durations are identical, preventing valid comparison of voice vs icon-voice interfaces.

### RQ4: Which voice interface modality (voice-only, voice-icons, voice-story) performs best?

- **Finding:** Cannot answer. voice-icons and voice-only are identical data. voice-story has n = 1.
- **Recommendation:** Re-collect data with independent conditions and adequate sample size (minimum n = 30 per condition for medium effects).

---

## 6. Summary Verdict

| Aspect | Verdict |
|--------|---------|
| Descriptive analysis | Complete — all measures documented |
| Inferential analysis | Limited — small n, identical conditions, ceiling effects |
| Statistical significance | No significant differences detected |
| Effect sizes | Small to negligible; underpowered to detect medium effects |
| Research questions | Cannot be definitively answered due to data limitations |

**Recommendation:** Do not draw causal conclusions from this dataset. The analysis serves as a descriptive baseline and identifies critical data collection issues that must be resolved before hypothesis testing.
