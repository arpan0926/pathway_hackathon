# Render Free Tier Deployment Solution

## Problem
Render's free tier doesn't support "Background Worker" service type.

## Solution
Deploy only the essential web services that work with free tier.

---

## What Will Be Deployed (Free Tier Compatible)

✅ **supply-chain-db** - PostgreSQL Database
✅ **backend-api** - Main API with WebSocket
✅ **chatbot** - RAG Chatbot API  
✅ **ai-alert-service** - AI Alert Service

❌ **gps-simulator** - Not deployed (background worker)
❌ **pathway-pipeline** - Not deployed (background worker)

---

## Quick Deploy Steps

### 1. Update Configuration
```bash
cd pathway_hackathon
copy render-free-tier.yaml render.yaml
git add render.yaml
git commit -m "Use free tier compatible configuration"
git push origin main
```

### 2. Deploy on Render
1. Go to [render.com](https://render.com)
2. Click "New +" → "Blueprint"
3. Connect your `pathway_hackathon` repository
4. Render will show 4 services (all compatible with free tier)
5. Enter your GROQ_API_KEY when prompted
6. Click "Create Resources"

### 3. Wait for Deployment
- Database: ~2 minutes
- Backend API: ~5-8 minutes
- Chatbot: ~5-8 minutes
- AI Alert Service: ~5-8 minutes

---

## Alternative: Run Background Services Locally

If you need GPS simulation and Pathway pipeline:

### Option A: Run Locally While Backend is on Render

1. **Get Database URL from Render**
   - Go to your database in Render dashboard
   - Copy "External Database URL"

2. **Create Local .env**
   ```bash
   cd pathway_hackathon
   echo DATABASE_URL=your_render_database_url > .env
   ```

3. **Run Background Services Locally**
   ```bash
   # Terminal 1: GPS Simulator
   cd backend
   python gps_simulator.py

   # Terminal 2: Pathway Pipeline
   cd pathway_pipeline
   python pipeline.py
   ```

### Option B: Deploy Background Services on Railway

Railway supports background workers on free tier:

1. **Deploy to Railway**
   ```bash
   npm i -g @railway/cli
   railway login
   railway init
   ```

2. **Deploy Only Workers**
   - Deploy gps-simulator as a service
   - Deploy pathway-pipeline as a service
   - Use Render's database URL

---

## Alternative: Manual Service Deployment

Deploy services one by one without Blueprint:

### 1. Create Database
1. Click "New +" → "PostgreSQL"
2. Name: `supply-chain-db`
3. Plan: Free
4. Click "Create Database"
5. Wait 2 minutes
6. Copy "Internal Database URL"

### 2. Deploy Backend API
1. Click "New +" → "Web Service"
2. Connect repository: `pathway_hackathon`
3. Name: `backend-api`
4. Root Directory: `backend`
5. Environment: Docker
6. Dockerfile Path: `./backend/Dockerfile`
7. Add Environment Variables:
   - `DATABASE_URL` = [paste internal database URL]
   - `GROQ_API_KEY` = [your Groq API key]
8. Click "Create Web Service"

### 3. Deploy Chatbot
1. Click "New +" → "Web Service"
2. Connect repository: `pathway_hackathon`
3. Name: `chatbot`
4. Root Directory: `genai_rag`
5. Environment: Docker
6. Dockerfile Path: `./genai_rag/Dockerfile`
7. Add Environment Variables:
   - `DATABASE_URL` = [paste internal database URL]
   - `GROQ_API_KEY` = [your Groq API key]
8. Click "Create Web Service"

### 4. Deploy AI Alert Service
1. Click "New +" → "Web Service"
2. Connect repository: `pathway_hackathon`
3. Name: `ai-alert-service`
4. Root Directory: `ai_alert_service`
5. Environment: Docker
6. Dockerfile Path: `./ai_alert_service/dockerfile`
7. Add Environment Variables:
   - `DATABASE_URL` = [paste internal database URL]
8. Click "Create Web Service"

---

## Initialize Database

After database is created, initialize the schema:

### Method 1: Using psql (Recommended)
```bash
# Get External Database URL from Render dashboard
psql "your_external_database_url" < database/init.sql
```

### Method 2: Using Render Shell
1. Go to database in Render dashboard
2. Click "Connect" → "External Connection"
3. Use provided psql command
4. Once connected, run:
```sql
\i database/init.sql
```

### Method 3: Manual SQL
Copy contents of `database/init.sql` and paste into Render's SQL editor.

---

## Verify Deployment

### 1. Check Services
All services should show "Live" (green) in dashboard.

### 2. Test Backend API
```bash
# Health check
curl https://your-backend-api.onrender.com/health

# API docs
# Visit: https://your-backend-api.onrender.com/docs

# Get shipments
curl https://your-backend-api.onrender.com/api/shipments
```

### 3. Test Database
```bash
psql "your_external_database_url" -c "\dt"
```

---

## What's Missing Without Background Workers?

### GPS Simulator
- **Impact**: No automatic GPS data generation
- **Workaround**: 
  - Run locally and connect to Render database
  - Use Railway for background workers
  - Manually insert test data

### Pathway Pipeline
- **Impact**: No automatic ETA calculations
- **Workaround**:
  - Run locally
  - Use Railway for background workers
  - Calculate ETAs in backend API directly

---

## Recommended Setup for Free Tier

**Best Free Combination:**
- **Render**: Backend API + Database + Chatbot + AI Alerts
- **Railway**: GPS Simulator + Pathway Pipeline (background workers)
- **Vercel**: Frontend Dashboard

This gives you:
- ✅ All services running
- ✅ 100% free
- ✅ No limitations
- ✅ Auto-deploy from GitHub

---

## Next Steps

### If Using Render Only (Core Services)
1. Deploy using updated render.yaml
2. Run background services locally when needed
3. Proceed to Vercel frontend deployment

### If Using Render + Railway (Full Stack)
1. Deploy core services on Render
2. Deploy background workers on Railway
3. Connect them using database URL
4. Proceed to Vercel frontend deployment

---

## Cost Comparison

### Render Only (Free)
- 3 web services (backend, chatbot, alerts)
- 1 PostgreSQL database
- Background services run locally
- **Cost**: $0/month

### Render + Railway (Free)
- Render: 3 web services + database
- Railway: 2 background workers
- All services in cloud
- **Cost**: $0/month (within free tier limits)

### Render Paid (24/7 No Sleep)
- Upgrade services to Starter plan
- No spin-down after inactivity
- **Cost**: ~$21/month (3 services × $7)

---

## Support

If you encounter issues:
1. Check Render logs for errors
2. Verify environment variables
3. Ensure database is initialized
4. Check Dockerfile paths

Need help? Let me know which option you want to pursue!
