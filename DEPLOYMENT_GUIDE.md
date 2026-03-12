# Free Deployment Guide - Supply Chain Tracker

## Overview
This guide covers deploying your full-stack supply chain application using free hosting platforms.

## Architecture
- **Frontend**: React + TypeScript Dashboard
- **Backend**: FastAPI with WebSocket
- **Database**: PostgreSQL
- **Services**: GPS Simulator, Pathway Pipeline, RAG Chatbot, AI Alerts

---

## Option 1: Railway (Recommended - All-in-One)

Railway offers free tier with 500 hours/month and supports Docker Compose.

### Prerequisites
1. GitHub account
2. Railway account (sign up at railway.app)
3. Groq API key

### Steps

#### 1. Prepare Your Repository
```bash
cd pathway_hackathon
git add .
git commit -m "Prepare for deployment"
git push origin main
```

#### 2. Deploy on Railway

**A. Create New Project**
- Go to railway.app
- Click "New Project"
- Select "Deploy from GitHub repo"
- Choose your `pathway_hackathon` repository

**B. Add PostgreSQL Database**
- Click "+ New"
- Select "Database" → "PostgreSQL"
- Railway will auto-provision the database

**C. Configure Environment Variables**
- Click on your project
- Go to "Variables" tab
- Add:
  ```
  GROQ_API_KEY=your_groq_api_key_here
  DATABASE_URL=${{Postgres.DATABASE_URL}}
  ```

**D. Deploy Services**
Railway will automatically detect your docker-compose.yml and deploy all services.

#### 3. Deploy Frontend Separately on Vercel

**A. Create vercel.json**
```json
{
  "buildCommand": "cd supply-chain-dashboard && npm install && npm run build",
  "outputDirectory": "supply-chain-dashboard/dist",
  "framework": "vite"
}
```

**B. Deploy**
- Go to vercel.com
- Import your GitHub repository
- Set root directory to `supply-chain-dashboard`
- Add environment variable:
  ```
  VITE_API_URL=https://your-railway-backend-url.railway.app
  ```
- Deploy

---

## Option 2: Render (Split Deployment)

### Backend on Render

#### 1. Create render.yaml

See render.yaml file in the root directory.

#### 2. Deploy Steps
- Go to render.com
- Click "New +" → "Blueprint"
- Connect your GitHub repository
- Render will detect render.yaml and deploy all services

### Frontend on Vercel
Same as Option 1, Step 3.

---

## Option 3: Free Tier Combination (Maximum Free Resources)

### Database: Supabase
- Go to supabase.com
- Create new project
- Get connection string from Settings → Database
- Run init.sql manually in SQL Editor

### Backend: Render Free Tier
- Deploy main backend API only
- Use Supabase database URL

### Frontend: Vercel
- Deploy React dashboard

### Background Services: Railway
- Deploy GPS simulator and other services

---

## Configuration Files

### 1. Frontend Environment Variables

Create `supply-chain-dashboard/.env.production`:
```env
VITE_API_URL=https://your-backend-url.com
VITE_WS_URL=wss://your-backend-url.com
VITE_MAPBOX_TOKEN=your_mapbox_token
```

### 2. Backend Environment Variables
```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
GROQ_API_KEY=your_groq_api_key
CORS_ORIGINS=https://your-frontend-url.vercel.app
```

---

## Step-by-Step: Railway Deployment (Easiest)

### 1. Sign Up & Connect GitHub
```bash
# Install Railway CLI (optional)
npm i -g @railway/cli
railway login
```

### 2. Initialize Project
```bash
cd pathway_hackathon
railway init
```

### 3. Add PostgreSQL
```bash
railway add --database postgresql
```

### 4. Set Environment Variables
```bash
railway variables set GROQ_API_KEY=your_key_here
```

### 5. Deploy
```bash
railway up
```

### 6. Get URLs
```bash
railway status
```

---

## Step-by-Step: Vercel Frontend Deployment

### 1. Install Vercel CLI
```bash
npm i -g vercel
```

### 2. Deploy
```bash
cd supply-chain-dashboard
vercel
```

### 3. Set Environment Variables
```bash
vercel env add VITE_API_URL production
# Enter your Railway backend URL
```

### 4. Redeploy
```bash
vercel --prod
```

---

## Post-Deployment Configuration

### 1. Update CORS in Backend
Edit `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend.vercel.app",
        "http://localhost:3000"  # for local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Update Frontend API URLs
Edit `supply-chain-dashboard/src/api/config.ts`:
```typescript
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
```

### 3. Database Initialization
If using external database, run:
```bash
psql $DATABASE_URL < database/init.sql
```

---

## Free Tier Limits

### Railway
- 500 hours/month
- $5 credit/month
- Shared CPU/RAM
- Sleeps after inactivity

### Render
- 750 hours/month
- Spins down after 15 min inactivity
- 512 MB RAM
- Shared CPU

### Vercel
- 100 GB bandwidth/month
- Unlimited deployments
- Automatic SSL
- Global CDN

### Supabase
- 500 MB database
- 2 GB bandwidth/month
- Unlimited API requests

---

## Troubleshooting

### Services Won't Start
- Check environment variables are set
- Verify DATABASE_URL format
- Check logs: `railway logs` or Render dashboard

### Frontend Can't Connect to Backend
- Verify CORS settings
- Check API URL in frontend .env
- Ensure backend is running

### Database Connection Failed
- Verify DATABASE_URL
- Check if database is provisioned
- Run init.sql if tables don't exist

### WebSocket Not Working
- Ensure backend supports WSS (secure WebSocket)
- Check firewall/proxy settings
- Verify Socket.IO configuration

---

## Monitoring & Logs

### Railway
```bash
railway logs
railway logs --service backend-api
```

### Render
- View logs in dashboard
- Set up log drains for persistence

### Vercel
```bash
vercel logs
```

---

## Cost Optimization

1. **Combine Services**: Run multiple services in one container
2. **Use Cron Jobs**: For periodic tasks instead of always-running services
3. **Optimize Database**: Use connection pooling, indexes
4. **Cache Static Assets**: Use CDN for frontend
5. **Lazy Loading**: Load services on-demand

---

## Production Checklist

- [ ] Environment variables configured
- [ ] Database initialized with schema
- [ ] CORS configured correctly
- [ ] API URLs updated in frontend
- [ ] SSL/HTTPS enabled
- [ ] Error logging configured
- [ ] Health check endpoints working
- [ ] WebSocket connection tested
- [ ] Map tiles loading (Mapbox token)
- [ ] Groq API key valid

---

## Alternative: Docker on Free VPS

If you prefer full control, use free VPS:

### Oracle Cloud (Always Free)
- 2 AMD VMs (1/8 OCPU, 1 GB RAM each)
- 200 GB storage
- 10 TB bandwidth/month

### Setup
```bash
# SSH into VPS
ssh ubuntu@your-vps-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone repo
git clone https://github.com/yourusername/pathway_hackathon.git
cd pathway_hackathon

# Set environment variables
cp .env.example .env
nano .env  # Add your keys

# Deploy
docker-compose up -d
```

---

## Next Steps

1. Choose deployment platform
2. Create accounts and connect GitHub
3. Configure environment variables
4. Deploy backend services
5. Deploy frontend
6. Test all functionality
7. Monitor logs and performance

---

## Support

For issues:
- Railway: docs.railway.app
- Render: render.com/docs
- Vercel: vercel.com/docs
- Supabase: supabase.com/docs

---

**Recommended Quick Start**: Railway + Vercel
- Railway: All backend services + database
- Vercel: Frontend dashboard
- Total setup time: ~30 minutes
