# Testing Guide - How to Verify Everything is Working

## Quick Status Check

### Method 1: Run System Status Checker (Recommended)
```bash
python check_system_status.py
```

This will check:
- ✅ Database connectivity and data counts
- ✅ GPS Simulator (recent telemetry)
- ✅ Pathway Pipeline (ETA predictions)
- ✅ Backend API (all endpoints)
- ✅ Dashboard (accessibility)

---

### Method 2: Run API Test Suite
```bash
python test_api.py
```

This tests all 15+ API endpoints and shows sample responses.

---

### Method 3: Manual Browser Checks

#### 1. Check Backend API
Open: **http://localhost:8000/docs**

You should see:
- Interactive Swagger UI
- All endpoints listed (shipments, telemetry, alerts, etc.)
- Green "Authorize" button (no auth needed)

Try these quick tests:
- Click `/health` → "Try it out" → "Execute"
- Should return: `{"status": "healthy", "database": "connected"}`

- Click `/api/stats` → "Try it out" → "Execute"
- Should return shipment counts, avg speed, etc.

#### 2. Check Dashboard
Open: **http://localhost:8501**

You should see:
- Live map with vehicle positions
- 4 KPI cards at top (Active Shipments, Avg Speed, etc.)
- AI Inspector panel on right
- Two tabs: "Live Command Center" and "AI Logistics Assistant"

**Signs it's working:**
- ✅ Map shows dots (vehicles) and lines (routes)
- ✅ KPI numbers are NOT zero
- ✅ No error messages at top
- ✅ Speed values are updating every 10 seconds

**Signs it's NOT working:**
- ❌ "Database connection failed" warning
- ❌ All KPIs show 0
- ❌ Map is empty
- ❌ Error messages in red

---

## Detailed Component Testing

### Test 1: Database Has Data

```bash
# Connect to database
docker exec -it supply_chain_db psql -U supply_chain_user -d supply_chain_db

# Check data counts
SELECT 
    (SELECT COUNT(*) FROM shipments) as shipments,
    (SELECT COUNT(*) FROM telemetry) as telemetry,
    (SELECT COUNT(*) FROM eta_history) as eta_predictions,
    (SELECT COUNT(*) FROM alerts) as alerts;

# Exit
\q
```

**Expected:**
- shipments: 2 (SH001, SH002)
- telemetry: 100+ (growing every 2 seconds)
- eta_predictions: 10+ (growing every few seconds)
- alerts: 0+ (depends on conditions)

---

### Test 2: GPS Simulator is Running

```bash
# Check logs
docker logs gps_simulator --tail 20
```

**Expected output:**
```
🟢 SH001: (19.0761, 72.8776) @ 40.3 km/h
🟢 SH001: (19.1234, 72.9876) @ 55.2 km/h
```

**If you see:**
- 🔴 Red dots: Vehicle is stopped (normal, happens randomly)
- 🟢 Green dots: Vehicle is moving
- ❌ Errors: Check database connection

---

### Test 3: Pathway Pipeline is Working

```bash
# Check logs
docker logs pathway_pipeline --tail 20
```

**Expected output:**
```
🔴 SH001: 1138.5km away | Speed: 40.3km/h | ETA: 1708min | Confidence: 85%
🟢 SH001: 1100.2km away | Speed: 65.0km/h | ETA: 1015min | Confidence: 90%
```

**If you see:**
- ETA calculations: ✅ Working
- "FileSystem: 0 entries": ⚠️ No data yet, wait 30 seconds
- Python errors: ❌ Check syntax errors

---

### Test 4: Backend API Endpoints

```bash
# Test health
curl http://localhost:8000/health

# Test shipments
curl http://localhost:8000/api/shipments

# Test latest telemetry
curl http://localhost:8000/api/telemetry/latest/SH001

# Test stats
curl http://localhost:8000/api/stats
```

**Expected:**
- All return JSON responses
- Status 200 OK
- No error messages

---

### Test 5: Dashboard Data Integration

Open dashboard at http://localhost:8501

#### Check Live Map:
1. You should see 2 vehicles (dots) on the map
2. Lines connecting source to destination
3. Hover over dots to see shipment ID and speed

#### Check AI Inspector:
1. Select "SH001" from dropdown
2. Should show:
   - Route: Mumbai → Delhi
   - Status badge (green/yellow/red)
   - Cargo temperature
   - ETA prediction in minutes
   - Delay reason (if applicable)

#### Check KPIs:
- Active Shipments: Should be 2
- Fleet Avg Speed: Should be 30-70 km/h
- On-Time Shipments: Should be 0-2
- Critical Alerts: Should be 0-2

#### Check Auto-Refresh:
- Wait 10 seconds
- Numbers should update
- Map positions should change

---

### Test 6: RAG Chatbot

1. Go to "AI Logistics Assistant" tab
2. Type: "What's the status of SH001?"
3. Click send or press Enter

**Expected:**
- Response appears in 2-5 seconds
- Contains information about SH001
- Mentions speed, location, or status

**If it fails:**
- Check if GROQ_API_KEY is set in .env
- Check dashboard logs: `docker logs dashboard`

---

## Common Issues and Solutions

### Issue: Dashboard shows "Database connection failed"

**Solution:**
```bash
# Rebuild dashboard with SQLAlchemy
docker-compose up -d --build dashboard

# Check if database is accessible
docker exec -it supply_chain_db psql -U supply_chain_user -d supply_chain_db -c "SELECT 1;"
```

---

### Issue: No telemetry data

**Solution:**
```bash
# Check GPS simulator
docker logs gps_simulator

# Restart if needed
docker-compose restart gps_simulator

# Wait 30 seconds for data to accumulate
```

---

### Issue: ETA predictions not showing

**Solution:**
```bash
# Check Pathway pipeline
docker logs pathway_pipeline

# Verify CSV bridge is syncing
docker exec -it pathway_pipeline ls -la /app/data/

# Restart if needed
docker-compose restart pathway_pipeline
```

---

### Issue: API returns empty arrays

**Cause:** GPS simulator hasn't generated data yet

**Solution:**
- Wait 1-2 minutes for data to accumulate
- Check database: `SELECT COUNT(*) FROM telemetry;`
- Should have 30+ records before APIs return data

---

### Issue: Chatbot not responding

**Solution:**
```bash
# Check if GROQ_API_KEY is set
docker exec -it dashboard env | grep GROQ

# If empty, add to .env file:
echo "GROQ_API_KEY=your_key_here" >> .env

# Restart dashboard
docker-compose restart dashboard
```

---

## Performance Benchmarks

**Normal Operation:**
- GPS updates: Every 2 seconds
- ETA calculations: Every 5-10 seconds
- Dashboard refresh: Every 10 seconds
- API response time: < 100ms
- Chatbot response: 2-5 seconds

**Data Growth:**
- Telemetry: ~30 records/minute per vehicle
- ETA history: ~6 records/minute per shipment
- Total DB size: ~10MB after 1 hour

---

## Quick Verification Checklist

Before demo, verify:
- [ ] All 6 Docker containers running: `docker-compose ps`
- [ ] Database has 100+ telemetry records
- [ ] API health check returns "healthy"
- [ ] Dashboard loads without errors
- [ ] Map shows 2 vehicles
- [ ] KPIs show non-zero values
- [ ] Chatbot responds to test query
- [ ] Auto-refresh updates data every 10s

---

## Demo Script

1. **Show API** (30 seconds)
   - Open http://localhost:8000/docs
   - Execute `/api/stats` endpoint
   - Show real-time data

2. **Show Dashboard** (2 minutes)
   - Open http://localhost:8501
   - Point out live map with moving vehicles
   - Show KPI metrics updating
   - Select shipment in AI Inspector
   - Explain ETA prediction and delay reasons

3. **Show Chatbot** (1 minute)
   - Switch to AI Assistant tab
   - Ask: "What's the current status of all shipments?"
   - Show AI-powered response

4. **Show Real-time Updates** (30 seconds)
   - Wait for auto-refresh
   - Point out changing positions and speeds
   - Highlight live data pipeline

**Total: 4 minutes** (leaves 1 minute for Q&A in 5-minute pitch)
