import pytest
from app.core.config import settings

def test_request_otp_success(client):
    res = client.post("/api/v1/auth/phone/request-otp", json={"phone": "9876543210"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["phone"] == "9876543210"
    assert data["data"]["expires_in_seconds"] == 300

def test_verify_otp_success_and_token(client):
    phone = "9876543210"
    client.post("/api/v1/auth/phone/request-otp", json={"phone": phone})
    
    # Use development mock OTP
    res = client.post("/api/v1/auth/phone/verify-otp", json={"phone": phone, "otp": settings.DEV_MOCK_OTP})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"
    assert data["data"]["user_id"] is not None

def test_verify_otp_invalid(client):
    res = client.post("/api/v1/auth/phone/verify-otp", json={"phone": "9876543210", "otp": "00000"})
    assert res.status_code == 400
    assert "Invalid or expired OTP" in res.text

def test_get_current_user_me(client):
    # Verify OTP first
    phone = "86524525856"
    client.post("/api/v1/auth/phone/request-otp", json={"phone": phone})
    auth_res = client.post("/api/v1/auth/phone/verify-otp", json={"phone": phone, "otp": settings.DEV_MOCK_OTP})
    token = auth_res.json()["data"]["access_token"]

    # Call /api/v1/auth/me
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()["data"]
    assert me_data["phone"] == phone
    assert me_data["name"] == "Raj Patil"
