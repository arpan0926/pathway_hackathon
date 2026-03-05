from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import psycopg2
import os
from datetime import datetime

app = FastAPI(title="RAG Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set")

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are a helpful supply chain logistics assistant. 
Answer questions about shipments, routes, vehicles, delivery status, and ETAs based on the provided data.
Be concise, accurate, and professional. Always cite specific data points when available.
If you don't have information to answer a question, say so clearly."""


class ChatRequest(BaseModel):
    query: str
    context: str | None = None
    session_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []


def get_db_connection():
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://supply_chain_user:supply_chain_pass@postgres:5432/supply_chain_db"
    )
    return psycopg2.connect(db_url)


def get_shipments_context():
    """Fetch current shipments with latest ETA data"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                s.shipment_id, 
                s.source, 
                s.destination, 
                s.vehicle_id, 
                s.status,
                s.current_eta,
                s.last_updated,
                CASE 
                    WHEN s.current_eta IS NOT NULL THEN 
                        EXTRACT(EPOCH FROM (s.current_eta - NOW()))/3600
                    ELSE NULL
                END as hours_to_eta
            FROM shipments s
            ORDER BY s.last_updated DESC
        """)
        rows = cur.fetchall()
        conn.close()
        
        if not rows:
            return "No shipments found in database."
        
        context = "Current shipments with ETA information:\n"
        for row in rows:
            ship_id, source, dest, vehicle, status, eta, updated, hours = row
            
            if eta and hours is not None:
                if hours < 0:
                    eta_str = f"OVERDUE by {abs(hours):.1f} hours"
                elif hours < 1:
                    eta_str = f"ETA in {int(hours * 60)} minutes (arriving at {eta.strftime('%H:%M')})"
                else:
                    eta_str = f"ETA in {hours:.1f} hours (arriving at {eta.strftime('%Y-%m-%d %H:%M')})"
            else:
                eta_str = "ETA not calculated"
            
            context += f"\n• {ship_id}: {source} → {dest} (Vehicle: {vehicle}, Status: {status})\n"
            context += f"  {eta_str}\n"
            context += f"  Last updated: {updated.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return context
        
    except Exception as e:
        return f"Database error: {e}"


def get_latest_telemetry(shipment_id: str | None = None):
    """Get latest GPS positions with speed and location"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        if shipment_id:
            cur.execute("""
                SELECT shipment_id, vehicle_id, lat, lon, speed_kmph, ts
                FROM telemetry
                WHERE shipment_id = %s
                ORDER BY ts DESC LIMIT 1
            """, (shipment_id,))
        else:
            cur.execute("""
                SELECT DISTINCT ON (shipment_id) 
                    shipment_id, vehicle_id, lat, lon, speed_kmph, ts
                FROM telemetry
                ORDER BY shipment_id, ts DESC
            """)
        
        rows = cur.fetchall()
        conn.close()
        
        if not rows:
            return "No GPS data available."
        
        context = "Latest GPS positions:\n"
        for row in rows:
            ship_id, vehicle, lat, lon, speed, ts = row
            context += f"• {ship_id} ({vehicle}): Location ({lat:.4f}, {lon:.4f}), Speed: {speed:.1f} km/h, Time: {ts.strftime('%H:%M:%S')}\n"
        
        return context
        
    except Exception as e:
        return f"Telemetry error: {e}"


def get_eta_predictions():
    """Get latest ETA predictions from Pathway pipeline"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT DISTINCT ON (shipment_id)
                shipment_id,
                predicted_eta,
                distance_remaining_km,
                current_speed_kmph,
                confidence,
                computed_at
            FROM eta_history
            ORDER BY shipment_id, computed_at DESC
        """)
        
        rows = cur.fetchall()
        conn.close()
        
        if not rows:
            return "No ETA predictions available."
        
        context = "Latest ETA predictions (from Pathway pipeline):\n"
        for row in rows:
            ship_id, pred_eta, distance, speed, confidence, computed = row
            
            if pred_eta:
                hours_to_arrival = (pred_eta - datetime.now()).total_seconds() / 3600
                if hours_to_arrival < 1:
                    eta_str = f"{int(hours_to_arrival * 60)} minutes"
                else:
                    eta_str = f"{hours_to_arrival:.1f} hours"
                
                context += f"\n• {ship_id}:\n"
                context += f"  - ETA: {pred_eta.strftime('%Y-%m-%d %H:%M')} (in {eta_str})\n"
                context += f"  - Distance remaining: {distance:.1f} km\n"
                context += f"  - Current speed: {speed:.1f} km/h\n"
                context += f"  - Confidence: {confidence:.0f}%\n"
                context += f"  - Calculated at: {computed.strftime('%H:%M:%S')}\n"
        
        return context
        
    except Exception as e:
        return f"ETA prediction error: {e}"


def get_active_alerts():
    """Get active alerts affecting shipments"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT shipment_id, alert_type, metric, value, threshold, created_at
            FROM alerts
            WHERE is_active = true
            ORDER BY created_at DESC
            LIMIT 20
        """)
        
        rows = cur.fetchall()
        conn.close()
        
        if not rows:
            return "No active alerts."
        
        context = "Active alerts:\n"
        for row in rows:
            ship_id, alert_type, metric, value, threshold, created = row
            context += f"• {ship_id}: {alert_type} ({metric}) - {value} (threshold: {threshold}) at {created.strftime('%H:%M:%S')}\n"
        
        return context
        
    except Exception as e:
        return f"Alerts error: {e}"


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Main chat endpoint with comprehensive context"""
    try:
        # Build comprehensive context from all data sources
        shipments_data = get_shipments_context()
        telemetry_data = get_latest_telemetry()
        eta_data = get_eta_predictions()
        alerts_data = get_active_alerts()
        
        # Add user-provided context if any
        additional_context = f"\n\nAdditional Context: {request.context}" if request.context else ""
        
        full_context = f"""
{SYSTEM_PROMPT}

=== DATABASE CONTEXT ===

{shipments_data}

{telemetry_data}

{eta_data}

{alerts_data}
{additional_context}

=== USER QUESTION ===
{request.query}

=== INSTRUCTIONS ===
Provide a helpful, accurate answer based on the context above. 
Include specific data points (times, distances, speeds) when relevant.
If asked about ETAs, reference both the shipment's current_eta AND the Pathway pipeline predictions.
Be concise but informative.
"""
        
        # Call Groq LLM
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": full_context}],
            temperature=0.3,
            max_tokens=500,
        )
        
        answer = response.choices[0].message.content
        
        # Determine which sources were relevant
        sources = ["shipments_table", "telemetry_table"]
        if "ETA" in request.query.upper() or "WHEN" in request.query.upper():
            sources.append("eta_history_table")
        if "ALERT" in request.query.upper() or "DELAY" in request.query.upper():
            sources.append("alerts_table")
        
        return ChatResponse(
            answer=answer,
            sources=sources
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "healthy", "groq_configured": bool(GROQ_API_KEY)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)