"""
Bridge script to read from PostgreSQL and write to CSV for Pathway
This runs continuously and syncs data
"""

import psycopg2
import csv
import time
import os
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://supply_chain_user:supply_chain_pass@postgres:5432/supply_chain_db")
OUTPUT_FILE = "./data/gps_stream.csv"

print("🔄 PostgreSQL to CSV Bridge")
print("=" * 60)

# Create data directory if it doesn't exist
os.makedirs("./data", exist_ok=True)

# Initialize CSV file with headers
with open(OUTPUT_FILE, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['shipment_id', 'ts', 'lat', 'lon', 'speed_kmph', 'load_status'])

print(f"📁 Writing to: {OUTPUT_FILE}")
print(f"📊 Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}")
print("\n⏳ Syncing data every 2 seconds...")
print("=" * 60)
print()

last_id = 0

try:
    while True:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            
            # Get new telemetry data since last sync
            cur.execute("""
                SELECT id, shipment_id, ts, lat, lon, speed_kmph, load_status
                FROM telemetry
                WHERE id > %s
                ORDER BY id
            """, (last_id,))
            
            rows = cur.fetchall()
            
            if rows:
                # Append new data to CSV
                with open(OUTPUT_FILE, 'a', newline='') as f:
                    writer = csv.writer(f)
                    for row in rows:
                        row_id, shipment_id, ts, lat, lon, speed, load_status = row
                        writer.writerow([shipment_id, ts, lat, lon, speed, load_status])
                        last_id = row_id
                        print(f"✅ Synced: {shipment_id} @ ({lat:.4f}, {lon:.4f}) - {speed:.1f} km/h")
            
            conn.close()
            
        except Exception as e:
            print(f"⚠️  Error: {e}")
        
        time.sleep(2)  # Sync every 2 seconds
        
except KeyboardInterrupt:
    print("\n\n🛑 Bridge stopped")
