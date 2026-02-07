# Member 2 – Backend, Alerts & Simulator

## Responsibilities
- GPS data simulator
- Alert logic implementation
- FastAPI endpoints
- Data logging

## Timeline
- Days 1-2: Plan GPS simulation, finalize alert condition
- Days 3-4: Build GPS simulator
- Days 5-6: Implement alert logic and logging
- Days 7-8: Create FastAPI endpoints
- Days 9-10: Ensure API reliability

## Key Files
- `main.py` - FastAPI application
- `simulator.py` - GPS data simulator
- `alerts.py` - Alert logic
- `models.py` - Pydantic models
- `config.py` - Backend configuration

## API Endpoints
- GET `/shipments` - List all shipments
- GET `/shipments/{id}` - Get shipment details
- GET `/shipments/{id}/location` - Current GPS location
- GET `/alerts` - Get active alerts
