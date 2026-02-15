-- Database initialization script
-- This runs automatically when PostgreSQL container starts for the first time

-- Create shipments table
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id TEXT PRIMARY KEY,
    vehicle_id TEXT NOT NULL,
    source TEXT NOT NULL,
    destination TEXT NOT NULL,
    source_lat NUMERIC(10, 6),
    source_lon NUMERIC(10, 6),
    dest_lat NUMERIC(10, 6),
    dest_lon NUMERIC(10, 6),
    status TEXT,
    current_eta TIMESTAMP,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Create telemetry table (GPS data from simulator)
CREATE TABLE IF NOT EXISTS telemetry (
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

-- Create indexes for telemetry
CREATE INDEX IF NOT EXISTS idx_telemetry_shipment ON telemetry(shipment_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_telemetry_vehicle ON telemetry(vehicle_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_telemetry_ts ON telemetry(ts DESC);

-- Create alerts table
CREATE TABLE IF NOT EXISTS alerts (
    alert_id SERIAL PRIMARY KEY,
    shipment_id TEXT REFERENCES shipments(shipment_id),
    alert_type TEXT,
    metric TEXT,
    value TEXT,
    threshold TEXT,
    duration INTERVAL,
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Create shipment_events table
CREATE TABLE IF NOT EXISTS shipment_events (
    event_id SERIAL PRIMARY KEY,
    shipment_id TEXT REFERENCES shipments(shipment_id),
    event_type TEXT,
    description TEXT,
    event_time TIMESTAMP,
    severity TEXT
);

-- Create eta_history table (for Member 1's output)
CREATE TABLE IF NOT EXISTS eta_history (
    id SERIAL PRIMARY KEY,
    shipment_id TEXT REFERENCES shipments(shipment_id),
    predicted_eta TIMESTAMP,
    distance_remaining_km NUMERIC(10, 2),
    current_speed_kmph NUMERIC(6, 2),
    confidence NUMERIC(5, 2),
    computed_at TIMESTAMP DEFAULT NOW()
);

-- Create index for eta_history
CREATE INDEX IF NOT EXISTS idx_eta_history_shipment ON eta_history(shipment_id, computed_at DESC);

-- Insert sample shipments
INSERT INTO shipments (shipment_id, vehicle_id, source, destination, source_lat, source_lon, dest_lat, dest_lon, status)
VALUES 
    ('SH001', 'VH001', 'Mumbai', 'Delhi', 19.0760, 72.8777, 28.6139, 77.2090, 'in_transit'),
    ('SH002', 'VH002', 'Bangalore', 'Chennai', 12.9716, 77.5946, 13.0827, 80.2707, 'in_transit')
ON CONFLICT (shipment_id) DO NOTHING;

-- Grant permissions (if needed)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO supply_chain_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO supply_chain_user;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Database initialized successfully!';
    RAISE NOTICE 'Tables created: shipments, telemetry, alerts, shipment_events, eta_history';
    RAISE NOTICE 'Sample shipments inserted: SH001, SH002';
END $$;
