import pytest
from app.core.config import settings

def get_demo_auth_token(client):
    phone = "86524525856"
    client.post("/api/v1/auth/phone/request-otp", json={"phone": phone})
    res = client.post("/api/v1/auth/phone/verify-otp", json={"phone": phone, "otp": settings.DEV_MOCK_OTP})
    return res.json()["data"]["access_token"]

def test_list_crops(client):
    res = client.get("/api/v1/farm/crops")
    assert res.status_code == 200
    crops = res.json()["data"]
    assert len(crops) >= 3
    crop_names = [c["name_en"] for c in crops]
    assert "Cotton" in crop_names
    assert "Wheat" in crop_names
    assert "Ragi" in crop_names

def test_production_records_and_add(client):
    token = get_demo_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Initial records list
    res = client.get("/api/v1/farm/production", headers=headers)
    assert res.status_code == 200
    records = res.json()["data"]
    assert len(records) >= 4

    # Add a new record
    new_record = {
        "crop_id": "crop_cotton",
        "year": 2026,
        "quantity_quintals": 24.5,
        "revenue_inr": 196000.0,
        "notes": "उत्कृष्ट हंगाम"
    }
    add_res = client.post("/api/v1/farm/production", json=new_record, headers=headers)
    assert add_res.status_code == 200
    added = add_res.json()["data"]
    assert added["year"] == 2026
    assert added["quantity_quintals"] == 24.5

def test_deterministic_expense_breakdown(client):
    token = get_demo_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/farm/expenses/breakdown", headers=headers)
    assert res.status_code == 200
    data = res.json()["data"]

    # Verify deterministic total & percentages (matches Figma Screen 14/15)
    assert data["total_expense_inr"] == 100000.0
    cat_map = {item["category"]: item["percentage"] for item in data["breakdown"]}
    assert cat_map["labor"] == 40.0
    assert cat_map["seeds"] == 25.0
    assert cat_map["fertilizer"] == 20.0
    assert cat_map["pesticides"] == 15.0

def test_crop_income_line_chart(client):
    token = get_demo_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Default should be Marathi
    res = client.get("/api/v1/farm/analytics/crop-income", headers=headers)
    assert res.status_code == 200
    chart = res.json()["data"]
    assert chart["type"] == "line"
    assert "मे" in chart["labels"]
    assert len(chart["datasets"]) >= 3

    # English query param
    res_en = client.get("/api/v1/farm/analytics/crop-income?language=en", headers=headers)
    assert res_en.status_code == 200
    chart_en = res_en.json()["data"]
    assert "May" in chart_en["labels"]

    # Hindi query param
    res_hi = client.get("/api/v1/farm/analytics/crop-income?language=hi", headers=headers)
    assert res_hi.status_code == 200
    chart_hi = res_hi.json()["data"]
    assert "मई" in chart_hi["labels"]
