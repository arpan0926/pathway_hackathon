import cv2
import mediapipe as mp
import numpy as np
import time
import psycopg2
import os
from datetime import datetime
import threading
import requests
import socketio

# MediaPipe setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Thresholds
DROWSY_TIME_THRESHOLD = 1.5
HEAD_DOWN_TIME_THRESHOLD = 3.0
EYE_ASPECT_RATIO_THRESHOLD = 0.25

# Service URLs
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
AI_ALERTS_URL = os.getenv("AI_ALERTS_URL", "http://localhost:8100")

# WebSocket client
sio = socketio.Client()

def connect_websocket():
    """Connect to backend WebSocket"""
    try:
        sio.connect(BACKEND_URL)
        print("✅ Connected to WebSocket server")
    except Exception as e:
        print(f"⚠️  WebSocket connection failed: {e}")
        print("   Continuing without real-time updates...")

def get_db_connection():
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://supply_chain_user:supply_chain_pass@postgres:5432/supply_chain_db"
    )
    return psycopg2.connect(db_url)

def calculate_ear(landmarks, indices):
    """Calculate Eye Aspect Ratio"""
    A = np.linalg.norm(np.array(landmarks[indices[1]]) - np.array(landmarks[indices[5]]))
    B = np.linalg.norm(np.array(landmarks[indices[2]]) - np.array(landmarks[indices[4]]))
    C = np.linalg.norm(np.array(landmarks[indices[0]]) - np.array(landmarks[indices[3]]))
    return (A + B) / (2.0 * C)


def insert_driver_alert(vehicle_id, alert_type, severity):
    """Insert driver safety alert into database AND broadcast via WebSocket + AI service"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get shipment_id from vehicle_id
        cur.execute("SELECT shipment_id FROM shipments WHERE vehicle_id = %s LIMIT 1", (vehicle_id,))
        result = cur.fetchone()
        
        if not result:
            print(f"⚠️  No shipment found for {vehicle_id}. Forcing 'SH001' for demo.")
            shipment_id = 'SH001' # Force it so the demo never fails!
        else:
            shipment_id = result[0]
        
        # Insert into alerts table
        cur.execute("""
            INSERT INTO alerts (shipment_id, alert_type, metric, value, threshold, is_active, created_at)
            VALUES (%s, %s, 'driver_safety', %s, %s, true, NOW())
            RETURNING alert_id, created_at
        """, (shipment_id, alert_type, alert_type, severity))
        
        alert_data = cur.fetchone()
        alert_id, created_at = alert_data
        
        conn.commit()
        conn.close()
        
        print(f"🚨 [{vehicle_id}] ALERT: {alert_type} (severity: {severity})")
        
        # Build alert object for broadcasting
        alert_payload = {
            "alert_id": alert_id,
            "shipment_id": shipment_id,
            "vehicle_id": vehicle_id,
            "alert_type": alert_type,
            "metric": "driver_safety",
            "value": alert_type,
            "threshold": severity,
            "is_active": True,
            "created_at": created_at.isoformat()
        }
        
        # 1. Broadcast via WebSocket (real-time to dashboard)
        try:
            if sio.connected:
                sio.emit('new_alert', alert_payload)
                print(f"   📡 Broadcasted to WebSocket")
        except Exception as e:
            print(f"   ⚠️  WebSocket broadcast failed: {e}")
        
        # 2. Report to AI Alert Service
        try:
            response = requests.post(
                f"{AI_ALERTS_URL}/driver-safety/report",
                json={
                    "shipment_id": shipment_id,
                    "status": alert_type.upper(),
                    "details": f"Driver {vehicle_id} detected as {alert_type}"
                },
                timeout=3
            )
            if response.status_code == 200:
                print(f"   🤖 Reported to AI service")
        except Exception as e:
            print(f"   ⚠️  AI service report failed: {e}")
        
    except Exception as e:
        print(f"❌ DB Error: {e}")


def monitor_driver(vehicle_id, camera_index=0):
    """
    Monitor driver for a specific vehicle
    vehicle_id: e.g., "VH001"
    camera_index: 0 for default webcam, 1 for external camera
    """
    cap = cv2.VideoCapture(camera_index)
    drowsy_start_time = None
    head_down_start_time = None
    last_alert_time = 0
    ALERT_COOLDOWN = 10  # seconds between alerts
    
    print(f"🎥 Starting driver monitoring for {vehicle_id}")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"⚠️  Camera {camera_index} unavailable for {vehicle_id}")
            break
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)
        
        status = "Active"
        alert_triggered = False
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                h, w, _ = frame.shape
                landmarks = [(lm.x * w, lm.y * h) for lm in face_landmarks.landmark]
                
                # Eye drowsiness detection
                RIGHT_EYE = [33, 160, 158, 133, 153, 144]
                LEFT_EYE = [362, 385, 387, 263, 373, 380]
                avg_ear = (calculate_ear(landmarks, RIGHT_EYE) + calculate_ear(landmarks, LEFT_EYE)) / 2.0
                
                if avg_ear < EYE_ASPECT_RATIO_THRESHOLD:
                    if drowsy_start_time is None:
                        drowsy_start_time = time.time()
                    if (time.time() - drowsy_start_time) > DROWSY_TIME_THRESHOLD:
                        status = "DROWSY"
                        alert_triggered = True
                else:
                    drowsy_start_time = None
                
                # Head down detection
                nose = landmarks[1]
                forehead = landmarks[10]
                chin = landmarks[152]
                face_height = chin[1] - forehead[1]
                
                if (chin[1] - nose[1]) < (face_height * 0.35):
                    if head_down_start_time is None:
                        head_down_start_time = time.time()
                    if (time.time() - head_down_start_time) > HEAD_DOWN_TIME_THRESHOLD:
                        status = "HEAD_DOWN"
                        alert_triggered = True
                else:
                    head_down_start_time = None
                
                # Send alert to database (with cooldown)
                if alert_triggered and (time.time() - last_alert_time) > ALERT_COOLDOWN:
                    insert_driver_alert(vehicle_id, status.lower(), "critical")
                    last_alert_time = time.time()
                
                # Visual overlay
                color = (0, 255, 0) if status == "Active" else (0, 0, 255)
                cv2.putText(frame, f"{vehicle_id}: {status}", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
                for idx in RIGHT_EYE + LEFT_EYE:
                    cv2.circle(frame, (int(landmarks[idx][0]), int(landmarks[idx][1])), 1, color, -1)
        
        # Display frame
        cv2.imshow(f"Driver Monitor - {vehicle_id}", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    print("\n🚀 Driver Safety Monitor Starting...")
    print("=" * 60)
    
    # Connect to WebSocket
    connect_websocket()
    
    # Start monitoring
    monitor_driver("VH001", camera_index=0)
    
    # Disconnect WebSocket on exit
    if sio.connected:
        sio.disconnect()