from fastapi import FastAPI
from .db import get_conn
from .models import StallCheckRequest, DriverSafetyReport
from .stall_detector import check_shipment_stall
from .driver_alerts import create_driver_alert
from fastapi import HTTPException
import traceback
from fastapi.middleware.cors import CORSMiddleware
from .db import get_conn
app = FastAPI(title="AI Alert Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health/db")
def health_db():
    try:
        conn = get_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            v = cur.fetchone()[0]
        conn.close()
        return {"db": "ok", "value": v}
    except Exception:
        raise HTTPException(status_code=500, detail=traceback.format_exc())



@app.post("/alerts/check-stall")
def check_stall(req: StallCheckRequest):
    conn = get_conn()
    created = []

    with conn:
        with conn.cursor() as cur:
            if req.shipment_id:
                shipment_ids = [req.shipment_id]
            else:
                cur.execute("SELECT shipment_id FROM shipments")
                shipment_ids = [r[0] for r in cur.fetchall()]

            for sid in shipment_ids:
                is_stalled, reason = check_shipment_stall(
                    cur,
                    sid,
                    req.stall_minutes,
                    req.speed_threshold_kmph,
                    req.max_move_meters
                )

                if is_stalled:
                    cur.execute("""
                        INSERT INTO alerts (shipment_id, alert_type, metric, value, threshold, is_active)
                        VALUES (%s, %s, %s, %s, %s, TRUE)
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


@app.post("/driver-safety/report")
def driver_safety(report: DriverSafetyReport):
    conn = get_conn()

    with conn:
        with conn.cursor() as cur:
            if report.status != "ACTIVE":
                create_driver_alert(
                    cur,
                    report.shipment_id,
                    report.status,
                    report.details or "webcam_trigger"
                )

    conn.close()
    return {"status": "processed"}