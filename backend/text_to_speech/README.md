# Text-to-Speech Layer

## Overview

This module provides a multilingual text-to-speech (TTS) layer for the agricultural analytics dashboard. It converts structured insights from the deterministic analytics engine into natural, localized speech output.

Supported languages (Module 1 selection):
- English (en)
- Hindi (hi)
- Tamil (ta)
- Telugu (te)
- Kannada (kn)
- Marathi (mr)
- Bengali (bn)

## Architecture

```
text_to_speech/
├── __init__.py           # Public API exports
├── schemas.py            # Pydantic request/response models
├── languages.py          # Language configuration and voice mapping
├── templates.py          # Response templates for each insight type
├── normalizer.py         # Number/unit normalization for TTS
├── provider.py           # Abstract provider + Mock + EdgeTTS implementations
├── engine.py             # High-level engine: structured insight → localized text → audio
├── api.py                # FastAPI router for /api/v1/tts/*
├── dataset.py            # Test dataset helpers
├── test_dataset.json     # Pronunciation test phrases
└── README.md             # This file
```

## Pipeline

```
Structured Insight (JSON)
    ↓
Human-readable response (templates + values)
    ↓
Localized response (number/unit normalization, language-specific terms)
    ↓
Speech synthesis (TTS provider)
    ↓
Audio output (MP3 bytes / URL)
```

## Response Templates

Templates are defined for each `InsightType` in all 7 supported languages. Numerical values originate from the structured insight and are inserted via string formatting. No generative model modifies numerical facts.

| Insight Type | Template Placeholders |
|---|---|
| `current_weather` | `{location}`, `{temperature}`, `{rain_probability}` |
| `forecast` | `{location}`, `{temperature_min}`, `{temperature_max}`, `{rain_probability}` |
| `rain_probability` | `{location}`, `{rain_probability}`, `{rainfall}` |
| `temperature` | `{location}`, `{temperature}`, `{temperature_feeling}` |
| `comparison` | `{location_a}`, `{location_b}`, `{metric}`, `{value_a}`, `{value_b}`, `{difference}` |
| `trend` | `{metric}`, `{direction}`, `{magnitude}`, `{period}` |
| `warning` | `{message}`, `{action}` |
| `clarification` | `{question}`, `{options}` |
| `unsupported` | (no placeholders) |
| `recommendation` | `{action}`, `{reason}` |
| `yield_report` | `{crop}`, `{location}`, `{yield_value}`, `{comparison}` |
| `soil_moisture` | `{location}`, `{moisture_value}`, `{status}` |

### Design Principles

1. **Short**: Responses are 1-2 sentences maximum
2. **Clear**: Simple sentence structure, no complex clauses
3. **Natural when spoken**: Avoids abbreviations, uses conversational phrasing
4. **Appropriate for target user**: Uses familiar agricultural terminology
5. **Numerically accurate**: Numbers come directly from structured insight, never altered
6. **Localized**: All non-numeric text is translated

## Provider Abstraction

The `TTSProvider` base class defines the contract:

```python
class TTSProvider(ABC):
    @abstractmethod
    async def synthesize(self, request: SynthesisRequest) -> SynthesisResponse:
        ...

    @abstractmethod
    def supports_language(self, language: str) -> bool:
        ...
```

Two implementations are included:

1. **MockTTSProvider** — Generates placeholder audio bytes for testing. Returns silent audio payloads with metadata about the requested synthesis.

2. **EdgeTTSProvider** — Uses Microsoft Edge's free TTS service (`edge-tts`). Supports all 7 languages with high-quality neural voices. Requires `pip install agristory-backend[tts]`.

Providers are registered via `register_tts_provider()` and resolved via `get_tts_provider(name=None)`.

## Number and Unit Handling

### Number Normalization

Numbers are formatted with locale-appropriate commas for readability:
- `1234` → `"1,234"`
- `1234.5` → `"1,234.50"`

The TTS engine then reads these as digits. For languages that require spelled-out numbers, extend `normalize_number()`.

### Unit Expansion

Before synthesis, abbreviated units are expanded for clarity:
- `mm` → `"millimeters"`
- `kg` → `"kilograms"`
- `km/h` → `"kilometers per hour"`

This ensures the TTS engine pronounces units correctly rather than spelling out abbreviations.

## Language Selection

- Languages are specified via BCP-47 codes (e.g., `en`, `hi-IN`, `ta-IN`)
- Unsupported languages fall back to English
- Each language has configured neural voices for male and female speech

### Voice Configuration

| Language | Female Voice | Male Voice |
|---|---|---|
| English | `en-IN-NeerjaNeural` | `en-IN-PrabhatNeural` |
| Hindi | `hi-IN-SwaraNeural` | `hi-IN-MadhurNeural` |
| Tamil | `ta-IN-PallaviNeural` | `ta-IN-ValluvarNeural` |
| Telugu | `te-IN-MohanNeural` | `te-IN-MohanNeural` |
| Kannada | `kn-IN-SapnaNeural` | `kn-IN-GaganNeural` |
| Marathi | `mr-IN-AarohiNeural` | `mr-IN-ManoharNeural` |
| Bengali | `bn-IN-TanishaaNeural` | `bn-IN-PrabirNeural` |

## API Endpoints

Registered under `/api/v1/tts`:

- `GET /languages` — List supported languages and provider capabilities
- `POST /localize` — Convert structured insight to localized text (no audio)
- `POST /synthesize` — Convert structured insight to localized audio
- `POST /synthesize-text` — Convert raw text to audio

### Example Request

```bash
curl -X POST "http://localhost:8000/api/v1/tts/synthesize" \
  -H "Content-Type: application/json" \
  -d '{
    "insight": {
      "type": "current_weather",
      "location": "Punjab",
      "value": 32,
      "values": {"rain_probability": 20, "rainfall": 10}
    },
    "language": "en",
    "voice_gender": "female"
  }'
```

## Text Normalization

Raw insight text is normalized before synthesis:

1. **Whitespace collapse**: Multiple spaces → single space
2. **Unit expansion**: `mm` → `millimeters`, `kg` → `kilograms`
3. **Trimming**: Remove leading/trailing whitespace

Numbers are preserved as digits with commas for TTS engines that handle digit pronunciation well (e.g., EdgeTTS).

## Error Handling

Error codes returned via `TTSProviderError`:

| Code | Description |
|---|---|
| `EMPTY_TEXT` | Text to synthesize is empty |
| `LANGUAGE_NOT_SUPPORTED` | Language not in supported set |
| `PROCESSING_ERROR` | Generic synthesis failure |
| `AUDIO_TOO_LONG` | Text exceeds maximum length (5000 chars) |

## Test Dataset

Pronunciation test phrases are stored in `test_dataset.json` and loaded by `dataset.py`. Coverage includes:

- **Weather terms**: rain, temperature, yield, soil moisture, humidity
- **Numerical values**: 55 millimeters, 30 degrees, 70 percent, 25 kg per hectare
- **Locations**: Punjab, Maharashtra, Tamil Nadu, Karnataka
- **Directions**: increasing, decreasing
- **Actions**: warning, recommendation

## Testing Pronunciation and Intelligibility

To test pronunciation with the EdgeTTS provider:

```bash
pip install agristory-backend[tts]
```

Then run:

```python
from text_to_speech.provider import EdgeTTSProvider, register_tts_provider
from text_to_speech.schemas import SynthesisRequest, VoiceGender

register_tts_provider(EdgeTTSProvider())

import asyncio

async def test():
    provider = EdgeTTSProvider()
    phrases = [
        ("en", "Rainfall is 55 millimeters today."),
        ("hi", "Barish ki sambhavana 55 percent hai."),
        ("ta", "Mazhai eivvathu 55 satam."),
    ]
    for lang, text in phrases:
        response = await provider.synthesize(
            SynthesisRequest(text=text, language=lang, voice_gender=VoiceGender.FEMALE)
        )
        if response.success:
            print(f"[{lang}] OK: {response.duration_ms}ms")
        else:
            print(f"[{lang}] FAIL: {response.message}")

asyncio.run(test())
```

### Manual Evaluation Checklist

For each language, verify:
1. Weather terms are pronounced clearly (rain, temperature, humidity, soil moisture)
2. Numerical values are intelligible (e.g., "55 millimeters" not "five five millimeters")
3. Location names are pronounced correctly
4. Agricultural terms (yield, production, irrigation) are understandable
5. Speech rate is appropriate for low-literacy users (0.9x–1.0x)

## Limitations

1. **EdgeTTS requires internet.** The `edge-tts` library streams audio from Microsoft's servers. Offline TTS is not supported by this provider.

2. **Number pronunciation is digit-by-digit.** The current implementation outputs numbers as digits (e.g., "55" is read as "fifty-five" by most TTS engines, but some may read it as "five five"). For languages where this is problematic, extend `normalize_number()` to spell out numbers.

3. **No SSML support.** The current API does not support Speech Synthesis Markup Language. For advanced pronunciation control (e.g., `<say-as>` for numbers), the provider would need to accept SSML input.

4. **Voice availability depends on EdgeTTS updates.** Voice names are hardcoded based on current EdgeTTS offerings. If Microsoft adds or removes voices, the configuration may need updating.

5. **No streaming.** The entire audio file is generated before being returned. For long responses, this may cause latency.

6. **No caching.** Each synthesis request generates new audio. For repeated insights (e.g., same weather query), add a caching layer.

7. **Limited dialect support.** The 7 languages use generic Indian-region voices. Dialect-specific variations (e.g., Punjabi vs. Haryanvi Hindi) are not distinguished.

8. **Backend TTS is optional.** The frontend uses browser-native `speechSynthesis` as the primary TTS. This backend module is for audio file generation, download, or devices without browser TTS.

## Dependencies

Install TTS support:

```bash
pip install agristory-backend[tts]
```

Or install directly:

```bash
pip install edge-tts==6.1.9
```

## Future Work

- Add SSML support for precise pronunciation control
- Add audio caching for repeated insights
- Add streaming synthesis for long responses
- Measure real intelligibility with native speakers
- Add dialect-specific voice selection
- Add offline TTS fallback (e.g., pyttsx3 or coqui-ai TTS)
