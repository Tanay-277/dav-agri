# WER Testing Protocol

## Purpose

To measure Word Error Rate (WER) of the Web Speech API for target languages and accents before the pilot study. This determines whether voice interaction is feasible or whether backend STT (Whisper) is required.

## Background

Word Error Rate (WER) is calculated as:

WER = (S + D + I) / N

Where:
- S = number of substitutions (wrong word)
- D = number of deletions (missing word)
- I = number of insertions (extra word)
- N = total number of words in reference

**Benchmarks:**
- WER ≤ 15%: Excellent — usable without modification
- WER 15–25%: Good — usable with clarification prompts
- WER 25–35%: Marginal — requires backend STT or significant UX adaptation
- WER > 35%: Unusable — must switch to backend STT

---

## Equipment

- Chrome browser on Android device (same device type as pilot)
- Quiet room (ambient noise < 40 dB)
- External microphone (optional, for baseline comparison)
- Test script printed in target language
- Recording device (to capture both system output and participant speech)

---

## Participants

| Group | N | Criteria |
|---|---|---|
| WER testers | 10 per language | Native speakers; 25–65 years; farming background preferred |

**Recruitment:** Separate from pilot participants to avoid learning transfer.

---

## Test Sentences

### English (calibration only)

1. "Show me wheat data for Punjab."
2. "What is the rainfall this month?"
3. "Is the soil moisture high or low?"
4. "Tell me the yield for rice in Karnataka."
5. "Should I irrigate now?"

### Hindi (हिंदी)

1. "गेहूं का डेटा पंजाब के लिए दिखाओ।"
2. "इस महीने की बारिश कितनी है?"
3. "मिट्टी की नमी कम है या ज्यादा?"
4. "कर्नाटक में चावल की पैदावार बताओ।"
5. "क्या मुझे अभी सिंचाई करनी चाहिए?"

### Kannada (ಕನ್ನಡ)

1. "ಗೋಧಿ ದತ್ತಾಂಶವನ್ನು ಪಂಜಾಬ್ ಗೆ ತೋರಿಸಿ."
2. "ಈ ತಿಂಗಳ ವರ್ಷಾವಾರಿ ಎಷ್ಟು?"
3. "ಮಣ್ಣಿನ ಆರ್ದ್ರತೆ ಕಡಿಮೆಯೇ ಅಥವಾ ಹೆಚ್ಚು?"
4. "ಕರ್ನಾಟಕದಲ್ಲಿ ಅಕ್ಕಿ ಇಳುವರಿ ಹೇಳಿ."
5. "ನನಗೆ ಇದಗೆ ನೀರು ಹಾಕಬೇಕಾ?"

### Tamil (தமிழ்)

1. "கோதுமை தரவு பஞ்சாபிற்கு காட்டு."
2. "இந்த மாத ஏற்ற precipitation எத்தனை?"
3. "மண் ஈரப்பதம் குறைவா அதிகமா?"
4. "கர்நாடகாவில் அரிசி உற்பத்தி சொல்லு."
5. "நான் இப்போ நீர்ப்பாசனம் செய்ய வேணா?"

### Telugu (తెలుగు)

1. "గోధుమల తొలగింపు పంజాబ్ కోసం చూపించు."
2. "ఈ నెల వర్షపాతం ఎంత?"
3. "నేల ఆర్ద్రత తక్కువగా ఉంది లేక ఎక్కువగా?"
4. "కర్ణాటకలో అక్కు దిగుబడి చెప్పు."
5. "నాకు ఇప్పుడు నీటిపారుదల చేయాలా?"

### Marathi (मराठी)

1. "गव्हाची माहिती पंजाब साठी दाखवा."
2. "या महिन्याचा पાઉસ/वर्षा किती आहे?"
3. "मृदा आर्द्रता कमी आहे की जास्त?"
4. "कर्नाटकमध्ये भाताचे उत्पादन सांगा."
5. "मला आता आपूkary करावे का?"

### Bengali (বাংলা)

1. "গমের তথ্য পাঞ্জাবের জন্য দেখাও।"
2. "এই মাসের বৃষ্টি কত?"
3. "মাটির আর্দ্রতা কম না বেশি?"
4. "কর্নাটকায় ধানের উৎপাদন বলো।"
5. "আমাকে এখন সেচ করা দরকার?"

*Note: Sentences should be reviewed by native speakers for naturalness before testing.*

---

## Protocol

### Step 1: Setup (5 minutes per participant)

1. Open Chrome browser on test device
2. Navigate to test page (simple page with microphone button and transcript display)
3. Set language selector to target language
4. Explain task: "I will show you sentences. Please read each one aloud when I point to it."
5. Obtain consent for recording

### Step 2: Calibration (2 minutes)

1. Ask participant to read one sentence in their language
2. Verify microphone is working
3. Adjust microphone distance (10–15 cm from mouth)
4. If WER > 50% on calibration sentence, adjust device or environment

### Step 3: Test (15 minutes)

1. Present sentences one at a time
2. Participant reads each sentence aloud
3. System transcribes via Web Speech API
4. Facilitator records:
   - Reference transcript (correct text)
   - System transcript (what system heard)
   - Time to transcribe
   - Whether participant self-corrected

### Step 4: Calculation

For each sentence:
1. Compare reference vs. system transcript
2. Count S, D, I
3. Calculate WER per sentence
4. Calculate overall WER

---

## Data Collection Form

| Participant ID | Language | Sentence | Reference | System Output | S | D | I | WER | Self-corrected |
|---|---|---|---|---|---|---|---|---|---|
| | | 1 | | | | | | | |
| | | 2 | | | | | | | |
| | | 3 | | | | | | | |
| | | 4 | | | | | | | |
| | | 5 | | | | | | | |

**Overall WER:** ___ %

---

## Decision Matrix

| WER | Decision |
|---|---|
| ≤ 20% for ≥5/7 languages | Proceed with current voice implementation |
| 20–30% for ≥5/7 languages | Add clarification prompts; pilot with prompts |
| > 30% for majority | Evaluate backend STT (Whisper) or reduce voice dependency |

---

## Reporting

Report per language:
- Mean WER
- Median WER
- 95% CI
- Common error types (substitutions, deletions, insertions)
- Failure rate (sentences with WER = 100%)

Report overall:
- Pass/fail for each language
- Recommendation for each condition
