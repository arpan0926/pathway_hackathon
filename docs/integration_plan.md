# Integration Plan - All Members

## Data Flow Architecture

```
Member 2 (GPS Simulator)
    ↓ writes to
PostgreSQL Database (telemetry table)
    ↓ reads from
Member 1 (Pathway Pipeline)
    ↓ writes to
PostgreSQL Database (eta_history table)
    ↓ reads from
Member 2 (Backend API)
    ↓ exposes
REST API Endpoints
    ↓ consumed by
Member 3 (Dashboard) & Member 4 (Chatbot)
```

## Database Setup (Member 2's Responsibility)

### PostgreSQL Database: `supply_chain_db`

**Tables:**
1. `shipments` - Shipment master data
2. `telemetry` - GPS data from simulator (needs to be created)
3. `alerts` - Alert records
4. `shipment_events` - Event logs
5. `eta_history` - ETA predictions from Member 1

### Connection Details

```python
DATABASE_URL = "postgresql://user:password@localhost:5432/supply_chain_db"
```

**Member 2:** Please create the `telemetry` table:

```sql
CREATE TABLE telemetry (
    id SERIAL PRIMARY KEY,
    ts TIMESTAMP NOT NULL,
    vehicle_id TEXT NOT NULL,
    shipment_id TEXT NOT NULL,
    lat NUMERIC(10, 6) NOT NULL,
    lon NUMERIC(10, 6) NOT NULL,
    speed_kmph NUMERIC(6, 2),
    load_status TEXT CHECK (load_status IN ('LOADED', 'UNLOADED', 'PARTIAL')),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_telemetry_shipment ON telemetry(shipment_id, ts DESC);
CREATE INDEX idx_telemetry_vehicle ON telemetry(vehicle_id, ts DESC);
```

## Member 1 (Pathway Pipeline) - Integration Tasks

### Input: Read from PostgreSQL
```python
# Read GPS telemetry from database
gps_stream = pw.io.postgres.read(
    connection_string=DATABASE_URL,
    table_name="telemetry",
    schema=GPSSchema
)
```

### Processing:
1. Calculate distance to destination
2. Calculate average speed (from last N points)
3. Compute ETA
4. Determine status (in_transit, delayed, stopped)
5. Calculate confidence score

### Output: Write to PostgreSQL
```python
# Write processed data to eta_history table
pw.io.postgres.write(
    processed_data,
    connection_string=DATABASE_URL,
    table_name="eta_history"
)
```

**Fields to write:**
- `shipment_id`
- `predicted_eta` (timestamp)
- `confidence` (0-100)
- `computed_at` (timestamp)

## Member 2 (Backend API) - Integration Tasks

### Read from Database:
1. Latest telemetry for each shipment
2. Latest ETA from eta_history
3. Active alerts

### API Endpoints:

```python
# 1. Get shipment status
GET /api/shipments/{shipment_id}
Response: {
    "shipment_id": "SH001",
    "vehicle_id": "VH001",
    "source": "Mumbai",
    "destination": "Delhi",
    "current_location": {"lat": 19.0760, "lon": 72.8777},
    "current_speed_kmph": 65.5,
    "distance_remaining_km": 1156.23,
    "eta_minutes": 1060,
    "predicted_eta": "2026-02-09T28:10:00",
    "confidence": 85.5,
    "status": "in_transit",
    "load_status": "LOADED"
}

# 2. Get all shipments
GET /api/shipments
Response: [...]

# 3. Get shipment location history
GET /api/shipments/{shipment_id}/location-history?limit=10
Response: [...]

# 4. Get all alerts
GET /api/alerts
Response: [...]

# 5. Get alerts for shipment
GET /api/alerts/{shipment_id}
Response: [...]
```

### Alert Logic:
```python
# Read latest ETA from eta_history
# Compare with expected ETA
# If difference > 30 minutes:
#   INSERT INTO alerts (shipment_id, alert_type, metric, value, threshold)
```

## Member 3 (Dashboard) - Integration Tasks

### Call Backend API:
```python
import requests

# Get all shipments
response = requests.get("http://localhost:8000/api/shipments")
shipments = response.json()

# Get alerts
response = requests.get("http://localhost:8000/api/alerts")
alerts = response.json()
```

### Display:
1. Live map with vehicle locations
2. ETA countdown for each shipment
3. Alert notifications
4. Shipment status cards

## Member 4 (Chatbot) - Integration Tasks

### Call Backend API:
```python
# Query shipment status
response = requests.get(f"http://localhost:8000/api/shipments/{shipment_id}")
data = response.json()

# Answer: "Shipment SH001 is 1156 km away, ETA is 17.6 hours"
```

### Sample Queries:
- "What is the ETA for shipment SH001?"
- "Show me all delayed shipments"
- "What alerts are active?"

## Testing Integration

### Day 3-4: Initial Integration Test

**Step 1:** Member 2 sets up PostgreSQL database
```bash
# Install PostgreSQL
# Create database and tables
# Share connection details with team
```

**Step 2:** Member 2 runs GPS simulator
```bash
python backend/simulator.py
# Should write to telemetry table
```

**Step 3:** Member 1 runs Pathway pipeline
```bash
docker-compose up pathway-pipeline
# Should read from telemetry, write to eta_history
```

**Step 4:** Member 2 starts Backend API
```bash
cd backend
uvicorn main:app --reload
# Should expose API endpoints
```

**Step 5:** Member 3 & 4 test API calls
```bash
curl http://localhost:8000/api/shipments
curl http://localhost:8000/api/alerts
```

### Day 5-6: Full Integration Test

Run all components together:
1. GPS Simulator (Member 2)
2. Pathway Pipeline (Member 1)
3. Backend API (Member 2)
4. Dashboard (Member 3)
5. Chatbot (Member 4)

Verify:
- GPS data flows to database
- Pathway processes and updates ETA
- API returns correct data
- Dashboard shows live updates
- Chatbot answers queries
- Alerts trigger correctly

## Environment Variables

Create `.env` file in project root:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/supply_chain_db

# Backend API
BACKEND_HOST=localhost
BACKEND_PORT=8000

# Dashboard
DASHBOARD_PORT=8501

# OpenAI (for chatbot)
OPENAI_API_KEY=your_key_here

# Pathway
PATHWAY_LICENSE_KEY=your_key_here
```

## Troubleshooting

### Database Connection Issues
```bash
# Test connection
psql -U user -d supply_chain_db -h localhost

# Check if tables exist
\dt

# View data
SELECT * FROM telemetry LIMIT 5;
SELECT * FROM eta_history LIMIT 5;
```

### API Not Responding
```bash
# Check if API is running
curl http://localhost:8000/docs

# View logs
docker logs backend_api
```

### Pathway Pipeline Issues
```bash
# Check logs
docker logs pathway_pipeline

# Verify input data
SELECT * FROM telemetry ORDER BY ts DESC LIMIT 5;
```

## Next Steps

**Member 1 (You):**
- [ ] Update Pathway pipeline to read from PostgreSQL
- [ ] Implement ETA calculation logic
- [ ] Write results to eta_history table
- [ ] Test with Member 2's simulator

**Member 2:**
- [ ] Create telemetry table in PostgreSQL
- [ ] Update GPS simulator to write to database
- [ ] Build FastAPI endpoints
- [ ] Implement alert logic

**Member 3:**
- [ ] Wait for API endpoints to be ready
- [ ] Build dashboard UI
- [ ] Integrate with Backend API

**Member 4:**
- [ ] Wait for API endpoints to be ready
- [ ] Build RAG chatbot
- [ ] Integrate with Backend API
