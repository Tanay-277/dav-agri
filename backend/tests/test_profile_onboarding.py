import pytest

def get_auth_token(client, username="9876543210", password="password123"):
    """Helper to register (if needed) and login, returning access token."""
    # Try login first (for demo users already in DB)
    res = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    if res.status_code == 200:
        return res.json()["data"]["access_token"]
    # Otherwise register new user
    res = client.post("/api/v1/auth/register", json={"username": username, "password": password})
    assert res.status_code == 200
    return res.json()["data"]["access_token"]

def test_onboarding_lifecycle(client):
    token = get_auth_token(client, username="newuser_onboard", password="password123")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Check initial status
    status_res = client.get("/api/v1/onboarding/status", headers=headers)
    assert status_res.status_code == 200
    assert status_res.json()["data"]["onboarding_completed"] is False

    # 2. Confirm Marathi language
    confirm_res = client.post("/api/v1/onboarding/confirm-language", json={"language": "mr"}, headers=headers)
    assert confirm_res.status_code == 200
    assert confirm_res.json()["data"]["preferred_language"] == "mr"

    # 3. Complete onboarding
    complete_res = client.put("/api/v1/onboarding", json={"voice_confirmed": True, "onboarding_completed": True}, headers=headers)
    assert complete_res.status_code == 200
    assert complete_res.json()["data"]["onboarding_completed"] is True
    assert complete_res.json()["data"]["voice_confirmed"] is True

def test_profile_read_and_update(client):
    # Use demo user from init_db (password123)
    token = get_auth_token(client, username="86524525856", password="password123")
    headers = {"Authorization": f"Bearer {token}"}

    # Read profile
    res = client.get("/api/v1/profile", headers=headers)
    assert res.status_code == 200
    p = res.json()["data"]
    assert p["name"] == "Raj Patil"
    assert p["location"] == "Pune, MH"
    assert p["age"] == 42
    assert "Cotton" in p["crops_grown"]

    # Update profile
    update_payload = {
        "name": "Rajendra Patil",
        "age": 43,
        "livestock": "Cow, Buffalo",
        "crops_grown": ["Cotton", "Wheat", "Ragi", "Soybean"]
    }
    update_res = client.put("/api/v1/profile", json=update_payload, headers=headers)
    assert update_res.status_code == 200
    updated_p = update_res.json()["data"]
    assert updated_p["name"] == "Rajendra Patil"
    assert updated_p["age"] == 43
    assert "Soybean" in updated_p["crops_grown"]

def test_user_data_isolation(client):
    # User A
    token_a = get_auth_token(client, username="user_a_isolation", password="password123")
    # User B
    token_b = get_auth_token(client, username="user_b_isolation", password="password123")

    # User A modifies name
    client.put("/api/v1/profile", json={"name": "Farmer Alpha"}, headers={"Authorization": f"Bearer {token_a}"})

    # User B reads profile - must not see Farmer Alpha
    res_b = client.get("/api/v1/profile", headers={"Authorization": f"Bearer {token_b}"})
    assert res_b.status_code == 200
    assert res_b.json()["data"]["name"] != "Farmer Alpha"