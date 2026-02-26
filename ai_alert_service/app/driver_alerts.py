def create_driver_alert(cur, shipment_id, status, details):
    alert_type = f"DRIVER_{status}"

    cur.execute("""
        INSERT INTO alerts (shipment_id, alert_type, metric, value, threshold, is_active)
        VALUES (%s, %s, %s, %s, %s, TRUE)
    """, (
        shipment_id,
        alert_type,
        "webcam_driver_safety",
        details,
        "edge_model_detected"
    ))