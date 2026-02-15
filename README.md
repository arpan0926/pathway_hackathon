# Real-Time Supply Chain Visibility & ETA Prediction

A real-time supply chain tracking system using Pathway Framework for live GPS processing and ETA prediction.

## Team Structure & Responsibilities

### Member 1 – Pathway & ETA Lead
- **Location**: `/pathway_pipeline/`
- **Focus**: GPS data ingestion, cleaning, ETA computation
- **Output**: Writes to `eta_history` table in PostgreSQL

### Member 2 – Backend, Alerts & Simulator
- **Location**: `/backend/`
- **Focus**: GPS simulator, alert logic, FastAPI endpoints
- **Output**: REST API for dashboard and chatbot

### Member 3 – Dashboard & Visualization
- **Location**: `/dashboard/`
- **Focus**: Streamlit UI, live map, alert display
- **Input**: Consumes Backend API

### Member 4 – GenAI, RAG & Pitch
- **Location**: `/genai_rag/` and `/docs/`
- **Focus**: RAG chatbot, pitch preparation
- **Input**: Consumes Backend API

---

## Git Workflow

**IMPORTANT: All development work happens in the `development` branch!**

### Initial Setup
```bash
# Clone the repository
git clone https://github.com/AYUSH-0305/pathway_hackathon.git
cd pathway_hackathon

# Switch to development branch
git checkout development

# Pull latest changes
git pull origin development
```

### Daily Workflow
```bash
# Always work in development branch
git checkout development

# Before starting work, pull latest changes
git pull origin development

# After completing your work
git add .
git commit -m "Your descriptive commit message"
git push origin development
```

### Branch Rules
- **development** - All active development happens here
- **main** - Production-ready code only (merge after demo is stable)
- Never push directly to main
- Final merge to main will be done after successful demo

---

## Quick Start with Docker

### Prerequisites
1. Install Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Start Docker Desktop and wait for it to be ready

### Setup Environment
```bash
# Copy environment file
cp .env.example .env

# Edit .env if needed (optional for local development)
```

### Start All Services
```bash
# Build and start all containers
docker-compose up --build

# Or run in background
docker-compose up -d
```

This will start:
- **PostgreSQL Database** (port 5432) - All tables created automatically
- **GPS Simulator** (Member 2) - Generates GPS data
- **Pathway Pipeline** (Member 1) - Processes GPS and calculates ETA
- **Backend API** (Member 2) - http://localhost:8000
- **Dashboard** (Member 3) - http://localhost:8501

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove database (fresh start)
docker-compose down -v
```

---

## Database Access

### Connection Details

**Inside Docker containers:**
```
Host: postgres
Port: 5432
Database: supply_chain_db
User: supply_chain_user
Password: supply_chain_pass
```

**From your host machine:**
```
Host: localhost
Port: 5432
Database: supply_chain_db
User: supply_chain_user
Password: supply_chain_pass
```

### Access Database
```bash
# Using docker exec
docker exec -it supply_chain_db psql -U supply_chain_user -d supply_chain_db

# Inside psql:
\dt                          # List tables
SELECT * FROM shipments;     # View shipments
SELECT * FROM telemetry ORDER BY ts DESC LIMIT 10;  # Latest GPS data
\q                           # Exit
```

### Database Tables

1. **shipments** - Master shipment data
2. **telemetry** - GPS data from simulator (Member 2 writes here)
3. **alerts** - Alert records (Member 2 creates alerts)
4. **shipment_events** - Event logs
5. **eta_history** - ETA predictions (Member 1 writes here)

---

## Development Workflow

### Member 1 (Pathway Pipeline)
```bash
# Edit code in pathway_pipeline/
# Restart to see changes
docker-compose restart pathway-pipeline

# View logs
docker-compose logs -f pathway-pipeline
```

### Member 2 (Backend & Simulator)
```bash
# Edit code in backend/
# API auto-reloads, restart simulator manually
docker-compose restart gps-simulator

# View logs
docker-compose logs -f backend-api
docker-compose logs -f gps-simulator
```

### Member 3 (Dashboard)
```bash
# Edit code in dashboard/
# Streamlit auto-reloads, just refresh browser

# View logs
docker-compose logs -f dashboard
```

### Member 4 (Chatbot)
```bash
# Edit code in genai_rag/
# Uncomment chatbot service in docker-compose.yml when ready
```

---

## Project Timeline

- **Days 1-2**: Setup & Learning, finalize schemas
- **Days 3-4**: Core Implementation, build components
- **Days 5-6**: Integration & Testing, connect all parts
- **Days 7-8**: Stabilization & API, fix bugs
- **Days 9-10**: Demo Preparation, polish and practice

---

## Key Files & Documentation

- **`README_DOCKER.md`** - Complete Docker guide with troubleshooting
- **`docs/integration_plan.md`** - How all components integrate
- **`docs/git_guide.md`** - Detailed Git workflow
- **`shared/schemas.py`** - Agreed data schemas for all members
- **`database/init.sql`** - Database initialization script
- **`.env.example`** - Environment variables template

---

## Demo Day Checklist

- [ ] All changes merged and tested in development branch
- [ ] GPS simulator running and generating data
- [ ] Pathway pipeline processing data and calculating ETA
- [ ] Backend API responding with correct data
- [ ] Dashboard showing live movement and ETA
- [ ] At least one alert triggered and displayed
- [ ] Chatbot answering one query
- [ ] 5-minute pitch ready
- [ ] Final merge to main branch after successful demo

---

## Accessing Services

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8501
- **Database**: localhost:5432

---

## Troubleshooting

### Containers won't start
```bash
# Clean up and restart
docker-compose down --remove-orphans
docker-compose up --build
```

### Database connection failed
```bash
# Check if postgres is healthy
docker-compose ps

# View postgres logs
docker-compose logs postgres
```

### Port already in use
```bash
# Stop all containers
docker-compose down

# Check what's using the port
netstat -ano | findstr :5432
netstat -ano | findstr :8000
```

### View all logs
```bash
docker-compose logs -f
```

---

## Need Help?

1. Check `README_DOCKER.md` for detailed Docker instructions
2. Check `docs/integration_plan.md` for integration details
3. Check `docs/git_guide.md` for Git workflow
4. Ask in team chat
5. Check service logs: `docker-compose logs -f <service-name>`

---

## Tech Stack

- **Pathway** - Real-time data processing
- **PostgreSQL** - Database
- **FastAPI** - Backend API
- **Streamlit** - Dashboard
- **Docker** - Containerization
- **OpenAI** - Chatbot (Member 4)
