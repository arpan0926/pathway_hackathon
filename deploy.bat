@echo off
REM Deployment Script for Supply Chain Tracker (Windows)

echo.
echo 🚀 Supply Chain Tracker - Deployment Helper
echo ===========================================
echo.

REM Check if .env exists
if not exist .env (
    echo ⚠️  .env file not found. Creating from example...
    copy .env.example .env
    echo ✅ Please edit .env and add your GROQ_API_KEY
    exit /b 1
)

REM Menu
echo Choose deployment platform:
echo 1) Railway (Recommended - All services)
echo 2) Render (Backend) + Vercel (Frontend)
echo 3) Vercel (Frontend only)
echo 4) Local Docker (Testing)
echo.
set /p choice="Enter choice [1-4]: "

if "%choice%"=="1" goto railway
if "%choice%"=="2" goto render
if "%choice%"=="3" goto vercel
if "%choice%"=="4" goto docker
goto invalid

:railway
echo.
echo 📦 Deploying to Railway...
echo.
echo Steps:
echo 1. Install Railway CLI: npm i -g @railway/cli
echo 2. Login: railway login
echo 3. Initialize: railway init
echo 4. Add PostgreSQL: railway add --database postgresql
echo 5. Set env vars: railway variables set GROQ_API_KEY=your_key
echo 6. Deploy: railway up
echo.
set /p completed="Have you completed these steps? (y/n): "
if "%completed%"=="y" (
    echo ✅ Great! Your backend should be deploying now.
    echo 📝 Note your Railway URL for frontend deployment
)
goto end

:render
echo.
echo 📦 Deploying to Render + Vercel...
echo.
echo Backend (Render):
echo 1. Go to render.com
echo 2. New Blueprint
echo 3. Connect your GitHub repo
echo 4. Render will use render.yaml
echo.
echo Frontend (Vercel):
echo 1. Go to vercel.com
echo 2. Import your GitHub repo
echo 3. Set root directory: supply-chain-dashboard
echo 4. Add env var: VITE_API_URL=your_render_backend_url
echo 5. Deploy
goto end

:vercel
echo.
echo 📦 Deploying Frontend to Vercel...
echo.
where vercel >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    cd supply-chain-dashboard
    echo Building frontend...
    call npm install
    call npm run build
    echo.
    echo Deploying to Vercel...
    call vercel --prod
) else (
    echo Vercel CLI not found. Installing...
    call npm i -g vercel
    echo Run this script again after installation
)
goto end

:docker
echo.
echo 🐳 Starting Local Docker Environment...
echo.
docker-compose down -v
docker-compose up -d --build
echo.
echo ✅ Services starting...
echo 📊 Dashboard: http://localhost:3000
echo 🔌 Backend API: http://localhost:8000
echo 💬 Chatbot: http://localhost:8001
echo.
echo View logs: docker-compose logs -f
goto end

:invalid
echo Invalid choice
exit /b 1

:end
echo.
echo 📚 For detailed instructions, see DEPLOYMENT_GUIDE.md
echo ✅ Deployment helper complete!
pause
