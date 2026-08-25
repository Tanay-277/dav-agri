# Voice-Interactive Data Storytelling System — Unified API

## Overview

This document describes the unified backend API for the Voice-Interactive Data Storytelling System for Rural/Low-Literacy Populations. The API integrates speech-to-text, natural-language understanding, data analytics, and text-to-speech into a single coherent service.

## Base URL

```
http://localhost:8000/api/v1/voice
```

## Authentication

No authentication is required for the MVP. All endpoints are open. Rate limiting is applied globally: 100 requests per 60 seconds per IP address.

## Content Type

All requests and responses use `application/json` unless otherwise specified (e.g., audio uploads use `multipart/form-data`).

## Error Format

Errors follow a consistent structure:

```json
{
  "detail": "Error message"
}
```

For validation errors:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "query"],
      "msg": "String should have at least 1 character",
      "input": ""
    }
  ]
}
```

## Endpoints

### 1. Health Check

`GET /health`

Returns service status, version, and capability information.

**Response:**

```json
{
  "status": "ok",
  "version": "0.1.0",
  "dataset_loaded": true,
  "dataset_rows": 600,
  "supported_languages": ["en", "hi", "ta", "te", "kn", "mr", "bn"],
  "stt_providers": ["MockSpeechProvider"],
  "tts_providers": ["MockTTSProvider"]
}
```

---

### 2. Locations

`GET /locations`

Returns available states, districts, and crops from the dataset.

**Response:**

```json
{
  "states": ["Punjab", "Maharashtra", "Karnataka", ...],
  "districts": ["Punjab", "Maharashtra", "Karnataka", ...],
  "crops": ["Wheat", "Rice", "Cotton", ...]
}
```

---

### 3. Weather

`GET /weather`

Returns current weather KPIs for the given filters.

**Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `crop` | string | Optional crop filter |
| `state` | string | Optional state filter |
| `district` | string | Optional district filter |
| `start_date` | string | Optional start date (YYYY-MM-DD) |
| `end_date` | string | Optional end date (YYYY-MM-DD) |

**Response:**

```json
{
  "filters": {"crop": "Wheat", "state": "Punjab"},
  "kpis": [
    {
      "label": "Average Rainfall",
      "value": 45.2,
      "unit": "mm",
      "change": -12.5,
      "change_label": "vs last month"
    }
  ],
  "rows": 24
}
```

---

### 4. Forecast

`GET /forecast`

Returns forecast KPIs for the given filters.

**Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `crop` | string | Optional crop filter |
| `state` | string | Optional state filter |
| `district` | string | Optional district filter |
| `days` | integer | Forecast horizon (1-30, default 7) |

**Response:**

```json
{
  "filters": {"crop": "Wheat", "state": "Punjab"},
  "kpis": [...],
  "forecast_days": 7
}
```

---

### 5. Natural-Language Query

`POST /query`

Submits a text query and returns structured query results, insights, and optional speech response.

**Request Body:**

```json
{
  "query": "Will it rain tomorrow?",
  "language": "en",
  "context": {}
}
```

**Response:**

```json
{
  "structured_query": {
    "intent": "forecast",
    "entities": {},
    "time_period": {
      "start": "2026-08-22",
      "end": "2026-08-22",
      "relative": "tomorrow",
      "is_historical": false,
      "is_future": true
    },
    "variables": ["rainfall_mm"],
    "comparison": null,
    "language": "en",
    "output_type": "summary",
    "confidence": 0.9,
    "needs_clarification": false,
    "clarification_options": [],
    "raw_query": "Will it rain tomorrow?",
    "ambiguity_reasons": [],
    "unsupported_reason": null
  },
  "insights": [
    {
      "type": "current_conditions",
      "metric": "rainfall",
      "message": "Current rainfall is 13.4mm.",
      "severity": "info",
      "magnitude": 13.4,
      "result": {"value": 13.4, "unit": "mm"},
      "confidence": 1.0,
      "source": "rule"
    }
  ],
  "speech_response": null,
  "message": "Processed query: Will it rain tomorrow?"
}
```

---

### 6. Voice Query

`POST /voice-query`

Uploads an audio file, transcribes it, processes the query, and returns results.

**Content-Type:** `multipart/form-data`

**Form Fields:**

| Field | Type | Description |
|---|---|---|
| `audio` | file | Audio file (WAV, MP3, OGG, WEBM, M4A, FLAC) |
| `language` | string | BCP-47 language code (default: "en") |
| `auto_detect` | boolean | Auto-detect language (default: false) |
| `noise_level` | string | Noise level: clean, low, medium, high (default: "clean") |

**Response:**

```json
{
  "structured_query": {...},
  "transcript": "Will it rain tomorrow?",
  "normalized_transcript": "will it rain tomorrow",
  "stt_confidence": 0.92,
  "insights": [...],
  "speech_response": null,
  "message": "Voice query processed"
}
```

---

### 7. Structured Insight

`GET /insight`

Returns structured insights for the given filters.

**Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `crop` | string | Optional crop filter |
| `state` | string | Optional state filter |
| `district` | string | Optional district filter |
| `start_date` | string | Optional start date |
| `end_date` | string | Optional end date |

**Response:**

```json
[
  {
    "type": "current_conditions",
    "metric": "rainfall",
    "message": "Current rainfall is 13.4mm.",
    "severity": "info",
    "magnitude": 13.4,
    "result": {"value": 13.4, "unit": "mm"},
    "confidence": 1.0,
    "source": "rule"
  }
]
```

---

### 8. Speech Response

`POST /speech-response`

Converts a structured insight to localized speech audio.

**Request Body:**

```json
{
  "insight": {
    "type": "current_weather",
    "location": "Punjab",
    "value": 32,
    "values": {"rain_probability": 20, "rainfall": 10}
  },
  "language": "en",
  "voice_gender": "female",
  "rate": 1.0
}
```

**Response:**

```json
{
  "text": "Current weather in Punjab: 32 degrees. Rain probability is 20 percent.",
  "language": "en",
  "audio_url": null,
  "audio_bytes": null,
  "content_type": "audio/mpeg",
  "duration_ms": 0,
  "provider": "mock",
  "success": true,
  "message": "Speech response generated"
}
```

---

## End-to-End Scenarios

### Scenario 1: "Will it rain tomorrow?"

```bash
curl -X POST "http://localhost:8000/api/v1/voice/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Will it rain tomorrow?", "language": "en"}'
```

**Expected:** `intent: forecast`, `time_period.relative: tomorrow`, insights with rain probability.

### Scenario 2: "Is tomorrow hotter than today?"

```bash
curl -X POST "http://localhost:8000/api/v1/voice/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Is tomorrow hotter than today?", "language": "en"}'
```

**Expected:** `intent: comparison`, comparison insights.

### Scenario 3: Supported question in another language

```bash
curl -X POST "http://localhost:8000/api/v1/voice/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Kya kal barish hogi?", "language": "hi"}'
```

**Expected:** `intent: forecast`, `language: hi`, insights in Hindi context.

### Scenario 4: Ambiguous question

```bash
curl -X POST "http://localhost:8000/api/v1/voice/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Weather?", "language": "en"}'
```

**Expected:** `needs_clarification: true`, `clarification_options` populated.

### Scenario 5: Unsupported question

```bash
curl -X POST "http://localhost:8000/api/v1/voice/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the stock price of wheat?", "language": "en"}'
```

**Expected:** `intent: unsupported`, `unsupported_reason` populated.

---

## Numerical Consistency

Numerical values flow through the system without modification:

1. **Data Retrieval**: Raw values from dataset (e.g., `rainfall: 13.4mm`)
2. **Analytics**: Computed KPIs and insights preserve exact values
3. **Structured Insight**: `result.value` and `magnitude` fields contain raw numbers
4. **Response Generation**: Template inserts `normalize_number(value)` which formats but does not alter the value
5. **TTS**: Text-to-speech reads the formatted string; no numerical transformation occurs

No generative model (LLM) is involved in numerical processing. All arithmetic is deterministic.

## API Documentation

Interactive API documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Rate Limiting

Global rate limit: 100 requests per 60 seconds per IP address. Exceeding the limit returns HTTP 429.

## Logging

All requests are logged with:
- Request ID
- Method and path
- Client IP
- Processing duration
- Errors (if any)

Logs are output in JSON format via the `agristory.request` logger.

## CORS

CORS is configured to allow origins from `settings.CORS_ORIGINS` (default: `http://localhost:5173`, `http://127.0.0.1:5173`).
