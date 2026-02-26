# Database Setup

## PostgreSQL Database Structure

### Tables

1. **shipments** - Master shipment data
2. **telemetry** - GPS data from simulator (Member 2)
3. **alerts** - Alert records (Member 2)
4. **shipment_events** - Event logs (Member 2)
5. **eta_history** - ETA predictions (Member 1)

### Initialization

The `init.sql` script runs automatically when the PostgreSQL container starts for the first time.

It creates:
- All required tables
- Indexes for performance
- Sample shipments (SH001, SH002)

### Connection Details

**Inside Docker:**
```
Host: postgres
Port: 5432
Database: supply_chain_db
User: supply_chain_user
Password: supply_chain_pass
```

**From Host Machine:**
```
Host: localhost
Port: 5432
Database: supply_chain_db
User: supply_chain_user
Password: supply_chain_pass
```

### Connection String

```python
# Inside Docker containers
DATABASE_URL = "postgresql://supply_chain_user:supply_chain_pass@postgres:5432/supply_chain_db"

# From host machine
DATABASE_URL = "postgresql://supply_chain_user:supply_chain_pass@localhost:5432/supply_chain_db"
```

### Accessing the Database

```bash
# Using docker exec
docker exec -it supply_chain_db psql -U supply_chain_user -d supply_chain_db

# Using psql from host (if installed)
psql -h localhost -U supply_chain_user -d supply_chain_db
```

### Useful Queries

```sql
-- View all tables
\dt

-- Count records in each table
SELECT 'shipments' as table_name, COUNT(*) FROM shipments
UNION ALL
SELECT 'telemetry', COUNT(*) FROM telemetry
UNION ALL
SELECT 'alerts', COUNT(*) FROM alerts
UNION ALL
SELECT 'eta_history', COUNT(*) FROM eta_history;

-- Latest GPS data
SELECT * FROM telemetry ORDER BY ts DESC LIMIT 10;

-- Latest ETA predictions
SELECT * FROM eta_history ORDER BY computed_at DESC LIMIT 10;

-- Active alerts
SELECT * FROM alerts WHERE is_active = TRUE;

-- Shipment status
SELECT 
    s.shipment_id,
    s.vehicle_id,
    s.source,
    s.destination,
    s.status,
    COUNT(t.id) as gps_points,
    MAX(t.ts) as last_update
FROM shipments s
LEFT JOIN telemetry t ON s.shipment_id = t.shipment_id
GROUP BY s.shipment_id, s.vehicle_id, s.source, s.destination, s.status;
```
