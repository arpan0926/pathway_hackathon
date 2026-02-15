import streamlit as st
import pandas as pd
import os
import random
import time
import textwrap

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
def generate_mock_data():
    mock_shipments = [
        {"id": "SH-MUM-DEL", "src": "Mumbai", "dst": "Delhi", "slat": 19.076, "slon": 72.877, "dlat": 28.704, "dlon": 77.102, "clat": 23.5, "clon": 74.5},
        {"id": "SH-BLR-CHN", "src": "Bangalore", "dst": "Chennai", "slat": 12.971, "slon": 77.594, "dlat": 13.082, "dlon": 80.270, "clat": 13.0, "clon": 79.0},
        {"id": "SH-HYD-PUN", "src": "Hyderabad", "dst": "Pune", "slat": 17.385, "slon": 78.486, "dlat": 18.520, "dlon": 73.856, "clat": 17.9, "clon": 76.0},
        {"id": "SH-KOL-PAT", "src": "Kolkata", "dst": "Patna", "slat": 22.572, "slon": 88.363, "dlat": 25.594, "dlon": 85.137, "clat": 24.0, "clon": 86.5}
    ]
    
    data = []
    for s in mock_shipments:
        data.append({
            "shipment_id": s["id"], "lat": s["clat"], "lon": s["clon"], 
            "source": s["src"], "destination": s["dst"],
            "source_lat": s["slat"], "source_lon": s["slon"], "dest_lat": s["dlat"], "dest_lon": s["dlon"],
            "avg_speed": random.randint(45, 75), "load_status": random.choice(["LOADED", "PARTIAL"])
        })
    return pd.DataFrame(data)

def fetch_live_telemetry():
    """Member 1: Connect your Pathway pipeline output here."""
    try:
        # Use SQLAlchemy connection string directly with pandas
        query = """
        SELECT s.shipment_id, s.source, s.destination, s.source_lat, s.source_lon, s.dest_lat, s.dest_lon,
               COALESCE(t.lat, s.source_lat) as lat, 
               COALESCE(t.lon, s.source_lon) as lon, 
               COALESCE(t.speed_kmph, 60.0) AS avg_speed, 
               COALESCE(t.load_status, 'LOADED') as load_status
        FROM shipments s
        LEFT JOIN telemetry t ON s.shipment_id = t.shipment_id
        WHERE t.ts = (SELECT MAX(ts) FROM telemetry t2 WHERE t2.shipment_id = s.shipment_id) OR t.ts IS NULL;
        """
        df = pd.read_sql(query, DATABASE_URL)
        return df if not df.empty else generate_mock_data()
    except Exception as e:
        st.warning(f"⚠️ Database connection failed: {e}. Using mock data for demo.")
        return generate_mock_data()

def fetch_model_predictions(df):
    """Member 2: Merge your ETA and Anomaly detection logic here."""
    if df.empty: return df
    
    df['predicted_eta'] = [random.randint(45, 300) for _ in range(len(df))]
    df['alert_level'] = [random.choice(['on_time', 'warning', 'critical']) for _ in range(len(df))]
    df['temperature'] = [-18.5 if a != 'critical' else 4.2 for a in df['alert_level']]
    
    # NEW: Logic to determine the probable cause of an ETA delay
    def calculate_delay_reason(row):
        if row['alert_level'] == 'on_time':
            return ""
        
        reasons = []
<<<<<<< HEAD
        # Handle None values safely
        avg_speed = row.get('avg_speed') or 60.0
        temperature = row.get('temperature') or -18.5
        
        if avg_speed < 50:
            reasons.append("Heavy traffic congestion or roadwork detected.")
        if temperature > -5:
            reasons.append("Mandatory halt required for cold-chain unit inspection.")
        if row['alert_level'] == 'critical' and avg_speed >= 50:
=======
        if row['avg_speed'] < 50:
            reasons.append("Heavy traffic congestion or roadwork detected.")
        if row['temperature'] > -5:
            reasons.append("Mandatory halt required for cold-chain unit inspection.")
        if row['alert_level'] == 'critical' and row['avg_speed'] >= 50:
>>>>>>> 4df3918a46fbb2b3630051c4003cf86120309288
            reasons.append("Unexpected route deviation (+14 km) detected.")
            
        return " ".join(reasons) if reasons else "Minor weather disruptions."

    df['delay_reason'] = df.apply(calculate_delay_reason, axis=1)
    
    return df

def get_dashboard_data():
    raw_df = fetch_live_telemetry()
    final_df = fetch_model_predictions(raw_df)
    return final_df

# ---------------------------------------------------------
# 3. RAG CHATBOT INTEGRATION (MEMBER 4)
# ---------------------------------------------------------
def generate_rag_response(user_query, context_df):
    """Member 4: Plug your LangChain/LlamaIndex RAG code here."""
    time.sleep(1) 
    return f"Based on our supply chain database, here is the answer to: '{user_query}'. All vehicle telemetry is nominal."

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
    
    with c1: st.markdown(f'<div class="dashboard-card"><div style="color:var(--text-muted); font-weight:bold; font-size:0.9rem;">ACTIVE SHIPMENTS</div><div style="font-size:2rem; font-weight:900; color:var(--teal-mid);">{active_count}</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="dashboard-card"><div style="color:var(--text-muted); font-weight:bold; font-size:0.9rem;">FLEET AVG SPEED</div><div style="font-size:2rem; font-weight:900; color:var(--teal-mid);">{avg_speed} km/h</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="dashboard-card"><div style="color:var(--text-muted); font-weight:bold; font-size:0.9rem;">NETWORK STATUS</div><div style="font-size:2rem; font-weight:900; color:var(--teal-mid);">Optimal</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="dashboard-card"><div style="color:var(--danger); font-weight:bold; font-size:0.9rem;">CRITICAL ANOMALIES</div><div style="font-size:2rem; font-weight:900; color:var(--danger);">{critical_count}</div></div>', unsafe_allow_html=True)
    
    st.write("")
    col_map, col_details = st.columns([2, 1])

    # Live Map Rendering (Removed HTML Wrappers to fix alignment)
    with col_map:
        if not df.empty and pdk:
            # Route Lines (Colored Teal Light)
            routes = [{"path": [[r['source_lon'], r['source_lat']], [r['dest_lon'], r['dest_lat']]]} for _, r in df.iterrows() if pd.notnull(r.get('source_lon'))]
            path_layer = pdk.Layer("PathLayer", data=routes, get_path="path", get_color=[130, 180, 185, 150], get_width=3)
            
            # Vehicle Dots (Colored Teal Dark)
            vehicle_layer = pdk.Layer("ScatterplotLayer", data=df, get_position='[lon, lat]', get_color=[18, 94, 110, 200], get_radius=25000, pickable=True)
            
            st.pydeck_chart(pdk.Deck(layers=[path_layer, vehicle_layer], initial_view_state=pdk.ViewState(latitude=21.0, longitude=78.0, zoom=3.5), tooltip={"html": "<b>ID: {shipment_id}</b><br>Speed: {avg_speed} km/h"}, map_style='light'), use_container_width=True)
# Smart Inspector (Anomaly UI)
    with col_details:
        st.markdown("### 📦 AI Inspector")
        if not df.empty:
            sid = st.selectbox("Select Shipment ID", df['shipment_id'].unique(), label_visibility="collapsed")
            row = df[df['shipment_id'] == sid].iloc[0]
            
            badge = "badge-critical" if row.get('alert_level') in ['warning', 'critical'] else "badge-ontime"
            temp_color = "var(--danger)" if row.get('temperature', 0) > -5 else "var(--teal-mid)"
            
            # NEW: Anomaly & Delay UI Logic
            reason_html = ""
            if row.get('delay_reason'):
                # Changes color to red if critical, teal/orange if just a warning
                border_color = "var(--danger)" if row.get('alert_level') == 'critical' else "var(--teal-mid)"
                text_color = "var(--danger)" if row.get('alert_level') == 'critical' else "var(--teal-dark)"
                
                reason_html = textwrap.dedent(f"""
                <div class="reason-box" style="border-left: 5px solid {border_color};">
                    <strong style="color:{text_color};">⚠️ ETA Delay Insight:</strong><br>
                    <span style="color:var(--text-muted); font-size: 0.95rem;">{row['delay_reason']}</span>
                </div>
                """).strip()

            card_html = textwrap.dedent(f"""
            <div class="dashboard-card">
                <div style="margin-bottom:1rem;"><small style="color:var(--text-muted) !important;">{row.get('source', 'N/A')} → {row.get('destination', 'N/A')}</small></div>
                <div style="display:flex; justify-content:space-between; margin-bottom:1rem;"><span>Status</span><span class="badge {badge}">{row.get('alert_level', 'N/A').replace('_', ' ')}</span></div>
                <div style="display:flex; justify-content:space-between; margin-bottom:1rem;"><span>Cargo Temp</span><span style="font-weight:800; font-size:1.2rem; color:{temp_color} !important;">{row.get('temperature', 'N/A')}°C</span></div>
                <div style="display:flex; justify-content:space-between; margin-bottom:1rem;"><span>ETA Prediction</span><span style="font-weight:700;">{row.get('predicted_eta', 'N/A')} mins</span></div>
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