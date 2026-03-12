#!/bin/bash

# Deployment Script for Supply Chain Tracker
# This script helps you deploy to various platforms

echo "🚀 Supply Chain Tracker - Deployment Helper"
echo "==========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from example..."
    cp .env.example .env
    echo "✅ Please edit .env and add your GROQ_API_KEY"
    exit 1
fi

# Menu
echo "Choose deployment platform:"
echo "1) Railway (Recommended - All services)"
echo "2) Render (Backend) + Vercel (Frontend)"
echo "3) Vercel (Frontend only)"
echo "4) Local Docker (Testing)"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "📦 Deploying to Railway..."
        echo ""
        echo "Steps:"
        echo "1. Install Railway CLI: npm i -g @railway/cli"
        echo "2. Login: railway login"
        echo "3. Initialize: railway init"
        echo "4. Add PostgreSQL: railway add --database postgresql"
        echo "5. Set env vars: railway variables set GROQ_API_KEY=your_key"
        echo "6. Deploy: railway up"
        echo ""
        read -p "Have you completed these steps? (y/n): " completed
        if [ "$completed" = "y" ]; then
            echo "✅ Great! Your backend should be deploying now."
            echo "📝 Note your Railway URL for frontend deployment"
        fi
        ;;
    
    2)
        echo ""
        echo "📦 Deploying to Render + Vercel..."
        echo ""
        echo "Backend (Render):"
        echo "1. Go to render.com"
        echo "2. New Blueprint"
        echo "3. Connect your GitHub repo"
        echo "4. Render will use render.yaml"
        echo ""
        echo "Frontend (Vercel):"
        echo "1. Go to vercel.com"
        echo "2. Import your GitHub repo"
        echo "3. Set root directory: supply-chain-dashboard"
        echo "4. Add env var: VITE_API_URL=your_render_backend_url"
        echo "5. Deploy"
        ;;
    
    3)
        echo ""
        echo "📦 Deploying Frontend to Vercel..."
        echo ""
        if command -v vercel &> /dev/null; then
            cd supply-chain-dashboard
            echo "Building frontend..."
            npm install
            npm run build
            echo ""
            echo "Deploying to Vercel..."
            vercel --prod
        else
            echo "Vercel CLI not found. Installing..."
            npm i -g vercel
            echo "Run this script again after installation"
        fi
        ;;
    
    4)
        echo ""
        echo "🐳 Starting Local Docker Environment..."
        echo ""
        docker-compose down -v
        docker-compose up -d --build
        echo ""
        echo "✅ Services starting..."
        echo "📊 Dashboard: http://localhost:3000"
        echo "🔌 Backend API: http://localhost:8000"
        echo "💬 Chatbot: http://localhost:8001"
        echo ""
        echo "View logs: docker-compose logs -f"
        ;;
    
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "📚 For detailed instructions, see DEPLOYMENT_GUIDE.md"
echo "✅ Deployment helper complete!"
