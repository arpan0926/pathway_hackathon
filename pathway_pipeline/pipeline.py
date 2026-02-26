"""
Pathway Pipeline - Member 1
Real-time ETA Calculation
"""

import pathway as pw
import os
import math
from datetime import datetime, timedelta

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://supply_chain_user:supply_chain_pass@postgres:5432/supply_chain_db")

print("=" * 60)
print("🚀 PATHWAY PIPELINE - ETA CALCULATION")
print("=" * 60)
print(f"📊 Database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}")
print()

# Destination coordinates (from shared/schemas.py)
DESTINATIONS = {
    "SH001": {"name": "Delhi", "lat": 28.6139, "lon": 77.2090},
    "SH002": {"name": "Chennai", "lat": 13.0827, "lon": 80.2707},
    "SH003": {"name": "Hyderabad", "lat": 17.3850, "lon": 78.4867},
    "SH004": {"name": "Ahmedabad", "lat": 23.0225, "lon": 72.5714},
}

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two GPS coordinates in kilometers
    Using Haversine formula
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


# Define schema for telemetry data
class TelemetrySchema(pw.Schema):
    shipment_id: str
    ts: str
    lat: float
    lon: float
    speed_kmph: float
    load_status: str


print("📡 Reading GPS telemetry from PostgreSQL...")

# Read from PostgreSQL telemetry table
telemetry = pw.io.csv.read(
    "./data/gps_stream.csv",
    schema=TelemetrySchema,
    mode="streaming"
)

# Note: Using CSV for now as Pathway's PostgreSQL connector requires specific setup
# In production, use: pw.io.postgres.read(connection_string=DATABASE_URL, table_name="telemetry")


print("🧮 Setting up ETA calculation functions...")

# UDF to calculate distance to destination
@pw.udf
def calculate_distance(shipment_id: str, lat: float, lon: float) -> float:
    """Calculate distance to destination using Haversine formula"""
    dest = DESTINATIONS.get(shipment_id)
    if not dest:
        return 0.0
    
    return haversine_distance(lat, lon, dest["lat"], dest["lon"])


# UDF to calculate ETA
@pw.udf
def calculate_eta(distance_km: float, speed_kmph: float) -> float:
    """Calculate ETA in minutes"""
    if speed_kmph <= 0 or speed_kmph is None:
        return 999.0  # Unknown/stopped
    
    eta_hours = distance_km / speed_kmph
    eta_minutes = eta_hours * 60
    return round(eta_minutes, 2)


# UDF to calculate confidence score
@pw.udf
def calculate_confidence(speed_kmph: float, distance_km: float) -> float:
    """Calculate confidence score (0-100)"""
    # Higher confidence when:
    # - Speed is consistent (not 0 or too high)
    # - Distance is reasonable
    
    if speed_kmph <= 0:
        return 50.0  # Low confidence when stopped
    elif speed_kmph > 100:
        return 60.0  # Medium confidence for high speed
    elif distance_km < 10:
        return 95.0  # High confidence when close
    else:
        return 85.0  # Good confidence for normal conditions


print("⚙️  Processing telemetry data...")

# Process telemetry data
processed = telemetry.select(
    shipment_id=telemetry.shipment_id,
    ts=telemetry.ts,
    current_lat=telemetry.lat,
    current_lon=telemetry.lon,
    current_speed_kmph=telemetry.speed_kmph,
    load_status=telemetry.load_status,
    distance_remaining_km=calculate_distance(telemetry.shipment_id, telemetry.lat, telemetry.lon)
)

# Add ETA calculation
result = processed.select(
    pw.this.shipment_id,
    pw.this.ts,
    pw.this.current_lat,
    pw.this.current_lon,
    pw.this.distance_remaining_km,
    pw.this.current_speed_kmph,
    pw.this.load_status,
    eta_minutes=calculate_eta(pw.this.distance_remaining_km, pw.this.current_speed_kmph),
    confidence=calculate_confidence(pw.this.current_speed_kmph, pw.this.distance_remaining_km)
)


print("💾 Writing results to output...")

# Write to CSV (for demo)
pw.io.csv.write(result, "./outputs/eta_predictions.csv")

# Also write to stdout for monitoring
def print_eta_update(key, row, time, is_addition):
    if is_addition:
        shipment = row.get('shipment_id', 'Unknown')
        distance = row.get('distance_remaining_km', 0)
        speed = row.get('current_speed_kmph', 0)
        eta = row.get('eta_minutes', 0)
        confidence = row.get('confidence', 0)
        
        # Status icon based on ETA
        if eta < 60:
            icon = "🟢"
        elif eta < 180:
            icon = "🟡"
        else:
            icon = "🔴"
        
        print(f"{icon} {shipment}: {distance:.1f}km away | Speed: {speed:.1f}km/h | ETA: {eta:.0f}min | Confidence: {confidence:.0f}%")
        
        # Write to PostgreSQL eta_history table
        try:
            import psycopg2
            from datetime import datetime, timedelta
            
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            
            # Calculate predicted ETA timestamp
            predicted_eta = datetime.now() + timedelta(minutes=float(eta))
            
            cur.execute("""
                INSERT INTO eta_history 
                (shipment_id, predicted_eta, distance_remaining_km, current_speed_kmph, confidence, computed_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (shipment, predicted_eta, distance, speed, confidence))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️  Database write error: {e}")

pw.io.subscribe(result, print_eta_update)


print("\n✅ Pathway pipeline configured successfully!")
print("\n📊 Monitoring ETA calculations...")
print("=" * 60)
print()

# Run the pipeline
try:
    pw.run()
except KeyboardInterrupt:
    print("\n\n🛑 Pipeline stopped by user")
except Exception as e:
    print(f"\n\n❌ Pipeline error: {e}")
    raise
