"""
Simple RAG Chatbot using Groq
Member 4 - GenAI & RAG
"""

from groq import Groq
import psycopg2
import os
from datetime import datetime

# Groq API Key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")
client = Groq(api_key=GROQ_API_KEY)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://supply_chain_user:supply_chain_pass@postgres:5432/supply_chain_db")

def get_shipment_context():
    """Fetch current shipments and telemetry from database"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Get shipments with latest telemetry
        query = """
        SELECT 
            s.shipment_id, 
            s.source, 
            s.destination, 
            s.vehicle_id, 
            s.status,
            t.lat,
            t.lon,
            t.speed_kmph,
            t.load_status,
            t.ts
        FROM shipments s
        LEFT JOIN telemetry t ON s.shipment_id = t.shipment_id
        WHERE t.ts = (SELECT MAX(ts) FROM telemetry t2 WHERE t2.shipment_id = s.shipment_id)
           OR t.ts IS NULL
        ORDER BY s.shipment_id
        """
        
        cur.execute(query)
        rows = cur.fetchall()
        conn.close()
        
        if not rows:
            return "No shipments found in the database."
        
        context_parts = []
        for row in rows:
            shipment_id, source, dest, vehicle, status, lat, lon, speed, load, ts = row
            
            if lat and lon:
                context_parts.append(
                    f"Shipment {shipment_id}: {source} → {dest} (Vehicle: {vehicle}). "
                    f"Current location: ({lat:.4f}, {lon:.4f}). "
                    f"Speed: {speed:.1f} km/h. Load: {load}. Status: {status}."
                )
            else:
                context_parts.append(
                    f"Shipment {shipment_id}: {source} → {dest} (Vehicle: {vehicle}). "
                    f"Status: {status}. No GPS data yet."
                )
        
        return "\n".join(context_parts)
        
    except Exception as e:
        return f"Error fetching data: {e}"

def ask_question(question):
    """Ask a question about shipments using Groq"""
    
    # Get current shipment data
    context = get_shipment_context()
    
    # System prompt
    system_prompt = """You are a helpful logistics assistant for a supply chain tracking system.
You have access to real-time shipment data including locations, speeds, and statuses.
Answer questions clearly and concisely based on the provided data.
If you don't have enough information, say so."""
    
    # User prompt with context
    user_prompt = f"""Current Shipment Data:
{context}

Question: {question}

Please answer based on the shipment data provided above."""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error calling Groq API: {e}"

def main():
    """Interactive chatbot loop"""
    print("🤖 Supply Chain RAG Chatbot (Powered by Groq)")
    print("� Conenected to live database")
    print("💬 Type your question or 'exit' to quit\n")
    print("-" * 60)
    
    while True:
        try:
            question = input("\n🔍 Ask: ").strip()
            
            if not question:
                continue
                
            if question.lower() in ["exit", "quit", "q"]:
                print("\n👋 Goodbye!")
                break
            
            print("\n⏳ Processing...")
            answer = ask_question(question)
            print(f"\n💡 Answer:\n{answer}")
            print("\n" + "-" * 60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Exiting.")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
