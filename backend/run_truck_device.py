# FILE: run_truck_device.py
import cv2
import time
from backend.webcam import process_frame # Re-use your existing logic

def run_edge_device():
    # 1. Setup Camera
    cap = cv2.VideoCapture(0)
    
    # Timer state
    drowsy_start_time = None
    
    print("✅ TRUCK DEVICE ACTIVE: Monitoring Driver...")
    print("ℹ️  Press 'q' in the video window to stop.")

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        # 2. Process using your logic
        frame, status, drowsy_start_time = process_frame(frame, drowsy_start_time)
        
        # 3. WRITE STATUS TO FILE (Simulating IoT Transmission)
        # We write 'ACTIVE' or 'DROWSY' to a text file that the dashboard reads
        with open("driver_status.txt", "w") as f:
            f.write(status)
            
        # 4. Show the "Driver's View" in a separate, smooth window
        cv2.imshow("🚛 Truck Cabin Monitor (Edge Device)", frame)
        
        # Quit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()
    # Cleanup
    with open("driver_status.txt", "w") as f:
        f.write("OFFLINE")

if __name__ == "__main__":
    run_edge_device()