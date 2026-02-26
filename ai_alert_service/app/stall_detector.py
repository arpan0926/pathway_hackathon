from datetime import datetime, timedelta
from .utils import haversine_km

def check_shipment_stall(cur, shipment_id, stall_minutes, speed_threshold, max_move_m):
    window_start = datetime.utcnow() - timedelta(minutes=stall_minutes)

    cur.execute("""
        SELECT ts, lat, lon, COALESCE(speed_kmph,0)
        FROM telemetry
        WHERE shipment_id = %s AND ts >= %s
        ORDER BY ts ASC
    """, (shipment_id, window_start))

    rows = cur.fetchall()
    if len(rows) < 2:
        return False, "INSUFFICIENT_DATA"

    start_lat, start_lon = rows[0][1], rows[0][2]
    end_lat, end_lon = rows[-1][1], rows[-1][2]

    dist_km = haversine_km(start_lat, start_lon, end_lat, end_lon)
    dist_m = dist_km * 1000

    all_low_speed = all(float(r[3]) <= speed_threshold for r in rows)

    if dist_m <= max_move_m and all_low_speed:
        return True, f"LOW_MOVEMENT_{dist_m:.1f}m"

    return False, "MOVING"