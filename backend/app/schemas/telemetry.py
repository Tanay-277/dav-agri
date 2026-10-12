import math
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator

# Mechanical constants specified in Patent Draft Section 4.5.11 (Best Mode)
# Drive wheel diameter: 65 mm = 0.065 m
DEFAULT_WHEEL_DIAMETER_M = 0.065
# Optical encoder disc with 20 slots: n_cpr = 20
DEFAULT_COUNTS_PER_REV = 20

def calculate_encoder_distance(n_pulse: int, d_wheel: float = DEFAULT_WHEEL_DIAMETER_M, n_cpr: int = DEFAULT_COUNTS_PER_REV) -> float:
    """Implements Patent Equation 1:
    d = (n_pulse * pi * D_wheel) / n_cpr
    """
    if n_pulse <= 0 or n_cpr <= 0 or d_wheel <= 0:
        return 0.0
    return round((float(n_pulse) * math.pi * float(d_wheel)) / float(n_cpr), 3)

class RobotTelemetryPacket(BaseModel):
    """Incoming telemetry packet schema matching Patent Section 4.5.4 & Claims 1, 5, 10.
    
    Carries:
    - air temperature (C)
    - relative humidity (%)
    - latitude & longitude (from NEO-6M, or null if fix not yet acquired)
    - accumulated encoder pulses or estimated distance
    - battery voltage (V)
    - optional ultrasonic obstacle distance (cm)
    - device timestamp
    """
    robot_id: str = Field(default="dav_robot_01", description="Identifier of the reporting robot")
    temperature_c: Optional[float] = Field(default=None, description="Air temperature in Celsius (-40 to 80)")
    humidity_pct: Optional[float] = Field(default=None, description="Relative humidity percentage (0 to 100)")
    latitude: Optional[float] = Field(default=None, description="Latitude from satellite receiver, or null if no fix")
    longitude: Optional[float] = Field(default=None, description="Longitude from satellite receiver, or null if no fix")
    gps_fix: Optional[bool] = Field(default=False, description="True if satellite fix acquired")
    
    # Distance travelled from wheel encoder pulses
    encoder_pulses: Optional[int] = Field(default=0, ge=0, description="Accumulated wheel encoder count")
    distance_m: Optional[float] = Field(default=None, ge=0.0, description="Estimated distance in meters")
    
    # Battery state
    battery_voltage: Optional[float] = Field(default=None, description="Battery voltage in Volts (e.g., 7.4V nominal)")
    
    # Obstacle distance from ultrasonic sensor
    obstacle_distance_cm: Optional[float] = Field(default=None, description="Distance to obstacle ahead in cm")
    
    # Sampling timestamp at microcontroller
    device_timestamp: Optional[datetime] = Field(default=None, description="Timestamp recorded at microcontroller")
    
    # Simulation flag: "live_hardware" or "simulation"
    source: str = Field(default="live_hardware", description="'live_hardware' or 'simulation'")

    @field_validator("temperature_c")
    @classmethod
    def validate_temperature_envelope(cls, v: Optional[float]) -> Optional[float]:
        # Physical range validation: Patent Claim 5 & Section 4.5.4
        if v is not None:
            if v < -40.0 or v > 85.0:
                raise ValueError(f"Temperature reading {v}°C lies outside physical range [-40°C, 85°C]")
        return v

    @field_validator("humidity_pct")
    @classmethod
    def validate_humidity_envelope(cls, v: Optional[float]) -> Optional[float]:
        # Physical range validation: Patent Claim 5 & Section 4.5.4
        if v is not None:
            if v < 0.0 or v > 100.0:
                raise ValueError(f"Humidity reading {v}% lies outside physical range [0%, 100%]")
        return v

    @field_validator("battery_voltage")
    @classmethod
    def validate_battery_envelope(cls, v: Optional[float]) -> Optional[float]:
        # 2x 18650 series pack nominal range: 5.0V to 9.0V
        if v is not None:
            if v < 0.0 or v > 15.0:
                raise ValueError(f"Battery voltage reading {v}V lies outside physical range [0V, 15V]")
        return v

    @field_validator("latitude")
    @classmethod
    def validate_latitude_envelope(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < -90.0 or v > 90.0):
            raise ValueError(f"Latitude {v} is out of bounds [-90, 90]")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude_envelope(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < -180.0 or v > 180.0):
            raise ValueError(f"Longitude {v} is out of bounds [-180, 180]")
        return v

class RobotTelemetryResponse(BaseModel):
    id: str
    robot_id: str
    temperature_c: Optional[float]
    humidity_pct: Optional[float]
    latitude: Optional[float]
    longitude: Optional[float]
    gps_fix: bool
    distance_m: float
    encoder_pulses: int
    battery_voltage: Optional[float]
    obstacle_distance_cm: Optional[float]
    device_timestamp: Optional[datetime]
    received_at: datetime
    is_stale: bool
    connection_status: str
    source: str

class RobotStatusSummary(BaseModel):
    """Robot status indication complying with Patent Claims 1, 9, 16 & Section 4.5.7.
    
    Reflects:
    - reporting state (online, offline, stale)
    - battery state (voltage, percentage estimate, low battery warning)
    - position fix state of positioning receiver
    - recency of last received packet
    """
    robot_id: str
    connection_status: str  # "ONLINE", "STALE", "DISCONNECTED"
    last_packet_at: Optional[datetime]
    seconds_since_last_packet: Optional[float]
    gps_fix_acquired: bool
    latitude: Optional[float]
    longitude: Optional[float]
    current_temperature_c: Optional[float]
    current_humidity_pct: Optional[float]
    total_distance_m: float
    battery_voltage: Optional[float]
    battery_percent: Optional[int]
    is_battery_low: bool
    obstacle_distance_cm: Optional[float]
    source: str
