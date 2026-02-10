"""
Dashboard - Member 3
Placeholder until Member 3 implements the actual dashboard
"""

import streamlit as st
import requests
import os

st.set_page_config(
    page_title="Supply Chain Tracker",
    page_icon="🚚",
    layout="wide"
)

st.title("🚚 Real-Time Supply Chain Tracker")
st.markdown("---")

# Backend API URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend-api:8000")

# Check backend connection
try:
    response = requests.get(f"{BACKEND_URL}/health", timeout=2)
    if response.status_code == 200:
        st.success("✅ Backend API is connected")
    else:
        st.error("❌ Backend API returned error")
except Exception as e:
    st.error(f"❌ Cannot connect to Backend API: {e}")

st.markdown("---")

# Placeholder content
st.header("📋 TODO: Member 3 - Implement Dashboard")

st.markdown("""
### What to build:

1. **Live Map** 🗺️
   - Show vehicle locations in real-time
   - Use folium or plotly for mapping
   - Update every few seconds

2. **Shipment Cards** 📦
   - Display shipment status
   - Show ETA countdown
   - Current location and destination

3. **Alert Panel** 🚨
   - Show active alerts
   - Highlight delays and issues
   - Color-coded by severity

4. **Metrics** 📊
   - Total shipments
   - In-transit count
   - Average ETA
   - Active alerts count

### API Endpoints to Use:
- `GET /api/shipments` - Get all shipments
- `GET /api/shipments/{id}` - Get shipment details
- `GET /api/alerts` - Get all alerts

### Reference:
Check `dashboard/components/` for component examples
""")

# Test API call
st.markdown("---")
st.subheader("🧪 Test API Connection")

if st.button("Fetch Shipments"):
    try:
        response = requests.get(f"{BACKEND_URL}/api/shipments")
        st.json(response.json())
    except Exception as e:
        st.error(f"Error: {e}")

if st.button("Fetch Alerts"):
    try:
        response = requests.get(f"{BACKEND_URL}/api/alerts")
        st.json(response.json())
    except Exception as e:
        st.error(f"Error: {e}")
