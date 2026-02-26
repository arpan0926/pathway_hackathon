# Real-Time Supply Chain Visibility & ETA Prediction System

A comprehensive supply chain tracking platform that provides real-time GPS monitoring, intelligent ETA predictions, AI-powered alerts, and driver safety monitoring. Built with modern microservices architecture and streaming data processing.

---

## Overview

This system enables logistics companies to track shipments in real-time, predict accurate delivery times, detect anomalies, and ensure driver safety through AI-powered monitoring. The platform processes live GPS data streams, calculates dynamic ETAs using the Pathway framework, and provides actionable insights through an intuitive dashboard.

### Key Capabilities

**Real-Time Tracking**
- Live GPS position updates every 2 seconds
- Interactive map visualization with route tracking
- WebSocket-based instant data synchronization
- Historical telemetry data analysis

**Intelligent Predictions**
- Dynamic ETA calculations using streaming data processing
- Confidence scoring for prediction accuracy
- Traffic pattern analysis and route optimization
- Automated stall detection and delay alerts

**AI-Powered Safety**
- Computer vision-based driver monitoring
- Drowsiness and distraction detection
- Real-time safety alerts and notifications
- Automated incident reporting

**Conversational AI**
- Natural language query interface
- Context-aware responses using RAG (Retrieval-Augmented Generation)
- Real-time data integration
- Multi-source information synthesis

---

## Architecture

### System Components

**Frontend Layer**
- Modern React application with TypeScript
- Material-UI component library for consistent design
- MapBox GL for interactive mapping
- Real-time updates via WebSocket connections

**Backend Services**
- RESTful API built with FastAPI
- WebSocket server for real-time communication
- Microservices architecture for scalability
- PostgreSQL database for persistent storage

**Data Processing**
- Pathway framework for streaming data processing
- Real-time ETA calculation engine
- GPS data validation and cleaning
- Historical data aggregation

**AI & Machine Learning**
- Groq AI for natural language processing
- MediaPipe for computer vision tasks
- Custom ML models for anomaly detection
- Predictive analytics for route optimization

### Technology Stack

**Frontend**
- React 19 with TypeScript
- Material-UI (MUI) v7
- MapBox GL for mapping
- Socket.IO for real-time updates
- React Query for data fetching
- Zustand for state management
- Recharts for data visualization

**Backend**
- Python 3.11
- FastAPI for REST API
- Socket.IO for WebSocket
- PostgreSQL 15 for database
- Pathway for stream processing
- Groq AI for language models
- OpenCV & MediaPipe for computer vision

**Infrastructure**
- Docker & Docker Compose
- Microservices architecture
- RESTful API design
- WebSocket protocol
- PostgreSQL with connection pooling

---

## Features

### Dashboard

The web-based dashboard provides a comprehensive view of the entire supply chain operation:

- **Live Map View**: Real-time vehicle positions with route visualization
- **KPI Metrics**: Active shipments, fleet speed, on-time performance, critical alerts
- **Shipment Management**: Detailed tracking information for each shipment
- **Alert System**: Real-time notifications for delays, stalls, and safety issues
- **Analytics**: Historical data analysis and trend visualization
- **AI Assistant**: Natural language interface for querying system data

### GPS Tracking

Realistic GPS simulation with:
- Multiple vehicle tracking
- Traffic pattern simulation
- Random event generation (stops, delays)
- Route waypoint navigation
- Speed variation modeling

### ETA Prediction

Advanced prediction system featuring:
- Haversine distance calculations
- Real-time speed analysis
- Confidence score generation
- Historical pattern learning
- Dynamic route adjustment

### Alert System

Intelligent alert generation for:
- Shipment stalls and delays
- Driver safety incidents
- Route deviations
- Temperature breaches (cold chain)
- System anomalies

### Driver Safety

Computer vision-based monitoring:
- Eye aspect ratio analysis for drowsiness
- Head position tracking
- Real-time alert generation
- Automated incident logging
- Dashboard integration

---

## Getting Started

### Prerequisites

- Docker Desktop (latest version)
- Node.js 18 or higher
- Git
- Groq API key (free tier available)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AYUSH-0305/pathway_hackathon.git
   cd pathway_hackathon
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Groq API key:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

3. **Start backend services**
   ```bash
   docker-compose up -d
   ```
   This will start:
   - PostgreSQL database
   - GPS simulator
   - Pathway pipeline
   - Backend API
   - RAG chatbot API
   - AI alert service

4. **Start the dashboard**
   ```bash
   cd supply-chain-dashboard
   npm install
   npm run dev
   ```

5. **Access the application**
   - Dashboard: http://localhost:3000
   - Backend API: http://localhost:8000/docs
   - RAG Chatbot: http://localhost:8001/docs
   - AI Alerts: http://localhost:8100/docs

### Quick Test

Verify the system is working:

```bash
# Check backend health
curl http://localhost:8000/health

# Check database connectivity
docker exec -it postgres psql -U supply_chain_user -d supply_chain_db -c "SELECT COUNT(*) FROM telemetry;"

# View GPS simulator logs
docker logs gps_simulator --tail 20
```

---

## API Documentation

### Backend API (Port 8000)

**Shipments**
- `GET /api/shipments` - List all shipments
- `GET /api/shipments/{id}` - Get shipment details
- `GET /api/stats` - System statistics

**Telemetry**
- `GET /api/telemetry` - GPS data with filtering
- `GET /api/telemetry/latest/{id}` - Latest position

**Alerts**
- `GET /api/alerts` - List alerts
- `GET /api/alerts/critical` - Critical alerts only

**ETA Predictions**
- `GET /api/eta-history` - Historical predictions
- `GET /api/eta-history/latest/{id}` - Latest ETA

### RAG Chatbot API (Port 8001)

**Chat**
- `POST /chat` - Send query, receive AI response
  ```json
  {
    "query": "What is the status of shipment SH001?",
    "context": "optional additional context"
  }
  ```

### AI Alert Service (Port 8100)

**Stall Detection**
- `POST /alerts/check-stall` - Check for stalled shipments
  ```json
  {
    "stall_minutes": 5,
    "speed_threshold_kmph": 5,
    "max_move_meters": 100
  }
  ```

**Driver Safety**
- `POST /driver-safety/report` - Report safety incident

---

## Project Structure

```
supply-chain-tracker/
├── supply-chain-dashboard/     # React TypeScript frontend
│   ├── src/
│   │   ├── api/               # API client functions
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Application pages
│   │   ├── hooks/             # Custom React hooks
│   │   └── store/             # State management
│   └── package.json
│
├── backend/                    # FastAPI backend services
│   ├── main.py                # Main API with WebSocket
│   ├── gps_simulator.py       # GPS data generator
│   └── driver_safety.py       # Webcam monitoring
│
├── pathway_pipeline/           # Streaming data processing
│   ├── pipeline.py            # ETA calculation engine
│   └── postgres_to_csv_bridge.py
│
├── genai_rag/                 # AI chatbot service
│   └── rag_api.py             # RAG implementation
│
├── ai_alert_service/          # Alert generation service
│   └── app/
│       ├── main.py
│       └── stall_detector.py
│
├── database/                   # Database schemas
│   └── init.sql
│
├── docs/                       # Documentation
│   ├── architecture.md
│   ├── testing_guide.md
│   └── integration_plan.md
│
└── docker-compose.yml          # Service orchestration
```

---

## Development

### Team Structure

**Member 1 - Data Processing**
- Pathway pipeline development
- ETA calculation algorithms
- Stream processing optimization

**Member 2 - Backend Development**
- API endpoint implementation
- GPS simulator development
- Driver safety monitoring
- Alert system integration

**Member 3 - Frontend Development**
- React dashboard implementation
- MapBox integration
- Real-time UI updates
- User experience design

**Member 4 - AI & Documentation**
- RAG chatbot development
- Groq AI integration
- Documentation maintenance
- Presentation materials

### Git Workflow

All development occurs in the `development` branch. Pull requests are required for merging to `main`.

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Description of changes"

# Push and create pull request
git push origin feature/your-feature-name
```

---

## Testing

Comprehensive testing procedures are documented in [COMPREHENSIVE_TESTING_PLAN.md](COMPREHENSIVE_TESTING_PLAN.md).

### Quick Test Commands

```bash
# Test backend API
curl http://localhost:8000/api/stats

# Test chatbot
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "How many shipments are active?"}'

# Check database
docker exec -it postgres psql -U supply_chain_user -d supply_chain_db
```

---

## Performance

### Metrics

- API response time: < 100ms
- WebSocket latency: < 50ms
- GPS update frequency: 2 seconds
- ETA calculation: Real-time streaming
- Dashboard refresh: 10 seconds

### Scalability

- Microservices architecture for horizontal scaling
- Database connection pooling
- Efficient WebSocket broadcasting
- Optimized database queries with indexing

---

## Documentation

- [Getting Started Guide](GETTING_STARTED.md) - Detailed setup instructions
- [Project Analysis](PROJECT_ANALYSIS.md) - Complete system analysis
- [Testing Plan](COMPREHENSIVE_TESTING_PLAN.md) - Testing procedures
- [Docker Setup](README_DOCKER.md) - Docker deployment guide
- [Git Workflow](GIT_COMMIT_GUIDE.md) - Contribution guidelines
- [Documentation Index](docs/README.md) - All documentation

---

## Troubleshooting

### Common Issues

**Services won't start**
```bash
docker-compose down -v
docker-compose up -d --build
```

**Database connection failed**
```bash
docker-compose restart postgres
# Wait 10 seconds
docker-compose restart backend-api
```

**Map not loading**
- Verify MapBox token in `supply-chain-dashboard/.env`

**Chatbot not responding**
- Verify Groq API key in `.env`
- Check service logs: `docker logs chatbot`

---

## License

This project was developed for the Pathway Hackathon 2026.

---

## Acknowledgments

- Pathway Framework for streaming data processing
- Groq for AI language models
- MapBox for mapping services
- MediaPipe for computer vision capabilities

---

## Contact

For questions or support, please refer to the documentation in the `docs/` directory or create an issue in the repository.

---

**Built with modern technologies for real-time supply chain visibility**
