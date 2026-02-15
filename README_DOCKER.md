# Docker Setup Guide

## Quick Start - Run Everything

### 1. Start All Services
```bash
cd supply-chain-tracker
docker-compose up --build
```

This will start:
- PostgreSQL database (port 5432)
- GPS Simulator (Member 2)
- Pathway Pipeline (Member 1)
- Backend API (Member 2) - http://localhost:8000
- Dashboard (Member 3) - http://localhost:8501

### 2. Stop All Services
```bash
# Press Ctrl+C, then:
docker-compose down
```

### 3. Stop and Remove Everything (including database)
```bash
docker-compose down -v
```

---

## Individual Service Management

### Start Specific Services
```bash
# Only database
docker-compose up postgres

# Database + GPS Simulator
docker-compose up postgres gps-simulator

# Database + Pathway Pipeline
docker-compose up postgres pathway-pipeline

# Database + Backend API
docker-compose up postgres backend-api

# Everything except chatbot
docker-compose up postgres gps-simulator pathway-pipeline backend-api dashboard
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f pathway-pipeline
docker-compose logs -f gps-simulator
docker-compose logs -f backend-api
docker-compose logs -f postgres
```

### Restart a Service
```bash
docker-compose restart pathway-pipeline
docker-compose restart gps-simulator
```

---

## Database Management

### Access PostgreSQL Database
```bash
# Connect to database
docker exec -it supply_chain_db psql -U supply_chain_user -d supply_chain_db

# Inside psql:
\dt                          # List tables
\d telemetry                 # Describe telemetry table
SELECT * FROM shipments;     # View shipments
SELECT * FROM telemetry ORDER BY ts DESC LIMIT 10;  # Latest GPS data
SELECT * FROM eta_history ORDER BY computed_at DESC LIMIT 10;  # Latest ETAs
\q                           # Exit
```

### Reset Database
```bash
# Stop and remove database volume
docker-compose down -v

# Start fresh
docker-compose up postgres
```

### Backup Database
```bash
docker exec supply_chain_db pg_dump -U supply_chain_user supply_chain_db > backup.sql
```

### Restore Database
```bash
docker exec -i supply_chain_db psql -U supply_chain_user supply_chain_db < backup.sql
```

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
# API auto-reloads (--reload flag)
# Restart simulator manually
docker-compose restart gps-simulator

# View logs
docker-compose logs -f backend-api
docker-compose logs -f gps-simulator
```

### Member 3 (Dashboard)
```bash
# Edit code in dashboard/
# Streamlit auto-reloads
# Just refresh browser

# View logs
docker-compose logs -f dashboard
```

### Member 4 (Chatbot)
```bash
# Uncomment chatbot service in docker-compose.yml
# Add OPENAI_API_KEY to .env
docker-compose up chatbot
```

---

## Accessing Services

### URLs
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8501
- **PostgreSQL**: localhost:5432

### Database Credentials
- **Host**: localhost (or `postgres` from inside Docker)
- **Port**: 5432
- **Database**: supply_chain_db
- **User**: supply_chain_user
- **Password**: supply_chain_pass

---

## Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
netstat -ano | findstr :5432
netstat -ano | findstr :8000
netstat -ano | findstr :8501

# Stop the process or change port in docker-compose.yml
```

### Container Won't Start
```bash
# Check logs
docker-compose logs <service-name>

# Rebuild
docker-compose build --no-cache <service-name>
docker-compose up <service-name>
```

### Database Connection Failed
```bash
# Check if postgres is healthy
docker-compose ps

# Wait for postgres to be ready
docker-compose logs postgres

# Test connection
docker exec supply_chain_db pg_isready -U supply_chain_user
```

### Clear Everything and Start Fresh
```bash
# Stop all containers
docker-compose down -v

# Remove all images
docker-compose rm -f

# Rebuild and start
docker-compose up --build
```

---

## Production Deployment

### Build for Production
```bash
# Build all images
docker-compose build

# Tag images
docker tag supply-chain-tracker_pathway-pipeline:latest your-registry/pathway-pipeline:v1.0
docker tag supply-chain-tracker_backend-api:latest your-registry/backend-api:v1.0
docker tag supply-chain-tracker_dashboard:latest your-registry/dashboard:v1.0

# Push to registry
docker push your-registry/pathway-pipeline:v1.0
docker push your-registry/backend-api:v1.0
docker push your-registry/dashboard:v1.0
```

### Environment Variables
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env with production values
nano .env
```

---

## Demo Day Checklist

### Before Demo
```bash
# 1. Start all services
docker-compose up -d

# 2. Check all services are running
docker-compose ps

# 3. Verify database has data
docker exec -it supply_chain_db psql -U supply_chain_user -d supply_chain_db -c "SELECT COUNT(*) FROM telemetry;"

# 4. Test API
curl http://localhost:8000/api/shipments

# 5. Open dashboard
# Visit http://localhost:8501
```

### During Demo
- Keep terminal with logs visible: `docker-compose logs -f`
- Have backup: screenshots or video recording
- Know how to restart services quickly

### After Demo
```bash
# Stop services
docker-compose down

# Keep data for later
# (don't use -v flag)
```

---

## Tips

1. **Use volumes for development** - Code changes reflect immediately
2. **Check logs frequently** - `docker-compose logs -f`
3. **Restart services after config changes** - `docker-compose restart <service>`
4. **Use health checks** - Services wait for dependencies to be ready
5. **Network isolation** - All services communicate via `supply-chain-network`
