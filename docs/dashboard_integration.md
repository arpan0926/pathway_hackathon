# Dashboard Integration - Complete System

## Overview
The dashboard now integrates all components:
- ✅ Real-time GPS telemetry from PostgreSQL
- ✅ ETA predictions from Pathway pipeline
- ✅ Active alerts from database
- ✅ Groq-powered RAG chatbot
- ✅ Live map visualization with pydeck

---

## Data Flow

```
GPS Simulator → PostgreSQL → Dashboard (Live Telemetry)
                    ↓
            Pathway Pipeline → eta_history table → Dashboard (ETA Predictions)
                    ↓
            Alert System → alerts table → Dashboard (Alert Status)
                    ↓
            Groq API ← Dashboard (RAG Chatbot)
```

---

## Dashboard Features

### 1. Live Command Center Tab

#### KPI Metrics (Top Row)
- **Active Shipments**: Total number of tracked shipments
- **Fleet Avg Speed**: Average speed across all vehicles
- **On-Time Shipments**: Count of shipments with no delays
- **Critical Alerts**: Number of critical issues

#### Live Map (Left Panel)
- Real-time vehicle positions from telemetry table
- Route lines from source to destination
- Color-coded by status (teal = normal)
- Hover tooltips show shipment ID and speed

#### AI Inspector (Right Panel)
- Select any shipment to view details
- Shows:
  - Route (source → destination)
  - Status badge (on_time/warning/critical)
  - Cargo temperature (mock IoT data)
  - ETA prediction from Pathway pipeline
  - Delay reason analysis (if applicable)

### 2. AI Logistics Assistant Tab

#### RAG Chatbot Features
- Powered by Groq's llama-3.1-8b-instant model
- Context-aware responses using:
  - Current shipment data
  - GPS telemetry statistics
  - Active alert counts
- Ask questions like:
  - "What's the status of SH001?"
  - "How many shipments are delayed?"
  - "Show me critical alerts"

---

## Database Queries

### Telemetry Query
```sql
WITH latest_telemetry AS (
    SELECT DISTINCT ON (s.shipment_id)
        s.shipment_id, s.source, s.destination,
        s.source_lat, s.source_lon, s.dest_lat, s.dest_lon,
        t.lat, t.lon, t.speed_kmph, t.load_status
    FROM shipments s
    LEFT JOIN telemetry t ON s.shipment_id = t.shipment_id
    ORDER BY s.shipment_id, t.ts DESC
)
SELECT * FROM latest_telemetry;
```

### ETA Predictions Query
```sql
SELECT DISTINCT ON (shipment_id)
    shipment_id, predicted_eta, distance_remaining_km,
    current_speed_kmph, confidence
FROM eta_history
WHERE shipment_id IN (...)
ORDER BY shipment_id, computed_at DESC;
```

### Active Alerts Query
```sql
SELECT shipment_id, COUNT(*) as alert_count,
       MAX(CASE WHEN alert_type = 'critical' THEN 1 ELSE 0 END) as has_critical
FROM alerts
WHERE is_active = true
GROUP BY shipment_id;
```

---

## Alert Level Logic

The dashboard determines alert levels based on:

1. **Critical** (Red):
   - Has critical alerts in database
   - ETA > 240 minutes (4 hours)
   - Temperature breach detected

2. **Warning** (Yellow):
   - ETA > 180 minutes (3 hours)
   - Speed < 40 km/h (traffic congestion)
   - Minor alerts present

3. **On Time** (Green):
   - ETA < 180 minutes
   - Normal speed (> 40 km/h)
   - No active alerts

---

## Delay Reason Analysis

Automatically generated based on:
- **Traffic**: Speed < 50 km/h
- **Cold-chain issue**: Temperature > -5°C
- **Route deviation**: Critical alert + normal speed
- **System alerts**: Active alerts in database

---

## Auto-Refresh

Dashboard refreshes every 10 seconds to show:
- Latest GPS positions
- Updated ETA predictions
- New alerts
- Real-time KPI changes

Configure refresh rate:
```python
REFRESH_RATE = 10  # seconds
```

---

## Environment Variables Required

```bash
DATABASE_URL=postgresql://supply_chain_user:supply_chain_pass@postgres:5432/supply_chain_db
GROQ_API_KEY=your_groq_api_key_here
```

---

## Testing the Integration

### 1. Start All Services
```bash
docker-compose up
```

### 2. Verify Data Flow
- GPS Simulator: Check logs for "🟢 SH001: (lat, lon) @ speed"
- Pathway Pipeline: Check logs for "🔴 SH001: distance km away | ETA: X min"
- Dashboard: Open http://localhost:8501

### 3. Check Database
```bash
# Check telemetry data
docker exec -it supply_chain_db psql -U supply_chain_user -d supply_chain_db \
  -c "SELECT COUNT(*) FROM telemetry;"

# Check ETA predictions
docker exec -it supply_chain_db psql -U supply_chain_user -d supply_chain_db \
  -c "SELECT * FROM eta_history ORDER BY computed_at DESC LIMIT 5;"
```

### 4. Test Chatbot
- Go to "AI Logistics Assistant" tab
- Ask: "What's the current status of all shipments?"
- Should get context-aware response from Groq

---

## Troubleshooting

### No Data on Dashboard
- Check if GPS simulator is running: `docker logs gps_simulator`
- Verify telemetry table has data: `SELECT COUNT(*) FROM telemetry;`
- Check dashboard logs: `docker logs dashboard`

### ETA Not Showing
- Verify Pathway pipeline is running: `docker logs pathway_pipeline`
- Check eta_history table: `SELECT COUNT(*) FROM eta_history;`
- Pipeline may take 30-60 seconds to start producing predictions

### Chatbot Not Working
- Verify GROQ_API_KEY is set in .env file
- Check dashboard logs for API errors
- Test API key: `curl https://api.groq.com/openai/v1/models -H "Authorization: Bearer $GROQ_API_KEY"`

### Map Not Rendering
- Check if pydeck is installed: `pip list | grep pydeck`
- Verify lat/lon values are valid numbers
- Check browser console for JavaScript errors

---

## Performance Notes

- Dashboard queries use `DISTINCT ON` for efficiency
- Auto-refresh limited to 10 seconds to avoid overload
- Telemetry query only fetches latest position per shipment
- ETA predictions cached per refresh cycle

---

## Next Steps for Demo

1. Let GPS simulator run for 2-3 minutes to generate data
2. Verify live map shows moving vehicles
3. Check ETA predictions are updating
4. Test chatbot with sample questions
5. Take screenshots for presentation

---

## Member Responsibilities

- **Member 1**: Pathway pipeline outputs to eta_history table ✅
- **Member 2**: GPS simulator + API endpoints ✅
- **Member 3**: Dashboard visualization + integration ✅
- **Member 4**: RAG chatbot with Groq API ✅
