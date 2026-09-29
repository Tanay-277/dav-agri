# DAV — Figma Feature Map & 17-Screen Architectural Flow

This document provides a comprehensive mapping of every screen from the Figma design to its user action, frontend component, REST API endpoint, backend service, database/AI/voice processing, and final UI display state.

---

## Screen 1: Launch Screen
* **Purpose:** Initial application boot, splash presentation, token validation, and initial routing.
* **Figma Reference:** Off-white textured canvas with radiant brown organic Iris/Sonic sphere centered.
* **User Action:** Opens application or taps canvas.
* **Frontend Component:** `<LaunchScreen />`
* **API Endpoint:** `GET /api/v1/auth/me`
* **Backend Service:** `AuthService.get_current_user`
* **Database / AI / Voice:** Queries `users` and `onboarding_preferences` by token claims.
* **API Response:**
  ```json
  {
    "success": true,
    "data": {
      "user_id": "usr_123",
      "phone": "+9186524525856",
      "onboarding": {
        "preferred_language": "mr",
        "voice_confirmed": true,
        "onboarding_completed": true
      }
    }
  }
  ```
* **Frontend Display:**
  * If valid token & `onboarding_completed == true` -> Routes to `HomeScreen`.
  * If valid token & `onboarding_completed == false` -> Routes to `LangSelectScreen`.
  * If unauthenticated (401) -> Smoothly transitions to `SignupOptionsScreen`.

---

## Screen 2: Signup Options
* **Purpose:** Entryway for new and returning farmers to choose sign-in or registration method.
* **Figma Reference:** Iris sphere on top; Pill buttons for Google ("Continue with Google"), Phone ("Sign up with phone"), and "Log in" pill.
* **User Action:**
  1. Taps "Sign up with phone" or "Log in".
  2. Or taps "Continue with Google".
* **Frontend Component:** `<SignupOptionsScreen />`
* **API Endpoint:**
  * For Phone: Routes directly to `PhoneScreen`.
  * For Google: `POST /api/v1/auth/google` (with OAuth credential token).
* **Backend Service:** `AuthService.authenticate_google`
* **Database / AI / Voice:** Finds or creates user in `users`, initializes default profile in `profiles`.
* **API Response:** Returns standard JWT access token and onboarding status.
* **Frontend Display:** Loading spinner on button during Google auth, error toast if cancelled, navigation to `PhoneScreen` on phone selection.

---

## Screen 3: Phone
* **Purpose:** Capture the farmer's mobile phone number for passwordless OTP authentication.
* **Figma Reference:** Iris sphere, title "Enter Your Phone Number", input box (sample `86524525856`), "Log in" submission pill.
* **User Action:** Enters 10-digit phone number, taps "Log in".
* **Frontend Component:** `<PhoneScreen />`
* **API Endpoint:** `POST /api/v1/auth/phone/request-otp`
* **Backend Service:** `AuthService.request_otp`
* **Database / AI / Voice:** Generates secure 5-digit OTP (cached in-memory/DB with 5 min TTL); logs OTP in dev mode or sends SMS via provider.
* **API Response:**
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
* **Frontend Display:** Transitions to `OtpScreen`, passing the phone number in session state.

---

## Screen 4: OTP (One-Time Password Verification)
* **Purpose:** Verify farmer's phone identity securely.
* **Figma Reference:** Iris sphere, title "Enter the OTP", 5 separate digit boxes `[4][4][4][4][4]`, button "Verify OTP".
* **User Action:** Types the 5 received digits (or uses dev code `44444`), taps "Verify OTP".
* **Frontend Component:** `<OtpScreen />`
* **API Endpoint:** `POST /api/v1/auth/phone/verify-otp`
* **Backend Service:** `AuthService.verify_otp`
* **Database / AI / Voice:** Validates OTP and TTL; creates or loads `User`, default `Profile`, and `OnboardingPreferences`. Generates JWT token.
* **API Response:**
  ```json
  {
    "success": true,
    "data": {
      "access_token": "jwt_token_string",
      "token_type": "bearer",
      "user": {
        "id": "usr_99",
        "phone": "86524525856",
        "onboarding_completed": false
      }
    }
  }
  ```
* **Frontend Display:** Stores token in secure client state. If `onboarding_completed` is false, routes to `LangSelectScreen`; otherwise routes to `HomeScreen`.

---

## Screen 5: Language Selection (Lang Select)
* **Purpose:** Select preferred regional language for voice and UI.
* **Figma Reference:** Rich dark soil terracotta background, Iris sphere, title "Choose your Voice", 3 pill buttons:
  * `ABC ENGLISH` + Play preview icon
  * `कखग हिन्दी` + Play preview icon
  * `कखग मराठी` + Play preview icon
* **User Action:** Taps language pill to select; taps preview play icon to hear sample TTS audio.
* **Frontend Component:** `<LangSelectScreen />`
* **API Endpoint:** `GET /api/v1/voice/sample?lang={en|hi|mr}`
* **Backend Service:** `VoiceService.get_sample_audio`
* **Database / AI / Voice:** Synthesizes/serves standard greeting audio sample in selected language.
* **API Response:** Audio stream or base64 audio data.
* **Frontend Display:** Active highlight on selected language pill; audio plays via client audio player; advances to `LanguageConfirmScreen`.

---

## Screen 6: Language Confirmation
* **Purpose:** Verify that the farmer can clearly hear the synthesized speech in their selected language.
* **Figma Reference:** Terracotta background, Iris sphere, prompt text:
  * "तुम्हाला खालील लिहिलेलं ऐकू येतंय का?"
  * "नमस्कार! हा एक छोटासा आवाजाचा चाचणी संदेश आहे."
  * "तुम्हाला माझा आवाज स्पष्ट ऐकू येतोय का?"
  * Green button: "हो, ऐकू येतोय ✓"
  * Red button: "नाही, ऐकू येत नाही ✕"
* **User Action:** Listens to audio prompt; taps Green ("Yes, I can hear") or Red ("No, I cannot").
* **Frontend Component:** `<LanguageConfirmScreen />`
* **API Endpoint:** `POST /api/v1/onboarding/confirm-language`
* **Backend Service:** `OnboardingService.confirm_language`
* **Database / AI / Voice:** Updates `onboarding_preferences.preferred_language = lang_code`.
* **API Response:**
  ```json
  {
    "success": true,
    "data": {
      "language": "mr",
      "confirmed": true
    }
  }
  ```
* **Frontend Display:** If Yes -> routes to `VoiceSetupScreen`. If No -> replays audio and shows device volume tip.

---

## Screen 7: Voice Setup / Test (Voice)
* **Purpose:** Verify farmer's microphone permissions and ensure voice input is recognized accurately.
* **Figma Reference:** Terracotta background, Iris sphere, text "आता तुम्ही बोलून पाहा", subtitle "नमस्कार, माझं नाव ......", audio waveform visualizer at bottom.
* **User Action:** Farmer speaks the test phrase into the device microphone.
* **Frontend Component:** `<VoiceSetupScreen />`
* **API Endpoint:** `POST /api/v1/voice/transcribe`
* **Backend Service:** `VoiceService.transcribe_audio`
* **Database / AI / Voice:** Ingests multipart audio file (WAV/WebM), validates audio headers/size, runs Speech-To-Text (STT) provider, extracts recognized text.
* **API Response:**
  ```json
  {
    "success": true,
    "data": {
      "text": "नमस्कार माझं नाव राज पाटील आहे",
      "confidence": 0.96,
      "language": "mr"
    }
  }
  ```
* **Frontend Display:** Waveform reacts to microphone volume; recognized speech appears in real-time or upon completion; automatically transitions to `OnboardedScreen`.

---

## Screen 8: Onboarded Screen
* **Purpose:** Celebrate completion of voice setup and transition farmer to main app.
* **Figma Reference:** Terracotta background, header "सगळं तयार आहे!", title "तुमच्यासाठी सगळं सेट करत आहोत.", subtitle "आता तुम्ही AI सोबत बोलायला सुरुवात करू शकता.", button "सुरू करा".
* **User Action:** Taps "सुरू करा" (Start).
* **Frontend Component:** `<OnboardedScreen />`
* **API Endpoint:** `PUT /api/v1/onboarding`
* **Backend Service:** `OnboardingService.complete_onboarding`
* **Database / AI / Voice:** Sets `onboarding_preferences.onboarding_completed = true` and `voice_confirmed = true`.
* **API Response:**
  ```json
  {
    "success": true,
    "data": {
      "onboarding_completed": true
    }
  }
  ```
* **Frontend Display:** Smooth transition to `HomeScreen`.

---

## Screen 9: Weather
* **Purpose:** Show detailed agricultural weather forecasting and irrigation recommendations.
* **Figma Reference:** Back button (`<`), Language pill (`अ`), 40mm precipitation water-bar indicator, 4 time slots ("सुबह", "दोपहर", "शाम", "रात"), rain duration ("दोपहर से शाम तक बारिश, करीब 3 घंटे"), intensity droplets ("कितनी तेज़: तेज़ बारिश"), status "आज सिंचाई की ज़रूरत नहीं है", bottom mic/play/help controls, white button "सेव करें".
* **User Action:** Views weather breakdown, taps play button to hear audio advisory, or taps "सेव करें" to save note.
* **Frontend Component:** `<WeatherScreen />`
* **API Endpoint:** `GET /api/v1/weather/current` and `GET /api/v1/weather/forecast`
* **Backend Service:** `WeatherService.get_agricultural_weather`
* **Database / AI / Voice:** Calls Open-Meteo / Weather provider for farmer's location (`Pune, MH`); caches result in `weather_cache`.
* **API Response:**
  ```json
  {
    "success": true,
    "data": {
      "location": "Pune, MH",
      "temperature_c": 27.0,
      "condition": "Rain",
      "expected_rainfall_mm": 40.0,
      "duration_hours": 3,
      "intensity": "heavy",
      "intensity_level": 3,
      "irrigation_needed": false,
      "irrigation_advisory": "आज सिंचाई की ज़रूरत नहीं है",
      "time_slots": [
        {"period": "morning", "temp_c": 24, "condition": "sunny_cloud"},
        {"period": "afternoon", "temp_c": 27, "condition": "rain"},
        {"period": "evening", "temp_c": 25, "condition": "rain_sun"},
        {"period": "night", "temp_c": 22, "condition": "cloud"}
      ]
    }
  }
  ```
* **Frontend Display:** Renders exact Figma gauges, rain bars, time cards, and audio playback of the irrigation advice.

---

## Screen 10: Home
* **Purpose:** Central hub for daily farmer activities, weather snapshot, quick agricultural categories, and voice interaction.
* **Figma Reference:** Hamburger menu (`≡`), Language pill (`अ`), weather card ("उन्हाळी हवामान 27°C पुणे"), 4 category cards:
  1. "हवामान" (Weather)
  2. "पिकांचे संरक्षण" (Crop Protection)
  3. "पिकांचे भाव" (Crop Prices)
  4. "सरकारी योजना" (Government Schemes)
  Center circular mic button with subtitle "बोलण्यासाठी टॅप करा". Bottom navigation: घर (Home), शेत (Farm), मी (Me).
* **User Action:** Taps weather banner, taps category card, or taps central mic button.
* **Frontend Component:** `<HomeScreen />`
* **API Endpoint:** `GET /api/v1/farm/summary` & `GET /api/v1/weather/current`
* **Backend Service:** `FarmService.get_farmer_summary`
* **Database / AI / Voice:** Queries current weather and active crops/alerts for user.
* **API Response:** Summary object with weather snippet and recent farm status.
* **Frontend Display:** Category grid, live weather card, floating mic with pulse animation on tap navigating to `ListeningScreen`.

---

## Screen 11: Listening Screen
* **Purpose:** Full-screen voice capture with visual sound wave reaction and real-time transcription feedback.
* **Figma Reference:** Hamburger menu, Language pill (`EN`), "Listening...", pulsating Iris sphere, transcription bubble ("My cotton production was 12 quintals in 2022, 15 in 2023, 18 in 2024, and ....."), bottom controls: Pause (⏸), Mic (🎙), Keyboard (⌨).
* **User Action:** Speaks question or taps pause/stop/keyboard.
* **Frontend Component:** `<ListeningScreen />`
* **API Endpoint:** `POST /api/v1/voice/transcribe` & `POST /api/v1/query`
* **Backend Service:** `VoiceService.transcribe_audio` -> `QueryService.process_query`
* **Database / AI / Voice:** Audio processed via STT; text query passed to `QueryService`.
* **API Response:** Returns parsed intent, transcript, and processed result id.
* **Frontend Display:** Live text stream in speech bubble; upon completion, navigates to `ProcessedResultScreen`.

---

## Screen 12: Processed Result
* **Purpose:** Present verified agricultural data, charts, natural language AI explanation, audio playback, and sharing.
* **Figma Reference:** Back button, Language pill (`EN`), Question bubble, Stacked Bar Chart for "Cotton Production" (years 2021-2025), action pills "🔊 Speak Out" and "🔗 Share", Explanation card ("You produced 9 more quintals in 2025 than in 2022, which is a 75% increase..."), text input bar + mic.
* **User Action:** Taps "Speak Out" to listen, taps "Share" to copy link, or asks follow-up.
* **Frontend Component:** `<ProcessedResultScreen />`
* **API Endpoint:** `POST /api/v1/query` and `POST /api/v1/voice/synthesize`
* **Backend Service:** `QueryService.process_query` -> `AnalyticsService` -> `AIService`
* **Database / AI / Voice:**
  1. `AnalyticsService` executes deterministic calculation on `production_records` (calculates 75% growth, +9 quintals).
  2. `AIService` creates localized explanation using verified numbers.
  3. Records saved to `query_history`.
* **API Response:**
  ```json
  {
    "success": true,
    "data": {
      "id": "qry_88",
      "query": "My cotton production was 12 quintals in 2022, 15 in 2023, 18 in 2024, and 21 in 2025. Show me how my production has changed over the years.",
      "visualization": {
        "type": "stacked_bar",
        "title": "Cotton Production",
        "unit": "quintals",
        "labels": ["2021", "2022", "2023", "2024", "2025"],
        "datasets": [
          {"name": "Base Yield", "color": "#8b5cf6", "data": [20, 25, 45, 60, 65]},
          {"name": "Secondary Yield", "color": "#14b8a6", "data": [40, 55, 65, 80, 95]},
          {"name": "Bonus Yield", "color": "#f97316", "data": [30, 45, 40, 40, 40]}
        ]
      },
      "explanation": "You produced 9 more quintals in 2025 than in 2022, which is a 75% increase in production. The highest jump was recorded between 2023 and 2024.",
      "share_token": "sh_token_4829"
    }
  }
  ```
* **Frontend Display:** Stacked bar chart rendered via SVG/Recharts, Speak Out button triggers synthesized speech audio stream, Share button copies verified link.

---

## Screen 13: Farm
* **Purpose:** Overview of farm activities, land details, recent voice conversations, and overall income trends.
* **Figma Reference:** Hamburger menu, Language pill (`अ`), top toggle pills "उत्पादन" (Production) & "माझी जमीन" (My Land), "माझे संवाद" (My Conversations) list with "सगळं पहा", Section "माझी जमीन" with multi-line chart ("वेगवेगळ्या पिकांमधून मिळालेले उत्पन्न" May-Sept), bottom nav.
* **User Action:** Taps conversation pill to review, toggles tabs, or taps chart to drill into topic.
* **Frontend Component:** `<FarmScreen />`
* **API Endpoint:** `GET /api/v1/farm/conversations` & `GET /api/v1/farm/analytics/crop-income`
* **Backend Service:** `FarmService.get_conversations` and `AnalyticsService.get_crop_income_trends`
* **Database / AI / Voice:** Queries `query_history` and joins `production_records` across crops for current user.
* **API Response:** List of recent conversations + multi-line chart data.
* **Frontend Display:** Toggleable tabs, clickable conversation pills, interactive multi-line chart, bottom nav with "Farm" active.

---

## Screen 14: Farm / Topic
* **Purpose:** Crop-specific analytics, new record creation, production trend line, and farm expense donut breakdown.
* **Figma Reference:** Back button (`< मागे`), Language pill (`अ`), header "उत्पादन" with "+ नवीन नोंद" button, crop filter pills ("कापूस", "गहू"), Line chart "कापूस पिकांमधून मिळालेले उत्पन्न" with "🔊 मला हे समजावून सांगा" button, Donut/Pie chart "माझ्या शेतीचा एकूण खर्च" (मजुरी 40%, बियाणे 25%, खत 20%, कीटकनाशके 15%), bottom nav.
* **User Action:** Taps "+ नवीन नोंद" to add production/expense, taps crop pill, or taps "मला हे समजावून सांगा" (Explain this to me).
* **Frontend Component:** `<FarmTopicScreen />`
* **API Endpoint:** `GET /api/v1/farm/crops` & `GET /api/v1/farm/analytics/crop/{crop_id}` & `GET /api/v1/farm/expenses/breakdown`
* **Backend Service:** `AnalyticsService.calculate_expense_breakdown`
* **Database / AI / Voice:** Deterministically calculates category sums from `expense_records` (Labor INR 40,000 / 40%, Seeds INR 25,000 / 25%, etc.).
* **API Response:** Structured donut chart percentages and production trend arrays.
* **Frontend Display:** Crop filter pills, monthly trend line, donut chart with color legend, "+ नवीन नोंद" modal. Tapping "मला हे समजावून सांगा" opens `TopicExplanationModal`.

---

## Screen 15: Farm / Topic / Topic Explanation
* **Purpose:** Deep-dive modal sheet explaining farm expense breakdown with verified calculations and audio narration.
* **Figma Reference:** Bottom sheet modal with Close button (✕), title "माझ्या शेतीचा एकूण खर्च", centered donut/pie chart with 4-part legend (मजुरी 40%, कीटकनाशके 15%, खत 20%, बियाणे 25%), Marathi explanation text ("या पाई चार्टमध्ये तुमच्या शेतीसाठी केलेल्या एकूण खर्चाचे... मजुरीवर सर्वाधिक खर्च झाला असून, 40% खर्च..."), button "🔊 मला हे समजावून सांगा".
* **User Action:** Reads explanation, taps "मला हे समजावून सांगा" to hear audio narration, or taps ✕ to close.
* **Frontend Component:** `<TopicExplanationModal />`
* **API Endpoint:** `GET /api/v1/farm/analytics/explanation?topic=expenses` & `POST /api/v1/voice/synthesize`
* **Backend Service:** `AnalyticsService` (calculates 40% labor fact) -> `AIService` (generates Marathi explanation) -> `VoiceService` (synthesizes Marathi speech).
* **Database / AI / Voice:** Fact-grounded generation ensures no hallucinated expenses.
* **API Response:** Text explanation + audio stream.
* **Frontend Display:** Modal sheet smoothly slides up; audio plays aloud on tap; close button dismisses back to `FarmTopicScreen`.

---

## Screen 16: Profile
* **Purpose:** Farmer identity overview, farm metadata snapshot, and access to application preferences.
* **Figma Reference:** Hamburger menu, circular farmer illustration avatar, "Raj Patil", "Pune, MH  42", Settings Card 1 (Edit Profile, Language: English, Notifications, Saved Visualizations, Farm Records), Settings Card 2 (Voice History, Terms & Conditions, Privacy Policy), bottom nav with "मी" (Me) active.
* **User Action:** Taps "Edit Profile", taps "Language", or taps "Saved Visualizations".
* **Frontend Component:** `<ProfileScreen />`
* **API Endpoint:** `GET /api/v1/profile`
* **Backend Service:** `ProfileService.get_profile`
* **Database / AI / Voice:** Queries `profiles` table for `user_id`.
* **API Response:**
  ```json
  {
    "success": true,
    "data": {
      "name": "Raj Patil",
      "location": "Pune, MH",
      "age": 42,
      "land_location": "Plot No. 124/2, Kothrud",
      "primary_crop": "Cotton",
      "land_size": "20 acres",
      "irrigation_type": "Rain Fed",
      "livestock": "Cow, Goat, Buffalo",
      "crops_grown": ["Cotton", "Wheat", "Ragi"],
      "preferred_language": "en"
    }
  }
  ```
* **Frontend Display:** Profile details card, navigation items, active bottom navigation on "Me".

---

## Screen 17: Edit Profile
* **Purpose:** Allow farmer to update personal and agricultural details.
* **Figma Reference:** Farmer avatar with "✏ Edit Image", Name ("Raj Patil"), Location ("Pune, MH"), Age ("42"), Farm Details: Land location ("Plot No. 124/2, Kothrud"), Primary crop ("Cotton"), Land Size ("20 acres"), Irrigation type dropdown ("Rain Fed ⌄"), Livestock ("Cow, Goat, Buffalo"), Crops grown tags (`Cotton`, `Wheat`, `Ragi`), bottom nav.
* **User Action:** Modifies fields, changes irrigation dropdown, adds crop tag, taps Save.
* **Frontend Component:** `<EditProfileScreen />`
* **API Endpoint:** `PUT /api/v1/profile`
* **Backend Service:** `ProfileService.update_profile`
* **Database / AI / Voice:** Validates data schema; updates `profiles` in database.
* **API Response:** Returns updated profile object.
* **Frontend Display:** Instant validation, saving spinner, success notification, returns to `ProfileScreen` with refreshed data.
