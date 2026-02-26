from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class StallCheckRequest(BaseModel):
    shipment_id: Optional[str] = None
    stall_minutes: int = 20
    speed_threshold_kmph: float = 2.0
    max_move_meters: float = 100.0

class DriverSafetyReport(BaseModel):
    shipment_id: str
    vehicle_id: str
    status: str  # ACTIVE, DROWSY, HEAD_DOWN, DRUNK
    confidence: Optional[float] = None
    details: Optional[str] = None
    ts: Optional[datetime] = None