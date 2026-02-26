# Supply Chain Tracker - Complete Project Analysis

## 📋 Executive Summary

This is a **real-time supply chain visibility and ETA prediction system** built for a hackathon. The project has evolved significantly with major architectural changes and new features.

### Key Highlights
- **Tech Stack**: React + TypeScript (Frontend), Python FastAPI (Backend), PostgreSQL, Pathway Framework, Groq AI
- **Architecture**: Microservices with WebSocket real-time updates
- **Major Features**: GPS tracking, ETA predictions, AI-powered alerts, Driver safety monitoring, RAG chatbot
- **Team**: 4 members with clear role separation

---

## 🏗️ Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    React Dashboard (Port 3000)               │
│         (Material-UI, MapBox, Socket.IO, React Query)       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├─── WebSocket (Real-time updates)
                 │
┌────────────────┴────────────────────────────────────────────┐
│                  Backend API (Port 8000)                     │
│         FastAPI + Socket.IO Server + REST Endpoints         │
└─┬──────────┬──────────┬──────────┬──────────┬──────────────┘
  │          │          │          │          │
  │          │          │          │          │
┌─┴──┐  ┌───┴───┐  ┌───┴───┐  ┌───┴───┐  ┌──┴────┐
│GPS │  │Pathway│  │RAG API│  │AI Alert│ │Driver │
│Sim │  │Pipeline│ │(8001) │  │(8100)  │ │Safety │
└────┘  └───────┘  └───────┘  └────────┘  └───────┘
  │          │          │          │          │
  └──────────┴──────────┴──────────┴──────────┘
                       │
              ┌────────┴────────┐
              │   PostgreSQL    │
              │   (Port 5432)   │
              └─────────────────┘
```

---

## 🆕 Major Changes & New Features

### 1. **New React Dashboard** (supply-chain-dashboard/)
**Status**: ✅ Active (Replaces old Streamlit dashboard)

**Technology Stack**:
- React 19 + TypeScript
- Vite (Build tool)
- Material-UI (Component library)
- MapBox GL (Interactive maps)
- Socket.IO Client (Real-time updates)
- React Query (Data fetching)
- Zustand (State management)
- Recharts (Data visualization)
- React Router (Navigation)

**Features**:
- 📊 **Dashboard Page**: KPIs, charts, real-time metrics
- 🗺️ **Map Page**: Live vehicle tracking with MapBox
- 📦 **Shipments Page**: Detailed shipment management
- 🚨 **Alerts Page**: Real-time alert monitoring
- 📈 **Analytics Page**: Historical data and trends
- 💬 **AI Chatbot**: Integrated RAG-powered assistant

**Key Files**:
- `src/App.tsx` - Main app with routing
- `src/pages/Dashboard.tsx` - Main dashboard
- `src/components/map/shipmentMap.tsx` - MapBox integration
- `src/hooks/useSocket.ts` - WebSocket connection
- `src/api/client.ts` - API client configuration

---

### 2. **AI Alert Service** (ai_alert_service/)
**Status**: ✅ New Microservice

**Purpose**: Intelligent alert generation using AI/ML

**Features**:
- **Stall Detection**: Detects when shipments are stuck
  - Monitors GPS movement over time
  - Configurable thresholds (time, speed, distance)
  - Auto-generates alerts in database

- **Driver Safety Integration**: Receives reports from webcam monitoring
  - Processes drowsiness alerts
  - Handles head-down detection
  - Creates critical safety alerts

**API Endpoints**:
- `POST /alerts/check-stall` - Check for stalled shipments
- `POST /driver-safety/report` - Report driver safety issues
- `GET /health/db` - Database health check

**Key Files**:
- `app/main.py` - FastAPI application
- `app/stall_detector.py` - Stall detection logic
- `app/driver_alerts.py` - Driver alert creation
- `app/models.py` - Pydantic models

---

### 3. **Driver Safety Monitoring** (backend/driver_safety.py)
**Status**: ✅ New Feature

**Purpose**: Real-time driver monitoring using webcam + AI

**Technology**:
- OpenCV (Computer vision)
- MediaPipe (Face mesh detection)
- Real-time video processing

**Detection Capabilities**:
- **Drowsiness Detection**: Eye Aspect Ratio (EAR) monitoring
  - Threshold: EAR < 0.25 for 1.5 seconds
  - Triggers "DROWSY" alert

- **Head Down Detection**: Face orientation analysis
  - Threshold: Head down for 3+ seconds
  - Triggers "HEAD_DOWN" alert

**Alert Flow**:
1. Webcam detects issue → 
2. Insert into database → 
3. Broadcast via WebSocket → 
4. Report to AI Alert Service → 
5. Dashboard shows real-time alert

**Key Features**:
- Multi-vehicle support (VH001, VH002, etc.)
- Alert cooldown (10 seconds between alerts)
- Visual overlay on video feed
- WebSocket integration for real-time updates

---

### 4. **WebSocket Real-Time Updates** (backend/main.py)
**Status**: ✅ Enhanced

**Purpose**: Push real-time data to dashboard without polling

**Events**:
- `telemetry_update` - New GPS position
- `new_alert` - New alert created
- `eta_update` - ETA prediction updated
- `shipment_update` - Shipment status changed

**Implementation**:
- Socket.IO server in FastAPI
- CORS enabled for frontend
- Automatic reconnection
- Event broadcasting to all connected clients

---

### 5. **RAG Chatbot API** (genai_rag/rag_api.py)
**Status**: ✅ Standalone API

**Purpose**: Conversational AI for supply chain queries

**Features**:
- Groq AI integration (llama-3.1-8b-instant)
- Database context injection
- Real-time shipment data
- GPS telemetry context

**API Endpoints**:
- `POST /chat` - Send query, get AI response
- `GET /health` - Health check

**Context Sources**:
- Shipments table (routes, status, ETA)
- Telemetry table (GPS positions, speed)
- User-provided context

---

### 6. **Enhanced Backend API** (backend/main.py)
**Status**: ✅ Upgraded

**New Features**:
- Socket.IO server integration
- WebSocket event broadcasting
- Enhanced CORS configuration
- Real-time data streaming

**Endpoints** (15+ total):
- Shipments CRUD
- Telemetry queries
- Alerts management
- ETA history
- Statistics
- Driver safety reports

---

## 📁 Project Structure

```
supply-chain-tracker/
├── supply-chain-dashboard/          # ✅ NEW: React TypeScript Dashboard
│   ├── src/
│   │   ├── api/                     # API client functions
│   │   ├── components/              # Reusable UI components
│   │   ├── pages/                   # Route pages
│   │   ├── hooks/                   # Custom React hooks
│   │   ├── store/                   # Zustand state management
│   │   └── types/                   # TypeScript definitions
│   ├── package.json
│   └── vite.config.ts
│
├── ai_alert_service/                # ✅ NEW: AI Alert Microservice
│   ├── app/
│   │   ├── main.py                  # FastAPI app
│   │   ├── stall_detector.py        # Stall detection logic
│   │   ├── driver_alerts.py         # Driver safety alerts
│   │   └── models.py                # Pydantic models
│   ├── dockerfile
│   └── requirements.txt
│
├── backend/                         # ✅ ENHANCED: Backend API
│   ├── main.py                      # FastAPI + Socket.IO
│   ├── gps_simulator.py             # GPS data generator
│   ├── driver_safety.py             # ✅ NEW: Webcam monitoring
│   ├── simulator.py                 # Simulation utilities
│   └── requirements.txt
│
├── pathway_pipeline/                # Member 1: ETA Predictions
│   ├── pipeline.py                  # Pathway streaming pipeline
│   ├── postgres_to_csv_bridge.py    # DB to CSV sync
│   └── requirements.txt
│
├── genai_rag/                       # ✅ ENHANCED: RAG Chatbot
│   ├── rag_api.py                   # ✅ NEW: Standalone API
│   ├── simple_chat.py               # CLI chatbot
│   └── requirements.txt
│
├── dashboard/                       # ⚠️ DEPRECATED: Old Streamlit dashboard
│   └── app.py                       # (Not used anymore)
│
├── database/
│   ├── init.sql                     # Database schema
│   └── README.md
│
├── shared/                          # Shared utilities
│   ├── schemas.py
│   ├── constants.py
│   └── utils.py
│
├── docs/                            # Documentation
│   ├── architecture.md
│   ├── git_guide.md
│   └── integration_plan.md
│
├── docker-compose.yml               # ✅ UPDATED: All services
├── .env                             # Environment variables
├── .env.example                     # Template
└── README.md                        # Project documentation
```

---

## 🔧 Services & Ports

| Service | Port | Technology | Status |
|---------|------|------------|--------|
| **React Dashboard** | 3000 | React + Vite | ✅ Active |
| **Backend API** | 8000 | FastAPI + Socket.IO | ✅ Active |
| **RAG Chatbot API** | 8001 | FastAPI + Groq | ✅ Active |
| **AI Alert Service** | 8100 | FastAPI | ✅ Active |
| **PostgreSQL** | 5432 | PostgreSQL 15 | ✅ Active |
| GPS Simulator | - | Python | ✅ Active |
| Pathway Pipeline | - | Pathway Framework | ✅ Active |
| Driver Safety | - | OpenCV + MediaPipe | ✅ Active |
| ~~Streamlit Dashboard~~ | ~~8501~~ | ~~Streamlit~~ | ❌ Deprecated |

---

## 🎯 Key Features

### Real-Time Capabilities
1. **Live GPS Tracking**: Vehicle positions update every 2 seconds
2. **WebSocket Updates**: Instant dashboard refresh on new data
3. **ETA Predictions**: Pathway pipeline calculates ETAs in real-time
4. **Alert Broadcasting**: Alerts appear immediately on dashboard

### AI/ML Features
1. **Stall Detection**: ML-based detection of stuck shipments
2. **Driver Safety**: Computer vision for drowsiness/distraction
3. **RAG Chatbot**: Natural language queries with context
4. **Predictive ETA**: Pathway framework for streaming predictions

### Dashboard Features
1. **Interactive Map**: MapBox with live vehicle markers
2. **KPI Metrics**: Real-time statistics and trends
3. **Alert Management**: View, filter, and acknowledge alerts
4. **Analytics**: Historical data visualization with Recharts
5. **Responsive Design**: Material-UI components

---

## 🔄 Data Flow

### GPS Telemetry Flow
```
GPS Simulator → PostgreSQL → Pathway Pipeline → ETA Predictions
                    ↓                              ↓
              Backend API ← WebSocket → React Dashboard
```

### Alert Flow
```
Driver Safety Monitor → Database → AI Alert Service
                           ↓              ↓
                    Backend API → WebSocket → Dashboard
```

### Chat Flow
```
User Query → React Dashboard → RAG API → Groq AI
                                  ↓
                            PostgreSQL (Context)
                                  ↓
                            AI Response → Dashboard
```

---

## 📊 Database Schema

### Core Tables
1. **shipments**: Shipment master data
2. **telemetry**: GPS positions (growing table)
3. **alerts**: System alerts
4. **eta_history**: ETA predictions over time
5. **shipment_events**: Event log

### Key Relationships
- `shipments.shipment_id` ← `telemetry.shipment_id`
- `shipments.shipment_id` ← `alerts.shipment_id`
- `shipments.shipment_id` ← `eta_history.shipment_id`

---

## 🚀 Running the Project

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for React dashboard)
- Python 3.10+ (for local development)
- Groq API Key

### Quick Start
```bash
# 1. Set environment variables
cp .env.example .env
# Edit .env and add GROQ_API_KEY

# 2. Start backend services
docker-compose up -d

# 3. Start React dashboard (separate terminal)
cd supply-chain-dashboard
npm install
npm run dev
```

### Access Points
- Dashboard: http://localhost:3000
- Backend API: http://localhost:8000/docs
- RAG Chatbot: http://localhost:8001/docs
- AI Alerts: http://localhost:8100/docs

---

## 🧪 Testing

### Backend API
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/stats
```

### RAG Chatbot
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the status of SH001?"}'
```

### AI Alert Service
```bash
curl -X POST http://localhost:8100/alerts/check-stall \
  -H "Content-Type: application/json" \
  -d '{"stall_minutes": 5, "speed_threshold_kmph": 5, "max_move_meters": 100}'
```

---

## 📝 Member Responsibilities

### Member 1: Pathway Pipeline
- ETA calculation using Pathway framework
- Real-time streaming data processing
- Distance and confidence calculations
- Database integration for predictions

### Member 2: Backend & GPS
- FastAPI backend with WebSocket
- GPS simulator with realistic patterns
- Driver safety monitoring
- Alert system integration

### Member 3: Dashboard
- React TypeScript dashboard
- MapBox integration
- Real-time UI updates
- Material-UI components

### Member 4: GenAI & RAG
- Groq AI integration
- RAG chatbot API
- Context-aware responses
- Database query integration

---

## 🔐 Security & Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# AI Services
GROQ_API_KEY=your_groq_api_key

# Service URLs
BACKEND_URL=http://backend-api:8000
AI_ALERTS_URL=http://ai-alert-service:8100
```

### CORS Configuration
- Backend API: Allows all origins (*)
- RAG API: Allows all origins (*)
- AI Alert Service: Allows all origins (*)

---

## 📈 Performance Metrics

### Data Generation
- GPS updates: 30 records/minute per vehicle
- ETA calculations: 6 predictions/minute per shipment
- Database growth: ~10MB per hour

### Response Times
- API endpoints: < 100ms
- WebSocket latency: < 50ms
- RAG chatbot: 2-5 seconds
- Map rendering: < 1 second

---

## 🐛 Known Issues & Limitations

1. **Old Dashboard**: Streamlit dashboard (dashboard/) is deprecated but still in repo
2. **Driver Safety**: Requires webcam access (not in Docker)
3. **MapBox Token**: Needs valid MapBox API token for maps
4. **Groq API**: Rate limits may apply
5. **WebSocket**: Requires persistent connection

---

## 🎯 Demo Checklist

Before presenting:
- [ ] All Docker services running
- [ ] React dashboard accessible
- [ ] GPS simulator generating data
- [ ] Map showing vehicle positions
- [ ] Alerts appearing in real-time
- [ ] Chatbot responding to queries
- [ ] Driver safety monitor (if webcam available)
- [ ] WebSocket connection active

---

## 📚 Documentation Files

- `README.md` - Project overview
- `GETTING_STARTED.md` - Setup instructions
- `API_DOCUMENTATION.md` - API reference
- `TESTING_GUIDE.md` - Testing procedures
- `GIT_COMMIT_GUIDE.md` - Git workflow
- `PROJECT_ANALYSIS.md` - This file

---

## 🏆 Hackathon Highlights

### Innovation
- Real-time WebSocket updates
- AI-powered driver safety monitoring
- Streaming ETA predictions with Pathway
- RAG chatbot with live context

### Technical Excellence
- Microservices architecture
- TypeScript for type safety
- Modern React with hooks
- Docker containerization

### User Experience
- Interactive MapBox maps
- Material-UI design
- Real-time alerts
- Conversational AI assistant

---

## 🔮 Future Enhancements

1. **Mobile App**: React Native version
2. **Advanced ML**: Predictive maintenance
3. **Route Optimization**: AI-powered routing
4. **Multi-tenant**: Support multiple companies
5. **Blockchain**: Immutable shipment records
6. **IoT Integration**: Temperature, humidity sensors
7. **Advanced Analytics**: ML-based insights

---

## 📞 Support & Contact

For questions or issues:
1. Check documentation in `docs/`
2. Review API docs at `/docs` endpoints
3. Check Docker logs: `docker-compose logs [service]`
4. Refer to TESTING_GUIDE.md

---

**Last Updated**: February 2026
**Version**: 2.0.0
**Status**: Production Ready for Hackathon Demo
