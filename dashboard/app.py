import streamlit as st
import pandas as pd
import os
import psycopg2
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

try:
    import pydeck as pdk
except ImportError:
    pdk = None
from streamlit_autorefresh import st_autorefresh

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Supply Chain Intelligence Platform", 
    page_icon="🚛", 
    layout="wide",
    initial_sidebar_state="expanded"
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://supply_chain_user:supply_chain_pass@postgres:5432/supply_chain_db")
REFRESH_RATE = 10

# ---------------------------------------------------------
# PROFESSIONAL STYLING
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    :root {
        --primary: #0066FF;
        --success: #00C48C;
        --warning: #FFA500;
        --danger: #FF4757;
        --info: #17A2B8;
        
        --bg-dark: #0A0E27;
        --bg-darker: #050814;
        --surface: #141B3D;
        --surface-light: #1E2749;
        
        --text-primary: #FFFFFF;
        --text-secondary: #A0AEC0;
        --text-muted: #718096;
        
        --border: #2D3748;
        --shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--bg-darker) 0%, var(--bg-dark) 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: var(--surface) !important;
        border-right: 1px solid var(--border);
    }
    
    [data-testid="stSidebar"] h1, h2, h3 {
        color: var(--text-primary) !important;
    }
    
    /* Header */
    .platform-header {
        background: linear-gradient(135deg, #0066FF 0%, #00C48C 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: var(--shadow);
    }
    
    .platform-title {
        font-size: 1.75rem;
        font-weight: 800;
        color: white !important;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .platform-subtitle {
        color: rgba(255, 255, 255, 0.85) !important;
        font-size: 0.875rem;
        margin-top: 0.25rem;
    }
    
    /* Metrics Cards */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.25rem;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--primary);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover::before {
        transform: scaleX(1);
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow);
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: var(--text-muted) !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: var(--text-primary) !important;
        line-height: 1;
    }
    
    .metric-delta {
        font-size: 0.75rem;
        margin-top: 0.5rem;
        font-weight: 600;
    }
    
    /* Panel Styles */
    .panel {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
    }
    
    .panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--border);
    }
    
    .panel-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text-primary) !important;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .panel-actions {
        display: flex;
        gap: 0.5rem;
    }
    
    /* Status Badge */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.375rem 0.875rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    
    .status-success { background: rgba(0, 196, 140, 0.15); color: var(--success) !important; border: 1px solid rgba(0, 196, 140, 0.3); }
    .status-warning { background: rgba(255, 165, 0, 0.15); color: var(--warning) !important; border: 1px solid rgba(255, 165, 0, 0.3); }
    .status-danger { background: rgba(255, 71, 87, 0.15); color: var(--danger) !important; border: 1px solid rgba(255, 71, 87, 0.3); }
    .status-info { background: rgba(23, 162, 184, 0.15); color: var(--info) !important; border: 1px solid rgba(23, 162, 184, 0.3); }
    
    /* Table Styles */
    .data-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
    }
    
    .data-table th {
        background: var(--surface-light);
        color: var(--text-secondary) !important;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.875rem 1rem;
        font-weight: 600;
        border-bottom: 2px solid var(--border);
        text-align: left;
    }
    
    .data-table td {
        padding: 1rem;
        border-bottom: 1px solid var(--border);
        color: var(--text-primary) !important;
        font-size: 0.875rem;
    }
    
    .data-table tr:hover {
        background: var(--surface-light);
        cursor: pointer;
    }
    
    /* Filter Pills */
    .filter-chip {
        display: inline-block;
        padding: 0.5rem 1rem;
        background: var(--surface-light);
        border: 1px solid var(--border);
        border-radius: 20px;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 0.875rem;
        color: var(--text-secondary) !important;
    }
    
    .filter-chip:hover {
        background: var(--primary);
        color: white !important;
        border-color: var(--primary);
    }
    
    .filter-chip.active {
        background: var(--primary);
        color: white !important;
        border-color: var(--primary);
    }
    
    /* Chat Interface */
    .chat-panel {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        height: calc(100vh - 200px);
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    
    .chat-header {
        background: var(--surface-light);
        padding: 1.25rem;
        border-bottom: 1px solid var(--border);
    }
    
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 1.5rem;
    }
    
    .chat-input-area {
        padding: 1.25rem;
        border-top: 1px solid var(--border);
        background: var(--surface-light);
    }
    
    /* Quick Actions */
    .quick-action {
        background: var(--surface-light);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.875rem 1.25rem;
        margin-bottom: 0.75rem;
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 0.875rem;
        color: var(--text-primary) !important;
    }
    
    .quick-action:hover {
        background: var(--primary);
        border-color: var(--primary);
        transform: translateX(4px);
    }
    
    /* Progress Bars */
    .progress-bar {
        height: 8px;
        background: var(--surface-light);
        border-radius: 4px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    
    .progress-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: var(--surface);
        padding: 0.5rem;
        border-radius: 12px;
        border: 1px solid var(--border);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: var(--text-secondary) !important;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--surface-light);
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary) !important;
        color: white !important;
    }
    
    /* Streamlit Overrides */
    .stSelectbox > div > div {
        background: var(--surface-light) !important;
        border-color: var(--border) !important;
        color: var(--text-primary) !important;
    }
    
    .stButton > button {
        background: var(--primary);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.625rem 1.25rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: #0052CC;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 102, 255, 0.3);
    }
    
    /* Alerts */
    .alert-item {
        background: var(--surface-light);
        border-left: 4px solid var(--danger);
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.75rem;
    }
    
    .alert-item.warning {
        border-left-color: var(--warning);
    }
    
    .alert-time {
        font-size: 0.75rem;
        color: var(--text-muted) !important;
        margin-bottom: 0.25rem;
    }
    
    .alert-message {
        color: var(--text-primary) !important;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    /* Map Legend */
    .map-legend {
        background: rgba(20, 27, 61, 0.95);
        backdrop-filter: blur(10px);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 1rem;
        position: absolute;
        top: 1rem;
        right: 1rem;
        z-index: 1000;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.5rem;
        font-size: 0.875rem;
        color: var(--text-primary) !important;
    }
    
    .legend-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-dark);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# DATA FUNCTIONS
# ---------------------------------------------------------
@st.cache_data(ttl=10)
def fetch_live_telemetry():
    """Fetch real-time telemetry data"""
    try:
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
            return pd.DataFrame()
        
        df['lat'] = df['lat'].fillna(df['source_lat'])
        df['lon'] = df['lon'].fillna(df['source_lon'])
        df['avg_speed'] = df['avg_speed'].fillna(60.0)
        df['load_status'] = df['load_status'].fillna('LOADED')
        
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

def fetch_eta_predictions(shipment_ids):
    """Fetch ETA predictions"""
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
                confidence,
                computed_at
            FROM eta_history
            WHERE shipment_id IN ({placeholders})
            ORDER BY shipment_id, computed_at DESC
        )
        SELECT * FROM latest_eta;
        """
        
        conn = psycopg2.connect(DATABASE_URL)
        df = pd.read_sql(query, conn, params=list(shipment_ids))
        conn.close()
        
        eta_dict = {}
        for _, row in df.iterrows():
            eta_dict[row['shipment_id']] = {
                'predicted_eta_minutes': None,
                'distance_km': row['distance_remaining_km'],
                'confidence': row['confidence']
            }
            
            if pd.notnull(row['predicted_eta']):
                eta_minutes = (row['predicted_eta'] - pd.Timestamp.now()).total_seconds() / 60
                eta_dict[row['shipment_id']]['predicted_eta_minutes'] = max(0, int(eta_minutes))
        
        return eta_dict
    except:
        return {}

def fetch_active_alerts(shipment_ids):
    """Fetch active alerts"""
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
    except:
        return {}

def enrich_telemetry_data(df):
    """Add predictions and analytics"""
    if df.empty:
        return df
    
    import math
    
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        return R * c
    
    shipment_ids = df['shipment_id'].tolist()
    eta_data = fetch_eta_predictions(shipment_ids)
    alert_data = fetch_active_alerts(shipment_ids)
    
    enriched = []
    for _, row in df.iterrows():
        sid = row['shipment_id']
        eta_info = eta_data.get(sid, {})
        predicted_eta = eta_info.get('predicted_eta_minutes', 180)
        confidence = eta_info.get('confidence', 85.0)
        distance_km = eta_info.get('distance_km')
        
        if distance_km is None or distance_km == 0:
            try:
                distance_km = haversine(row['lat'], row['lon'], row['dest_lat'], row['dest_lon'])
            except:
                distance_km = 0
        
        alert_info = alert_data.get(sid, {'count': 0, 'has_critical': False})
        avg_speed = row.get('avg_speed', 60.0)
        
        if alert_info['has_critical'] or predicted_eta > 240:
            alert_level = 'critical'
        elif predicted_eta > 180 or avg_speed < 40:
            alert_level = 'warning'
        else:
            alert_level = 'on_time'
        
        temperature = -18.5 if alert_level != 'critical' else 4.2
        
        enriched.append({
            **row.to_dict(),
            'predicted_eta': predicted_eta,
            'alert_level': alert_level,
            'temperature': temperature,
            'confidence': confidence,
            'distance_km': distance_km,
            'alert_count': alert_info['count'],
            'progress': max(0, min(100, 100 - (distance_km / (distance_km + 500) * 100)))
        })
    
    return pd.DataFrame(enriched)

def generate_rag_response(user_query, context_df):
    """RAG chatbot"""
    try:
        import requests
        
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            return "⚠️ Groq API key not configured."
        
        context = "Supply Chain Status:\n"
        if not context_df.empty:
            for _, row in context_df.iterrows():
                context += f"\n- Shipment {row['shipment_id']}: {row['source']} → {row['destination']}"
                context += f"\n  Speed: {row.get('avg_speed', 0):.1f} km/h, ETA: {row.get('predicted_eta', 0):.0f} min"
                if row.get('alert_level') != 'on_time':
                    context += f", Status: {row['alert_level']}"
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": f"You are a supply chain analyst. Use this data:\n\n{context}"},
                    {"role": "user", "content": user_query}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"⚠️ API Error: {response.status_code}"
            
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# ---------------------------------------------------------
# UI COMPONENTS
# ---------------------------------------------------------
def render_metric_card(label, value, delta=None, delta_positive=True, color="primary"):
    """Render a metric card"""
    delta_html = ""
    if delta:
        delta_color = "var(--success)" if delta_positive else "var(--danger)"
        delta_icon = "↑" if delta_positive else "↓"
        delta_html = f'<div class="metric-delta" style="color: {delta_color} !important;">{delta_icon} {delta}</div>'
    
    color_map = {
        "primary": "var(--primary)",
        "success": "var(--success)",
        "warning": "var(--warning)",
        "danger": "var(--danger)"
    }
    
    st.markdown(f'''
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color: {color_map.get(color, 'var(--primary)')} !important;">{value}</div>
        {delta_html}
    </div>
    ''', unsafe_allow_html=True)

# ---------------------------------------------------------
# MAIN APPLICATION
# ---------------------------------------------------------
st_autorefresh(interval=REFRESH_RATE * 1000, key="refresh")

# Sidebar
with st.sidebar:
    st.markdown('<div class="panel-title">⚙️ Control Panel</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### 📊 View Mode")
    view_mode = st.radio("", ["Overview", "Analytics", "Operations"], label_visibility="collapsed")
    
    st.markdown("### 🔍 Filters")
    status_filter = st.multiselect(
        "Status",
        ["on_time", "warning", "critical"],
        default=["on_time", "warning", "critical"]
    )
    
    st.markdown("### 📍 Routes")
    show_all_routes = st.checkbox("Show all routes", value=True)
    
    st.markdown("---")
    st.markdown("### 🚨 Quick Alerts")
    
    df_temp = fetch_live_telemetry()
    if not df_temp.empty:
        df_enriched = enrich_telemetry_data(df_temp)
        critical = len(df_enriched[df_enriched['alert_level'] == 'critical'])
        warning = len(df_enriched[df_enriched['alert_level'] == 'warning'])
        
        if critical > 0:
            st.markdown(f'''
            <div class="alert-item">
                <div class="alert-time">{datetime.now().strftime("%H:%M")}</div>
                <div class="alert-message">🔴 {critical} critical shipment(s)</div>
            </div>
            ''', unsafe_allow_html=True)
        
        if warning > 0:
            st.markdown(f'''
            <div class="alert-item warning">
                <div class="alert-time">{datetime.now().strftime("%H:%M")}</div>
                <div class="alert-message">⚠️ {warning} delayed shipment(s)</div>
            </div>
            ''', unsafe_allow_html=True)

# Header
st.markdown('''
<div class="platform-header">
    <div class="platform-title">🚛 Supply Chain Intelligence Platform</div>
    <div class="platform-subtitle">Real-time monitoring • Predictive analytics • AI-powered insights</div>
</div>
''', unsafe_allow_html=True)

# Fetch data
df = fetch_live_telemetry()
if not df.empty:
    df = enrich_telemetry_data(df)
    
    # Filter by status
    if status_filter:
        df = df[df['alert_level'].isin(status_filter)]

# Main Content
if view_mode == "Overview":
    # KPI Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total = len(df) if not df.empty else 0
        render_metric_card("Total Shipments", total, "+3 today", True, "primary")
    
    with col2:
        on_time = len(df[df['alert_level'] == 'on_time']) if not df.empty else 0
        render_metric_card("On Time", on_time, "95%", True, "success")
    
    with col3:
        avg_speed = int(df['avg_speed'].mean()) if not df.empty else 0
        render_metric_card("Avg Speed", f"{avg_speed} km/h", "+5 km/h", True, "primary")
    
    with col4:
        delayed = len(df[df['alert_level'] == 'warning']) if not df.empty else 0
        render_metric_card("Delayed", delayed, "-2", True, "warning")
    
    with col5:
        critical = len(df[df['alert_level'] == 'critical']) if not df.empty else 0
        render_metric_card("Critical", critical, "Attention", False, "danger")
    
    # Main Layout
    map_col, data_col = st.columns([2, 1])
    
    with map_col:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">🗺️ Live Fleet Map</div>', unsafe_allow_html=True)
        
        if not df.empty and pdk:
            color_map = {
                'on_time': [0, 196, 140, 200],
                'warning': [255, 165, 0, 200],
                'critical': [255, 71, 87, 200]
            }
            
            # Routes
            routes = []
            for _, r in df.iterrows():
                if pd.notnull(r.get('source_lon')):
                    routes.append({
                        'path': [[r['source_lon'], r['source_lat']], [r['dest_lon'], r['dest_lat']]],
                        'color': color_map.get(r.get('alert_level', 'on_time'), [130, 180, 185, 150]),
                        'width': 5 if r.get('alert_level') == 'critical' else 3
                    })
            
            path_layer = pdk.Layer(
                "PathLayer",
                data=routes,
                get_path="path",
                get_color="color",
                get_width="width",
                width_scale=1000,
                width_min_pixels=2
            )
            
            # Vehicles
            vehicles = df.copy()
            vehicles['color'] = vehicles['alert_level'].map(color_map)
            vehicles['radius'] = vehicles['alert_level'].apply(
                lambda x: 35000 if x == 'critical' else 28000
            )
            
            vehicle_layer = pdk.Layer(
                "ScatterplotLayer",
                data=vehicles,
                get_position='[lon, lat]',
                get_color='color',
                get_radius='radius',
                pickable=True,
                opacity=0.9
            )
            
            st.pydeck_chart(
                pdk.Deck(
                    layers=[path_layer, vehicle_layer],
                    initial_view_state=pdk.ViewState(
                        latitude=21.0,
                        longitude=78.0,
                        zoom=3.5,
                        pitch=0
                    ),
                    tooltip={
                        "html": "<b>{shipment_id}</b><br>{source} → {destination}<br>Speed: {avg_speed} km/h<br>ETA: {predicted_eta} min",
                        "style": {
                            "backgroundColor": "#141B3D",
                            "color": "white",
                            "border": "1px solid #2D3748",
                            "borderRadius": "8px",
                            "padding": "12px"
                        }
                    },
                    map_style='mapbox://styles/mapbox/dark-v10'
                ),
                use_container_width=True
            )
        else:
            st.info("📡 Waiting for GPS data...")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with data_col:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">📋 Active Shipments</div>', unsafe_allow_html=True)
        
        if not df.empty:
            for _, row in df.head(8).iterrows():
                status_class = f"status-{row['alert_level'].replace('_', '-')}" if row['alert_level'] != 'on_time' else "status-success"
                progress = row.get('progress', 50)
                
                st.markdown(f'''
                <div style="background: var(--surface-light); padding: 1rem; border-radius: 8px; margin-bottom: 0.75rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <span style="font-weight: 700; color: var(--text-primary) !important;">{row['shipment_id']}</span>
                        <span class="status-pill {status_class}">{row['alert_level'].replace('_', ' ').title()}</span>
                    </div>
                    <div style="font-size: 0.8125rem; color: var(--text-secondary) !important; margin-bottom: 0.5rem;">
                        📍 {row['source']} → {row['destination']}
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted) !important; margin-bottom: 0.5rem;">
                        <span>ETA: {int(row['predicted_eta'])} min</span>
                        <span>{row['avg_speed']:.0f} km/h</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {progress}%; background: {'var(--success)' if row['alert_level'] == 'on_time' else 'var(--warning)' if row['alert_level'] == 'warning' else 'var(--danger)'};"></div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

elif view_mode == "Analytics":
    # Analytics View
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">📊 Performance Metrics</div>', unsafe_allow_html=True)
        
        if not df.empty:
            # Speed Distribution
            fig = px.histogram(
                df,
                x='avg_speed',
                nbins=20,
                title="Speed Distribution",
                labels={'avg_speed': 'Speed (km/h)'},
                color_discrete_sequence=['#0066FF']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#A0AEC0'),
                title_font=dict(size=14, color='#FFFFFF'),
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">🎯 Status Overview</div>', unsafe_allow_html=True)
        
        if not df.empty:
            status_counts = df['alert_level'].value_counts()
            fig = go.Figure(data=[go.Pie(
                labels=status_counts.index,
                values=status_counts.values,
                marker=dict(colors=['#00C48C', '#FFA500', '#FF4757']),
                hole=0.5
            )])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#A0AEC0'),
                height=300,
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed Table
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">📋 Shipment Details</div>', unsafe_allow_html=True)
    
    if not df.empty:
        display_df = df[['shipment_id', 'source', 'destination', 'avg_speed', 'predicted_eta', 'distance_km', 'alert_level', 'confidence']].copy()
        display_df.columns = ['ID', 'Origin', 'Destination', 'Speed (km/h)', 'ETA (min)', 'Distance (km)', 'Status', 'Confidence (%)']
        st.dataframe(display_df, use_container_width=True, height=400)
    
    st.markdown('</div>', unsafe_allow_html=True)

else:  # Operations view with AI Assistant
    chat_col, ops_col = st.columns([1.5, 1])
    
    with chat_col:
        st.markdown('<div class="chat-panel">', unsafe_allow_html=True)
        st.markdown('''
        <div class="chat-header">
            <div class="panel-title">🤖 AI Operations Assistant</div>
            <div style="font-size: 0.875rem; color: var(--text-secondary) !important; margin-top: 0.5rem;">
                Ask me anything about fleet operations, delays, or logistics
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
        
        if "messages" not in st.session_state:
            st.session_state.messages = [{
                "role": "assistant",
                "content": "👋 Hello! I'm your AI Operations Assistant. I can help you analyze fleet performance, identify delays, and provide operational insights. What would you like to know?"
            }]
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if prompt := st.chat_input("Ask about your fleet operations..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    response = generate_rag_response(prompt, df)
                    st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with ops_col:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">⚡ Quick Actions</div>', unsafe_allow_html=True)
        
        if st.button("📊 Fleet Status Summary", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Give me a complete fleet status summary"})
            st.rerun()
        
        if st.button("⚠️ Show Critical Issues", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "What are the critical issues right now?"})
            st.rerun()
        
        if st.button("📈 Performance Analysis", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Analyze overall fleet performance"})
            st.rerun()
        
        if st.button("🚨 Delayed Shipments", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": "Show me all delayed shipments"})
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Recent Alerts
        st.markdown('<div class="panel" style="margin-top: 1.5rem;">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">🚨 Recent Alerts</div>', unsafe_allow_html=True)
        
        if not df.empty:
            critical_shipments = df[df['alert_level'] == 'critical']
            for _, row in critical_shipments.head(5).iterrows():
                st.markdown(f'''
                <div class="alert-item">
                    <div class="alert-time">{datetime.now().strftime("%H:%M:%S")}</div>
                    <div class="alert-message">
                        <b>{row['shipment_id']}</b> - Delayed by {int(row['predicted_eta'] - 180)} min
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)