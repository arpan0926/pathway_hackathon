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
    
class OverspeedCheckRequest(BaseModel):
    shipment_id: Optional[str] = None
    speed_limit_kmph: Optional[float] = 80.0  # Default speed limit
    duration_minutes: Optional[int] = 10  # Look back window
    min_violations: Optional[int] = 5  # Min violations to trigger alert