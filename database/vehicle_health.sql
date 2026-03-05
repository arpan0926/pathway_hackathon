-- Vehicle health telemetry table
CREATE TABLE IF NOT EXISTS vehicle_health (
    id SERIAL PRIMARY KEY,
    vehicle_id VARCHAR(20) NOT NULL,
    shipment_id VARCHAR(20),
    ts TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Engine metrics
    engine_temp_celsius FLOAT,
    engine_rpm INTEGER,
    oil_pressure_psi FLOAT,
    coolant_level_percent FLOAT,
    
    -- Mechanical wear
    vibration_level FLOAT,  -- 0-10 scale
    brake_pad_thickness_mm FLOAT,
    tire_pressure_psi FLOAT,
    
    -- Electrical
    battery_voltage FLOAT,
    alternator_output FLOAT,
    
    -- Computed health scores
    engine_health_score FLOAT,  -- 0-100
    brake_health_score FLOAT,
    tire_health_score FLOAT,
    battery_health_score FLOAT,
    overall_health_score FLOAT,
    
    -- Maintenance predictions
    predicted_failure_type VARCHAR(50),
    predicted_failure_days INTEGER,
    maintenance_urgency VARCHAR(20)  -- low, medium, high, critical
);

-- Drop indexes if they exist (to avoid errors)
DROP INDEX IF EXISTS idx_vehicle_health_vehicle;
DROP INDEX IF EXISTS idx_vehicle_health_ts;
DROP INDEX IF EXISTS idx_vehicle_health_urgency;

-- Create indexes
CREATE INDEX idx_vehicle_health_vehicle ON vehicle_health(vehicle_id);
CREATE INDEX idx_vehicle_health_ts ON vehicle_health(ts);
CREATE INDEX idx_vehicle_health_urgency ON vehicle_health(maintenance_urgency);

-- Maintenance alerts table (drop and recreate cleanly)
DROP TABLE IF EXISTS maintenance_alerts CASCADE;

CREATE TABLE maintenance_alerts (
    alert_id SERIAL PRIMARY KEY,
    vehicle_id VARCHAR(20) NOT NULL,
    shipment_id VARCHAR(20),
    alert_type VARCHAR(50) NOT NULL,  -- 'engine_overheating', 'brake_wear', etc.
    component VARCHAR(50),
    severity VARCHAR(20),  -- low, medium, high, critical
    predicted_failure_date TIMESTAMP,
    current_value FLOAT,
    threshold_value FLOAT,
    recommendation TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);

CREATE INDEX idx_maintenance_alerts_vehicle ON maintenance_alerts(vehicle_id);
CREATE INDEX idx_maintenance_alerts_active ON maintenance_alerts(is_active);