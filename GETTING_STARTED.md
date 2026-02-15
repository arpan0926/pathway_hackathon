# Getting Started - Supply Chain Tracker

## For All Team Members

### Step 1: Clone and Setup
```bash
# Clone repository
git clone https://github.com/AYUSH-0305/pathway_hackathon.git
cd pathway_hackathon

# Switch to development branch
git checkout development

# Copy environment file
cp .env.example .env
```

### Step 2: Install Docker
1. Download Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Install and start Docker Desktop
3. Wait for Docker to be ready (green icon)

### Step 3: Start Everything
```bash
# Start all services
docker-compose up

# Or run in background
docker-compose up -d
```

### Step 4: Verify Everything Works
- Database: `docker exec -it supply_chain_db psql -U supply_chain_user -d supply_chain_db`
- Backend API: http://localhost:8000/docs
- Dashboard: http://localhost:8501

---

## What's Already Set Up

✅ **PostgreSQL Database** with all tables:
- `shipments` - Master shipment data (SH001, SH002 already inserted)
- `telemetry` - For GPS data (Member 2 writes here)
- `alerts` - For alert records (Member 2 creates)
- `shipment_events` - For event logs
- `eta_history` - For ETA predictions (Member 1 writes here)

✅ **Docker Environment** - All services containerized

✅ **Shared Schemas** - See `shared/schemas.py`

✅ **Integration Plan** - See `docs/integration_plan.md`

---

## Member-Specific Tasks

### Member 1 (Pathway & ETA) - Start Here!

**Your file**: `pathway_pipeline/pipeline.py`

**What to do**:
1. Read GPS data from PostgreSQL `telemetry` table
2. Calculate distance to destination using Haversine formula
3. Calculate average speed from last N GPS points
4. Compute ETA = distance / speed
5. Write results to `eta_history` table

**Database connection**:
```python
DATABASE_URL = "postgresql://supply_chain_user:supply_chain_pass@postgres:5432/supply_chain_db"
```

**Test your changes**:
```bash
docker-compose restart pathway-pipeline
docker-compose logs -f pathway-pipeline
```

---

### Member 2 (Backend & Simulator) - Start Here!

**Your files**: 
- `backend/simulator.py` - GPS data generator
- `backend/main.py` - FastAPI endpoints
- `backend/alerts.py` - Alert logic

**What to do**:

**1. GPS Simulator** (`simulator.py`):
- Generate GPS coordinates for vehicles
- Write to `telemetry` table in PostgreSQL
- Use schema from `shared/schemas.py`

**2. Backend API** (`main.py`):
- Implement endpoints:
  - `GET /api/shipments` - List all shipments
  - `GET /api/shipments/{id}` - Get shipment details
  - `GET /api/alerts` - Get all alerts
- Read from database tables
- Return JSON responses

**3. Alert Logic** (`alerts.py`):
- Read ETA from `eta_history` table
- Compare with expected ETA
- Create alerts if delayed > 30 minutes
- Write to `alerts` table

**Test your changes**:
```bash
docker-compose restart gps-simulator
docker-compose restart backend-api
docker-compose logs -f backend-api
```

---

### Member 3 (Dashboard) - Start Here!

**Your file**: `dashboard/app.py`

**What to do**:
1. Call Backend API endpoints
2. Display live map with vehicle locations (use folium or plotly)
3. Show ETA countdown for each shipment
4. Display alerts with color coding
5. Auto-refresh every few seconds

**Backend API**: `http://backend-api:8000` (inside Docker) or `http://localhost:8000` (from browser)

**Test your changes**:
```bash
# Streamlit auto-reloads, just refresh browser
docker-compose logs -f dashboard
```

---

### Member 4 (GenAI & Chatbot) - Start Here!

**Your files**: 
- `genai_rag/chatbot.py` - RAG implementation
- `genai_rag/document_store.py` - Pathway Document Store
- `docs/pitch_script.md` - 5-minute pitch

**What to do**:
1. Set up Pathway Document Store with shipment data
2. Implement RAG chatbot using OpenAI
3. Enable queries like "What is ETA for SH001?"
4. Prepare 5-minute pitch script
5. Lead demo narration

**Backend API**: `http://backend-api:8000`

**Add OpenAI key to `.env`**:
```
OPENAI_API_KEY=your_key_here
```

---

## Daily Workflow

### Before Starting Work
```bash
git checkout development
git pull origin development
```

### After Completing Work
```bash
git add .
git commit -m "Descriptive message of what you did"
git pull origin development  # Get latest changes
git push origin development
```

### If You Get Merge Conflicts
```bash
# Edit conflicted files
# Remove conflict markers (<<<<<<, =======, >>>>>>>)
git add <resolved-files>
git commit -m "Resolved merge conflict"
git push origin development
```

---

## Common Commands

```bash
# Start services
docker-compose up

# Stop services
docker-compose down

# Restart specific service
docker-compose restart pathway-pipeline

# View logs
docker-compose logs -f pathway-pipeline

# Access database
docker exec -it supply_chain_db psql -U supply_chain_user -d supply_chain_db

# Clean restart
docker-compose down -v
docker-compose up --build
```

---

## Need Help?

1. **README.md** - Project overview
2. **README_DOCKER.md** - Complete Docker guide
3. **docs/integration_plan.md** - How components integrate
4. **docs/git_guide.md** - Detailed Git workflow
5. **shared/schemas.py** - Data schemas
6. Team chat - Ask questions!

---

## Timeline

- **Days 1-2**: Setup, learn tools, finalize schemas
- **Days 3-4**: Build core components
- **Days 5-6**: Integration and testing
- **Days 7-8**: Stabilization and bug fixes
- **Days 9-10**: Demo preparation and practice

---

## Success Criteria for Demo

✅ GPS simulator generating data  
✅ Pathway pipeline calculating ETA  
✅ Backend API responding  
✅ Dashboard showing live updates  
✅ At least one alert triggered  
✅ Chatbot answering one query  
✅ 5-minute pitch ready  

**Let's build something amazing! 🚀**
