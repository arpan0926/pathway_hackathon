# Complete Deployment Guide - All Services

Deploy your entire Supply Chain Tracker with GPS Simulator and Pathway Pipeline.

---

## 🎯 Deployment Architecture

**Render** (Free Tier):
- PostgreSQL Database
- Backend API
- Chatbot API
- AI Alert Service

**Railway** (Free Tier):
- GPS Simulator + Pathway Pipeline (combined)

**Vercel** (Free Tier):
- Frontend Dashboard

**Total Cost**: $0/month (with sleep mode) or ~$5-10/month (24/7)

---

## 📋 Prerequisites Checklist

- [ ] GitHub account with code pushed
- [ ] Render account ([render.com](https://render.com))
- [ ] Railway account ([railway.app](https://railway.app))
- [ ] Vercel account ([vercel.com](https://vercel.com))
- [ ] Groq API key ([console.groq.com](https://console.groq.com))

---

## Part 1: Deploy on Render (15 minutes)

### Step 1: Commit Your Code
```bash
cd pathway_hackathon
git add .
git commit -m "Ready for complete deployment"
git push origin main
```

### Step 2: Deploy on Render

1. **Go to [render.com](https://render.com)**
2. **Sign up with GitHub**
3. **Click "New +" → "Blueprint"**
4. **Select `pathway_hackathon` repository**
5. **You'll see 4 services**:
   - supply-chain-db (Database)
   - backend-api (Web Service)
   - chatbot (Web Service)
   - ai-alert-service (Web Service)
6. **Enter GROQ_API_KEY** when prompted
7. **Click "Create Resources"**
8. **Wait 10-15 minutes** for deployment

### Step 3: Get Database URL

1. **Go to Render Dashboard**
2. **Click on `supply-chain-db`**
3. **Scroll to "Connections" section**
4. **Copy "Internal Database URL"**
   - Looks like: `postgresql://supply_chain_user:xxx@dpg-xxx.oregon-postgres.render.com/supply_chain_db`
5. **SAVE THIS URL** - you need it for Railway!

### Step 4: Get Backend API URL

1. **Click on `backend-api` service**
2. **Copy the URL at the top**
   - Looks like: `https://backend-api-xxxx.onrender.com`
3. **SAVE THIS URL** - you need it for Vercel!

### Step 5: Verify Render Deployment

Test your backend:
```bash
# Health check
curl https://your-backend-api.onrender.com/health

# Should return: {"status": "healthy", "database": "connected"}
```

✅ **Render deployment complete!**

---

## Part 2: Deploy Workers on Railway (10 minutes)

### Step 6: Create Railway Account

1. **Go to [railway.app](https://railway.app)**
2. **Click "Login with GitHub"**
3. **Authorize Railway**

### Step 7: Deploy Combined Workers

#### Option A: Using Railway Dashboard (Easiest)

1. **Click "New Project"**
2. **Select "Deploy from GitHub repo"**
3. **Choose `pathway_hackathon`**
4. **Click "Deploy Now"**

5. **Configure the Service**:
   - Click on the deployed service
   - Go to "Settings" tab
   - **Service Name**: `background-workers`
   - **Custom Start Command**: Leave empty (uses Dockerfile)
   - **Dockerfile Path**: `Dockerfile.workers`

6. **Add Environment Variable**:
   - Click "Variables" tab
   - Click "New Variable"
   - **Key**: `DATABASE_URL`
   - **Value**: [Paste your Render database Internal URL from Step 3]
   - Click "Add"

7. **Redeploy**:
   - Go to "Settings"
   - Click "Redeploy"
   - Wait 5-8 minutes

#### Option B: Using Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
cd pathway_hackathon
railway init

# Link to your project
railway link

# Set environment variable
railway variables set DATABASE_URL="your_render_database_url_here"

# Deploy
railway up
```

### Step 8: Verify Railway Deployment

1. **Go to Railway Dashboard**
2. **Click on your service**
3. **Click "Deployments" → "View Logs"**
4. **Look for**:
   ```
   Generated GPS data for SH001
   Generated GPS data for SH002
   Processing telemetry data...
   Calculating ETA...
   ```

5. **Check Database**:
   ```bash
   # Use Render External Database URL
   psql "your_render_external_db_url" -c "SELECT COUNT(*) FROM telemetry;"
   # Should show increasing numbers
   ```

✅ **Railway deployment complete!**

---

## Part 3: Deploy Frontend on Vercel (5 minutes)

### Step 9: Deploy on Vercel

1. **Go to [vercel.com](https://vercel.com)**
2. **Sign up with GitHub**
3. **Click "Add New" → "Project"**
4. **Import `pathway_hackathon` repository**
5. **Configure Project**:
   - **Framework Preset**: Vite
   - **Root Directory**: `supply-chain-dashboard`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

6. **Add Environment Variables**:
   Click "Environment Variables" and add:
   ```
   VITE_API_URL = https://your-backend-api.onrender.com
   VITE_WS_URL = wss://your-backend-api.onrender.com
   ```
   (Use your Backend API URL from Step 4)

7. **Click "Deploy"**
8. **Wait 2-3 minutes**

### Step 10: Get Frontend URL

1. **Vercel will show your URL**:
   - Example: `https://your-app.vercel.app`
2. **SAVE THIS URL** - you need it for CORS!

✅ **Vercel deployment complete!**

---

## Part 4: Configure CORS (5 minutes)

### Step 11: Update Backend CORS

1. **Open `backend/main.py` locally**

2. **Find the CORS middleware** (around line 30):
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       ...
   )
   ```

3. **Update to**:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "https://your-app.vercel.app",  # Your Vercel URL
           "http://localhost:3000"  # For local development
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

4. **Commit and push**:
   ```bash
   git add backend/main.py
   git commit -m "Configure CORS for production"
   git push origin main
   ```

5. **Render auto-redeploys** (wait 5 minutes)

✅ **CORS configured!**

---

## Part 5: Final Verification (5 minutes)

### Step 12: Test Complete System

1. **Visit your Vercel URL**: `https://your-app.vercel.app`

2. **Check Dashboard Loads**:
   - Map should appear
   - Shipments should load
   - Stats should show data

3. **Check Real-Time Updates**:
   - GPS markers should move on map
   - Telemetry data should update
   - Alerts should appear

4. **Test API Endpoints**:
   ```bash
   # Get shipments
   curl https://your-backend-api.onrender.com/api/shipments
   
   # Get telemetry
   curl https://your-backend-api.onrender.com/api/telemetry?limit=5
   
   # Get stats
   curl https://your-backend-api.onrender.com/api/stats
   ```

5. **Check Database**:
   ```bash
   psql "your_render_external_db_url" -c "
   SELECT 
     (SELECT COUNT(*) FROM shipments) as shipments,
     (SELECT COUNT(*) FROM telemetry) as telemetry,
     (SELECT COUNT(*) FROM eta_history) as eta_history,
     (SELECT COUNT(*) FROM alerts) as alerts;
   "
   ```

✅ **Everything working!**

---

## 🎉 Deployment Complete!

### Your Live URLs

- **Frontend**: `https://your-app.vercel.app`
- **Backend API**: `https://backend-api-xxxx.onrender.com`
- **API Docs**: `https://backend-api-xxxx.onrender.com/docs`
- **Chatbot**: `https://chatbot-xxxx.onrender.com`

### Services Running

✅ PostgreSQL Database (Render)
✅ Backend API (Render)
✅ Chatbot API (Render)
✅ AI Alert Service (Render)
✅ GPS Simulator (Railway)
✅ Pathway Pipeline (Railway)
✅ Frontend Dashboard (Vercel)

---

## 📊 Monitoring

### Check Service Health

**Render**:
- Dashboard: https://dashboard.render.com
- View logs for each service
- Monitor resource usage

**Railway**:
- Dashboard: https://railway.app
- View deployment logs
- Check metrics

**Vercel**:
- Dashboard: https://vercel.com/dashboard
- View deployment logs
- Check analytics

---

## 🔧 Troubleshooting

### Frontend Not Loading

1. Check browser console for errors
2. Verify VITE_API_URL in Vercel environment variables
3. Check CORS settings in backend/main.py
4. Ensure backend is running (visit /health endpoint)

### No GPS Data

1. Check Railway logs for gps-simulator
2. Verify DATABASE_URL is correct
3. Check database connection:
   ```bash
   psql "your_db_url" -c "SELECT COUNT(*) FROM telemetry;"
   ```

### Backend Errors

1. Check Render logs for backend-api
2. Verify GROQ_API_KEY is set
3. Check database connection
4. Verify all environment variables

### Services Sleeping

Free tier services sleep after 15 min inactivity:
- First request takes 30-60 seconds (cold start)
- Subsequent requests are fast
- Upgrade to paid plan to prevent sleeping

---

## 💰 Cost Summary

### Free Tier (With Sleep Mode)
- Render: Free (750 hours/month per service)
- Railway: Free ($5 credit/month)
- Vercel: Free (100 GB bandwidth)
- **Total**: $0/month

### 24/7 Operation
- Render: $21/month (3 services × $7)
- Railway: $5-7/month (1 service)
- Vercel: Free
- **Total**: ~$26-28/month

---

## 🚀 Next Steps

1. **Custom Domain** (Optional):
   - Add custom domain in Vercel
   - Update CORS in backend

2. **Monitoring** (Optional):
   - Add Sentry for error tracking
   - Set up uptime monitoring

3. **Optimization**:
   - Add Redis caching
   - Optimize database queries
   - Add CDN for assets

---

## 📚 Documentation

- [Render Docs](https://render.com/docs)
- [Railway Docs](https://docs.railway.app)
- [Vercel Docs](https://vercel.com/docs)

---

**Congratulations! Your complete supply chain tracker is now live! 🎉**
