# DAV — REST API Specification (`/api/v1`)

All endpoints are versioned under `/api/v1/` and return a standard `APIResponse[T]` envelope:
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```
Or upon error:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable explanation",
    "details": { ... }
  }
}
```

---

## 1. Authentication (`/api/v1/auth/*`)

### 1.1 Request Phone OTP
* **Method:** `POST`
* **Path:** `/api/v1/auth/phone/request-otp`
* **Request Body:**
  ```json
  { "phone": "86524525856" }
  ```
* **Response (200 OK):**
  ```json
  {
    "success": true,
    "data": {
      "phone": "86524525856",
      "expires_in_seconds": 300,
      "message": "OTP sent successfully"
    }
  }
  ```

### 1.2 Verify Phone OTP
* **Method:** `POST`
* **Path:** `/api/v1/auth/phone/verify-otp`
* **Request Body:**
  ```json
  { "phone": "86524525856", "otp": "44444" }
  ```
* **Response (200 OK):**
  ```json
  {
    "success": true,
    "data": {
      "access_token": "eyJhbGciOiJIUzI1NiIs...",
      "token_type": "bearer",
      "user_id": "usr_demo_raj_patil",
      "phone": "86524525856",
      "onboarding_completed": true,
      "preferred_language": "mr"
    }
  }
  ```

### 1.3 Get Current User Session
* **Method:** `GET`
* **Path:** `/api/v1/auth/me`
* **Headers:** `Authorization: Bearer <TOKEN>`
* **Response (200 OK):** Returns current user details and onboarding flag.

---

## 2. Onboarding (`/api/v1/onboarding/*`)

### 2.1 Get Status
* **Method:** `GET`
* **Path:** `/api/v1/onboarding/status`
* **Headers:** `Authorization: Bearer <TOKEN>`

### 2.2 Confirm Language
* **Method:** `POST`
* **Path:** `/api/v1/onboarding/confirm-language`
* **Headers:** `Authorization: Bearer <TOKEN>`
* **Request Body:** `{ "language": "mr" }`

### 2.3 Complete Onboarding
* **Method:** `PUT`
* **Path:** `/api/v1/onboarding`
* **Headers:** `Authorization: Bearer <TOKEN>`
* **Request Body:**
  ```json
  { "voice_confirmed": true, "onboarding_completed": true }
  ```

---

## 3. Profile (`/api/v1/profile/*`)

### 3.1 Get Profile
* **Method:** `GET`
* **Path:** `/api/v1/profile`
* **Headers:** `Authorization: Bearer <TOKEN>`
* **Response (200 OK):**
  ```json
  {
    "success": true,
    "data": {
      "id": "prof_demo_raj_patil",
      "user_id": "usr_demo_raj_patil",
      "name": "Raj Patil",
      "location": "Pune, MH",
      "age": 42,
      "land_location": "Plot No. 124/2, Kothrud",
      "primary_crop": "Cotton",
      "land_size": "20 acres",
      "irrigation_type": "Rain Fed",
      "livestock": "Cow, Goat, Buffalo",
      "crops_grown": ["Cotton", "Wheat", "Ragi"],
      "preferred_language": "mr"
    }
  }
  ```

### 3.2 Update Profile
* **Method:** `PUT`
* **Path:** `/api/v1/profile`
* **Headers:** `Authorization: Bearer <TOKEN>`
* **Request Body:** Partial profile updates.

---

## 4. Farm & Analytics (`/api/v1/farm/*`)

* `GET /api/v1/farm/crops`: List supported agricultural crops.
* `GET /api/v1/farm/summary`: Aggregated dashboard metrics for current farmer.
* `POST /api/v1/farm/production`: Record new harvest yield.
* `GET /api/v1/farm/production`: List historical yields (optional `?crop_id=...`).
* `POST /api/v1/farm/expenses`: Record farm expenditure.
* `GET /api/v1/farm/expenses`: List farm expenses.
* `GET /api/v1/farm/expenses/breakdown`: Deterministic category breakdown (Labor, Seeds, Fertilizer, Pesticides).
* `GET /api/v1/farm/analytics/crop-income`: Multi-month crop revenue trend lines.
* `GET /api/v1/farm/conversations`: Recent voice and query dialogues.

---

## 5. Weather (`/api/v1/weather/*`)

* `GET /api/v1/weather/current`: Current agricultural weather, expected rainfall (e.g. 40mm), intensity droplets, and irrigation advisory.
* `GET /api/v1/weather/forecast`: 24-hour agricultural time slots (Morning, Afternoon, Evening, Night).

---

## 6. Query & Intelligence (`/api/v1/query/*`)

* `POST /api/v1/query`: Process text/voice query, return structured chart JSON + AI explanation.
* `GET /api/v1/query/history`: List recent queries.
* `GET /api/v1/query/share/{token}`: Public deep-link sharing endpoint for verified charts.

---

## 7. Voice (`/api/v1/voice/*`)

* `POST /api/v1/voice/transcribe`: Ingests multipart audio file (`file: UploadFile`, `language: Form[str]`), validates audio headers, returns recognized text and confidence.
* `POST /api/v1/voice/synthesize`: Ingests JSON `{ "text": "...", "language": "mr" }`, returns streaming `audio/wav` response.
* `GET /api/v1/voice/sample`: Serves preview audio sample for language selection.
