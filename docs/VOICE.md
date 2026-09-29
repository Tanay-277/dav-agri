# DAV — Voice Architecture & Multilingual Pipeline

DAV is designed from the ground up as a **voice-first** application for farmers speaking **Marathi (`mr`)**, **Hindi (`hi`)**, and **English (`en`)**.

---

## 1. Voice Interaction Lifecycle

```
 Mobile Microphone (or Browser)
               │
               ▼
   Client MediaRecorder API
   - Captures WAV / WebM audio
   - Streams audio bytes
               │
               ▼
   POST /api/v1/voice/transcribe
   - Validates audio size (< 15MB)
   - Validates audio magic headers
               │
               ▼
   Speech-To-Text Provider (STT)
   - Transcribes to Marathi / Hindi / English
   - Returns recognized text + confidence
               │
               ▼
   Query Intelligence Processing
   - Deterministic Analytics (factual calculations)
   - AI generates natural language explanation
               │
               ▼
   POST /api/v1/voice/synthesize
   - Text-To-Speech Provider (TTS)
   - Generates streaming audio/wav
               │
               ▼
   Client Audio Playback (HTML5 Audio)
```

---

## 2. Resilient Error Handling

The voice pipeline protects against:
* **Empty Audio (0 bytes):** Returns HTTP 400 with `Audio payload cannot be empty`.
* **Corrupted / Invalid Audio Header:** Returns HTTP 400 with `Unsupported audio format or corrupted file header`.
* **Oversized Audio (> 15MB):** Returns HTTP 400 with `Audio payload size exceeds 15MB limit`.
* **Microphone Permission Denied:** Handled on client with actionable user permissions alert.
* **Provider Failure / Offline Mode:** The provider abstraction gracefully falls back to local synthesis and deterministic rule engines.
