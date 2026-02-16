import streamlit as st
import pandas as pd
import os
import random
import time
import textwrap
import psycopg2

try:
    import pydeck as pdk
except ImportError:
    pdk = None
from streamlit_autorefresh import st_autorefresh

# ---------------------------------------------------------
# 1. UI CONFIGURATION & THEME (MEMBER 3)
# ---------------------------------------------------------
st.set_page_config(page_title="Supply Chain Command Center", page_icon="🚚", layout="wide")

# PostgreSQL connection from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://supply_chain_user:supply_chain_pass@postgres:5432/supply_chain_db")
REFRESH_RATE = 10 

st.markdown("""
<style>
    /* --- TEAL & BREEZE PALETTE --- */
    :root {
        --teal-dark: #125e6e;    
        --teal-mid: #0a8799;     
        --teal-light: #82b4b9;   
        --bg-breeze: #EBF4F6;    
        
        --card-bg: #ffffff;
        --border: #82b4b9;
        
        --text-main: #125e6e;
        --text-muted: #5a8a92;
        --danger: #d32f2f;       
        
        --shadow: 0 4px 12px -2px rgba(18, 94, 110, 0.15);
    }
    
    .stApp { background-color: var(--bg-breeze); font-family: 'Inter', sans-serif; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: var(--card-bg); border-right: 2px solid var(--border); }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: var(--teal-dark) !important; }
    
    /* Typography */
    h1, h2, h3 { color: var(--teal-dark) !important; font-weight: 800 !important; }
    p, div, span, small { color: var(--text-main); }
    
    .dashboard-header { margin-bottom: 2rem; border-bottom: 2px solid var(--border); padding-bottom: 1rem; }
    .dashboard-card { background-color: var(--card-bg); border: 1px solid var(--border); border-radius: 16px; padding: 1.5rem; box-shadow: var(--shadow); }
    
    /* Badges & Alerts */
    .badge { display: inline-block; padding: 0.4em 0.8em; font-size: 0.85rem; font-weight: 800; border-radius: 8px; text-transform: uppercase; }
    .badge-critical { background: #ffebee; color: var(--danger) !important; border: 1px solid #ffcdd2; }
    .badge-ontime { background: var(--bg-breeze); color: var(--teal-mid) !important; border: 1px solid var(--teal-light); }
    .reason-box { background: #f8fbfc; border-left: 5px solid var(--teal-mid); padding: 15px; margin-top: 15px; border-radius: 8px; }
    
    /* Streamlit Tab Styling for Light Theme */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: transparent; border-radius: 4px 4px 0px 0px; gap: 1px; padding-top: 10px; padding-bottom: 10px; color: var(--teal-dark); }
    .stTabs [aria-selected="true"] { color: var(--teal-mid) !important; font-weight: 800; border-bottom: 3px solid var(--teal-mid); }
    
    /* Selectbox Fixes */
    div[data-baseweb="select"] > div { background-color: var(--card-bg) !important; color: var(--teal-dark) !important; border: 2px solid var(--teal-light) !important; border-radius: 12px !important; }
    div[data-baseweb="select"] span { color: var(--teal-dark) !important; font-weight: 600 !important; }
    div[data-baseweb="select"] svg { fill: var(--teal-dark) !important; }
    ul[data-baseweb="menu"] { background-color: var(--card-bg) !important; }
    li[data-baseweb="option"] { color: var(--teal-dark) !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DATA PIPELINE INTEGRATION (MEMBER 1 & 2)
# ---------------------------------------------------------
def fetch_live_telemetry():
    """Fetch real-time telemetry data from database"""
    try:
        # Try using SQLAlchemy for pandas
        try:
            from sqlalchemy import create_engine
            engine = create_engine(DATABASE_URL)
            query = """
            WITH latest_telemetry AS (
                SELECT DISTINCT ON (s.shipment_id)
                    s.shipment_id,
                    s.source,
                    s.destination,
                    s.source_lat,
                    s.source_lon,
                    s.dest_lat,
                    s.dest_lon,
                    s.status,
                    t.lat,
                    t.lon,
                    t.speed_kmph as avg_speed,
                    t.load_status,
                    t.ts as last_update
                FROM shipments s
                LEFT JOIN telemetry t ON s.shipment_id = t.shipment_id
                ORDER BY s.shipment_id, t.ts DESC NULLS LAST
            )
            SELECT * FROM latest_telemetry;
            """
            df = pd.read_sql(query, engine)
        except ImportError:
            # Fallback to psycopg2 direct connection
            conn = psycopg2.connect(DATABASE_URL)
            query = """
            WITH latest_telemetry AS (
                SELECT DISTINCT ON (s.shipment_id)
                    s.shipment_id,
                    s.source,
                    s.destination,
                    s.source_lat,
                    s.source_lon,
                    s.dest_lat,
                    s.dest_lon,
                    s.status,
                    t.lat,
                    t.lon,
                    t.speed_kmph as avg_speed,
                    t.load_status,
                    t.ts as last_update
                FROM shipments s
                LEFT JOIN telemetry t ON s.shipment_id = t.shipment_id
                ORDER BY s.shipment_id, t.ts DESC NULLS LAST
            )
            SELECT * FROM latest_telemetry;
            """
            df = pd.read_sql(query, conn)
            conn.close()
        
        if df.empty:
            st.warning("⚠️ No telemetry data available yet. GPS simulator may still be starting...")
            return pd.DataFrame()
        
        # Handle None values
        df['lat'] = df['lat'].fillna(df['source_lat'])
        df['lon'] = df['lon'].fillna(df['source_lon'])
        df['avg_speed'] = df['avg_speed'].fillna(60.0)
        df['load_status'] = df['load_status'].fillna('LOADED')
        
        return df
    except Exception as e:
        st.error(f"❌ Database error: {e}")
        return pd.DataFrame()

def fetch_eta_predictions(shipment_ids):
    """Fetch latest ETA predictions from Pathway pipeline output"""
    try:
        if not shipment_ids:
            return {}
        
        placeholders = ','.join(['%s'] * len(shipment_ids))
        query = f"""
        WITH latest_eta AS (
            SELECT DISTINCT ON (shipment_id)
                shipment_id,
                predicted_eta,
                distance_remaining_km,
                current_speed_kmph,
                confidence,
                computed_at
            FROM eta_history
            WHERE shipment_id IN ({placeholders})
            ORDER BY shipment_id, computed_at DESC
        )
        SELECT * FROM latest_eta;
        """
        
        # Use psycopg2 directly
        conn = psycopg2.connect(DATABASE_URL)
        df = pd.read_sql(query, conn, params=list(shipment_ids))
        conn.close()
        
        # Convert to dictionary for easy lookup
        eta_dict = {}
        for _, row in df.iterrows():
            eta_dict[row['shipment_id']] = {
                'predicted_eta_minutes': None,
                'distance_km': row['distance_remaining_km'],
                'confidence': row['confidence']
            }
            
            # Calculate ETA in minutes if predicted_eta exists
            if pd.notnull(row['predicted_eta']):
                eta_minutes = (row['predicted_eta'] - pd.Timestamp.now()).total_seconds() / 60
                eta_dict[row['shipment_id']]['predicted_eta_minutes'] = max(0, int(eta_minutes))
        
        return eta_dict
    except Exception as e:
        st.warning(f"⚠️ ETA data not available: {e}")
        return {}

def fetch_active_alerts(shipment_ids):
    """Fetch active alerts from database"""
    try:
        if not shipment_ids:
            return {}
        
        placeholders = ','.join(['%s'] * len(shipment_ids))
        query = f"""
        SELECT shipment_id, COUNT(*) as alert_count, 
               MAX(CASE WHEN alert_type = 'critical' THEN 1 ELSE 0 END) as has_critical
        FROM alerts
        WHERE shipment_id IN ({placeholders}) AND is_active = true
        GROUP BY shipment_id;
        """
        
        # Use psycopg2 directly
        conn = psycopg2.connect(DATABASE_URL)
        df = pd.read_sql(query, conn, params=list(shipment_ids))
        conn.close()
        
        alert_dict = {}
        for _, row in df.iterrows():
            alert_dict[row['shipment_id']] = {
                'count': row['alert_count'],
                'has_critical': bool(row['has_critical'])
            }
        
        return alert_dict
    except Exception as e:
        return {}

def fetch_model_predictions(df):
    """Integrate ETA predictions and alerts with telemetry data"""
    if df.empty:
        return df
    
    # Fetch ETA predictions from Pathway pipeline
    shipment_ids = df['shipment_id'].tolist()
    eta_data = fetch_eta_predictions(shipment_ids)
    alert_data = fetch_active_alerts(shipment_ids)
    
    # Helper function to calculate distance using Haversine formula
    def haversine_distance(lat1, lon1, lat2, lon2):
        import math
        R = 6371  # Earth's radius in km
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c
    
    # Merge predictions into dataframe
    predictions = []
    for _, row in df.iterrows():
        sid = row['shipment_id']
        
        # Get ETA prediction
        eta_info = eta_data.get(sid, {})
        predicted_eta = eta_info.get('predicted_eta_minutes', 180)  # Default 3 hours
        confidence = eta_info.get('confidence', 85.0)
        distance_km = eta_info.get('distance_km')
        
        # Calculate distance if not available from ETA history
        if distance_km is None or distance_km == 0:
            try:
                distance_km = haversine_distance(
                    row['lat'], row['lon'],
                    row['dest_lat'], row['dest_lon']
                )
            except:
                distance_km = 0
        
        # Determine alert level based on ETA and speed
        alert_info = alert_data.get(sid, {'count': 0, 'has_critical': False})
        avg_speed = row.get('avg_speed', 60.0)
        
        if alert_info['has_critical'] or predicted_eta > 240:
            alert_level = 'critical'
        elif predicted_eta > 180 or avg_speed < 40:
            alert_level = 'warning'
        else:
            alert_level = 'on_time'
        
        # Mock temperature (in real system, this would come from IoT sensors)
        temperature = -18.5 if alert_level != 'critical' else 4.2
        
        predictions.append({
            **row.to_dict(),
            'predicted_eta': predicted_eta,
            'alert_level': alert_level,
            'temperature': temperature,
            'confidence': confidence,
            'distance_km': distance_km,
            'alert_count': alert_info['count']
        })
    
    result_df = pd.DataFrame(predictions)
    
    # Calculate delay reasons
    def calculate_delay_reason(row):
        if row['alert_level'] == 'on_time':
            return ""
        
        reasons = []
        avg_speed = row.get('avg_speed', 60.0)
        temperature = row.get('temperature', -18.5)
        
        if avg_speed < 50:
            reasons.append("Heavy traffic congestion or roadwork detected.")
        if temperature > -5:
            reasons.append("Mandatory halt required for cold-chain unit inspection.")
        if row['alert_level'] == 'critical' and avg_speed >= 50:
            reasons.append("Unexpected route deviation detected.")
        if row.get('alert_count', 0) > 0:
            reasons.append(f"{row['alert_count']} active system alerts.")
            
        return " ".join(reasons) if reasons else "Minor weather disruptions."

    result_df['delay_reason'] = result_df.apply(calculate_delay_reason, axis=1)
    
    return result_df

def get_dashboard_data():
    raw_df = fetch_live_telemetry()
    if raw_df.empty:
        return raw_df
    final_df = fetch_model_predictions(raw_df)
    return final_df

# ---------------------------------------------------------
# 3. RAG CHATBOT INTEGRATION (MEMBER 4)
# ---------------------------------------------------------
def generate_rag_response(user_query, context_df):
    """Member 4: Groq-powered RAG chatbot integration"""
    try:
        import requests
        
        # Get API key from environment
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            return "⚠️ Groq API key not configured. Please set GROQ_API_KEY in .env file."
        
        # Prepare context from current shipment data
        context = "Current Supply Chain Status:\n"
        if not context_df.empty:
            for _, row in context_df.iterrows():
                context += f"\n- Shipment {row['shipment_id']}: {row['source']} → {row['destination']}"
                context += f"\n  Speed: {row.get('avg_speed', 0):.1f} km/h, Status: {row.get('load_status', 'N/A')}"
                if 'predicted_eta' in row:
                    context += f", ETA: {row['predicted_eta']:.0f} minutes"
                if 'alert_level' in row and row['alert_level'] != 'on_time':
                    context += f", Alert: {row['alert_level']}"
        
        # Query database for additional context
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            
            # Get total telemetry count
            cur.execute("SELECT COUNT(*) FROM telemetry")
            telemetry_count = cur.fetchone()[0]
            
            # Get active alerts
            cur.execute("SELECT COUNT(*) FROM alerts WHERE is_active = true")
            alert_count = cur.fetchone()[0]
            
            context += f"\n\nSystem Stats: {telemetry_count} GPS records, {alert_count} active alerts"
            
            conn.close()
        except:
            pass
        
        # Call Groq API
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "system",
                        "content": f"You are a helpful supply chain logistics assistant. Use this context to answer questions:\n\n{context}"
                    },
                    {
                        "role": "user",
                        "content": user_query
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 500
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"⚠️ API Error: {response.status_code} - {response.text[:200]}"
            
    except Exception as e:
        return f"⚠️ Chatbot error: {str(e)}. Check if GROQ_API_KEY is set correctly."

# ---------------------------------------------------------
# 4. DASHBOARD UI RENDERING (MEMBER 3)
# ---------------------------------------------------------
st_autorefresh(interval=REFRESH_RATE * 1000, key="datarefresh")

st.markdown('<div class="dashboard-header"><h1>🚛 Pathway Supply Chain OS</h1></div>', unsafe_allow_html=True)

df = get_dashboard_data()

# --- MAIN NAVIGATION ---
tab_map, tab_chat = st.tabs(["🗺️ Live Command Center", "💬 AI Logistics Assistant (RAG)"])

# ==========================================
# TAB 1: LIVE MAP & INSPECTOR
# ==========================================
with tab_map:
    # Top KPI Metrics
    c1, c2, c3, c4 = st.columns(4)
    active_count = len(df)
    avg_speed = int(df["avg_speed"].mean()) if not df.empty and "avg_speed" in df else 0
    critical_count = len(df[df["alert_level"]=="critical"]) if not df.empty and "alert_level" in df else 0
    on_time_count = len(df[df["alert_level"]=="on_time"]) if not df.empty and "alert_level" in df else 0
    
    with c1: st.markdown(f'<div class="dashboard-card"><div style="color:var(--text-muted); font-weight:bold; font-size:0.9rem;">ACTIVE SHIPMENTS</div><div style="font-size:2rem; font-weight:900; color:var(--teal-mid);">{active_count}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="dashboard-card"><div style="color:var(--text-muted); font-weight:bold; font-size:0.9rem;">FLEET AVG SPEED</div><div style="font-size:2rem; font-weight:900; color:var(--teal-mid);">{avg_speed} km/h</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="dashboard-card"><div style="color:var(--text-muted); font-weight:bold; font-size:0.9rem;">ON-TIME SHIPMENTS</div><div style="font-size:2rem; font-weight:900; color:var(--teal-mid);">{on_time_count}</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="dashboard-card"><div style="color:var(--danger); font-weight:bold; font-size:0.9rem;">CRITICAL ALERTS</div><div style="font-size:2rem; font-weight:900; color:var(--danger);">{critical_count}</div></div>', unsafe_allow_html=True)
    
    st.write("")
    col_map, col_details = st.columns([2, 1])

    # Live Map Rendering
    with col_map:
        st.markdown("### 🗺️ Live Fleet Tracking")
        if not df.empty and pdk:
            # Route Lines (Colored Teal Light)
            routes = [{"path": [[r['source_lon'], r['source_lat']], [r['dest_lon'], r['dest_lat']]]} for _, r in df.iterrows() if pd.notnull(r.get('source_lon'))]
            path_layer = pdk.Layer("PathLayer", data=routes, get_path="path", get_color=[130, 180, 185, 150], get_width=3)
            
            # Vehicle Dots (Colored Teal Dark)
            vehicle_layer = pdk.Layer("ScatterplotLayer", data=df, get_position='[lon, lat]', get_color=[18, 94, 110, 200], get_radius=25000, pickable=True)
            
            st.pydeck_chart(pdk.Deck(layers=[path_layer, vehicle_layer], initial_view_state=pdk.ViewState(latitude=21.0, longitude=78.0, zoom=3.5), tooltip={"html": "<b>ID: {shipment_id}</b><br>Speed: {avg_speed} km/h"}, map_style='light'), use_container_width=True)
        else:
            st.info("📡 Waiting for GPS data...")
    
    # Smart Inspector (Anomaly UI)
    with col_details:
        st.markdown("### 📦 AI Inspector")
        if not df.empty:
            sid = st.selectbox("Select Shipment ID", df['shipment_id'].unique(), label_visibility="collapsed")
            row = df[df['shipment_id'] == sid].iloc[0]
            
            badge = "badge-critical" if row.get('alert_level') in ['warning', 'critical'] else "badge-ontime"
            temp_color = "var(--danger)" if row.get('temperature', 0) > -5 else "var(--teal-mid)"
            
            # Anomaly & Delay UI Logic
            reason_html = ""
            if row.get('delay_reason'):
                border_color = "var(--danger)" if row.get('alert_level') == 'critical' else "var(--teal-mid)"
                text_color = "var(--danger)" if row.get('alert_level') == 'critical' else "var(--teal-dark)"
                
                reason_html = textwrap.dedent(f"""
                <div class="reason-box" style="border-left: 5px solid {border_color};">
                    <strong style="color:{text_color};">⚠️ ETA Delay Insight:</strong><br>
                    <span style="color:var(--text-muted); font-size: 0.95rem;">{row['delay_reason']}</span>
                </div>
                """).strip()

            # Additional metrics
            confidence_color = "var(--teal-mid)" if row.get('confidence', 0) > 80 else "var(--text-muted)"
            
            card_html = textwrap.dedent(f"""
            <div class="dashboard-card">
                <div style="margin-bottom:1rem;"><small style="color:var(--text-muted) !important;">{row.get('source', 'N/A')} → {row.get('destination', 'N/A')}</small></div>
                <div style="display:flex; justify-content:space-between; margin-bottom:1rem;"><span>Status</span><span class="badge {badge}">{row.get('alert_level', 'N/A').replace('_', ' ')}</span></div>
                <div style="display:flex; justify-content:space-between; margin-bottom:1rem;"><span>Current Speed</span><span style="font-weight:700;">{row.get('avg_speed', 0):.1f} km/h</span></div>
                <div style="display:flex; justify-content:space-between; margin-bottom:1rem;"><span>Distance Left</span><span style="font-weight:700;">{row.get('distance_km', 0):.1f} km</span></div>
                <div style="display:flex; justify-content:space-between; margin-bottom:1rem;"><span>ETA Prediction</span><span style="font-weight:700;">{row.get('predicted_eta', 'N/A')} mins</span></div>
                <div style="display:flex; justify-content:space-between; margin-bottom:1rem;"><span>Confidence</span><span style="font-weight:700; color:{confidence_color} !important;">{row.get('confidence', 0):.1f}%</span></div>
                <div style="display:flex; justify-content:space-between; margin-bottom:1rem;"><span>Cargo Temp</span><span style="font-weight:800; font-size:1.2rem; color:{temp_color} !important;">{row.get('temperature', 'N/A')}°C</span></div>
                <div style="display:flex; justify-content:space-between; margin-bottom:1rem;"><span>Load Status</span><span style="font-weight:700;">{row.get('load_status', 'N/A')}</span></div>
                {reason_html}
            </div>
            """).strip()
            
            st.markdown(card_html, unsafe_allow_html=True)


# ==========================================
# TAB 2: RAG CHATBOT (MEMBER 4)
# ==========================================
with tab_chat:
    st.markdown("### 🤖 Logistics Copilot")
    st.markdown("<small style='color:var(--text-muted) !important;'>Ask questions about supply chain documents, routing policies, or live fleet status.</small>", unsafe_allow_html=True)
    st.write("") # Spacer
    
    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your RAG-powered Logistics Copilot. How can I assist you today?"}]

    # Display Chat History (Removed HTML Wrappers)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input Trigger
    if prompt := st.chat_input("Ask about weather delays, policy documents, or specific trucks..."):
        # Add User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate & Add Bot Response
        with st.chat_message("assistant"):
            with st.spinner("Searching knowledge base..."):
                response = generate_rag_response(prompt, df) 
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})