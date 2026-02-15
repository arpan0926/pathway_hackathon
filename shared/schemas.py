"""
Shared Data Schemas for Supply Chain Tracker
Agreed upon by all team members
"""

from datetime import datetime
from typing import Optional

# ============================================================================
# GPS TELEMETRY SCHEMA (from Member 2's simulator)
# ============================================================================

GPS_TELEMETRY_SCHEMA = {
    "ts": "ISO-8601 timestamp",           # Timestamp of GPS reading
    "vehicle_id": "string",                # Vehicle identifier
    "shipment_id": "string",               # Shipment identifier
    "lat": "float",                        # Latitude
    "lon": "float",                        # Longitude
    "speed_kmph": "float",                 # Current speed in km/h
    "load_status": "string"                # LOADED|UNLOADED|PARTIAL
}

# Example:
# {
#     "ts": "2026-02-09T10:30:00.000Z",
#     "vehicle_id": "VH001",
#     "shipment_id": "SH001",
#     "lat": 19.0760,
#     "lon": 72.8777,
#     "speed_kmph": 65.5,
#     "load_status": "LOADED"
# }


# ============================================================================
# PROCESSED OUTPUT SCHEMA (from Member 1's Pathway pipeline)
# ============================================================================

PROCESSED_OUTPUT_SCHEMA = {
    "ts": "ISO-8601 timestamp",
    "vehicle_id": "string",
    "shipment_id": "string",
    "current_lat": "float",
    "current_lon": "float",
    "destination_lat": "float",
    "destination_lon": "float",
    "distance_remaining_km": "float",      # Distance to destination
    "current_speed_kmph": "float",         # Current/average speed
    "eta_minutes": "float",                # ETA in minutes
    "predicted_eta": "ISO-8601 timestamp", # Actual arrival timestamp
    "confidence": "float",                 # ETA confidence (0-100)
    "status": "string",                    # in_transit|delayed|stopped|arrived
    "load_status": "string"                # LOADED|UNLOADED|PARTIAL
}


# ============================================================================
# DATABASE SCHEMAS (Member 2's PostgreSQL tables)
# ============================================================================

# Table: shipments
SHIPMENTS_TABLE = """
CREATE TABLE shipments (
    shipment_id TEXT PRIMARY KEY,
    vehicle_id TEXT NOT NULL,
    source TEXT NOT NULL,
    destination TEXT NOT NULL,
    status TEXT,
    current_eta TIMESTAMP,
    last_updated TIMESTAMP DEFAULT NOW()
);
"""

# Table: alerts
ALERTS_TABLE = """
CREATE TABLE alerts (
    alert_id SERIAL PRIMARY KEY,
    shipment_id TEXT REFERENCES shipments(shipment_id),
    alert_type TEXT,
    metric TEXT,
    value TEXT,
    threshold TEXT,
    duration INTERVAL,
    created_at TIMESTAMP DEFAULT NOW()
);
"""

# Table: shipment_events
SHIPMENT_EVENTS_TABLE = """
CREATE TABLE shipment_events (
    event_id SERIAL PRIMARY KEY,
    shipment_id TEXT REFERENCES shipments(shipment_id),
    event_type TEXT,
    description TEXT,
    event_time TIMESTAMP,
    severity TEXT
);
"""

# Table: eta_history
ETA_HISTORY_TABLE = """
CREATE TABLE eta_history (
    id SERIAL PRIMARY KEY,
    shipment_id TEXT REFERENCES shipments(shipment_id),
    predicted_eta TIMESTAMP,
    confidence NUMERIC(5,2),
    computed_at TIMESTAMP DEFAULT NOW()
);
"""


# ============================================================================
# SHIPMENT ROUTES (Reference Data)
# ============================================================================

ROUTES = {
    "SH001": {
        "shipment_id": "SH001",
        "vehicle_id": "VH001",
        "source": {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
        "destination": {"name": "Delhi", "lat": 28.6139, "lon": 77.2090},
        "expected_duration_minutes": 1200  # ~20 hours
    },
    "SH002": {
        "shipment_id": "SH002",
        "vehicle_id": "VH002",
        "source": {"name": "Bangalore", "lat": 12.9716, "lon": 77.5946},
        "destination": {"name": "Chennai", "lat": 13.0827, "lon": 80.2707},
        "expected_duration_minutes": 360   # ~6 hours
    }
}


# ============================================================================
# CONSTANTS
# ============================================================================

# Load status options
LOAD_STATUS = {
    "LOADED": "Vehicle is fully loaded",
    "UNLOADED": "Vehicle is empty",
    "PARTIAL": "Vehicle is partially loaded"
}

# Shipment status options
SHIPMENT_STATUS = {
    "in_transit": "Shipment is moving",
    "delayed": "Shipment is delayed",
    "stopped": "Vehicle has stopped",
    "arrived": "Shipment has reached destination"
}

# Alert types
ALERT_TYPES = {
    "delay": "Shipment is delayed beyond threshold",
    "speed": "Vehicle speed anomaly",
    "stopped": "Vehicle stopped for extended period",
    "route_deviation": "Vehicle deviated from expected route"
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_destination_coords(shipment_id: str) -> Optional[dict]:
    """Get destination coordinates for a shipment"""
    route = ROUTES.get(shipment_id)
    if route:
        return {
            "lat": route["destination"]["lat"],
            "lon": route["destination"]["lon"]
        }
    return None


def get_source_coords(shipment_id: str) -> Optional[dict]:
    """Get source coordinates for a shipment"""
    route = ROUTES.get(shipment_id)
    if route:
        return {
            "lat": route["source"]["lat"],
            "lon": route["source"]["lon"]
        }
    return None


# ============================================================================
# DATA EXCHANGE AGREEMENT
# ============================================================================

"""
DATA FLOW:

1. Member 2 (GPS Simulator) → PostgreSQL database → telemetry table
   - Writes GPS data with schema: GPS_TELEMETRY_SCHEMA
   
2. Member 1 (Pathway Pipeline) reads from PostgreSQL → processes → writes back
   - Reads: GPS telemetry
   - Writes: Processed output to eta_history table
   - Schema: PROCESSED_OUTPUT_SCHEMA
   
3. Member 2 (Backend API) reads processed data
   - Reads: eta_history, shipments tables
   - Creates: alerts based on ETA and speed
   - Exposes: REST API endpoints
   
4. Member 3 (Dashboard) calls Backend API
   - Displays: shipments, alerts, live map
   
5. Member 4 (Chatbot) calls Backend API
   - Answers: queries about shipments and ETAs
"""
