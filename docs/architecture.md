# System Architecture

## Components

### 1. GPS Simulator (Member 2)
- Emits live GPS coordinates
- Simulates vehicle movement
- Outputs to Pathway pipeline

### 2. Pathway Pipeline (Member 1)
- Ingests GPS stream
- Cleans and validates data
- Computes ETA and speed
- Outputs processed data

### 3. Backend API (Member 2)
- FastAPI endpoints
- Alert logic
- Data aggregation
- Serves dashboard and chatbot

### 4. Dashboard (Member 3)
- Streamlit UI
- Live map visualization
- ETA display
- Alert notifications

### 5. RAG Chatbot (Member 4)
- Pathway Document Store
- Natural language queries
- Shipment information retrieval

## Data Flow
```
GPS Simulator → Pathway Pipeline → Backend API → Dashboard
                                              ↓
                                         Document Store → Chatbot
```

## Integration Points
- Pathway outputs to shared data store or API
- Backend exposes REST endpoints
- Dashboard polls backend for updates
- Chatbot queries backend via API
