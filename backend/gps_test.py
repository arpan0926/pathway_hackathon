import psycopg2
from datetime import datetime
import time
import random

def send_gps_update(shipment_id, lat, lon, speed):
    conn = psycopg2.connect(
        host="localhost", port=5532, database="ai", user="ai", password="ai"
    )
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO telemetry (shipment_id, ts, lat, lon, speed_kmph, load_status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (shipment_id, datetime.now(), lat, lon, speed, "Loaded"))
    conn.commit()
    conn.close()
    print(f"📍 {shipment_id}: {lat}, {lon} @ {speed} km/h")

# Simulate Mumbai to Delhi journey
lat, lon = 19.0760, 72.8777  # Start at Mumbai

for i in range(20):
    # Move towards Delhi (28.6139, 77.2090)
    lat += 0.5
    lon += 0.2
    speed = random.uniform(40, 70)
    
    send_gps_update("SHP001", lat, lon, speed)
    time.sleep(3)