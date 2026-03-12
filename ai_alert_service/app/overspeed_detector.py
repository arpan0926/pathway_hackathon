from datetime import datetime, timedelta

def check_shipment_overspeed(cur, shipment_id, speed_limit_kmph, duration_minutes, min_violations):
    """
    Check if a shipment has been overspeeding
    
    Args:
        cur: Database cursor
        shipment_id: Shipment ID to check
        speed_limit_kmph: Maximum allowed speed (e.g., 80 km/h)
        duration_minutes: Time window to check (e.g., 10 minutes)
        min_violations: Minimum number of violations to trigger alert (e.g., 5)
    
    Returns:
        (is_overspeeding, reason) tuple
    """
    window_start = datetime.utcnow() - timedelta(minutes=duration_minutes)

    # Get telemetry data from the time window
    cur.execute("""
        SELECT ts, speed_kmph, lat, lon
        FROM telemetry
        WHERE shipment_id = %s AND ts >= %s
        ORDER BY ts DESC
    """, (shipment_id, window_start))

    rows = cur.fetchall()
    
    if len(rows) < min_violations:
        return False, "INSUFFICIENT_DATA"

    # Count violations
    violations = [row for row in rows if float(row[1]) > speed_limit_kmph]
    violation_count = len(violations)
    
    if violation_count < min_violations:
        return False, "NO_VIOLATIONS"

    # Calculate statistics
    max_speed = max(float(row[1]) for row in violations)
    avg_speed_violations = sum(float(row[1]) for row in violations) / len(violations)
    
    # Calculate violation percentage
    violation_percentage = (violation_count / len(rows)) * 100

    reason = (
        f"OVERSPEEDING: {violation_count}/{len(rows)} readings exceeded {speed_limit_kmph} km/h "
        f"({violation_percentage:.0f}% violations). "
        f"Max speed: {max_speed:.1f} km/h, Avg during violations: {avg_speed_violations:.1f} km/h"
    )

    return True, reason


def get_current_speed(cur, shipment_id):
    """Get the most recent speed for a shipment"""
    cur.execute("""
        SELECT speed_kmph
        FROM telemetry
        WHERE shipment_id = %s
        ORDER BY ts DESC
        LIMIT 1
    """, (shipment_id,))
    
    result = cur.fetchone()
    return float(result[0]) if result else 0.0


def check_excessive_acceleration(cur, shipment_id, window_minutes=5, accel_threshold=20):
    """
    Check for dangerous acceleration (speed increase > threshold in short time)
    
    Args:
        cur: Database cursor
        shipment_id: Shipment ID
        window_minutes: Time window (default 5 min)
        accel_threshold: Speed increase threshold in km/h (default 20)
    
    Returns:
        (is_dangerous, reason) tuple
    """
    window_start = datetime.utcnow() - timedelta(minutes=window_minutes)
    
    cur.execute("""
        SELECT ts, speed_kmph
        FROM telemetry
        WHERE shipment_id = %s AND ts >= %s
        ORDER BY ts ASC
    """, (shipment_id, window_start))
    
    rows = cur.fetchall()
    
    if len(rows) < 2:
        return False, "INSUFFICIENT_DATA"
    
    # Check for rapid acceleration
    for i in range(1, len(rows)):
        speed_diff = float(rows[i][1]) - float(rows[i-1][1])
        time_diff = (rows[i][0] - rows[i-1][0]).total_seconds() / 60  # minutes
        
        if time_diff > 0 and speed_diff > accel_threshold:
            accel_rate = speed_diff / time_diff  # km/h per minute
            reason = (
                f"DANGEROUS_ACCELERATION: Speed increased by {speed_diff:.1f} km/h "
                f"in {time_diff:.1f} minutes ({accel_rate:.1f} km/h/min)"
            )
            return True, reason
    
    return False, "NORMAL_ACCELERATION"