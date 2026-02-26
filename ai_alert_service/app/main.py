from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import psycopg2
import os

app = FastAPI(title="AI Alert Service")

# CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://supply_chain_user:supply_chain_pass@postgres:5432/supply_chain_db"
)

def get_conn():
    return psycopg2.connect(DATABASE_URL)


# ===== REQUEST MODELS =====
class StallCheckRequest(BaseModel):
    shipment_id: Optional[str] = None
    stall_minutes: Optional[float] = 15.0  # Default 15 minutes
    speed_threshold_kmph: Optional[float] = 5.0  # Default 5 km/h
    max_move_meters: Optional[float] = 100.0  # Default 100 meters


class DriverSafetyReport(BaseModel):
    shipment_id: str
    status: str
    details: Optional[str] = None


# ===== ENDPOINTS =====
@app.get("/health/db")
def health_db():
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            v = cur.fetchone()[0]
        conn.close()
        return {"db": "ok", "value": v}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/alerts/check-stall")
def check_stall(req: StallCheckRequest):
    """Check for stalled shipments"""
    conn = get_conn()
    created = []

    try:
        with conn:
            with conn.cursor() as cur:
                # Get shipments to check
                if req.shipment_id:
                    shipment_ids = [req.shipment_id]
                else:
                    cur.execute("SELECT shipment_id FROM shipments WHERE status = 'IN_TRANSIT'")
                    shipment_ids = [r[0] for r in cur.fetchall()]

                for sid in shipment_ids:
                    # Check if shipment has been stationary
                    cur.execute("""
                        SELECT 
                            AVG(speed_kmph) as avg_speed,
                            MAX(ts) as last_update,
                            EXTRACT(EPOCH FROM (NOW() - MAX(ts)))/60 as minutes_since_update
                        FROM telemetry
                        WHERE shipment_id = %s
                        AND ts > NOW() - INTERVAL '%s minutes'
                        GROUP BY shipment_id
                    """, (sid, req.stall_minutes * 2))  # Look at 2x the window
                    
                    result = cur.fetchone()
                    
                    if result:
                        avg_speed, last_update, minutes_since = result
                        
                        is_stalled = False
                        reason = ""
                        
                        # Check if speed is below threshold
                        if avg_speed < req.speed_threshold_kmph:
                            is_stalled = True
                            reason = f"Average speed {avg_speed:.1f} km/h below threshold ({req.speed_threshold_kmph} km/h)"
                        
                        # Check if no updates recently
                        if minutes_since > req.stall_minutes:
                            is_stalled = True
                            reason = f"No GPS updates for {minutes_since:.1f} minutes"
                        
                        if is_stalled:
                            # Insert alert
                            cur.execute("""
                                INSERT INTO alerts (shipment_id, alert_type, metric, value, threshold, is_active, created_at)
                                VALUES (%s, %s, %s, %s, %s, TRUE, NOW())
                            """, (
                                sid,
                                "SHIPMENT_STALLED",
                                "movement",
                                reason,
                                f"{req.stall_minutes}min"
                            ))
                            created.append({"shipment_id": sid, "reason": reason})

        conn.close()
        return {"created_alerts": created}
    
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/driver-safety/report")
def driver_safety(report: DriverSafetyReport):
    """Report driver safety issue"""
    conn = get_conn()

    try:
        with conn:
            with conn.cursor() as cur:
                if report.status.upper() != "ACTIVE":
                    cur.execute("""
                        INSERT INTO alerts (shipment_id, alert_type, metric, value, threshold, is_active, created_at)
                        VALUES (%s, %s, 'driver_safety', %s, 'critical', TRUE, NOW())
                    """, (
                        report.shipment_id,
                        report.status.lower(),
                        report.status.lower()
                    ))

        conn.close()
        return {"status": "processed"}
    
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))