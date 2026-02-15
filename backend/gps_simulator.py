import time
import random
import psycopg2
from datetime import datetime
import numpy as np

class RealisticGPSSimulator:
    def __init__(self, shipment_id, route_points, vehicle_id):
        """
        route_points: List of (lat, lon) waypoints along the route
        """
        self.shipment_id = shipment_id
        self.route_points = route_points
        self.vehicle_id = vehicle_id
        self.current_segment = 0
        self.segment_progress = 0.0
        
        # Vehicle state
        self.speed = 0
        self.is_stopped = False
        self.delay_remaining = 0
        
    def simulate_traffic_conditions(self):
        """Simulate realistic traffic patterns"""
        hour = datetime.now().hour
        
        # Rush hour slowdowns (7-10 AM, 5-8 PM)
        if 7 <= hour <= 10 or 17 <= hour <= 20:
            return random.uniform(0.5, 0.8)  # 50-80% speed
        
        # Night time (faster)
        if hour < 6 or hour > 22:
            return random.uniform(1.0, 1.2)  # 100-120% speed
        
        return 1.0  # Normal
    
    def get_next_position(self):
        """Get next position along route"""
        if self.current_segment >= len(self.route_points) - 1:
            return None  # Journey complete
        
        # Random events
        if random.random() < 0.05:  # 5% chance of stop
            self.is_stopped = True
            self.delay_remaining = random.randint(5, 15)  # 5-15 seconds
            self.speed = 0
            
        if self.is_stopped:
            self.delay_remaining -= 1
            if self.delay_remaining <= 0:
                self.is_stopped = False
        
        # Calculate position
        p1 = self.route_points[self.current_segment]
        p2 = self.route_points[self.current_segment + 1]
        
        # Interpolate
        lat = p1[0] + (p2[0] - p1[0]) * self.segment_progress
        lon = p1[1] + (p2[1] - p1[1]) * self.segment_progress
        
        # Add GPS noise
        lat += random.gauss(0, 0.0001)  # ~11m accuracy
        lon += random.gauss(0, 0.0001)
        
        # Update progress
        if not self.is_stopped:
            traffic_factor = self.simulate_traffic_conditions()
            speed_variation = random.uniform(0.9, 1.1)
            self.speed = 60 * traffic_factor * speed_variation  # Base 60 km/h
            
            step = random.uniform(0.02, 0.05)
            self.segment_progress += step
            
            if self.segment_progress >= 1.0:
                self.current_segment += 1
                self.segment_progress = 0.0
        
        return (lat, lon, self.speed)


# Realistic routes (waypoints)
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
}


def run_realistic_simulation(shipment_id, origin, destination, vehicle_id):
    """Run realistic GPS simulation"""
    route = ROUTES.get((origin, destination))
    if not route:
        print(f"❌ No route defined for {origin} → {destination}")
        return
    
    sim = RealisticGPSSimulator(shipment_id, route, vehicle_id)
    
    print(f"\n🚛 {shipment_id}: {origin} → {destination}")
    print("=" * 60)
    
    while True:
        result = sim.get_next_position()
        if result is None:
            break
        
        lat, lon, speed = result
        load_status = "Loaded" if speed > 0 else "Stopped"
        
        # Insert to database
        insert_telemetry(shipment_id, lat, lon, speed, load_status)
        
        time.sleep(2)  # Update every 2 seconds
    
    print(f"✅ {shipment_id} completed!")


def insert_telemetry(shipment_id, lat, lon, speed, load_status):
    """Insert GPS data into PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5532,
            database="ai",
            user="ai",
            password="ai"
        )
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO telemetry (shipment_id, ts, lat, lon, speed_kmph, load_status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (shipment_id, datetime.now(), lat, lon, speed, load_status))
        
        conn.commit()
        conn.close()
        
        status_icon = "🟢" if speed > 40 else "🟡" if speed > 0 else "🔴"
        print(f"{status_icon} {shipment_id}: ({lat:.4f}, {lon:.4f}) @ {speed:.1f} km/h")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    run_realistic_simulation("SHP001", "Mumbai", "Delhi", "TRK-22")