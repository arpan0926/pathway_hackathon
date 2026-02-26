"""
FastAPI Backend - Member 2
Real-time Supply Chain API with GPS tracking, alerts, and ETA predictions
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import psycopg2
import psycopg2.extras
import os
import socketio
from groq import Groq

from dotenv import load_dotenv
load_dotenv()
# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://supply_chain_user:supply_chain_pass@localhost:5432/supply_chain_db")
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set")

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are a helpful supply chain logistics assistant. 
Answer questions about shipments, routes, vehicles, and delivery status based on the provided data.
Be concise and accurate."""

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
socket_app = socketio.ASGIApp(sio, app)

# Socket events

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def connect(sid, environ):
    print(f"🔌 Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"🔌 Client disconnected: {sid}")

@sio.on('new_alert')
async def handle_new_alert(sid, data):
    print(f"🔄 Relaying alert to React Dashboard: {data.get('alert_type')}")
    await sio.emit('new_alert', data, skip_sid=sid)


# Function to broadcast telemetry (call from your GPS route handlers)
async def broadcast_telemetry(data: dict):
    await sio.emit('telemetry_update', data)

# Function to broadcast alerts (called by driver_safety.py or other services)
async def broadcast_alert(alert_data: dict):
    """Broadcast new alert to all connected clients"""
    await sio.emit('new_alert', alert_data)
    print(f"📡 Alert broadcasted: {alert_data['alert_type']}")






class ChatRequest(BaseModel):
    query: str
    context: str | None = None
    session_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []
# Pydantic Models
class ShipmentResponse(BaseModel):
    shipment_id: str
    vehicle_id: str
    source: str
    destination: str
    status: str
    current_eta: Optional[datetime]
    last_updated: datetime

class TelemetryResponse(BaseModel):
    id: int
    ts: datetime
    vehicle_id: str
    shipment_id: str
    lat: float
    lon: float
    speed_kmph: float
    load_status: str

class AlertResponse(BaseModel):
    alert_id: int
    shipment_id: str
    alert_type: str
    metric: Optional[str]
    value: Optional[str]
    threshold: Optional[str]
    created_at: datetime
    is_active: bool

class ETAHistoryResponse(BaseModel):
    id: int
    shipment_id: str
    predicted_eta: Optional[datetime]
    distance_remaining_km: Optional[float]
    current_speed_kmph: Optional[float]
    confidence: Optional[float]
    computed_at: datetime

# Database helper
def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "Supply Chain Tracker API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "shipments": "/api/shipments",
            "telemetry": "/api/telemetry",
            "alerts": "/api/alerts",
            "eta_history": "/api/eta-history"
        }
    }

@app.get("/health")
def health_check():
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except:
        return {"status": "unhealthy", "database": "disconnected"}

# Shipments endpoints
@app.get("/api/shipments", response_model=List[ShipmentResponse])
def get_shipments(status: Optional[str] = None):
    """Get all shipments, optionally filtered by status"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    if status:
        cur.execute("SELECT * FROM shipments WHERE status = %s ORDER BY last_updated DESC", (status,))
    else:
        cur.execute("SELECT * FROM shipments ORDER BY last_updated DESC")
    
    shipments = cur.fetchall()
    conn.close()
    
    return shipments

@app.get("/api/shipments/{shipment_id}", response_model=ShipmentResponse)
def get_shipment(shipment_id: str):
    """Get specific shipment details"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cur.execute("SELECT * FROM shipments WHERE shipment_id = %s", (shipment_id,))
    shipment = cur.fetchone()
    conn.close()
    
    if not shipment:
        raise HTTPException(status_code=404, detail=f"Shipment {shipment_id} not found")
    
    return shipment

# Telemetry endpoints
@app.get("/api/telemetry", response_model=List[TelemetryResponse])
def get_telemetry(
    shipment_id: Optional[str] = None,
    vehicle_id: Optional[str] = None,
    limit: int = Query(100, le=1000)
):
    """Get GPS telemetry data"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    query = "SELECT * FROM telemetry WHERE 1=1"
    params = []
    
    if shipment_id:
        query += " AND shipment_id = %s"
        params.append(shipment_id)
    
    if vehicle_id:
        query += " AND vehicle_id = %s"
        params.append(vehicle_id)
    
    query += " ORDER BY ts DESC LIMIT %s"
    params.append(limit)
    
    cur.execute(query, params)
    telemetry = cur.fetchall()
    conn.close()
    
    return telemetry

@app.get("/api/telemetry/latest/{shipment_id}", response_model=TelemetryResponse)
def get_latest_telemetry(shipment_id: str):
    """Get latest GPS position for a shipment"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cur.execute("""
        SELECT * FROM telemetry 
        WHERE shipment_id = %s 
        ORDER BY ts DESC 
        LIMIT 1
    """, (shipment_id,))
    
    telemetry = cur.fetchone()
    conn.close()
    
    if not telemetry:
        raise HTTPException(status_code=404, detail=f"No telemetry found for shipment {shipment_id}")
    
    return telemetry

# Alerts endpoints
@app.get("/api/alerts", response_model=List[AlertResponse])
def get_alerts(
    shipment_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    limit: int = Query(50, le=500)
):
    """Get alerts, optionally filtered by shipment and active status"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    query = "SELECT * FROM alerts WHERE 1=1"
    params = []
    
    if shipment_id:
        query += " AND shipment_id = %s"
        params.append(shipment_id)
    
    if is_active is not None:
        query += " AND is_active = %s"
        params.append(is_active)
    
    query += " ORDER BY created_at DESC LIMIT %s"
    params.append(limit)
    
    cur.execute(query, params)
    alerts = cur.fetchall()
    conn.close()
    
    return alerts

@app.get("/api/alerts/critical", response_model=List[AlertResponse])
def get_critical_alerts():
    """Get all active critical alerts"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cur.execute("""
        SELECT * FROM alerts 
        WHERE is_active = true 
        AND alert_type IN ('critical', 'delay', 'temperature_breach')
        ORDER BY created_at DESC
    """)
    
    alerts = cur.fetchall()
    conn.close()
    
    return alerts

# ETA History endpoints
@app.get("/api/eta-history", response_model=List[ETAHistoryResponse])
def get_eta_history(
    shipment_id: Optional[str] = None,
    limit: int = Query(100, le=1000)
):
    """Get ETA prediction history"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    if shipment_id:
        cur.execute("""
            SELECT * FROM eta_history 
            WHERE shipment_id = %s 
            ORDER BY computed_at DESC 
            LIMIT %s
        """, (shipment_id, limit))
    else:
        cur.execute("""
            SELECT * FROM eta_history 
            ORDER BY computed_at DESC 
            LIMIT %s
        """, (limit,))
    
    history = cur.fetchall()
    conn.close()
    
    return history

@app.get("/api/eta-history/latest/{shipment_id}", response_model=ETAHistoryResponse)
def get_latest_eta(shipment_id: str):
    """Get latest ETA prediction for a shipment"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    cur.execute("""
        SELECT * FROM eta_history 
        WHERE shipment_id = %s 
        ORDER BY computed_at DESC 
        LIMIT 1
    """, (shipment_id,))
    
    eta = cur.fetchone()
    conn.close()
    
    if not eta:
        raise HTTPException(status_code=404, detail=f"No ETA history found for shipment {shipment_id}")
    
    return eta

# Statistics endpoint
@app.get("/api/stats")
def get_statistics():
    """Get overall system statistics"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    # Total shipments
    cur.execute("SELECT COUNT(*) as total FROM shipments")
    total_shipments = cur.fetchone()['total']
    
    # Active alerts
    cur.execute("SELECT COUNT(*) as total FROM alerts WHERE is_active = true")
    active_alerts = cur.fetchone()['total']
    
    # Average speed from recent telemetry
    cur.execute("""
        SELECT AVG(speed_kmph) as avg_speed 
        FROM telemetry 
        WHERE ts > NOW() - INTERVAL '1 hour'
    """)
    avg_speed = cur.fetchone()['avg_speed'] or 0
    
    # Telemetry count
    cur.execute("SELECT COUNT(*) as total FROM telemetry")
    total_telemetry = cur.fetchone()['total']
    
    conn.close()
    
    return {
        "total_shipments": total_shipments,
        "active_alerts": active_alerts,
        "avg_fleet_speed_kmph": round(float(avg_speed), 2),
        "total_telemetry_records": total_telemetry,
        "timestamp": datetime.now().isoformat()
    }
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Main chat endpoint"""
    try:
        # Build context from database
        shipments_data = get_shipments_context()
        telemetry_data = get_latest_telemetry()
        
        # Add user-provided context if any
        additional_context = f"\n\n{request.context}" if request.context else ""
        
        full_context = f"""
{SYSTEM_PROMPT}

Database Context:
{shipments_data}

{telemetry_data}
{additional_context}

User Question: {request.query}

Provide a helpful, accurate answer based on the context above.
"""
        
        # Call Groq
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": full_context}],
            temperature=0.3,
            max_tokens=500,
        )
        
        answer = response.choices[0].message.content
        
        return ChatResponse(
            answer=answer,
            sources=["shipments_table", "telemetry_table"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
