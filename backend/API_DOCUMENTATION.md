# Supply Chain Tracker API Documentation

## Base URL
```
http://localhost:8000
```

## Interactive API Docs
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Endpoints

### Health & Info

#### `GET /`
Root endpoint with API information
```json
{
  "message": "Supply Chain Tracker API",
  "status": "running",
  "version": "1.0.0",
  "endpoints": {...}
}
```

#### `GET /health`
Health check endpoint
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

### Shipments

#### `GET /api/shipments`
Get all shipments

**Query Parameters:**
- `status` (optional): Filter by status (e.g., "in_transit", "delivered")

**Response:**
```json
[
  {
    "shipment_id": "SH001",
    "vehicle_id": "VH001",
    "source": "Mumbai",
    "destination": "Delhi",
    "status": "in_transit",
    "current_eta": "2026-02-16T10:30:00",
    "last_updated": "2026-02-15T18:00:00"
  }
]
```

#### `GET /api/shipments/{shipment_id}`
Get specific shipment details

**Example:** `/api/shipments/SH001`

---

### Telemetry (GPS Data)

#### `GET /api/telemetry`
Get GPS telemetry data

**Query Parameters:**
- `shipment_id` (optional): Filter by shipment
- `vehicle_id` (optional): Filter by vehicle
- `limit` (optional, default=100, max=1000): Number of records

**Response:**
```json
[
  {
    "id": 1,
    "ts": "2026-02-15T18:00:00",
    "vehicle_id": "VH001",
    "shipment_id": "SH001",
    "lat": 19.0760,
    "lon": 72.8777,
    "speed_kmph": 65.5,
    "load_status": "LOADED"
  }
]
```

#### `GET /api/telemetry/latest/{shipment_id}`
Get latest GPS position for a shipment

**Example:** `/api/telemetry/latest/SH001`

---

### Alerts

#### `GET /api/alerts`
Get alerts

**Query Parameters:**
- `shipment_id` (optional): Filter by shipment
- `is_active` (optional): Filter by active status (true/false)
- `limit` (optional, default=50, max=500): Number of records

**Response:**
```json
[
  {
    "alert_id": 1,
    "shipment_id": "SH001",
    "alert_type": "delay",
    "metric": "eta_deviation",
    "value": "45",
    "threshold": "30",
    "created_at": "2026-02-15T18:00:00",
    "is_active": true
  }
]
```

#### `GET /api/alerts/critical`
Get all active critical alerts

---

### ETA History

#### `GET /api/eta-history`
Get ETA prediction history

**Query Parameters:**
- `shipment_id` (optional): Filter by shipment
- `limit` (optional, default=100, max=1000): Number of records

**Response:**
```json
[
  {
    "id": 1,
    "shipment_id": "SH001",
    "predicted_eta": "2026-02-16T10:30:00",
    "distance_remaining_km": 1150.5,
    "current_speed_kmph": 65.0,
    "confidence": 85.5,
    "computed_at": "2026-02-15T18:00:00"
  }
]
```

#### `GET /api/eta-history/latest/{shipment_id}`
Get latest ETA prediction for a shipment

**Example:** `/api/eta-history/latest/SH001`

---

### Statistics

#### `GET /api/stats`
Get overall system statistics

**Response:**
```json
{
  "total_shipments": 2,
  "active_alerts": 0,
  "avg_fleet_speed_kmph": 62.5,
  "total_telemetry_records": 150,
  "timestamp": "2026-02-15T18:00:00"
}
```

---

## Error Responses

### 404 Not Found
```json
{
  "detail": "Shipment SH999 not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Database connection failed: ..."
}
```

---

## Usage Examples

### cURL Examples

```bash
# Get all shipments
curl http://localhost:8000/api/shipments

# Get specific shipment
curl http://localhost:8000/api/shipments/SH001

# Get latest telemetry for SH001
curl http://localhost:8000/api/telemetry/latest/SH001

# Get active alerts
curl "http://localhost:8000/api/alerts?is_active=true"

# Get statistics
curl http://localhost:8000/api/stats
```

### Python Examples

```python
import requests

# Get all shipments
response = requests.get("http://localhost:8000/api/shipments")
shipments = response.json()

# Get latest telemetry
response = requests.get("http://localhost:8000/api/telemetry/latest/SH001")
telemetry = response.json()

# Get statistics
response = requests.get("http://localhost:8000/api/stats")
stats = response.json()
```

---

## Testing

Access the interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test all endpoints directly from the Swagger UI interface.
