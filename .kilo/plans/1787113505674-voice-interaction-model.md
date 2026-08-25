# Voice-Interaction Model Design

## Branch

All research deliverables are tracked on `research/personas-scope-mvrs`.

---

## 1. Design Principles

The voice interaction model is governed by three constraints:

1. **Literacy-agnostic:** Users cannot read charts, tables, or menus. Voice must carry all information density.
2. **Low-bandwidth tolerant:** Responses must be short, redundant, and resumable. Internet may drop mid-utterance.
3. **Trust-building:** Agricultural decisions carry financial risk. The system must explain *why* and *what to do*, not just state facts.

---

## 2. Supported Voice Commands

### 2.1 Filter / Navigation Commands

| Command pattern | Example | Action |
|---|---|---|
| `show [crop] in [state]` | "show wheat in Punjab" | Apply crop + state filter |
| `show [crop] in [state] [district]` | "show cotton in Maharashtra Pune" | Apply crop + state + district filter |
| `filter by [district]` | "filter by Coimbatore" | Apply district filter |
| `from [date] to [date]` | "from 2023-01-01 to 2023-06-01" | Apply date range |
| `reset filters` / `clear` / `show all` | "reset filters" | Clear all filters |
| `read aloud` / `tell me the story` | "read aloud" | Trigger TTS narration of story panel |
| `stop` / `pause` / `resume` | "stop" | Cancel / pause / resume TTS |
| `simple mode` / `standard mode` | "simple mode" | Toggle simple view |
| `help` / `what can you do` | "help" | List supported commands |

### 2.2 Data Query Commands

| Command pattern | Example | Action |
|---|---|---|
| `weather tomorrow` / `will it rain tomorrow` | "will it rain tomorrow?" | Query forecast (postponed; currently returns historical trend for selected period) |
| `temperature today` / `how hot is it` | "how hot is it today?" | Return current period average temperature |
| `rainfall this month` / `how much rain` | "how much rain this month?" | Return summed/averaged rainfall for selected period |
| `soil moisture` / `is soil wet` | "is soil moisture okay?" | Return soil moisture status + irrigation recommendation |
| `yield [crop]` / `how is [crop] doing` | "how is wheat doing?" | Return yield insight for selected crop |
| `trend [metric]` / `is [metric] increasing` | "is rainfall increasing?" | Return trend direction and magnitude |
| `compare [crop] with [crop]` | "compare wheat with rice" | Return side-by-side comparison |
| `why [metric] dropped` / `why [crop] low` | "why yield dropped?" | Return causal explanation from story engine |
| `recommend` / `what should I do` | "what should I do?" | Return top recommendation |
| `summary` / `overview` | "give me a summary" | Return full story narrative |

### 2.3 Confirmation / Correction Commands

| Command pattern | Example | Action |
|---|---|---|
| `yes` / `correct` / `right` | "yes" | Confirm pending action |
| `no` / `wrong` / `cancel` | "no" | Cancel pending action |
| `undo` / `go back` | "undo" | Revert last filter change |

---

## 3. Natural-Language Question Handling

The system uses **intent-first parsing** (no LLM dependency):

1. **Normalize:** lowercase, trim, remove filler words ("please", "can you tell me", "I want to know")
2. **Tokenize:** split on whitespace and punctuation
3. **Match entities:** crop names, state names, district names, dates (YYYY-MM-DD), metrics (rain, temperature, yield, etc.)
4. **Match intent:** filter, query, confirm, cancel, help, unknown
5. **Execute:** map intent to API call or UI action
6. **Respond:** generate TTS output + optional visual update

**Fallback hierarchy:**
- Exact entity match → execute
- Partial entity match + high-confidence intent → execute with confirmation
- High-confidence intent, no entity → execute with default context (current filter)
- Low-confidence intent → ask clarification
- No match → say "I don't understand" + offer help

---

## 4. Follow-Up Question Handling

The system maintains a **short-term context buffer** (last 3 turns) in-memory:

- **Anaphora resolution:** If user says "compare it with rice" after asking about wheat, "it" resolves to the most recently mentioned crop.
- **Ellipsis handling:** If user says "and temperature?" after asking about rainfall, the system assumes same time range and location as previous query.
- **Context decay:** Context buffer clears on filter change, condition switch, or after 60 seconds of silence.

**Example follow-up flow:**
```
User: "How is wheat doing in Punjab?"
System: "Wheat yield is 450 kg per hectare, 12% above average for the selected period."
User: "And rice?"
System: "Rice yield is 520 kg per hectare, 8% above average."
```

---

## 5. Clarification Handling

When the system detects low-confidence intent or ambiguous entities, it asks a **single, closed-ended clarification question**:

- **Ambiguous crop:** "Did you mean wheat or rice?"
- **Ambiguous location:** "Which district? Ludhiana or Amritsar?"
- **Ambiguous date:** "Which date? 2023-01-01 or 2023-02-01?"
- **Ambiguous metric:** "Do you mean rainfall or soil moisture?"

**Rule:** Maximum one clarification round per turn. If the user's response is still ambiguous, fall back to the most likely interpretation and state it explicitly: "I'll show you wheat in Punjab. Say 'no' to cancel."

---

## 6. Confirmation Handling

For **destructive or high-impact actions** (filter changes that remove data, reset all filters), the system asks for confirmation using a **yes/no prompt**:

```
User: "reset filters"
System: "This will clear all filters. Are you sure? Say yes or no."
User: "yes"
System: "Filters cleared."
```

For **non-destructive actions** (applying a new filter), the system applies immediately and confirms:
```
User: "show rice in Tamil Nadu"
System: "Showing rice in Tamil Nadu. 12 results found."
```

---

## 7. Error Recovery

### 7.1 Speech Recognition Errors

| Error type | System response |
|---|---|
| `no-speech` / timeout | "I didn't hear anything. Please try again." |
| `not-allowed` / permission denied | "Microphone access is blocked. Please enable it in your browser settings." |
| `network` / offline | "I'm having trouble hearing you. Please check your internet connection." |
| `aborted` / interrupted | (silent — user intentionally stopped) |

### 7.2 No Data / Empty Results

```
User: "show cotton in Rajasthan"
System: "No data found for cotton in Rajasthan. Try another crop or state."
```

### 7.3 Partial Understanding

If the system understands the intent but not all entities, it proceeds with what it knows and states the assumption:
```
User: "show wheat in..."
System: "Showing wheat for all states. Say a state name to narrow down."
```

---

## 8. Unknown-Question Handling

When the system cannot map a question to any known intent or entity, it responds with a **graceful fallback** and redirects to supported commands:

```
User: "What is the GDP of India?"
System: "I don't have that information. I can help with weather, rainfall, soil moisture, yield, and recommendations for your farm. Say 'help' for a list of questions."
```

**Rule:** Never say "I don't know" without offering an alternative path.

---

## 9. Multilingual Interaction

### 9.1 Language Selection

- User selects language from dropdown (8 languages: English, Hindi, Tamil, Telugu, Kannada, Marathi, Bengali)
- Selection persists in `localStorage`
- Both STT (`SpeechRecognition.lang`) and TTS (`speechSynthesis.lang`) use the same code

### 9.2 Code-Switching Support

The system accepts **mixed-language input** (e.g., Hindi + English agricultural terms like "wheat", "rainfall", "yield"). Entity matching is case-insensitive and language-agnostic for technical terms.

### 9.3 Fallback Behavior

- If browser does not support the selected language for STT/TTS, show a toast: "Voice in [language] is not supported by your browser. Using English instead."
- If STT returns low confidence (< 0.6), ask: "I think you said [transcript]. Is that correct?"

---

## 10. Text-to-Speech Responses

### 10.1 Voice Characteristics

- **Rate:** 0.9x default speed (slightly slower for low-literacy users)
- **Pitch:** default (1.0)
- **Volume:** 1.0
- **Voice selection:** prefer local-language voice if available; fall back to default system voice

### 10.2 Turn-Taking

- System speaks one **utterance** at a time
- User can interrupt at any time by speaking (system stops, listens to new input)
- Visual indicator: pulsing mic icon while listening, sound-wave animation while speaking

---

## 11. Voice Response Length and Complexity

### 11.1 Maximum Response Length

- **Ideal:** 1 sentence (15–25 words)
- **Maximum:** 3 sentences (40–60 words)
- **Exception:** Story narration mode (user explicitly requests "read story") allows up to 120 words, with pause points every 30 words

### 11.2 Complexity Rules

| Information type | Preferred format | Example |
|---|---|---|
| Numbers | Round to nearest whole number; use "about" for estimates | "About 55 millimeters of rain" |
| Percentages | Convert to plain comparisons | "Rainfall is down by 20 percent" |
| Dates | Relative rather than absolute | "Tomorrow morning" instead of "2024-09-15 06:00" |
| Comparisons | Use "more than" / "less than" / "same as" | "Soil moisture is less than normal" |
| Recommendations | Action-first, reason-second | "Irrigate tomorrow morning. Soil moisture is low." |
| Lists | Maximum 3 items; use "and" before last item | "Rain is expected, temperature will rise, and humidity will fall." |

### 11.3 Information Prioritization

When a query has multiple relevant answers, the system provides **one primary answer** and offers to elaborate:

```
User: "How is the weather?"
System: "It will rain tomorrow. Do you want the full forecast?"
User: "yes"
System: "Rain in the morning, 26 to 30 degrees, light wind."
```

---

## 12. Voice Response Policy

### 12.1 When to Use Numbers

- **Use:** KPIs, thresholds, percentages (when necessary for action)
- **Avoid:** Raw decimals, large integers, precision beyond 1 decimal place
- **Prefer:** "about 55 mm" over "54.7 mm"

### 12.2 When to Use Comparisons

- **Use:** Trend questions, yield comparisons, anomaly detection
- **Format:** "X is [higher/lower/same] than [reference] by [amount]"
- **Example:** "Rainfall is lower than last month by 20 percent."

### 12.3 When to Repeat Information

- **Repeat:** Recommendations, safety-critical advice (e.g., "Do not spray pesticide today")
- **Do not repeat:** Raw data points unless user asks again
- **Strategy:** Summarize at end of story narration: "Remember: irrigate tomorrow morning."

### 12.4 When to Ask Clarification

- **Ask:** When intent confidence < 0.7 OR when required entity is missing AND cannot be inferred from context
- **Do not ask:** For confirmation of obvious actions (e.g., "show wheat" when wheat is already selected)
- **Strategy:** One-shot clarification, then proceed with best guess

### 12.5 When to Use Icons/Visuals in Addition to Speech

| Condition | Visual support |
|---|---|
| Metric mentioned (rain, temperature, yield, etc.) | Highlight corresponding icon in legend |
| Trend direction mentioned | Show up/down arrow icon |
| Recommendation given | Show action icon (water drop for irrigate, spray for pesticide) |
| Forecast mentioned | Show calendar/day icons |
| Comparison mentioned | Show side-by-side icons |
| Error or empty state | Show large X icon with text fallback |

**Synchronization rule:** TTS and visual highlighting should be loosely coupled. If TTS is unavailable or cancelled, visuals alone must still convey the message.

---

## 13. Example Conversations (20+)

### Weather Queries

**Example 1: Basic weather outlook**
```
User: "What is the weather tomorrow?"
System: "Tomorrow, there is a 70 percent chance of rain. Temperature will be 26 to 30 degrees."
```

**Example 2: Rain-specific query**
```
User: "Will it rain tomorrow?"
System: "Yes, rain is expected tomorrow morning. Do not spray pesticides."
```

**Example 3: Temperature query**
```
User: "How hot will it be?"
System: "Temperature will be 34 degrees today. Work early morning to avoid heat."
```

### Forecast Comparison

**Example 4: Today vs. tomorrow**
```
User: "Is tomorrow hotter than today?"
System: "Tomorrow will be 2 degrees hotter. Today: 34 degrees. Tomorrow: 36 degrees."
```

**Example 5: Weekly comparison**
```
User: "How is this week compared to last week?"
System: "This week is drier. Rainfall is 30 percent lower than last week."
```

### Rainfall Questions

**Example 6: Monthly trend**
```
User: "How is the rainfall this month?"
System: "Rainfall is 20 percent below normal. The monsoon is slightly delayed."
```

**Example 7: Cumulative rainfall**
```
User: "How much rain fell this week?"
System: "About 45 millimeters of rain this week. Normal is 60 millimeters."
```

**Example 8: Rain vs. yield**
```
User: "Does rain affect yield?"
System: "Yes. More rain usually means higher yield. This season, low rainfall may reduce yield."
```

### Temperature Questions

**Example 9: Temperature trend**
```
User: "Is temperature rising?"
System: "Yes, temperature is rising. It is 2 degrees higher than last month."
```

**Example 10: Temperature and soil moisture**
```
User: "How does temperature affect soil moisture?"
System: "Higher temperature dries the soil. Soil moisture is decreasing as temperature rises."
```

### Trend Questions

**Example 11: Yield trend**
```
User: "Is yield improving?"
System: "Yield is stable. No significant change compared to last year."
```

**Example 12: Multi-metric trend**
```
User: "What is the trend for rainfall and temperature?"
System: "Rainfall is decreasing. Temperature is increasing. This is not ideal for crops."
```

### Follow-Up Questions

**Example 13: Ellipsis follow-up**
```
User: "How is wheat doing?"
System: "Wheat yield is 450 kg per hectare, 12 percent above average."
User: "And rice?"
System: "Rice yield is 520 kg per hectare, 8 percent above average."
```

**Example 14: Anaphora follow-up**
```
User: "Show me wheat in Punjab."
System: "Showing wheat in Punjab. 24 results found."
User: "What about the temperature there?"
System: "Average temperature in Punjab is 31 degrees."
```

**Example 15: Depth follow-up**
```
User: "Why did yield drop?"
System: "Yield dropped because rainfall was 30 percent below normal."
User: "What should I do?"
System: "Irrigate to compensate for low rainfall. Monitor soil moisture daily."
```

### Ambiguous Questions

**Example 16: Ambiguous crop**
```
User: "How is it doing?"
System: "Which crop do you mean? Say wheat, rice, or cotton."
```

**Example 17: Ambiguous metric**
```
User: "Is it high?"
System: "Do you mean temperature, rainfall, or soil moisture?"
```

**Example 18: Ambiguous location**
```
User: "Show me data for my district."
System: "Which district? Say the district name."
```

### Unsupported Questions

**Example 19: Out-of-domain question**
```
User: "What is the market price of wheat?"
System: "I don't have market price information. I can help with weather, rainfall, soil moisture, yield, and recommendations."
```

**Example 20: Too complex**
```
User: "Predict the yield for next season based on the last 5 years and El Niño."
System: "I can't predict future yield. I can show you past yield trends. Say 'yield trend' to see."
```

### Incorrect Speech Recognition

**Example 21: Low-confidence recognition**
```
User: "Show weat in Pendjab"
System: "I think you said 'show wheat in Punjab.' Is that correct?"
User: "yes"
System: "Showing wheat in Punjab. 24 results found."
```

**Example 22: Complete misinterpretation**
```
User: "Call my brother"
System: "I don't understand. I can help with weather, rainfall, soil moisture, yield, and recommendations. Say 'help' for more."
```

### Error Recovery

**Example 23: No data result**
```
User: "Show cotton in Rajasthan"
System: "No data found for cotton in Rajasthan. Try another crop or state."
```

**Example 24: Permission denied**
```
User: "show rice"
System: "Microphone access is blocked. Please enable it in your browser settings to use voice."
```

---

## 14. Conversation Flow Diagram (Textual)

```
User speaks
    |
    v
[STT] --> transcript
    |
    v
[Normalize + Tokenize]
    |
    v
[Intent + Entity Matching]
    |
    +-- Intent: filter, Entity: complete --> [Apply filter] --> [Confirm] --> [TTS response]
    |
    +-- Intent: filter, Entity: partial --> [Ask clarification] --> [User responds] --> loop back
    |
    +-- Intent: query --> [Compute answer] --> [Format response] --> [TTS + visual highlight]
    |
    +-- Intent: confirm/cancel --> [Execute] --> [TTS confirmation]
    |
    +-- Intent: help --> [List commands] --> [TTS help text]
    |
    +-- Intent: unknown --> [Graceful fallback] --> [TTS redirect + offer help]
```

---

## 15. Implementation Requirements

### 15.1 Frontend Hooks to Modify

- `use-voice-input.ts` — add intent parsing callback, context buffer, confirmation state
- `use-voice-output.ts` — add utterance queue, pause/resume, rate control
- `voice-intents.ts` — extend entity lists, add confidence scoring, add context resolver
- `voice-controls.tsx` — add confirmation UI, clarification UI, help modal

### 15.2 Backend Changes

- **None required** for MVRS. All intent parsing and conversation management is client-side.
- Future: move intent parsing to backend if command set grows beyond 20 patterns.

### 15.3 New Components

- `VoiceConfirmation.tsx` — yes/no prompt for destructive actions
- `VoiceClarification.tsx` — multiple-choice clarification UI
- `VoiceHelpModal.tsx` — lists all supported voice commands with examples

---

## 16. Validation Plan

1. **Wizard-of-Oz:** Human simulates voice system with 5 users; record actual vs. expected commands
2. **Command coverage test:** Verify all 20+ example conversations execute without error
3. **Edge-case test:** Empty results, permission denied, network loss, partial understanding
4. **Multilingual test:** Each supported language with 2 native speakers
5. **Accessibility test:** Screen reader compatibility, keyboard-only navigation for confirmation/clarification UI

---

## 17. Open Questions

1. **Should the system support wake-word activation?** Recommendation: No for MVRS. Manual mic button is sufficient and avoids always-on microphone concerns.
2. **Should voice commands support continuous conversation mode?** Recommendation: Yes, with 5-second silence timeout. User can say "stop" to end.
3. **Should the system speak icon labels when highlighting?** Recommendation: Yes, but only in voice-story condition. In voice-icons condition, speak only on explicit "read aloud" command.
