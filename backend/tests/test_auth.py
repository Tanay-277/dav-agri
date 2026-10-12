import pytest

def test_register_success(client):
    res = client.post("/api/v1/auth/register", json={"username": "9876543219", "password": "password123"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"
    assert data["data"]["user_id"] is not None
    assert data["data"]["phone"] == "9876543219"

def test_register_duplicate_username(client):
    # First registration
    client.post("/api/v1/auth/register", json={"username": "testuser", "password": "password123"})
    # Duplicate username
    res = client.post("/api/v1/auth/register", json={"username": "testuser", "password": "password123"})
    assert res.status_code == 400
    assert "already registered" in res.text

def test_register_duplicate_phone(client):
    # First registration with phone as username
    client.post("/api/v1/auth/register", json={"username": "9998887777", "password": "password123"})
    # Duplicate phone
    res = client.post("/api/v1/auth/register", json={"username": "9998887777", "password": "differentpass"})
    assert res.status_code == 400
    assert "already registered" in res.text

def test_login_success(client):
    # Register first
    client.post("/api/v1/auth/register", json={"username": "testuser2", "password": "password123"})
    # Login
    res = client.post("/api/v1/auth/login", json={"username": "testuser2", "password": "password123"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"

def test_login_invalid_password(client):
    client.post("/api/v1/auth/register", json={"username": "testuser3", "password": "password123"})
    res = client.post("/api/v1/auth/login", json={"username": "testuser3", "password": "wrongpass"})
    assert res.status_code == 401
    assert "Invalid username or password" in res.text

def test_login_nonexistent_user(client):
    res = client.post("/api/v1/auth/login", json={"username": "nonexistent", "password": "password123"})
    assert res.status_code == 401
    assert "Invalid username or password" in res.text

def test_get_current_user_me(client):
    # Register and login
    client.post("/api/v1/auth/register", json={"username": "9876543211", "password": "password123"})
    login_res = client.post("/api/v1/auth/login", json={"username": "9876543211", "password": "password123"})
    token = login_res.json()["data"]["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()["data"]
    assert me_data["phone"] == "9876543211"
    assert me_data["username"] is None  # phone registered, so username is None
    assert me_data["name"] == "Farmer 3211"

def test_get_current_user_me_username(client):
    # Register with username (not phone)
    client.post("/api/v1/auth/register", json={"username": "farmer_john", "password": "password123"})
    login_res = client.post("/api/v1/auth/login", json={"username": "farmer_john", "password": "password123"})
    token = login_res.json()["data"]["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()["data"]
    assert me_data["username"] == "farmer_john"
    assert me_data["phone"] is None
    assert me_data["name"] == "Farmer"

def test_google_auth_placeholder(client):
    # Google auth requires valid ID token - test structure only
    res = client.post("/api/v1/auth/google", json={"id_token": "invalid_token"})
    assert res.status_code == 400