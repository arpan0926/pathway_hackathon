# Render Backend Deployment Guide

Complete step-by-step guide to deploy your Supply Chain Tracker backend on Render.

---

## What You'll Deploy

- ✅ Backend API (FastAPI with WebSocket)
- ✅ PostgreSQL Database (Managed by Render)
- ✅ GPS Simulator (Background worker)
- ✅ Pathway Pipeline (Background worker)
- ✅ RAG Chatbot API
- ✅ AI Alert Service

---

## Prerequisites

### 1. GitHub Repository
Your code must be on GitHub. If not already done:

```bash
cd pathway_hackathon
git init
git add .
git commit -m "Initial commit for Render deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/pathway_hackathon.git
git push -u origin main
```

### 2. Render Account
- Go to [render.com](https://render.com)
- Click "Get Started for Free"
- Sign up with GitHub (recommended) or email
- No credit card required for free tier

### 3. Groq API Key
- Go to [console.groq.com](https://console.groq.com)
- Sign up/login
- Create a new API key
- Copy and save it (you'll need it later)

---

## Step 1: Push Your Code to GitHub

Make sure your latest changes are pushed:

```bash
cd pathway_hackathon
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

---

## Step 2: Create Render Account & Connect GitHub

1. **Go to Render**
   - Visit [render.com](https://render.com)
   - Click "Get Started"

2. **Sign Up with GitHub**
   - Click "GitHub" button
   - Authorize Render to access your repositories
   - Select "All repositories" or just your pathway_hackathon repo

3. **Verify Connection**
   - You should see your GitHub account connected
   - Dashboard should show "New +"

---

## Step 3: Deploy Using Blueprint (Easiest Method)

### Option A: Using render.yaml (Recommended)

1. **Click "New +"**
   - From your Render dashboard
   - Select "Blueprint"

2. **Connect Repository**
   - Click "Connect a repository"
   - Find and select `pathway_hackathon`
   - Click "Connect"

3. **Render Detects Configuration**
   - Render will automatically detect `render.yaml`
   - You'll see a preview of all services:
     - supply-chain-db (PostgreSQL)
     - backend-api (Web Service)
     - gps-simulator (Background Worker)
     - pathway-pipeline (Background Worker)
     - chatbot (Web Service)
     - ai-alert-service (Web Service)

4. **Review Services**
   - All services should show "Free" plan
   - Click "Apply" to proceed

5. **Set Environment Variables**
   - You'll be prompted for `GROQ_API_KEY`
   - Paste your Groq API key
   - Click "Apply"

6. **Deploy**
   - Click "Create Resources"
   - Render will start deploying all services
   - This takes 10-15 minutes

---

## Step 4: Manual Setup (Alternative Method)

If Blueprint doesn't work, deploy services manually:

### A. Create PostgreSQL Database

1. **Click "New +"**
   - Select "PostgreSQL"

2. **Configure Database**
   - Name: `supply-chain-db`
   - Database: `supply_chain_db`
   - User: `supply_chain_user`
   - Region: Choose closest to you
   - Plan: **Free**

3. **Create Database**
   - Click "Create Database"
   - Wait 2-3 minutes for provisioning

4. **Get Connection String**
   - Go to database dashboard
   - Copy "Internal Database URL"
   - Save it for later

5. **Initialize Database Schema**
   - Click "Connect" → "External Connection"
   - Use provided connection string
   - Run this command locally:
   ```bash
   psql "your_connection_string_here" < database/init.sql
   ```

### B. Deploy Backend API

1. **Click "New +"**
   - Select "Web Service"

2. **Connect Repository**
   - Select `pathway_hackathon`
   - Click "Connect"

3. **Configure Service**
   - Name: `backend-api`
   - Region: Same as database
   - Branch: `main`
   - Root Directory: `backend`
   - Environment: `Docker`
   - Dockerfile Path: `./backend/Dockerfile`
   - Plan: **Free**

4. **Add Environment Variables**
   - Click "Advanced" → "Add Environment Variable"
   - Add:
     ```
     DATABASE_URL = [paste your database internal URL]
     GROQ_API_KEY = [paste your Groq API key]
     ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for build

### C. Deploy GPS Simulator (Background Worker)

1. **Click "New +"**
   - Select "Background Worker"

2. **Connect Repository**
   - Select `pathway_hackathon`

3. **Configure Worker**
   - Name: `gps-simulator`
   - Region: Same as database
   - Branch: `main`
   - Root Directory: `backend`
   - Environment: `Docker`
   - Dockerfile Path: `./backend/Dockerfile`
   - Docker Command: `python gps_simulator.py`
   - Plan: **Free**

4. **Add Environment Variables**
   ```
   DATABASE_URL = [paste your database internal URL]
   ```

5. **Deploy**
   - Click "Create Background Worker"

### D. Deploy Pathway Pipeline (Background Worker)

Repeat same steps as GPS Simulator but:
- Name: `pathway-pipeline`
- Root Directory: `pathway_pipeline`
- Dockerfile Path: `./pathway_pipeline/Dockerfile`
- Docker Command: (leave default)

### E. Deploy RAG Chatbot

Repeat same steps as Backend API but:
- Name: `chatbot`
- Root Directory: `genai_rag`
- Dockerfile Path: `./genai_rag/Dockerfile`
- Environment Variables: DATABASE_URL + GROQ_API_KEY

### F. Deploy AI Alert Service

Repeat same steps as Backend API but:
- Name: `ai-alert-service`
- Root Directory: `ai_alert_service`
- Dockerfile Path: `./ai_alert_service/dockerfile`
- Environment Variables: DATABASE_URL

---

## Step 5: Verify Deployment

### Check Service Status

1. **Go to Dashboard**
   - All services should show "Live" (green)
   - If any show "Build Failed" or "Deploy Failed", check logs

2. **Check Backend API**
   - Click on `backend-api` service
   - Copy the URL (e.g., `https://backend-api-xxxx.onrender.com`)
   - Visit: `https://your-backend-url.onrender.com/health`
   - Should return: `{"status": "healthy", "database": "connected"}`

3. **Check API Documentation**
   - Visit: `https://your-backend-url.onrender.com/docs`
   - You should see FastAPI Swagger UI

4. **Test Endpoints**
   ```bash
   # Get shipments
   curl https://your-backend-url.onrender.com/api/shipments
   
   # Get stats
   curl https://your-backend-url.onrender.com/api/stats
   ```

### Check Database

1. **Go to Database Dashboard**
   - Click on `supply-chain-db`
   - Check "Connections" - should show active connections

2. **Verify Tables**
   - Click "Connect" → "External Connection"
   - Use psql or any PostgreSQL client
   - Run:
   ```sql
   \dt  -- List tables
   SELECT COUNT(*) FROM shipments;
   SELECT COUNT(*) FROM telemetry;
   ```

### Check Background Workers

1. **GPS Simulator**
   - Click on `gps-simulator` service
   - Check logs - should show GPS data being generated
   - Look for: "Generated GPS data for..."

2. **Pathway Pipeline**
   - Click on `pathway-pipeline` service
   - Check logs - should show ETA calculations
   - Look for: "Processing telemetry..."

---

## Step 6: Get Your Backend URLs

You'll need these for frontend deployment:

1. **Backend API URL**
   - Go to `backend-api` service
   - Copy the URL at the top
   - Example: `https://backend-api-xxxx.onrender.com`
   - **Save this - you'll need it for Vercel!**

2. **Chatbot API URL** (optional)
   - Go to `chatbot` service
   - Copy the URL
   - Example: `https://chatbot-xxxx.onrender.com`

3. **AI Alert Service URL** (optional)
   - Go to `ai-alert-service` service
   - Copy the URL
   - Example: `https://ai-alert-service-xxxx.onrender.com`

---

## Step 7: Configure CORS for Frontend

Once you know your Vercel frontend URL (you'll get this in next step), update CORS:

1. **Edit backend/main.py locally**
   
   Find this section:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Update to**:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "https://your-app.vercel.app",  # Add your Vercel URL here
           "http://localhost:3000"  # Keep for local development
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Commit and Push**:
   ```bash
   git add backend/main.py
   git commit -m "Update CORS for production"
   git push origin main
   ```

4. **Render Auto-Redeploys**
   - Render detects the change
   - Automatically rebuilds and redeploys
   - Wait 5-10 minutes

---

## Troubleshooting

### Build Failed

**Check Logs**:
1. Click on the failed service
2. Click "Logs" tab
3. Look for error messages

**Common Issues**:
- Missing Dockerfile: Ensure Dockerfile exists in correct directory
- Wrong path: Check `dockerfilePath` in render.yaml
- Missing dependencies: Check requirements.txt

**Solution**:
```bash
# Test build locally first
cd backend
docker build -t test-backend .
docker run test-backend
```

### Deploy Failed

**Check Environment Variables**:
- Ensure DATABASE_URL is set
- Ensure GROQ_API_KEY is set
- Check for typos

**Check Database Connection**:
- Ensure database is "Available"
- Check if init.sql ran successfully
- Verify connection string format

### Service Keeps Restarting

**Check Logs for Errors**:
- Database connection timeout
- Missing environment variables
- Port binding issues

**Common Fixes**:
- Increase health check timeout
- Check if database is in same region
- Verify all dependencies installed

### Database Connection Failed

**Verify Connection String**:
- Should start with `postgresql://`
- Should use internal URL (not external)
- Should include username and password

**Initialize Schema**:
```bash
# Connect to database
psql "your_external_connection_string"

# Run init script
\i database/init.sql

# Verify tables
\dt
```

### Free Tier Limitations

**Services Spin Down**:
- Free tier services sleep after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds
- Subsequent requests are fast

**Workaround**:
- Use a cron job to ping your service every 14 minutes
- Upgrade to paid plan ($7/month per service)

**Database Limitations**:
- 90 days of inactivity = database deleted
- 1 GB storage limit
- Shared resources

---

## Monitoring & Maintenance

### View Logs

1. **Real-Time Logs**:
   - Click on any service
   - Click "Logs" tab
   - See live logs streaming

2. **Filter Logs**:
   - Use search box to filter
   - Look for errors or warnings

### Monitor Performance

1. **Metrics**:
   - Click on service
   - Click "Metrics" tab
   - See CPU, memory, bandwidth usage

2. **Set Up Alerts** (Paid feature):
   - Get notified of downtime
   - Monitor resource usage

### Update Services

**Automatic Updates**:
- Push to GitHub
- Render auto-detects and redeploys
- No manual intervention needed

**Manual Redeploy**:
- Click on service
- Click "Manual Deploy" → "Deploy latest commit"

---

## Cost Breakdown

### Free Tier Includes:
- ✅ 750 hours/month per service
- ✅ PostgreSQL database (1 GB)
- ✅ Automatic SSL/HTTPS
- ✅ Automatic deployments
- ✅ Custom domains

### Limitations:
- ⚠️ Services spin down after 15 min inactivity
- ⚠️ 512 MB RAM per service
- ⚠️ Shared CPU
- ⚠️ 100 GB bandwidth/month

### Upgrade Options:
- **Starter**: $7/month per service (no spin down)
- **Standard**: $25/month per service (more resources)
- **Pro**: $85/month per service (dedicated resources)

---

## Next Steps

✅ Backend deployed on Render
✅ Database initialized
✅ All services running
✅ Backend URL obtained

**Now proceed to frontend deployment on Vercel!**

Your backend URL: `https://backend-api-xxxx.onrender.com`

Save this URL - you'll need it for the Vercel deployment.

---

## Quick Reference

### Important URLs
- Render Dashboard: https://dashboard.render.com
- Backend API: https://backend-api-xxxx.onrender.com
- API Docs: https://backend-api-xxxx.onrender.com/docs
- Health Check: https://backend-api-xxxx.onrender.com/health

### Important Commands
```bash
# Test backend locally
curl https://your-backend-url.onrender.com/health

# Check database
psql "your_connection_string" -c "\dt"

# View logs
# (Use Render dashboard)

# Redeploy
git push origin main
```

### Support
- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- Status Page: https://status.render.com
