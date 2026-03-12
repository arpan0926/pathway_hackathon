from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import psycopg2
import os
from .overspeed_detector import check_shipment_overspeed, check_excessive_acceleration  # ADD THIS

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
    stall_minutes: Optional[float] = 15.0
    speed_threshold_kmph: Optional[float] = 5.0
    max_move_meters: Optional[float] = 100.0

class DriverSafetyReport(BaseModel):
    shipment_id: str
    status: str
    details: Optional[str] = None

# ADD THIS:
class OverspeedCheckRequest(BaseModel):
    shipment_id: Optional[str] = None
    speed_limit_kmph: Optional[float] = 80.0
    duration_minutes: Optional[int] = 10
    min_violations: Optional[int] = 5


# ===== EXISTING ENDPOINTS =====
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
                if req.shipment_id:
                    shipment_ids = [req.shipment_id]
                else:
                    cur.execute("SELECT shipment_id FROM shipments WHERE status = 'IN_TRANSIT'")
                    shipment_ids = [r[0] for r in cur.fetchall()]

                for sid in shipment_ids:
                    cur.execute("""
                        SELECT 
                            AVG(speed_kmph) as avg_speed,
                            MAX(ts) as last_update,
                            EXTRACT(EPOCH FROM (NOW() - MAX(ts)))/60 as minutes_since_update
                        FROM telemetry
                        WHERE shipment_id = %s
                        AND ts > NOW() - INTERVAL '%s minutes'
                        GROUP BY shipment_id
                    """, (sid, req.stall_minutes * 2))
                    
                    result = cur.fetchone()
                    
                    if result:
                        avg_speed, last_update, minutes_since = result
                        
                        is_stalled = False
                        reason = ""
                        
                        if avg_speed < req.speed_threshold_kmph:
                            is_stalled = True
                            reason = f"Average speed {avg_speed:.1f} km/h below threshold ({req.speed_threshold_kmph} km/h)"
                        
                        if minutes_since > req.stall_minutes:
                            is_stalled = True
                            reason = f"No GPS updates for {minutes_since:.1f} minutes"
                        
                        if is_stalled:
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


# ADD THIS NEW ENDPOINT:
@app.post("/alerts/check-overspeed")
def check_overspeed(req: OverspeedCheckRequest):
    """Check for overspeeding violations"""
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
                    # Check for overspeeding
                    is_overspeeding, reason = check_shipment_overspeed(
                        cur,
                        sid,
                        req.speed_limit_kmph,
                        req.duration_minutes,
                        req.min_violations
                    )

                    if is_overspeeding:
                        # Check if alert already exists (avoid duplicates)
                        cur.execute("""
                            SELECT alert_id FROM alerts
                            WHERE shipment_id = %s 
                            AND alert_type = 'OVERSPEED'
                            AND is_active = TRUE
                            AND created_at > NOW() - INTERVAL '30 minutes'
                        """, (sid,))
                        
                        if not cur.fetchone():
                            # Insert alert
                            cur.execute("""
                                INSERT INTO alerts (shipment_id, alert_type, metric, value, threshold, is_active, created_at)
                                VALUES (%s, %s, %s, %s, %s, TRUE, NOW())
                            """, (
                                sid,
                                "OVERSPEED",
                                "speed",
                                reason,
                                f"{req.speed_limit_kmph}kmh"
                            ))
                            created.append({"shipment_id": sid, "reason": reason})

                    # Also check for dangerous acceleration
                    is_dangerous, accel_reason = check_excessive_acceleration(cur, sid)
                    if is_dangerous:
                        cur.execute("""
                            SELECT alert_id FROM alerts
                            WHERE shipment_id = %s 
                            AND alert_type = 'DANGEROUS_ACCELERATION'
                            AND is_active = TRUE
                            AND created_at > NOW() - INTERVAL '15 minutes'
                        """, (sid,))
                        
                        if not cur.fetchone():
                            cur.execute("""
                                INSERT INTO alerts (shipment_id, alert_type, metric, value, threshold, is_active, created_at)
                                VALUES (%s, %s, %s, %s, %s, TRUE, NOW())
                            """, (
                                sid,
                                "DANGEROUS_ACCELERATION",
                                "acceleration",
                                accel_reason,
                                "20kmh_per_min"
                            ))
                            created.append({"shipment_id": sid, "reason": accel_reason})

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