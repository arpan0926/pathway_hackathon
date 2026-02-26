from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
import psycopg2
import os

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
Answer questions about shipments, routes, vehicles, and delivery status based on the provided data.
Be concise and accurate."""


class ChatRequest(BaseModel):
    query: str
    context: str | None = None
    session_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []


def get_shipments_context():
    """Fetch current shipments from database"""
    try:
        db_url = os.getenv(
            "DATABASE_URL",
            "postgresql://supply_chain_user:supply_chain_pass@postgres:5432/supply_chain_db"
        )
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT shipment_id, source, destination, vehicle_id, status, 
                   current_eta, last_updated
            FROM shipments
            ORDER BY last_updated DESC
        """)
        rows = cur.fetchall()
        conn.close()
        
        if not rows:
            return "No shipments found in database."
        
        context = "Current shipments:\n" + "\n".join([
            f"• {row[0]}: {row[1]} → {row[2]} (Vehicle: {row[3]}, Status: {row[4]}, ETA: {row[5]}, Updated: {row[6]})"
            for row in rows
        ])
        return context
        
    except Exception as e:
        return f"Database error: {e}"


def get_latest_telemetry(shipment_id: str | None = None):
    """Get latest GPS positions"""
    try:
        db_url = os.getenv(
            "DATABASE_URL",
            "postgresql://supply_chain_user:supply_chain_pass@postgres:5432/supply_chain_db"
        )
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        if shipment_id:
            cur.execute("""
                SELECT shipment_id, lat, lon, speed_kmph, ts
                FROM telemetry
                WHERE shipment_id = %s
                ORDER BY ts DESC LIMIT 1
            """, (shipment_id,))
        else:
            cur.execute("""
                SELECT DISTINCT ON (shipment_id) 
                    shipment_id, lat, lon, speed_kmph, ts
                FROM telemetry
                ORDER BY shipment_id, ts DESC
            """)
        
        rows = cur.fetchall()
        conn.close()
        
        if not rows:
            return "No GPS data available."
        
        context = "Latest positions:\n" + "\n".join([
            f"• {row[0]}: ({row[1]:.4f}, {row[2]:.4f}) @ {row[3]:.1f} km/h (as of {row[4]})"
            for row in rows
        ])
        return context
        
    except Exception as e:
        return f"Telemetry error: {e}"


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


@app.get("/health")
def health():
    return {"status": "healthy", "groq_configured": bool(GROQ_API_KEY)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)