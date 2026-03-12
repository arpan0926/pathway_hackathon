# Quick Deploy Guide - 15 Minutes to Production

## Fastest Path: Railway + Vercel (100% Free)

### What You'll Get
- ✅ Full backend with all microservices
- ✅ PostgreSQL database
- ✅ React dashboard with real-time updates
- ✅ HTTPS/SSL automatically
- ✅ Custom domain support
- ✅ 500 hours/month free (enough for 24/7 operation)

---

## Prerequisites (5 minutes)

1. **GitHub Account** - Push your code to GitHub
2. **Railway Account** - Sign up at [railway.app](https://railway.app) (free, no credit card)
3. **Vercel Account** - Sign up at [vercel.com](https://vercel.com) (free, no credit card)
4. **Groq API Key** - Get free key at [console.groq.com](https://console.groq.com)

---

## Step 1: Deploy Backend on Railway (5 minutes)

### Option A: Using Railway Dashboard (Easiest)

1. **Go to Railway**
   - Visit [railway.app](https://railway.app)
   - Click "Start a New Project"

2. **Deploy from GitHub**
   - Click "Deploy from GitHub repo"
   - Select your `pathway_hackathon` repository
   - Railway will detect docker-compose.yml

3. **Add PostgreSQL**
   - Click "+ New"
   - Select "Database" → "PostgreSQL"
   - Railway auto-provisions it

4. **Set Environment Variables**
   - Click on your project
   - Go to "Variables" tab
   - Add:
     ```
     GROQ_API_KEY=your_groq_api_key_here
     ```
   - Railway automatically sets DATABASE_URL

5. **Deploy**
   - Click "Deploy"
   - Wait 3-5 minutes for build

6. **Get Your Backend URL**
   - Click on "backend-api" service
   - Go to "Settings" → "Networking"
   - Click "Generate Domain"
   - Copy the URL (e.g., `https://your-app.railway.app`)

### Option B: Using Railway CLI (For Developers)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
cd pathway_hackathon
railway init

# Add PostgreSQL
railway add --database postgresql

# Set environment variables
railway variables set GROQ_API_KEY=your_groq_api_key_here

# Deploy
railway up

# Get service URLs
railway status
```

---

## Step 2: Deploy Frontend on Vercel (5 minutes)

### Option A: Using Vercel Dashboard (Easiest)

1. **Go to Vercel**
   - Visit [vercel.com](https://vercel.com)
   - Click "Add New" → "Project"

2. **Import Repository**
   - Select your `pathway_hackathon` repository
   - Click "Import"

3. **Configure Project**
   - Framework Preset: Vite
   - Root Directory: `supply-chain-dashboard`
   - Build Command: `npm run build`
   - Output Directory: `dist`

4. **Add Environment Variables**
   - Click "Environment Variables"
   - Add:
     ```
     VITE_API_URL=https://your-railway-backend-url.railway.app
     VITE_WS_URL=wss://your-railway-backend-url.railway.app
     ```
   - Replace with your actual Railway URL from Step 1

5. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes

6. **Get Your Frontend URL**
   - Vercel will show your URL (e.g., `https://your-app.vercel.app`)

### Option B: Using Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to frontend
cd supply-chain-dashboard

# Create .env.production
echo "VITE_API_URL=https://your-railway-backend-url.railway.app" > .env.production
echo "VITE_WS_URL=wss://your-railway-backend-url.railway.app" >> .env.production

# Deploy
vercel --prod
```

---

## Step 3: Configure CORS (2 minutes)

Update your backend to allow your Vercel frontend:

1. **Edit backend/main.py**
   
   Find the CORS middleware section and update:
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

2. **Commit and Push**
   ```bash
   git add backend/main.py
   git commit -m "Update CORS for production"
   git push
   ```

3. **Railway Auto-Redeploys**
   - Railway detects the change and redeploys automatically

---

## Step 4: Test Your Deployment (3 minutes)

1. **Visit Your Frontend**
   - Go to your Vercel URL
   - You should see the dashboard

2. **Check Backend Health**
   - Visit `https://your-railway-backend-url.railway.app/health`
   - Should return: `{"status": "healthy", "database": "connected"}`

3. **Test Real-Time Features**
   - Watch the map for GPS updates
   - Check if shipments are loading
   - Verify alerts are appearing

4. **Test API Endpoints**
   ```bash
   # Get shipments
   curl https://your-railway-backend-url.railway.app/api/shipments
   
   # Get stats
   curl https://your-railway-backend-url.railway.app/api/stats
   ```

---

## Troubleshooting

### Frontend Can't Connect to Backend

**Problem**: Dashboard shows "Loading..." forever

**Solution**:
1. Check browser console for errors
2. Verify VITE_API_URL is correct in Vercel environment variables
3. Check CORS settings in backend/main.py
4. Ensure Railway backend is running (check Railway dashboard)

### Database Connection Failed

**Problem**: Backend shows database errors

**Solution**:
1. Check Railway PostgreSQL is running
2. Verify DATABASE_URL is set automatically by Railway
3. Check if init.sql ran successfully
4. Manually run init.sql:
   ```bash
   railway run psql $DATABASE_URL < database/init.sql
   ```

### Services Not Starting

**Problem**: Railway services show "Crashed"

**Solution**:
1. Check Railway logs for errors
2. Verify all environment variables are set
3. Check if GROQ_API_KEY is valid
4. Rebuild: Click "Redeploy" in Railway dashboard

### WebSocket Not Working

**Problem**: Real-time updates not appearing

**Solution**:
1. Ensure VITE_WS_URL uses `wss://` (not `ws://`)
2. Check if backend supports WebSocket (it does by default)
3. Verify Socket.IO is working: check browser console

---

## Cost Breakdown (Free Tier)

### Railway
- **Free Tier**: $5 credit/month (500 hours)
- **Your Usage**: ~5 services × 24/7 = 3,600 hours/month
- **Optimization**: Services sleep after inactivity (saves hours)
- **Actual Cost**: $0 with sleep mode, or ~$10/month for 24/7

### Vercel
- **Free Tier**: 100 GB bandwidth, unlimited deployments
- **Your Usage**: ~1-5 GB/month (typical)
- **Cost**: $0

### Total Monthly Cost
- **With Sleep Mode**: $0 (Railway free tier)
- **24/7 Operation**: ~$10/month (Railway paid)
- **Recommended**: Start free, upgrade if needed

---

## Optimization Tips

### Reduce Railway Costs

1. **Combine Services**
   - Run multiple services in one container
   - Edit docker-compose.yml to merge services

2. **Use Cron Jobs**
   - Instead of always-running GPS simulator
   - Use Railway Cron to run periodically

3. **Enable Sleep Mode**
   - Services sleep after 15 min inactivity
   - Wake up on first request (adds 2-3 sec delay)

### Improve Performance

1. **Enable Caching**
   - Add Redis for caching (Railway has free Redis)
   - Cache API responses

2. **Optimize Database**
   - Add indexes to frequently queried columns
   - Use connection pooling

3. **CDN for Frontend**
   - Vercel automatically uses CDN
   - No additional configuration needed

---

## Next Steps

1. **Custom Domain** (Optional)
   - Vercel: Add custom domain in settings (free SSL)
   - Railway: Add custom domain in service settings

2. **Monitoring**
   - Railway: Built-in metrics and logs
   - Vercel: Analytics dashboard
   - Add Sentry for error tracking (free tier)

3. **CI/CD**
   - Already set up! Push to GitHub = auto-deploy
   - Add GitHub Actions for tests before deploy

4. **Scaling**
   - Railway: Increase resources in settings
   - Vercel: Automatically scales
   - Add load balancer if needed

---

## Support & Resources

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)
- **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
- **Vercel Discord**: [vercel.com/discord](https://vercel.com/discord)

---

## Summary

You now have:
- ✅ Full-stack application deployed
- ✅ PostgreSQL database running
- ✅ Real-time WebSocket updates
- ✅ HTTPS/SSL enabled
- ✅ Auto-deploy on git push
- ✅ Free hosting (or ~$10/month for 24/7)

**Total Time**: ~15 minutes
**Total Cost**: $0 (free tier) or $10/month (24/7 operation)

🎉 **Congratulations! Your supply chain tracker is live!**
