"""
FastAPI Backend - Member 2
Placeholder until Member 2 implements the actual API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Supply Chain Tracker API",
    description="Real-time supply chain visibility and ETA prediction",
    version="1.0.0"
)

# Enable CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "Supply Chain Tracker API",
        "status": "running",
        "note": "Member 2: Implement your endpoints here!"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Placeholder endpoints for Member 2 to implement
@app.get("/api/shipments")
def get_shipments():
    return {
        "message": "TODO: Member 2 - Implement get all shipments",
        "shipments": []
    }

@app.get("/api/shipments/{shipment_id}")
def get_shipment(shipment_id: str):
    return {
        "message": f"TODO: Member 2 - Implement get shipment {shipment_id}",
        "shipment_id": shipment_id
    }

@app.get("/api/alerts")
def get_alerts():
    return {
        "message": "TODO: Member 2 - Implement get alerts",
        "alerts": []
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
