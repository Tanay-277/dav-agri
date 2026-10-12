import pytest
from datetime import datetime, timezone
from app.schemas.telemetry import calculate_encoder_distance, RobotTelemetryPacket
from app.models.telemetry import RobotTelemetryRecord

def test_calculate_encoder_distance_equation_1():
    """Verify Patent Equation 1: d = (n_pulse * pi * D_wheel) / n_cpr.
    For D_wheel = 0.065m and n_cpr = 20:
    circumference = 0.065 * pi = 0.2042035m per revolution.
    For 20 pulses (1 rev): distance should be ~0.204m.
    For 200 pulses (10 revs): distance should be ~2.042m.
    """
    assert calculate_encoder_distance(0) == 0.0
    dist_1_rev = calculate_encoder_distance(20, d_wheel=0.065, n_cpr=20)
    assert round(dist_1_rev, 3) == 0.204

    dist_10_rev = calculate_encoder_distance(200, d_wheel=0.065, n_cpr=20)
    assert round(dist_10_rev, 3) == 2.042

def test_telemetry_packet_range_validation():
    """Verify physical range envelope validation (Patent Claim 5)."""
    # Valid packet
    p = RobotTelemetryPacket(
        robot_id="dav_robot_01",
        temperature_c=28.5,
        humidity_pct=65.0,
        latitude=18.5204,
        longitude=73.8567,
        gps_fix=True,
        encoder_pulses=50,
        battery_voltage=7.4,
    )
    assert p.temperature_c == 28.5
    assert p.humidity_pct == 65.0

    # Temperature outside envelope rejected
    with pytest.raises(ValueError):
        RobotTelemetryPacket(temperature_c=99.0)

    # Humidity outside envelope rejected
    with pytest.raises(ValueError):
        RobotTelemetryPacket(humidity_pct=105.0)

    # Battery outside envelope rejected
    with pytest.raises(ValueError):
        RobotTelemetryPacket(battery_voltage=24.0)

def test_telemetry_packet_absent_values_honest():
    """Verify absent GPS and sensors are preserved honestly as None (Patent Claim 7)."""
    p = RobotTelemetryPacket(
        robot_id="dav_robot_01",
        temperature_c=25.0,
        humidity_pct=None,
        latitude=None,
        longitude=None,
        gps_fix=False,
    )
    assert p.latitude is None
    assert p.longitude is None
    assert p.gps_fix is False

def test_telemetry_api_ingest_and_status(client):
    """Test full API ingestion, status summary, and history endpoints."""
    # 1. Ingest packet without GPS fix
    payload = {
        "robot_id": "dav_test_robot",
        "temperature_c": 31.2,
        "humidity_pct": 58.0,
        "gps_fix": False,
        "encoder_pulses": 40,
        "battery_voltage": 7.6,
        "obstacle_distance_cm": 45.0,
    }
    res = client.post("/api/v1/telemetry/packet", json=payload)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["robot_id"] == "dav_test_robot"
    assert data["temperature_c"] == 31.2
    assert data["humidity_pct"] == 58.0
    assert data["distance_m"] == 0.408  # 40 pulses = 2 revs = ~0.408m
    assert data["gps_fix"] is False
    assert data["latitude"] is None
    assert data["connection_status"] == "ONLINE"

    # 2. Get Status
    res_status = client.get("/api/v1/telemetry/status?robot_id=dav_test_robot")
    assert res_status.status_code == 200
    status_data = res_status.json()["data"]
    assert status_data["robot_id"] == "dav_test_robot"
    assert status_data["connection_status"] == "ONLINE"
    assert status_data["battery_percent"] > 60
    assert status_data["is_battery_low"] is False
    assert status_data["current_temperature_c"] == 31.2

    # 3. Get History
    res_hist = client.get("/api/v1/telemetry/history?robot_id=dav_test_robot")
    assert res_hist.status_code == 200
    hist = res_hist.json()["data"]
    assert len(hist) >= 1
    assert hist[-1]["temperature_c"] == 31.2

def test_telemetry_out_of_bounds_rejected(client):
    """Verify server rejects values outside physical range envelope (Patent Claim 5)."""
    bad_payload = {
        "robot_id": "dav_test_robot",
        "temperature_c": 120.0,  # Invalid
        "humidity_pct": 50.0,
    }
    res = client.post("/api/v1/telemetry/packet", json=bad_payload)
    assert res.status_code == 422  # Pydantic validation error
