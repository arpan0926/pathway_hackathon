import cv2
import mediapipe as mp
import numpy as np
import time
import subprocess

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5)

DROWSY_TIME_THRESHOLD = 1.5
EYE_ASPECT_RATIO_THRESHOLD = 0.25

def calculate_ear(landmarks, indices):
    A = np.linalg.norm(np.array(landmarks[indices[1]]) - np.array(landmarks[indices[5]]))
    B = np.linalg.norm(np.array(landmarks[indices[2]]) - np.array(landmarks[indices[4]]))
    C = np.linalg.norm(np.array(landmarks[indices[0]]) - np.array(landmarks[indices[3]]))
    return (A + B) / (2.0 * C)

def insert_alert():
    """Insert alert directly via docker exec - no Python DB connection needed!"""
    cmd = [
        'docker', 'exec', 'pathway_hackathon-postgres-1', 
        'psql', '-U', 'supply_chain_user', '-d', 'supply_chain_db',
        '-c', "INSERT INTO alerts (shipment_id, alert_type, metric, value, threshold, is_active, created_at) VALUES ('SH003', 'drowsy', 'driver_safety', 'drowsy', 'critical', true, NOW());"
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print("🚨 DROWSY ALERT INSERTED TO DATABASE!")
    except Exception as e:
        print(f"❌ Alert insert failed: {e}")

cap = cv2.VideoCapture(0)
drowsy_start_time = None
last_alert_time = 0

print("\n" + "="*60)
print("🎥 DRIVER SAFETY WEBCAM DEMO")
print("="*60)
print("✓ Close your eyes for 2 seconds to trigger drowsy alert")
print("✓ Alert will appear on dashboard automatically")
print("✓ Press 'q' to quit\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(frame_rgb)
    
    status = "ACTIVE"
    color = (0, 255, 0)
    
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            h, w, _ = frame.shape
            landmarks = [(lm.x * w, lm.y * h) for lm in face_landmarks.landmark]
            
            RIGHT_EYE = [33, 160, 158, 133, 153, 144]
            LEFT_EYE = [362, 385, 387, 263, 373, 380]
            avg_ear = (calculate_ear(landmarks, RIGHT_EYE) + calculate_ear(landmarks, LEFT_EYE)) / 2.0
            
            if avg_ear < EYE_ASPECT_RATIO_THRESHOLD:
                if drowsy_start_time is None:
                    drowsy_start_time = time.time()
                    print("👁️  Eyes closing detected...")
                
                elapsed = time.time() - drowsy_start_time
                if elapsed > DROWSY_TIME_THRESHOLD:
                    status = "⚠️ DROWSY DETECTED"
                    color = (0, 0, 255)
                    
                    # Insert alert (max once per 10 seconds)
                    if (time.time() - last_alert_time) > 10:
                        insert_alert()
                        last_alert_time = time.time()
                else:
                    status = f"Drowsy in {DROWSY_TIME_THRESHOLD - elapsed:.1f}s"
                    color = (0, 165, 255)
            else:
                drowsy_start_time = None
            
            # Draw eye landmarks
            for idx in RIGHT_EYE + LEFT_EYE:
                cv2.circle(frame, (int(landmarks[idx][0]), int(landmarks[idx][1])), 2, color, -1)
    
    # Display status
    cv2.putText(frame, f"VH001: {status}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.putText(frame, "Press 'q' to quit", (20, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    cv2.imshow("Driver Safety Monitor - VH001", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("\n👋 Monitor stopped")