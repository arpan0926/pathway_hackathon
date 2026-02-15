from groq import Groq
import psycopg2
import os
from prompts import SYSTEM_PROMPT

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key")
client = Groq(api_key=GROQ_API_KEY)



def get_shipments():
    """Fetch current shipments from database"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5532,
            database="ai",
            user="ai",
            password="ai"
        )
        cur = conn.cursor()
        cur.execute("SELECT shipment_id, source, destination, vehicle_id, status FROM shipments")
        rows = cur.fetchall()
        conn.close()
        
        if not rows:
            return "No shipments found."
        
        context = "\n".join([
            f"• Shipment {row[0]} from {row[1]} to {row[2]}. Vehicle: {row[3]}. Status: {row[4]}."
            for row in rows
        ])
        return context
    except Exception as e:
        return f"Error fetching data: {e}"

def ask_question(question):
    """Ask a question about shipments"""
    context = get_shipments()
    
    prompt = f"""{SYSTEM_PROMPT}

Context (Current Shipments):
{context}

Question: {question}

Answer:"""
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    
    return response.choices[0].message.content

# Interactive loop
print("🤖 Logistics RAG Chatbot")
print("📊 Querying live database")
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