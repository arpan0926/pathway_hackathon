# Member 1 (YOU) - TODO List

## What You Need to Implement

### Pathway Pipeline for ETA Calculation

**File:** `pathway_pipeline/pipeline.py`

---

## Step-by-Step Implementation Guide

### Step 1: Define Schema (5 minutes)

```python
import pathway as pw

class TelemetrySchema(pw.Schema):
    id: int
    shipment_id: str
    ts: str  # timestamp
    lat: float
    lon: float
    speed_kmph: float
    load_status: str
```

### Step 2: Read from PostgreSQL (10 minutes)

```python
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://...")

telemetry = pw.io.postgres.read(
    connection_string=DATABASE_URL,
    table_name="telemetry",
    schema=TelemetrySchema,
    mode="streaming"  # Real-time updates
)
```

### Step 3: Calculate Distance (15 minutes)

```python
# Destination coordinates
DESTINATIONS = {
    "SH001": {"name": "Delhi", "lat": 28.6139, "lon": 77.2090},
    "SH002": {"name": "Chennai", "lat": 13.0827, "lon": 80.2707}
}

@pw.udf
def calculate_distance(shipment_id: str, lat: float, lon: float) -> float:
    """Calculate distance to destination using Haversine formula"""
    dest = DESTINATIONS.get(shipment_id)
    if not dest:
        return 0.0
    
    return haversine_distance(lat, lon, dest["lat"], dest["lon"])

# Haversine formula (already provided in pipeline.py)
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in km
    # ... (see pipeline.py for full implementation)
```

### Step 4: Calculate Average Speed (20 minutes)

```python
# Option A: Simple - use current speed
processed = telemetry.select(
    shipment_id=telemetry.shipment_id,
    current_speed=telemetry.speed_kmph,
    distance_km=calculate_distance(telemetry.shipment_id, telemetry.lat, telemetry.lon)
)

# Option B: Advanced - rolling average (if you have time)
# Use pw.temporal.sliding_window to calculate average of last 5 points
```

### Step 5: Calculate ETA (10 minutes)

```python
@pw.udf
def calculate_eta(distance_km: float, speed_kmph: float) -> float:
    """Calculate ETA in minutes"""
    if speed_kmph <= 0:
        return 999.0  # Unknown/stopped
    
    eta_hours = distance_km / speed_kmph
    eta_minutes = eta_hours * 60
    return round(eta_minutes, 2)

# Add ETA to processed data
result = processed.select(
    *pw.this,
    eta_minutes=calculate_eta(pw.this.distance_km, pw.this.current_speed)
)
```

### Step 6: Write to PostgreSQL (10 minutes)

```python
# Write results to eta_history table
pw.io.postgres.write(
    result,
    connection_string=DATABASE_URL,
    table_name="eta_history",
    columns={
        "shipment_id": "shipment_id",
        "distance_remaining_km": "distance_km",
        "current_speed_kmph": "current_speed",
        "predicted_eta": "eta_minutes",  # Will be converted to timestamp
        "confidence": 85.0  # Fixed confidence for now
    }
)
```

### Step 7: Run the Pipeline (2 minutes)

```python
print("✅ Pathway pipeline started!")
pw.run()
```

---

## Complete Example (Simplified)

```python
import pathway as pw
import os
import math

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://...")

# Schema
class TelemetrySchema(pw.Schema):
    shipment_id: str
    lat: float
    lon: float
    speed_kmph: float

# Destinations
DESTINATIONS = {
    "SH001": {"lat": 28.6139, "lon": 77.2090},
    "SH002": {"lat": 13.0827, "lon": 80.2707}
}

# Haversine distance function
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

# UDFs
@pw.udf
def calc_distance(shipment_id: str, lat: float, lon: float) -> float:
    dest = DESTINATIONS.get(shipment_id)
    if not dest:
        return 0.0
    return haversine_distance(lat, lon, dest["lat"], dest["lon"])

@pw.udf
def calc_eta(distance: float, speed: float) -> float:
    if speed <= 0:
        return 999.0
    return (distance / speed) * 60

# Read
telemetry = pw.io.postgres.read(
    connection_string=DATABASE_URL,
    table_name="telemetry",
    schema=TelemetrySchema
)

# Process
result = telemetry.select(
    shipment_id=telemetry.shipment_id,
    distance_km=calc_distance(telemetry.shipment_id, telemetry.lat, telemetry.lon),
    speed_kmph=telemetry.speed_kmph,
    eta_minutes=calc_eta(pw.this.distance_km, telemetry.speed_kmph)
)

# Write
pw.io.postgres.write(result, connection_string=DATABASE_URL, table_name="eta_history")

# Run
pw.run()
```

---

## Testing Your Pipeline

### 1. Start GPS Simulator
```bash
docker-compose up postgres gps-simulator
```

### 2. Start Your Pipeline
```bash
docker-compose up pathway-pipeline
```

### 3. Check Results
```bash
# Connect to database
docker exec -it supply_chain_db psql -U supply_chain_user -d supply_chain_db

# Check ETA history
SELECT * FROM eta_history ORDER BY computed_at DESC LIMIT 10;
```

### 4. View on Dashboard
Open http://localhost:8501 - should show your ETA predictions!

---

## Timeline

- **Day 2 (Today)**: Implement basic pipeline (Steps 1-7)
- **Day 3**: Test and debug
- **Day 4**: Add rolling average speed (if time)
- **Day 5**: Integration testing with full system

---

## Resources

- **Pathway Docs**: https://pathway.com/developers/documentation
- **PostgreSQL Connector**: https://pathway.com/developers/user-guide/connect/connectors/
- **Your test files**: `pathway_pipeline/test/` folder
- **Integration plan**: `docs/integration_plan.md`

---

## Need Help?

1. Check Pathway documentation
2. Look at test examples in `pathway_pipeline/test/`
3. Ask team members
4. Check `shared/schemas.py` for data structures

---

## Success Criteria

✅ Pipeline reads from telemetry table  
✅ Calculates distance correctly  
✅ Computes ETA  
✅ Writes to eta_history table  
✅ Dashboard shows ETA predictions  

**You got this! 🚀**
