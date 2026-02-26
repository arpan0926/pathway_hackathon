#Webcam for driver safety
import cv2
import mediapipe as mp
import numpy as np
import time
import winsound 

#TIME THRESHOLD SETTING 
DROWSY_TIME_THRESHOLD = 1.5 
HEAD_DOWN_TIME_THRESHOLD = 3.0
eye_aspect_ratio_threshold = 0.25 


# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def calculate_ear(landmarks, indices):
    """Calculates Eye Aspect Ratio (EAR)."""
    A = np.linalg.norm(np.array(landmarks[indices[1]]) - np.array(landmarks[indices[5]]))
    B = np.linalg.norm(np.array(landmarks[indices[2]]) - np.array(landmarks[indices[4]]))
    C = np.linalg.norm(np.array(landmarks[indices[0]]) - np.array(landmarks[indices[3]]))
    return (A + B) / (2.0 * C)

def process_frame(frame, drowsy_start_time, head_down_start_time):
    """
    Tracks eye closure and head position duration.
    """
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(frame_rgb)
    
    status = "Active"
    
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            h, w, _ = frame.shape
            landmarks = [(lm.x * w, lm.y * h) for lm in face_landmarks.landmark]
            
            # --- 1. DROWSINESS LOGIC (EYES) ---
            RIGHT_EYE = [33, 160, 158, 133, 153, 144]
            LEFT_EYE = [362, 385, 387, 263, 373, 380]
            
            avg_ear = (calculate_ear(landmarks, RIGHT_EYE) + calculate_ear(landmarks, LEFT_EYE)) / 2.0
            
            if avg_ear < eye_aspect_ratio_threshold:
                if drowsy_start_time is None:
                    drowsy_start_time = time.time()
                if (time.time() - drowsy_start_time) > DROWSY_TIME_THRESHOLD:
                    status = "DROWSY"
            else:
                drowsy_start_time = None

            # --- 2. HEAD DOWN LOGIC ---
           
            nose = landmarks[1]
            forehead = landmarks[10]
            chin = landmarks[152]
            
            face_height = chin[1] - forehead[1]
            # If nose-to-chin vertical distance is very small relative to face height, head is down
            if (chin[1] - nose[1]) < (face_height * 0.35):
                if head_down_start_time is None:
                    head_down_start_time = time.time()
                if (time.time() - head_down_start_time) > HEAD_DOWN_TIME_THRESHOLD:
                    status = "HEAD DOWN"
            else:
                head_down_start_time = None

            # --- 3. ALERTS & UI ---
            color = (0, 255, 0)
            if status != "Active":
                color = (0, 0, 255)
                # Visual Alert
                cv2.putText(frame, f"ALERT: {status}!", (50, 100), 
                            cv2.FONT_HERSHEY_DUPLEX, 1.5, color, 3)
                # Audio Alert (1000Hz for 200ms)
                winsound.Beep(1000, 200)
            else:
                cv2.putText(frame, "Active", (50, 100), 
                            cv2.FONT_HERSHEY_DUPLEX, 1, color, 3)
            
            # Draw eye landmarks for visual feedback
            for idx in RIGHT_EYE + LEFT_EYE:
                cv2.circle(frame, (int(landmarks[idx][0]), int(landmarks[idx][1])), 1, color, -1)

    return frame, status, drowsy_start_time, head_down_start_time

# --- TESTING BLOCK ---
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    drowsy_timer = None 
    head_timer = None
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        # Pass both timers into the function
        processed_frame, current_status, drowsy_timer, head_timer = process_frame(frame, drowsy_timer, head_timer)
        
        cv2.imshow("Driver Safety Test", processed_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break
            
    cap.release()
    cv2.destroyAllWindows()
