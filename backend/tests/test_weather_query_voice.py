import io
import pytest
from app.core.config import settings

def get_demo_auth_token(client):
    phone = "86524525856"
    client.post("/api/v1/auth/phone/request-otp", json={"phone": phone})
    res = client.post("/api/v1/auth/phone/verify-otp", json={"phone": phone, "otp": settings.DEV_MOCK_OTP})
    return res.json()["data"]["access_token"]

def test_weather_endpoint(client):
    res = client.get("/api/v1/weather/current")
    assert res.status_code == 200
    w = res.json()["data"]
    assert "temperature_c" in w
    assert "expected_rainfall_mm" in w
    assert "time_slots" in w
    assert len(w["time_slots"]) == 4

def test_multilingual_queries_and_visualization(client):
    token = get_demo_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. English Cotton query matching Figma Screen 12
    en_query = {
        "text": "My cotton production was 12 quintals in 2022, 15 in 2023, 18 in 2024, and 21 in 2025. Show me how my production has changed over the years.",
        "language": "en"
    }
    res_en = client.post("/api/v1/query", json=en_query, headers=headers)
    assert res_en.status_code == 200
    q_en = res_en.json()["data"]
    assert q_en["intent"] == "production_trend"
    assert "75" in q_en["answer"] or "9" in q_en["answer"]
    assert q_en["visualization"]["type"] == "stacked_bar"
    assert q_en["share_token"] is not None

    # 2. Marathi Expense query matching Figma Screen 14/15
    mr_query = {
        "text": "पिकांवर झालेला एकूण खर्च आणि प्रमाण सांगा",
        "language": "mr"
    }
    res_mr = client.post("/api/v1/query", json=mr_query, headers=headers)
    assert res_mr.status_code == 200
    q_mr = res_mr.json()["data"]
    assert q_mr["intent"] == "expense_breakdown"
    assert "मजुरी" in q_mr["answer"]
    assert q_mr["visualization"]["type"] == "donut"

    # 3. Hindi query
    hi_query = {
        "text": "कपास के उत्पादन की स्थिति बताएं",
        "language": "hi"
    }
    res_hi = client.post("/api/v1/query", json=hi_query, headers=headers)
    assert res_hi.status_code == 200
    q_hi = res_hi.json()["data"]
    assert "उत्पादन" in q_hi["answer"]

def test_voice_transcribe_and_synthesize(client):
    # Test audio upload with simulated WAV header
    wav_header = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x40\x1f\x00\x00\x40\x1f\x00\x00\x01\x00\x08\x00data\x00\x00\x00\x00"
    file_tuple = ("test_audio.wav", io.BytesIO(wav_header), "audio/wav")

    res = client.post(
        "/api/v1/voice/transcribe",
        files={"file": file_tuple},
        data={"language": "mr"}
    )
    assert res.status_code == 200
    assert res.json()["data"]["text"] != ""
    assert res.json()["data"]["confidence"] > 0.9

    # Test synthesize
    synth_res = client.post(
        "/api/v1/voice/synthesize",
        json={"text": "नमस्कार, शेतकरी मित्रांनो", "language": "mr"}
    )
    assert synth_res.status_code == 200
    assert synth_res.headers["content-type"] in ["audio/mpeg", "audio/wav"]
    assert len(synth_res.content) > 100

def test_voice_query_unified(client, db):
    wav_header = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x40\x1f\x00\x00\x40\x1f\x00\x00\x01\x00\x08\x00data\x00\x00\x00\x00"
    file_tuple = ("query_audio.wav", io.BytesIO(wav_header), "audio/wav")

    res = client.post(
        "/api/v1/voice/query",
        files={"file": file_tuple},
        data={"language": "mr", "synthesize_response": "true"}
    )
    assert res.status_code == 200
    data = res.json()["data"]
    assert "transcription" in data
    assert "query_response" in data
    assert data["audio_base64"] is not None

def test_voice_error_handling_empty_payload(client):
    empty_tuple = ("empty.wav", io.BytesIO(b""), "audio/wav")
    res = client.post(
        "/api/v1/voice/transcribe",
        files={"file": empty_tuple},
        data={"language": "mr"}
    )
    assert res.status_code == 400
    assert "empty" in res.text.lower()

def test_security_unauthorized_rejections(client):
    # Attempting to access protected endpoints without token
    res_profile = client.get("/api/v1/profile")
    assert res_profile.status_code == 401

    res_farm = client.get("/api/v1/farm/summary")
    assert res_farm.status_code == 401

    res_query = client.post("/api/v1/query", json={"text": "Hello"})
    assert res_query.status_code == 401

    # Attempting with invalid token
    res_invalid = client.get("/api/v1/profile", headers={"Authorization": "Bearer invalid_gibberish_token"})
    assert res_invalid.status_code == 401
