# Speech-to-Text Layer

## Overview

This module provides a pluggable speech-to-text (STT) layer for the agricultural analytics dashboard. It is designed for rural/low-literacy users and supports the languages selected in Module 1:

- English (en)
- Hindi (hi)
- Tamil (ta)
- Telugu (te)
- Kannada (kn)
- Marathi (mr)
- Bengali (bn)

## Architecture

```
speech_to_text/
├── __init__.py           # Public API exports
├── schemas.py            # Pydantic request/response models
├── languages.py          # Language configuration and mapping
├── normalizer.py         # Transcript normalization for NLU
├── provider.py           # Abstract provider + Mock + Whisper implementations
├── integration.py        # High-level engine connecting STT → NLU
├── api.py                # FastAPI router for /api/v1/speech/*
├── metrics.py            # WER and alignment utilities
├── dataset.py            # Test dataset helpers
├── test_dataset.json     # Representative spoken queries
└── README.md             # This file
```

## Provider Abstraction

The `SpeechProvider` base class defines the contract:

```python
class SpeechProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, request: TranscriptionRequest) -> TranscriptionResponse:
        ...

    @abstractmethod
    def supports_language(self, language: str) -> bool:
        ...
```

Two implementations are included:

1. **MockSpeechProvider** — Deterministic simulation for testing. Uses SHA-256 of audio bytes to select a reference transcript from the test dataset, then applies configurable noise models (clean/low/medium/high) to simulate substitution, deletion, and insertion errors.

2. **WhisperSpeechProvider** — Real OpenAI Whisper integration via `faster-whisper`. Loads a small model on CPU with int8 quantization. Requires the `faster-whisper` package.

Providers are registered via `register_speech_provider()` and resolved via `get_speech_provider(name=None)`.

## Audio Input Handling

- Supported formats: WAV, MP3, OGG, WEBM, M4A, FLAC
- Maximum size: 50 MB
- Empty audio is rejected with `EMPTY_AUDIO` error
- Oversized audio is rejected with `AUDIO_TOO_LONG` error

## Language Selection and Detection

- Users select a language via the `language` field in `TranscriptionRequest`
- Supported codes: `en`, `hi`, `ta`, `te`, `kn`, `mr`, `bn` (and BCP-47 variants like `hi-IN`)
- `auto_detect_language=True` passes the language hint to the provider but allows auto-detection
- If a language is not supported, the system falls back to English and sets `detected_language` to the original code

## Noise and Error Handling

The `NoiseLevel` enum controls simulated noise in the mock provider:

| Level | Substitution | Deletion | Insertion |
|-------|-------------|----------|-----------|
| clean | 2% | 1% | 1% |
| low | 8% | 3% | 3% |
| medium | 18% | 8% | 6% |
| high | 30% | 15% | 10% |

Error codes returned via `SpeechRecognitionError`:

- `EMPTY_AUDIO` — Zero-byte upload
- `AUDIO_TOO_LONG` — Exceeds 50 MB
- `NO_SPEECH` — No speech detected in audio
- `LANGUAGE_NOT_SUPPORTED` — Language not in supported set
- `PROCESSING_ERROR` — Generic transcription failure

## Confidence Information

- `SpeechRecognitionResult.confidence` — Overall confidence (0.0–1.0)
- `RecognitionSegment.confidence` — Per-segment confidence
- Mock provider estimates confidence based on word overlap and noise model
- Whisper provider uses average log probability across segments

## Normalization

Raw STT output is normalized before passing to the NLU engine:

1. Remove filler words: "please", "can you", "tell me", "um", "uh", etc.
2. Remove punctuation
3. Collapse whitespace
4. Lowercase

## NLU Integration

`SpeechToTextEngine.process_audio()` returns a dict containing:

```python
{
    "success": bool,
    "transcript": str | None,
    "normalized_transcript": str | None,
    "language": str,
    "confidence": float,
    "nlu_result": StructuredQuery | None,
    "error": str | None,
    "provider": str,
    "processing_time_ms": int,
}
```

If an `nlu_engine` is provided, the normalized transcript is automatically parsed and the `StructuredQuery` result is included.

## API Endpoints

Registered under `/api/v1/speech`:

- `GET /languages` — List supported languages and provider capabilities
- `POST /transcribe` — Upload audio and receive transcription

## Test Dataset

Representative spoken queries are stored in `test_dataset.json` and loaded by `dataset.py`. Coverage includes:

- **Weather**: "What is the weather in Punjab", "Velli ennatha", "Hava kasa ahe"
- **Rain**: "Will it rain tomorrow", "Kya kal barish hogi", "Naalai mazhai peirum"
- **Temperature**: "How hot is it today", "Punjab mein temperature kya hai"
- **Forecast**: "Will it rain tomorrow", "Naalai mavagadi vastundha"
- **Comparisons**: "Compare tomorrow with today", "Kal aaj se thanda hoga"
- **Follow-up questions**: "And rice yield?", "Goroo hogayta ideya"

## WER Measurement

Word Error Rate is computed using Levenshtein distance at the word level:

```
WER = (S + D + I) / N
```

Where S = substitutions, D = deletions, I = insertions, N = reference word count.

The `metrics.py` module provides:

- `wer(reference, hypothesis)` — Returns float 0.0–1.0
- `wer_details(reference, hypothesis)` — Returns breakdown dict
- `compute_batch_wer(results)` — Aggregate statistics over multiple pairs

## Limitations

1. **Browser-native STT is not implemented here.** This backend module does not use the Web Speech API. Frontend voice capture must upload audio files to `/api/v1/speech/transcribe`.

2. **Whisper requires manual installation.** The `faster-whisper` package is not included in `requirements.txt`. Install it separately if you want real ASR:
   ```bash
   pip install faster-whisper
   ```

3. **Language support is limited to tested languages.** We do not claim support for languages outside the 7 listed above. The mock provider will accept any language code but only the 7 supported languages have test datasets and language configs.

4. **Accent and dialect coverage is limited.** The test dataset uses standardized spoken forms. Rural accents, code-switching, and dialectal variations may increase WER beyond simulated levels.

5. **WER is simulated for mock provider.** The mock provider uses a noise model to corrupt reference transcripts. Real WER depends on the actual Whisper model, audio quality, speaker accent, and background noise.

6. **No real-time streaming.** The current implementation processes complete audio files. For streaming/continuous recognition, the provider interface would need extension.

7. **No custom vocabulary/grammar.** The system does not support domain-specific grammar constraints (e.g., forcing crop/state names). This could improve accuracy but is not implemented.

8. **No speaker diarization.** Single-speaker queries are assumed.

9. **No offline mode on backend.** Whisper inference requires the model to be loaded in memory. For true offline capability, consider a frontend-only Web Speech API approach.

## Testing

Run the STT test suite:

```bash
pytest tests/test_speech_to_text.py -v
```

Run WER evaluation against the test dataset:

```python
from speech_to_text.metrics import wer, compute_batch_wer
from speech_to_text.dataset import get_test_queries

queries = get_test_queries("en")
# Simulate hypothesis with noise and compute WER
```

## Future Work

- Add VAD (Voice Activity Detection) to trim silence
- Add streaming transcription support
- Add domain-specific vocabulary boosting
- Measure real WER with native speakers for each language
- Add speaker diarization for multi-user scenarios
