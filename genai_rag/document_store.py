import psycopg2
from psycopg2.extras import RealDictCursor
from langchain_core.documents import Document

from langchain_community.vectorstores.pgvector import PGVector
from langchain_ollama import OllamaEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

from config import settings


# ---------- DB ----------
def get_conn():
    return psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
    )


def fetch_all(query):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()


# ---------- BUILD RAG DOCUMENTS ----------
def build_documents():
    shipments = fetch_all("SELECT * FROM shipments")

    docs = []

    for s in shipments:
        shipment_id = s["shipment_id"]

        # Latest telemetry
        telemetry = fetch_all(f"""
            SELECT * FROM telemetry
            WHERE shipment_id = '{shipment_id}'
            ORDER BY ts DESC
            LIMIT 1
        """)

        # Latest ETA
        eta = fetch_all(f"""
            SELECT * FROM eta_history
            WHERE shipment_id = '{shipment_id}'
            ORDER BY computed_at DESC
            LIMIT 1
        """)

        # Active alerts
        alerts = fetch_all(f"""
            SELECT * FROM alerts
            WHERE shipment_id = '{shipment_id}'
            AND is_active = TRUE
        """)

        # Recent events
        events = fetch_all(f"""
            SELECT * FROM shipment_events
            WHERE shipment_id = '{shipment_id}'
            ORDER BY event_time DESC
            LIMIT 3
        """)

        text = f"""
Shipment {shipment_id} from {s['source']} to {s['destination']}.
Vehicle: {s['vehicle_id']}.
Current status: {s['status']}.
Scheduled ETA: {s['current_eta']}.
"""

        # Telemetry
        if telemetry:
            t = telemetry[0]
            text += f"""
Latest telemetry:
- Timestamp: {t['ts']}
- Location: ({t['lat']}, {t['lon']})
- Speed: {t['speed_kmph']} km/h
- Load status: {t['load_status']}
"""

        # ETA history
        if eta:
            e = eta[0]
            text += f"""
Latest ETA prediction:
- Predicted ETA: {e['predicted_eta']}
- Distance remaining: {e['distance_remaining_km']} km
- Current speed: {e['current_speed_kmph']} km/h
- Confidence: {e['confidence']}%
"""

        # Alerts
        if alerts:
            text += "\nActive alerts:\n"
            for a in alerts:
                text += f"- {a['alert_type']} ({a['metric']} = {a['value']}, threshold {a['threshold']})\n"

        # Events
        if events:
            text += "\nRecent events:\n"
            for ev in events:
                text += f"- {ev['event_type']} at {ev['event_time']}: {ev['description']}\n"

        docs.append(
            Document(
                page_content=text.strip(),
                metadata={"shipment_id": shipment_id}
            )
        )

    return docs


# ---------- INGEST ----------
def ingest_documents():
    docs = build_documents()

    embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


    vector_store = PGVector(
        connection_string=settings.connection_string,
        collection_name=settings.COLLECTION_NAME,
        embedding_function=embeddings
    )

    vector_store.add_documents(docs)

    print(f"✅ Embedded {len(docs)} shipment summaries into pgvector.")
