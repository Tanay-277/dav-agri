import json
import logging
from typing import List, Set
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session
from app.database.session import get_db, SessionLocal
from app.schemas.common import APIResponse
from app.schemas.telemetry import (
    RobotTelemetryPacket,
    RobotTelemetryResponse,
    RobotStatusSummary,
)
from app.services.telemetry_service import TelemetryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telemetry", tags=["Robot Telemetry"])

class ConnectionManager:
    """Manages active WebSocket connections for live real-time telemetry streaming (Patent Claim 8, 15)."""
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"[WS] Telemetry client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"[WS] Telemetry client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        dead_connections = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"[WS] Error broadcasting to client: {e}")
                dead_connections.add(connection)
        for dead in dead_connections:
            self.active_connections.discard(dead)

manager = ConnectionManager()

@router.post("/packet", response_model=APIResponse[RobotTelemetryResponse])
async def ingest_telemetry_packet(packet: RobotTelemetryPacket, db: Session = Depends(get_db)):
    """Ingest, validate, store, and broadcast robot telemetry packet (Patent Section 4.5.4 & Claims 1, 5)."""
    service = TelemetryService(db)
    try:
        res = service.ingest_packet(packet)
        # Broadcast to active WebSocket clients for real-time dashboard update (Patent Section 4.5.6)
        await manager.broadcast(res.model_dump(mode="json"))
        return APIResponse.ok(res)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to ingest telemetry packet: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Telemetry ingestion failed")

@router.get("/status", response_model=APIResponse[RobotStatusSummary])
def get_robot_status(robot_id: str = "dav_robot_01", db: Session = Depends(get_db)):
    """Get current robot status, staleness indicator, and hardware diagnostics (Patent Claims 6, 9)."""
    service = TelemetryService(db)
    summary = service.get_latest_status(robot_id)
    return APIResponse.ok(summary)

@router.get("/history", response_model=APIResponse[List[RobotTelemetryResponse]])
def get_telemetry_history(robot_id: str = "dav_robot_01", limit: int = 50, db: Session = Depends(get_db)):
    """Fetch timestamped historical logs for graphing and trend inspection (Patent Section 4.5.8)."""
    service = TelemetryService(db)
    history = service.get_history(robot_id, limit=min(limit, 500))
    return APIResponse.ok(history)

@router.websocket("/live")
async def websocket_telemetry_feed(websocket: WebSocket):
    """Real-time WebSocket feed pushing validated readings to dashboard (Patent Section 4.5.6 & Claim 8)."""
    await manager.connect(websocket)
    db = SessionLocal()
    try:
        # Send initial status packet immediately upon connecting
        service = TelemetryService(db)
        status_summary = service.get_latest_status()
        await websocket.send_json({"type": "INIT_STATUS", "data": status_summary.model_dump(mode="json")})
        
        while True:
            # Keep connection open; receive ping or commands from client
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"[WS] WebSocket error: {e}")
        manager.disconnect(websocket)
    finally:
        db.close()
