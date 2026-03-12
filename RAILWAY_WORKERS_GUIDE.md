# Railway Background Workers Deployment Guide

Deploy GPS Simulator and Pathway Pipeline on Railway (supports background workers on free tier).

---

## Prerequisites

- Render backend already deployed
- Database URL from Render (Internal Database URL)
- Railway account (free, no credit card needed)

---

## Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Click "Login" → "Login with GitHub"
3. Authorize Railway to access your repositories
4. No credit card required for free tier

---

## Step 2: Deploy GPS Simulator

### A. Create New Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose `pathway_hackathon` repository
4. Click "Deploy Now"

### B. Configure GPS Simulator Service

1. **After deployment starts, click on the service**
2. **Go to "Settings" tab**
3. **Update Configuration**:
   - Service Name: `gps-simulator`
   - Root Directory: `backend`
   - Start Command: `python gps_simulator.py`

4. **Add Environment Variables**:
   - Click "Variables" tab
   - Click "New Variable"
   - Add:
     ```
     DATABASE_URL = [paste your Render database Internal URL]
     ```
   - Example: `postgresql://supply_chain_user:password@dpg-xxx.oregon-postgres.render.com/supply_chain_db`

5. **Redeploy**:
   - Click "Settings" → "Redeploy"
   - Wait 3-5 minutes

### C. Verify GPS Simulator

1. Click "Deployments" tab
2. Check logs - should see:
   ```
   Generated GPS data for SH001
   Generated GPS data for SH002
   ```
3. If you see errors, check the DATABASE_URL

---

## Step 3: Deploy Pathway Pipeline

### A. Add Second Service

1. **In the same Railway project**, click "+ New"
2. Select "GitHub Repo"
3. Choose `pathway_hackathon` again
4. Click "Deploy"

### B. Configure Pathway Pipeline Service

1. **Click on the new service**
2. **Go to "Settings" tab**
3. **Update Configuration**:
   - Service Name: `pathway-pipeline`
   - Root Directory: `pathway_pipeline`
   - Start Command: `sh -c "python postgres_to_csv_bridge.py & python pipeline.py"`

4. **Add Environment Variables**:
   - Click "Variables" tab
   - Add:
     ```
     DATABASE_URL = [paste your Render database Internal URL]
     PYTHONUNBUFFERED = 1
     ```

5. **Add Volume for Data** (Optional):
   - Click "Settings" → "Volumes"
   - Click "New Volume"
   - Mount Path: `/app/data`
   - Size: 1 GB

6. **Redeploy**:
   - Click "Settings" → "Redeploy"

### C. Verify Pathway Pipeline

1. Click "Deployments" tab
2. Check logs - should see:
   ```
   Processing telemetry data...
   Calculating ETA for shipment...
   ```

---

## Step 4: Verify Complete System

### Check All Services

**Render Services:**
- ✅ supply-chain-db (Database)
- ✅ backend-api (Running)
- ✅ chatbot (Running)
- ✅ ai-alert-service (Running)

**Railway Services:**
- ✅ gps-simulator (Running)
- ✅ pathway-pipeline (Running)

### Test Data Flow

1. **Check GPS Data Generation**:
   ```bash
   # Use Render database External URL
   psql "your_render_external_db_url" -c "SELECT COUNT(*) FROM telemetry;"
   ```
   Should show increasing count.

2. **Check ETA Calculations**:
   ```bash
   psql "your_render_external_db_url" -c "SELECT COUNT(*) FROM eta_history;"
   ```
   Should show ETA records.

3. **Test Backend API**:
   ```bash
   curl https://your-backend-api.onrender.com/api/telemetry?limit=5
   ```
   Should return recent GPS data.

---

## Alternative: Railway CLI Method

If you prefer command line:

### Install Railway CLI
```bash
npm i -g @railway/cli
```

### Deploy GPS Simulator
```bash
cd pathway_hackathon/backend
railway login
railway init
railway up

# Set environment variables
railway variables set DATABASE_URL="your_render_database_url"

# Set start command
railway run python gps_simulator.py
```

### Deploy Pathway Pipeline
```bash
cd ../pathway_pipeline
railway init
railway up

# Set environment variables
railway variables set DATABASE_URL="your_render_database_url"
railway variables set PYTHONUNBUFFERED=1

# Deploy
railway run sh -c "python postgres_to_csv_bridge.py & python pipeline.py"
```

---

## Troubleshooting

### GPS Simulator Not Generating Data

**Check Logs**:
- Go to Railway dashboard
- Click on gps-simulator service
- Check "Deployments" → "View Logs"

**Common Issues**:
1. **Database connection failed**
   - Verify DATABASE_URL is correct
   - Use Internal URL from Render (not External)
   - Check if Render database allows external connections

2. **Module not found**
   - Check if requirements.txt is in backend folder
   - Verify Dockerfile installs dependencies

**Solution**:
```bash
# Test locally first
cd backend
export DATABASE_URL="your_render_database_url"
python gps_simulator.py
```

### Pathway Pipeline Errors

**Check Logs**:
- Railway dashboard → pathway-pipeline → View Logs

**Common Issues**:
1. **No telemetry data**
   - GPS simulator must run first
   - Check if telemetry table has data

2. **CSV file errors**
   - Add volume for persistent storage
   - Or modify code to skip CSV export

**Solution**:
```bash
# Test locally
cd pathway_pipeline
export DATABASE_URL="your_render_database_url"
python pipeline.py
```

### Database Connection Issues

**Render Database Security**:
Render databases are accessible from anywhere by default, but verify:

1. Go to Render database dashboard
2. Check "Connections" section
3. Ensure "External Connections" is enabled

**Connection String Format**:
```
postgresql://user:password@host:5432/database
```

Make sure:
- No extra spaces
- Password is URL-encoded if it contains special characters
- Using correct port (5432)

---

## Cost Breakdown

### Railway Free Tier
- $5 credit/month
- 500 hours/month
- 2 services × 24/7 = ~1,440 hours/month
- **With sleep mode**: Free
- **24/7 operation**: ~$10/month

### Optimization Tips

1. **Enable Sleep Mode**:
   - Services sleep after 15 min inactivity
   - Wake on database activity
   - Saves hours

2. **Combine Services**:
   - Run both workers in one service
   - Reduces to 1 service = 720 hours/month
   - Fits in free tier!

3. **Use Cron Jobs**:
   - Run GPS simulator every 5 minutes instead of continuously
   - Dramatically reduces hours

---

## Combined Service Option (Save Resources)

Run both workers in one Railway service:

### Create Combined Dockerfile

Create `pathway_hackathon/workers/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy backend requirements
COPY backend/requirements.txt /app/backend/
RUN pip install -r backend/requirements.txt

# Copy pathway requirements
COPY pathway_pipeline/requirements.txt /app/pathway_pipeline/
RUN pip install -r pathway_pipeline/requirements.txt

# Copy source code
COPY backend/ /app/backend/
COPY pathway_pipeline/ /app/pathway_pipeline/
COPY shared/ /app/shared/

# Run both services
CMD python backend/gps_simulator.py & python pathway_pipeline/pipeline.py & wait
```

### Deploy Combined Service

1. Create `workers` folder
2. Add Dockerfile above
3. Deploy to Railway:
   - Root Directory: `workers`
   - Dockerfile Path: `./Dockerfile`
4. Add DATABASE_URL environment variable
5. Deploy

This runs both workers in one service = half the cost!

---

## Next Steps

Once Railway workers are deployed:

1. ✅ Verify all services running
2. ✅ Check data flowing through system
3. ✅ Get backend API URL from Render
4. ✅ Proceed to Vercel frontend deployment

---

## Summary

**What You Have Now**:
- Render: Backend API, Database, Chatbot, AI Alerts
- Railway: GPS Simulator, Pathway Pipeline
- All services connected via shared database
- 100% free (with sleep mode) or ~$10/month (24/7)

**Your Backend URL**: `https://backend-api-xxxx.onrender.com`

Save this URL for Vercel deployment!
