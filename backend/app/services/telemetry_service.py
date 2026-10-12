import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.telemetry import RobotTelemetryRecord
from app.schemas.telemetry import (
    RobotTelemetryPacket,
    RobotStatusSummary,
    RobotTelemetryResponse,
    calculate_encoder_distance,
)

logger = logging.getLogger(__name__)

# Stale packet threshold in seconds as specified in Patent Section 4.5.7 (default 60s sample interval + grace period)
STALE_THRESHOLD_SECONDS = 60.0
# Low battery threshold for 2S 18650 pack (nominal 7.4V, cutoff ~6.6V)
LOW_BATTERY_THRESHOLD_V = 6.8

class TelemetryService:
    def __init__(self, db: Session):
        self.db = db

    def ingest_packet(self, packet: RobotTelemetryPacket) -> RobotTelemetryResponse:
        """Validate, calculate wheel distance (Eq 1), store in timestamped log, and format response."""
        now = datetime.now(timezone.utc)
        
        # Calculate distance using Equation 1 if pulses provided and distance not explicit
        distance_m = packet.distance_m
        if distance_m is None and packet.encoder_pulses is not None:
            distance_m = calculate_encoder_distance(packet.encoder_pulses)
        elif distance_m is None:
            distance_m = 0.0

        # Preserve honesty of GPS fix (Patent Section 4.5.4):
        # If fix is not acquired, coordinates are set to None
        has_fix = bool(packet.gps_fix and packet.latitude is not None and packet.longitude is not None)
        lat = packet.latitude if has_fix else None
        lon = packet.longitude if has_fix else None

        record = RobotTelemetryRecord(
            robot_id=packet.robot_id,
            temperature_c=packet.temperature_c,
            humidity_pct=packet.humidity_pct,
            latitude=lat,
            longitude=lon,
            gps_fix=has_fix,
            distance_m=distance_m,
            encoder_pulses=packet.encoder_pulses or 0,
            battery_voltage=packet.battery_voltage,
            obstacle_distance_cm=packet.obstacle_distance_cm,
            device_timestamp=packet.device_timestamp or now,
            received_at=now,
            source=packet.source,
        )

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        logger.info(f"[TELEMETRY] Ingested packet from {record.robot_id}: Temp={record.temperature_c}°C, Dist={record.distance_m}m, Fix={record.gps_fix}")

        return self._to_response(record, now)

    def get_latest_status(self, robot_id: str = "dav_robot_01") -> RobotStatusSummary:
        """Calculate live status indication including staleness and battery state (Patent Section 4.5.7)."""
        now = datetime.now(timezone.utc)
        latest = (
            self.db.query(RobotTelemetryRecord)
            .filter(RobotTelemetryRecord.robot_id == robot_id)
            .order_by(desc(RobotTelemetryRecord.received_at))
            .first()
        )

        if not latest:
            return RobotStatusSummary(
                robot_id=robot_id,
                connection_status="DISCONNECTED",
                last_packet_at=None,
                seconds_since_last_packet=None,
                gps_fix_acquired=False,
                latitude=None,
                longitude=None,
                current_temperature_c=None,
                current_humidity_pct=None,
                total_distance_m=0.0,
                battery_voltage=None,
                battery_percent=None,
                is_battery_low=False,
                obstacle_distance_cm=None,
                source="live_hardware",
            )

        # Ensure received_at is timezone-aware for delta calculation
        rec_at = latest.received_at
        if rec_at.tzinfo is None:
            rec_at = rec_at.replace(tzinfo=timezone.utc)

        delta_seconds = (now - rec_at).total_seconds()
        
        if delta_seconds <= STALE_THRESHOLD_SECONDS:
            connection_status = "ONLINE"
        else:
            connection_status = "STALE"

        # Battery percentage estimation for 2x 18650 cells (6.0V = 0%, 8.4V = 100%)
        batt_pct = None
        is_low = False
        if latest.battery_voltage is not None:
            v = latest.battery_voltage
            pct = int(max(0.0, min(100.0, (v - 6.0) / (8.4 - 6.0) * 100.0)))
            batt_pct = pct
            is_low = v <= LOW_BATTERY_THRESHOLD_V

        return RobotStatusSummary(
            robot_id=robot_id,
            connection_status=connection_status,
            last_packet_at=latest.received_at,
            seconds_since_last_packet=round(delta_seconds, 1),
            gps_fix_acquired=latest.gps_fix,
            latitude=latest.latitude,
            longitude=latest.longitude,
            current_temperature_c=latest.temperature_c,
            current_humidity_pct=latest.humidity_pct,
            total_distance_m=latest.distance_m,
            battery_voltage=latest.battery_voltage,
            battery_percent=batt_pct,
            is_battery_low=is_low,
            obstacle_distance_cm=latest.obstacle_distance_cm,
            source=latest.source,
        )

    def get_history(self, robot_id: str = "dav_robot_01", limit: int = 100) -> List[RobotTelemetryResponse]:
        """Fetch historical records for graphs and reconstruction (Patent Section 4.5.8)."""
        now = datetime.now(timezone.utc)
        records = (
            self.db.query(RobotTelemetryRecord)
            .filter(RobotTelemetryRecord.robot_id == robot_id)
            .order_by(desc(RobotTelemetryRecord.received_at))
            .limit(limit)
            .all()
        )
        return [self._to_response(r, now) for r in reversed(records)]

    def _to_response(self, record: RobotTelemetryRecord, now: datetime) -> RobotTelemetryResponse:
        rec_at = record.received_at
        if rec_at.tzinfo is None:
            rec_at = rec_at.replace(tzinfo=timezone.utc)
        delta = (now - rec_at).total_seconds()
        is_stale = delta > STALE_THRESHOLD_SECONDS
        conn_status = "ONLINE" if not is_stale else "STALE"

        return RobotTelemetryResponse(
            id=record.id,
            robot_id=record.robot_id,
            temperature_c=record.temperature_c,
            humidity_pct=record.humidity_pct,
            latitude=record.latitude,
            longitude=record.longitude,
            gps_fix=record.gps_fix,
            distance_m=record.distance_m,
            encoder_pulses=record.encoder_pulses or 0,
            battery_voltage=record.battery_voltage,
            obstacle_distance_cm=record.obstacle_distance_cm,
            device_timestamp=record.device_timestamp,
            received_at=record.received_at,
            is_stale=is_stale,
            connection_status=conn_status,
            source=record.source,
        )
