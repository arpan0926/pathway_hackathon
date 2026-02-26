import time
import random
import psycopg2
import os
from datetime import datetime
import numpy as np
import threading

class RealisticGPSSimulator:
    def __init__(self, shipment_id, route_points, vehicle_id):
        self.shipment_id = shipment_id
        self.route_points = route_points
        self.vehicle_id = vehicle_id
        self.current_segment = 0
        self.segment_progress = 0.0
        self.speed = 0
        self.is_stopped = False
        self.delay_remaining = 0

    def simulate_traffic_conditions(self):
        hour = datetime.now().hour
        if 7 <= hour <= 10 or 17 <= hour <= 20:
            return random.uniform(0.5, 0.8)
        if hour < 6 or hour > 22:
            return random.uniform(1.0, 1.2)
        return 1.0

    def get_next_position(self):
        if self.current_segment >= len(self.route_points) - 1:
            # Loop back to start for continuous demo
            self.current_segment = 0
            self.segment_progress = 0.0

        if random.random() < 0.05:
            self.is_stopped = True
            self.delay_remaining = random.randint(5, 15)
            self.speed = 0

        if self.is_stopped:
            self.delay_remaining -= 1
            if self.delay_remaining <= 0:
                self.is_stopped = False

        p1 = self.route_points[self.current_segment]
        p2 = self.route_points[self.current_segment + 1]

        lat = p1[0] + (p2[0] - p1[0]) * self.segment_progress
        lon = p1[1] + (p2[1] - p1[1]) * self.segment_progress

        lat += random.gauss(0, 0.0001)
        lon += random.gauss(0, 0.0001)

        if not self.is_stopped:
            traffic_factor = self.simulate_traffic_conditions()
            speed_variation = random.uniform(0.9, 1.1)
            self.speed = 60 * traffic_factor * speed_variation

            step = random.uniform(0.02, 0.05)
            self.segment_progress += step

            if self.segment_progress >= 1.0:
                self.current_segment += 1
                self.segment_progress = 0.0

        return (lat, lon, self.speed)


# Routes with 4 different shipments
ROUTES = {
    ("Mumbai", "Delhi"): [
        (19.0760, 72.8777),  # Mumbai
        (20.5937, 78.9629),  # Madhya Pradesh
        (23.2599, 77.4126),  # Bhopal
        (26.9124, 75.7873),  # Jaipur
        (28.6139, 77.2090),  # Delhi
    ],
    ("Bangalore", "Chennai"): [
        (12.9716, 77.5946),  # Bangalore
        (12.8406, 78.1182),  # Waypoint
        (13.0827, 80.2707),  # Chennai
    ],
    ("Kolkata", "Hyderabad"): [
        (22.5726, 88.3639),  # Kolkata
        (21.1458, 79.0882),  # Nagpur
        (19.0760, 79.0882),  # Waypoint
        (17.3850, 78.4867),  # Hyderabad
    ],
    ("Pune", "Ahmedabad"): [
        (18.5204, 73.8567),  # Pune
        (19.9975, 73.7898),  # Nashik
        (21.1702, 72.8311),  # Surat
        (23.0225, 72.5714),  # Ahmedabad
    ],
}


def get_db_connection():
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://supply_chain_user:supply_chain_pass@postgres:5432/supply_chain_db"
    )
    return psycopg2.connect(db_url)


def ensure_shipments_exist():
    """Make sure all 4 shipments exist in shipments table"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO shipments (shipment_id, vehicle_id, source, destination, status, last_updated)
            VALUES
                ('SH001', 'VH001', 'Mumbai', 'Delhi', 'IN_TRANSIT', NOW()),
                ('SH002', 'VH002', 'Bangalore', 'Chennai', 'IN_TRANSIT', NOW()),
                ('SH003', 'VH003', 'Kolkata', 'Hyderabad', 'IN_TRANSIT', NOW()),
                ('SH004', 'VH004', 'Pune', 'Ahmedabad', 'IN_TRANSIT', NOW())
            ON CONFLICT (shipment_id) DO UPDATE
                SET status = 'IN_TRANSIT', last_updated = NOW();
        """)
        conn.commit()
        conn.close()
        print("✅ All 4 shipments ready in DB")
    except Exception as e:
        print(f"⚠️  Could not ensure shipments: {e}")


def insert_telemetry(shipment_id, vehicle_id, lat, lon, speed, load_status):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO telemetry (shipment_id, vehicle_id, ts, lat, lon, speed_kmph, load_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (shipment_id, vehicle_id, datetime.now(), lat, lon, speed, load_status))

        cur.execute("""
            UPDATE shipments
            SET last_updated = NOW(), status = 'IN_TRANSIT'
            WHERE shipment_id = %s
        """, (shipment_id,))

        conn.commit()
        conn.close()

        icon = "🟢" if speed > 40 else "🟡" if speed > 0 else "🔴"
        print(f"{icon} [{shipment_id}] ({lat:.4f}, {lon:.4f}) @ {speed:.1f} km/h | {load_status}")

    except Exception as e:
        print(f"❌ DB Error [{shipment_id}]: {e}")


def run_simulation(shipment_id, origin, destination, vehicle_id):
    """Run a single shipment simulation in a loop"""
    route = ROUTES.get((origin, destination))
    if not route:
        print(f"❌ No route for {origin} → {destination}")
        return

    sim = RealisticGPSSimulator(shipment_id, route, vehicle_id)
    print(f"\n🚛 Starting {shipment_id}: {origin} → {destination}")

    while True:
        result = sim.get_next_position()
        if result is None:
            sim.current_segment = 0
            sim.segment_progress = 0.0
            continue

        lat, lon, speed = result
        load_status = "LOADED" if speed > 0 else "PARTIAL"
        insert_telemetry(shipment_id, vehicle_id, lat, lon, speed, load_status)
        time.sleep(2)


if __name__ == "__main__":
    print("\n🚀 Starting GPS Simulator — 4 Shipments in Parallel")
    print("=" * 60)

    # Wait for DB
    print("⏳ Waiting for database...")
    for attempt in range(10):
        try:
            conn = get_db_connection()
            conn.close()
            print("✅ Database connected!")
            break
        except Exception:
            print(f"   Attempt {attempt + 1}/10 — retrying in 3s...")
            time.sleep(3)

    ensure_shipments_exist()

    # Run ALL 4 shipments in parallel threads
    threads = [
        threading.Thread(target=run_simulation, args=("SH001", "Mumbai", "Delhi", "VH001"), daemon=True),
        threading.Thread(target=run_simulation, args=("SH002", "Bangalore", "Chennai", "VH002"), daemon=True),
        threading.Thread(target=run_simulation, args=("SH003", "Kolkata", "Hyderabad", "VH003"), daemon=True),
        threading.Thread(target=run_simulation, args=("SH004", "Pune", "Ahmedabad", "VH004"), daemon=True),
    ]

    for i, t in enumerate(threads):
        t.start()
        time.sleep(0.5)  # Stagger starts

    print("\n✅ All 4 simulators running! Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Simulator stopped.")