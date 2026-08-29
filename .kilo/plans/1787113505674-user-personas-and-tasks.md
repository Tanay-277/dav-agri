# User Personas and Task Analysis: Voice-Interactive Agricultural/Weather Analytics

## Evidence Base

Demographic assumptions are grounded in the following verified sources:
- **ASER 2024** (Annual Status of Education Report, Rural India): 82.2% of rural youth aged 14–16 can use a smartphone; 65.9% could bring a smartphone for digital tasks; gender gap in ownership persists (36.2% male vs. 26.9% female among those who know how to use a smartphone).
- **ASER 2023**: 90% of rural households have smartphones; 94.7% male and 89.8% female youth can use a smartphone.
- **Nielsen Bharat 2.0 / IAMAI**: 425 million rural internet users in India (Jan 2023); 45% growth in active rural internet users since 2019.
- **Precision Development (PxD)**: Smallholder farmers under-supplied with weather information; forecasts have high potential value but face cognitive, trust, and accessibility barriers.
- **Medhi et al. (2011)**: Text interfaces are unusable by first-time low-literacy users; graphical and spoken-dialog interfaces outperform text.
- **Sarvam AI Agri & Rural Voice Agents documentation**: Voice is often the *only* accessible interface for low-literacy rural users; 2G/3G connectivity is common; regional-language-only speech is the norm.

---

## Personas

### Persona 1: Rammohan — The Subsistence Wheat Farmer

| Attribute | Detail |
|---|---|
| **Age** | 52 |
| **Literacy level** | Functional illiterate — can sign name, cannot read newspapers or charts |
| **Digital literacy** | Low. Owns a basic feature phone; uses it for calls only. Cannot use smartphone independently. Relies on adult children for WhatsApp messages. |
| **Typical devices** | Basic feature phone (Nokia-style). Has access to family member’s smartphone ~1 hour/day. |
| **Connectivity** | Village has 2G coverage; no broadband. Voice calls and SMS work. Internet data is expensive and used sparingly. |
| **Language requirements** | Hindi (primary). Limited technical vocabulary. Prefers spoken instructions over written. |
| **Agricultural information needs** | When to sow wheat, expected rainfall for the coming week, whether to apply irrigation, pest warnings, mandi prices. |
| **Weather-related decisions** | Sowing date, irrigation scheduling, harvest timing, fertilizer application windows. |
| **Barriers to conventional dashboards** | Cannot read axis labels, legends, or tooltips. Bar charts and line graphs are meaningless abstractions. Navigation menus require literacy he does not possess. |
| **Voice interaction requirements** | Voice-only interaction in Hindi. Short, simple sentences. No technical jargon (e.g., say "rain" not "precipitation"). Confirmation prompts before actions. |
| **Accessibility considerations** | Large touch targets, high-contrast icons, no reliance on color alone, audio feedback for every action. |

**Evidence vs. assumption:** Literacy level and device ownership are assumptions based on ASER 2024 rural averages. The specific crop and region are assumptions that should be validated with users.

---

### Persona 2: Lakshmi — The Market-Gardening Woman Farmer

| Attribute | Detail |
|---|---|
| **Age** | 38 |
| **Literacy level** | Semi-literate — can read simple Hindi text with effort, cannot interpret tables or charts |
| **Digital literacy** | Moderate. Owns a smartphone (inherited from son). Can open WhatsApp, watch YouTube, and use basic apps. Struggles with data entry, dropdowns, and forms. |
| **Typical devices** | Android smartphone (entry-level, 2GB RAM). Uses it for WhatsApp group messages and YouTube farming videos. |
| **Connectivity** | 4G coverage in village, but speeds drop after 6 PM. Wi-Fi available only at home (metered). Data costs constrain video streaming. |
| **Language requirements** | Kannada (primary), basic Hindi. Prefers local dialect for agricultural terms. |
| **Agricultural information needs** | Vegetable market prices, pest identification, organic pesticide recipes, government scheme eligibility. |
| **Weather-related decisions** | When to spray pesticides (needs dry window), whether to cover crops before hailstorm, irrigation frequency during dry spells. |
| **Barriers to conventional dashboards** | Dropdown menus are hard to navigate; small text is unreadable on phone screen; scrolling through long tables causes confusion. |
| **Voice interaction requirements** | Voice input in Kannada/Hindi. Voice output should be slower than default TTS rate. Visual icons should reinforce voice (e.g., rain icon when system says "rain"). |
| **Accessibility considerations** | Touch targets ≥ 48dp, clear visual feedback on tap, no hover-only interactions, support for screen magnification. |

**Evidence vs. assumption:** Smartphone ownership among rural women is supported by ASER 2024 (26.9% ownership among females who know how to use smartphones). Kannada language preference is an assumption requiring validation.

---

### Persona 3: Dinesh — The Progressive Cash-Crop Farmer

| Attribute | Detail |
|---|---|
| **Age** | 34 |
| **Literacy level** | Literate — 12th grade education, can read newspapers and simple charts |
| **Digital literacy** | High for his context. Owns a smartphone, uses agricultural apps, watches market price videos, and tracks weather on a basic app. |
| **Typical devices** | Mid-range Android smartphone, laptop (shared with son). |
| **Connectivity** | 4G with unlimited data plan at home. Occasional signal loss in fields. |
| **Language requirements** | English + Gujarati. Comfortable with technical terms if explained. |
| **Agricultural information needs** | Market price trends, yield comparisons across seasons, fertilizer optimization, pest outbreak alerts. |
| **Weather-related decisions** | Long-range planning (which crop to plant based on monsoon forecast), short-term (spraying schedule), input procurement timing. |
| **Barriers to conventional dashboards** | Existing dashboards show data for all of India, not his district. Too many irrelevant filters. Charts update slowly on mobile. |
| **Voice interaction requirements** | Voice as a *shortcut* for filters (e.g., "show cotton prices in Gujarat last month"). Prefers mixed mode: voice for navigation, charts for deep analysis. |
| **Accessibility considerations** | Keyboard shortcuts, dark mode, export-to-PDF for offline sharing with cooperative. |

**Evidence vs. assumption:** Existence of progressive farmers who use smartphones for agriculture is documented in literature (e.g., Digital Green, IFPRI). Specific crop (cotton in Gujarat) is an assumption.

---

### Persona 4: Meena — The Community Agricultural Volunteer / ASHA-Level Worker

| Attribute | Detail |
|---|---|
| **Age** | 41 |
| **Literacy level** | Literate — high school pass, can read government forms and basic charts |
| **Digital literacy** | Moderate-high. Trained on government apps (e.g., mHealth apps). Can navigate menus and forms with some difficulty. |
| **Typical devices** | Government-issued Android smartphone. Uses it for work reports and beneficiary tracking. |
| **Connectivity** | 4G coverage in headquarters village, weak in outlying hamlets. Uses Wi-Fi at office. |
| **Language requirements** | Marathi (primary), basic English for app terms. Needs to explain data to illiterate farmers in simple terms. |
| **Agricultural information needs** | Village-level weather alerts, crop-specific advisories to pass on, government scheme enrollment numbers, pest outbreak tracking. |
| **Weather-related decisions** | When to schedule community training on irrigation, whether to alert farmers about impending drought, which villages need seed distribution. |
| **Barriers to conventional dashboards** | Dashboards designed for individual farmers, not for community-level aggregation. Too many technical terms. No "share" or "print summary" function. |
| **Voice interaction requirements** | Voice for hands-free operation while traveling between villages. Ability to *save* voice-generated reports and share via WhatsApp. |
| **Accessibility considerations** | Ability to export/share reports, offline mode for field use, group-level data summaries. |

**Evidence vs. assumption:** ASHA/Anganwadi worker profile is well-documented in Indian public health and development literature. Agricultural extension worker analog is an extrapolation requiring validation.

---

### Persona 5: Father Thomas — The Priest-Led Self-Help Group Coordinator

| Attribute | Detail |
|---|---|
| **Age** | 62 |
| **Literacy level** | Highly literate in English and Malayalam, but low data literacy — cannot interpret scatter plots or correlation matrices |
| **Digital literacy** | Low-moderate. Uses email and Facebook on a laptop. Finds mobile apps confusing. Distrusts "black box" systems. |
| **Typical devices** | Windows laptop (shared with parish), basic Android phone. |
| **Connectivity** | Broadband at parish office (unreliable during monsoons). 4G on phone. |
| **Language requirements** | Malayalam, English. Prefers formal, respectful voice tone. |
| **Agricultural information needs** | Aggregate village farming data to apply for government grants, weather risk assessments for group insurance, training schedules. |
| **Weather-related decisions** | Whether to recommend crop insurance to group members, when to schedule pre-monsoon training, whether to request emergency water supply. |
| **Barriers to conventional dashboards** | "Too many numbers, not enough explanation." Wants to know *what it means* and *what to do*, not just raw trends. |
| **Voice interaction requirements** | Voice as a *narrative* medium — wants the system to "tell a story" about the data, not read numbers. Slow, deliberate speech with pauses. |
| **Accessibility considerations** | Large fonts option, high contrast, ability to print or email reports, clear provenance of data sources. |

**Evidence vs. assumption:** Church/community leader role in rural development is documented. Specific age and tech profile is an assumption requiring validation.

---

## Task Analysis: 10 Representative Tasks

### Task 1: Understanding Tomorrow's Weather

| Field | Detail |
|---|---|
| **User goal** | Know if it will rain tomorrow so I can plan pesticide spraying |
| **Required data** | Next-day forecast: precipitation probability, temperature range, wind speed |
| **Expected voice interaction** | User: "Will it rain tomorrow?" → System confirms location, responds: "Tomorrow, there is a 70% chance of rain in the morning. Temperature will be 26 to 30 degrees." |
| **Expected visual/icon output** | Large rain icon (70% opacity = probability), thermometer icon showing 26–30°C range, calendar icon highlighting "tomorrow" |
| **Expected system response** | Audio: short, direct answer with actionable advice: "Do not spray pesticides tomorrow. Wait for a dry day." |
| **Success condition** | User can state whether spraying is advisable without asking follow-up questions |

**Assumptions to validate:** 70% rain probability threshold for "advisable to spray" is agronomic assumption; should be validated with agricultural experts and farmers.

---

### Task 2: Determining Whether Rain Is Expected in the Next 3 Days

| Field | Detail |
|---|---|
| **User goal** | Decide whether to harvest early or wait, given an approaching dry spell |
| **Required data** | 3-day rainfall forecast, cumulative rainfall for current week |
| **Expected voice interaction** | User: "Will it rain in the next 3 days?" → System: "No heavy rain expected for the next 3 days. Light drizzle possible on day 2. Good time to harvest." |
| **Expected visual/icon output** | 3-icon strip (day 1: sun, day 2: cloud-small-rain, day 3: sun), cumulative rainfall bar |
| **Expected system response** | Audio with temporal sequencing: "Today: dry. Tomorrow: light drizzle. Day after: dry again." |
| **Success condition** | User decides to harvest within 24 hours without seeking external confirmation |

**Assumptions to validate:** "Light drizzle" interpretation varies by crop and soil type; threshold for "dry spell" should be crop-specific.

---

### Task 3: Comparing Today's and Tomorrow's Temperature

| Field | Detail |
|---|---|
| **User goal** | Assess heat stress risk for laborers working in the field |
| **Required data** | Today's max temperature, tomorrow's max temperature, humidity correlation |
| **Expected voice interaction** | User: "Is tomorrow hotter than today?" → System: "Tomorrow will be 2 degrees hotter. Today: 34 degrees. Tomorrow: 36 degrees. Work early morning to avoid heat." |
| **Expected visual/icon output** | Two thermometer icons side-by-side, 34°C and 36°C, with a red upward arrow and sun icon |
| **Expected system response** | Audio: direct comparison + safety advice |
| **Success condition** | User adjusts work schedule (starts earlier) without asking family or neighbors |

**Assumptions to validate:** 2°C difference threshold for "hotter" is arbitrary; should test what temperature differential farmers perceive as meaningful.

---

### Task 4: Understanding Rainfall Trends Over the Past Month

| Field | Detail |
|---|---|
| **User goal** | Decide whether the monsoon is delayed or on schedule |
| **Required data** | Daily rainfall for past 30 days, long-term average for same period |
| **Expected voice interaction** | User: "How is the rainfall this month?" → System: "This month, rainfall is 20% below normal. Last week was dry. The monsoon is slightly delayed." |
| **Expected visual/icon output** | Bar chart with 30 days, each bar colored by intensity (blue gradient), overlay of "normal" line, trend arrow down |
| **Expected system response** | Audio: trend summary + comparison to normal + plain-language interpretation ("delayed" not "deficit") |
| **Success condition** | User can explain to a neighbor whether the monsoon is late, without reading the chart |

**Assumptions to validate:** "20% below normal" threshold for "delayed" is agronomic assumption; "delayed" vs. "deficit" framing may be region-specific.

---

### Task 5: Deciding Whether Conditions Are Suitable for Sowing

| Field | Detail |
|---|---|
| **User goal** | Determine optimal sowing window for Kharif season |
| **Required data** | Soil moisture, 7-day rainfall forecast, temperature range, last year's sowing date |
| **Expected voice interaction** | User: "Is it time to sow cotton?" → System: "Soil moisture is good. Rain expected in 5 days. Wait 2 more days for soil to settle, then sow." |
| **Expected visual/icon output** | Soil moisture gauge (green = good), calendar with "wait 2 days" marker, cotton icon |
| **Expected system response** | Audio: recommendation with reasoning + temporal urgency |
| **Success condition** | User postpones sowing by 2 days and achieves better germination (verified later by user) |

**Assumptions to validate:** Soil moisture thresholds for "good" are crop-specific and region-specific; must be validated with local agronomists.

---

### Task 6: Checking Soil Moisture to Plan Irrigation

| Field | Detail |
|---|---|
| **User goal** | Avoid over-irrigation (wastes water/cost) or under-irrigation (crop stress) |
| **Required data** | Current soil moisture %, 3-day forecast, crop growth stage |
| **Expected voice interaction** | User: "Should I irrigate?" → System: "Soil moisture is 28%. It is low. Irrigate tomorrow morning." |
| **Expected visual/icon output** | Droplet icon with percentage, colored gauge (red = low, yellow = moderate, green = good), clock icon for "morning" |
| **Expected system response** | Audio: current status + recommendation + timing |
| **Success condition** | User irrigates at recommended time and observes no crop wilting in following 2 days |

**Assumptions to validate:** 28% soil moisture threshold for "low" depends on crop type and soil texture; assumption based on generic agricultural guidelines.

---

### Task 7: Understanding Yield Trends to Choose Next Season's Crop

| Field | Detail |
|---|---|
| **User goal** | Decide whether to continue with wheat or switch to pulses based on past performance |
| **Required data** | Yield per hectare for user's land over past 3 seasons, market price trends, input cost trends |
| **Expected voice interaction** | User: "Which crop gave better yield last year?" → System: "Wheat yield was 450 kg per hectare. Pulses yield was 320 kg. But pulses need less water and cost less to grow." |
| **Expected visual/icon output** | Two bar icons side-by-side (wheat vs. pulses), yield numbers inside bars, water-drop icon for "less water" |
| **Expected system response** | Audio: direct comparison + contextual trade-offs (yield vs. input cost vs. water) |
| **Success condition** | User makes an informed crop choice that matches their risk tolerance and resource constraints |

**Assumptions to validate:** "Better yield" framing ignores input costs and water availability; trade-off weighting is highly personal and must be user-tested.

---

### Task 8: Determining Whether a Temperature Inversion Is Expected

| Field | Detail |
|---|---|
| **User goal** | Decide whether to apply pesticide tonight (temperature inversion increases drift risk) |
| **Required data** | Tonight's temperature range, wind speed, humidity, inversion risk index |
| **Expected voice interaction** | User: "Can I spray pesticide tonight?" → System: "No. Wind is high tonight. Spray tomorrow morning when wind is calm." |
| **Expected visual/icon output** | Wind icon with speed indicator, prohibition overlay, calendar icon for "tomorrow morning" |
| **Expected system response** | Audio: negative answer + alternative timing + brief reason ("wind") |
| **Success condition** | User does not spray and avoids pesticide drift damage to neighbor's crop |

**Assumptions to validate:** Wind speed threshold for "high" is agronomic assumption; "calm" morning definition varies by region and crop.

---

### Task 9: Getting a Voice Summary of the Dashboard for the Selected Filters

| Field | Detail |
|---|---|
| **User goal** | Understand the overall agricultural conditions for selected filters without reading charts |
| **Required data** | All KPIs, insights, and recommendations for current filter selection |
| **Expected voice interaction** | User taps "Read Aloud" button → System narrates: "For Wheat in Punjab, average rainfall is 55 mm, temperature is 31 degrees. Yield is below average by 8%. Recommendation: monitor soil moisture." |
| **Expected visual/icon output** | Highlighted icon legend (rain icon pulses while rainfall is mentioned, thermometer pulses while temperature is mentioned) |
| **Expected system response** | Audio: sequential narration of KPIs → insights → recommendations, ~60 seconds total |
| **Success condition** | User can repeat the main recommendation to a family member without looking at the screen |

**Assumptions to validate:** Narration length tolerance (~60 seconds) is an assumption; some users may prefer shorter summaries or the ability to skip sections.

---

### Task 10: Asking Why Yield Dropped and Getting an Explanation

| Field | Detail |
|---|---|
| **User goal** | Understand causality: why did my cotton yield drop last season? |
| **Required data** | Yield trend, rainfall trend, temperature anomaly, pest/disease reports, input usage |
| **Expected voice interaction** | User: "Why did cotton yield drop?" → System: "Yield dropped because rainfall was 30% below normal last season. Less rain means less water for crops." |
| **Expected visual/icon output** | Two mini sparklines (yield down, rain down), causal arrow from rain icon to yield icon, exclamation mark for "reason" |
| **Expected system response** | Audio: single causal explanation, not a list of statistics. Follow-up question offered: "Do you want irrigation tips?" |
| **Success condition** | User understands the single primary cause (not all possible causes) and can name one corrective action |

**Assumptions to validate:** "Single primary cause" simplification may be misleading (yield is multi-factorial); must validate whether farmers prefer single-cause or multi-cause explanations.

---

## Distinguishing Evidence from Assumption

| Element | Evidence-Based | Assumption (Needs Validation) |
|---|---|---|
| Device ownership (smartphones in rural India) | ASER 2024, Nielsen | Specific device models, OS versions |
| Connectivity (2G/4G availability) | ITU, GSMA | Actual data costs and speeds in target villages |
| Literacy levels | ASER 2024, UNESCO | Exact literacy of our specific user segment |
| Voice preference over text | Medhi et al. (2011), Sarvam AI docs | Voice UI design preferences (pace, tone, gender of voice) |
| Weather information gaps | PxD, Frontiers 2026 | Specific local weather phenomena that matter most |
| Agricultural decision factors | Undp precision ag report, IITA | Crop-specific thresholds for the user's region |
| Icon comprehension | Bayor et al. (2018) | Which icons are culturally recognizable in target community |
| Language/dialect | ASER 2024 (state-wise) | Exact dialect, code-switching patterns, technical vocabulary gaps |

---

## Next Steps for Validation

1. **Co-design workshops** with 8–12 target users per persona group to validate icons, voice prompts, and task prioritization.
2. **Wizard-of-Oz testing** where a human simulates the voice system to validate interaction patterns before engineering.
3. **Agricultural expert review** of all thresholds, recommendations, and causal explanations embedded in the system.
4. **Pilot deployment** with 20–30 users for 2 weeks, measuring task completion rates and qualitative feedback.
