import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text
from app.database.session import Base

class RobotTelemetryRecord(Base):
    """Timestamped raw telemetry record from the mobile environmental monitoring robot.
    
    Implements Patent Draft 'Darft-3.pdf':
    - Section 4.5.3 (Environmental Sensing & Location)
    - Section 4.5.4 (Formation of the Telemetry Packet)
    - Section 4.5.8 (Data Logging & Historical Records)
    - Claims 1, 5, 6, 7, 9, 10
    """
    __tablename__ = "robot_telemetry_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    robot_id = Column(String(50), nullable=False, default="dav_robot_01", index=True)
    
    # Air temperature (Celsius) from DHT22 digital sensor (Claim 1, 10)
    temperature_c = Column(Float, nullable=True)
    
    # Relative humidity (%) from DHT22 digital sensor (Claim 1, 10)
    humidity_pct = Column(Float, nullable=True)
    
    # Spatial position from NEO-6M satellite positioning receiver (Claim 1, 3, 10, 12)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    gps_fix = Column(Boolean, default=False, nullable=False)
    
    # Accumulated distance travelled estimated from wheel encoder pulses (Claim 1, 3, 10; Equation 1)
    distance_m = Column(Float, nullable=False, default=0.0)
    encoder_pulses = Column(Integer, nullable=True, default=0)
    
    # Battery voltage (V) from 18650 series cells via resistive divider (Section 4.5.9, 4.5.11; Claim 11)
    battery_voltage = Column(Float, nullable=True)
    
    # Optional obstacle distance from HC-SR04 ultrasonic sensor (Claim 4, 13)
    obstacle_distance_cm = Column(Float, nullable=True)
    
    # Device timestamp recorded at microcontroller sampling instant (Section 4.5.3, 4.5.4)
    device_timestamp = Column(DateTime, nullable=True)
    
    # Server receipt timestamp
    received_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    
    # Telemetry source status: "live_hardware" or "simulation"
    source = Column(String(20), default="live_hardware", nullable=False)
    notes = Column(Text, nullable=True)
