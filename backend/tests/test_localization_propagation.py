import pytest
from app.core.config import settings

def get_demo_auth_token(client):
    phone = "86524525856"
    client.post("/api/v1/auth/phone/request-otp", json={"phone": phone})
    res = client.post("/api/v1/auth/phone/verify-otp", json={"phone": phone, "otp": settings.DEV_MOCK_OTP})
    return res.json()["data"]["access_token"]

def test_weather_localization_all_languages(client):
    # Marathi (Default)
    res_mr = client.get("/api/v1/weather/current?language=mr")
    assert res_mr.status_code == 200
    data_mr = res_mr.json()["data"]
    assert data_mr["language"] == "mr"
    assert "पाऊस" in data_mr["advisory"] or "पाणी" in data_mr["advisory"]

    # Hindi
    res_hi = client.get("/api/v1/weather/current?language=hi")
    assert res_hi.status_code == 200
    data_hi = res_hi.json()["data"]
    assert data_hi["language"] == "hi"
    assert "बारिश" in data_hi["advisory"] or "सिंचाई" in data_hi["advisory"]

    # English
    res_en = client.get("/api/v1/weather/current?language=en")
    assert res_en.status_code == 200
    data_en = res_en.json()["data"]
    assert data_en["language"] == "en"
    assert "rain" in data_en["advisory"].lower() or "irrigat" in data_en["advisory"].lower()

    # Invalid language rejected
    res_invalid = client.get("/api/v1/weather/current?language=es")
    assert res_invalid.status_code in [400, 422]

def test_farm_expenses_localization(client):
    token = get_demo_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # English
    res_en = client.get("/api/v1/farm/expenses/breakdown?language=en", headers=headers)
    assert res_en.status_code == 200
    labels_en = res_en.json()["data"]["labels"]
    assert "Labor" in labels_en
    assert "Seeds" in labels_en

    # Hindi
    res_hi = client.get("/api/v1/farm/expenses/breakdown?language=hi", headers=headers)
    assert res_hi.status_code == 200
    labels_hi = res_hi.json()["data"]["labels"]
    assert "मजदूरी" in labels_hi
    assert "बीज" in labels_hi

    # Marathi
    res_mr = client.get("/api/v1/farm/expenses/breakdown?language=mr", headers=headers)
    assert res_mr.status_code == 200
    labels_mr = res_mr.json()["data"]["labels"]
    assert "मजुरी" in labels_mr
    assert "बियाणे" in labels_mr

    # Invalid language
    res_bad = client.get("/api/v1/farm/expenses/breakdown?language=fr", headers=headers)
    assert res_bad.status_code in [400, 422]

def test_ai_query_strict_language_lock(client):
    token = get_demo_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Input English query, but lock language to Marathi
    res_mr = client.post("/api/v1/query", json={
        "text": "Tell me about my cotton production",
        "language": "mr"
    }, headers=headers)
    assert res_mr.status_code == 200
    answer_mr = res_mr.json()["data"]["answer"]
    assert res_mr.json()["data"]["language"] == "mr"
    # Response must contain Devanagari Marathi characters
    assert any("\u0900" <= ch <= "\u097f" for ch in answer_mr)

    # Input Marathi query, but lock language to English
    res_en = client.post("/api/v1/query", json={
        "text": "माझ्या कापूस उत्पादनाची माहिती द्या",
        "language": "en"
    }, headers=headers)
    assert res_en.status_code == 200
    answer_en = res_en.json()["data"]["answer"]
    assert res_en.json()["data"]["language"] == "en"
    assert "cotton" in answer_en.lower() or "production" in answer_en.lower() or "farm" in answer_en.lower()

def test_voice_strict_validation(client):
    token = get_demo_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Invalid language must be rejected with 400 or 422 (Zero Silent Fallback)
    res_invalid = client.post("/api/v1/voice/synthesize", json={
        "text": "Bonjour",
        "language": "fr"
    }, headers=headers)
    assert res_invalid.status_code in [400, 422]

    # Valid language succeeds
    res_valid = client.post("/api/v1/voice/synthesize", json={
        "text": "Hello, welcome to DAV.",
        "language": "en"
    }, headers=headers)
    assert res_valid.status_code == 200
    assert len(res_valid.content) > 100

def test_profile_language_persistence(client):
    token = get_demo_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Update preferred language via PUT /api/v1/profile
    update_res = client.put("/api/v1/profile", json={
        "preferred_language": "hi"
    }, headers=headers)
    assert update_res.status_code == 200
    data = update_res.json()["data"]
    assert data["preferred_language"] == "hi"

    # Verify retrieval preserves hi
    get_res = client.get("/api/v1/profile", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["data"]["preferred_language"] == "hi"
