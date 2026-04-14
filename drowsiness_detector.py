import cv2
import mediapipe as mp
import numpy as np
import time
import argparse
import json
import os

# Import our custom modules
from modules.config import (
    EAR_THRESHOLD, DROWSINESS_FRAMES, CRITICAL_DROWSY_LIMIT,
    MAR_THRESHOLD, YAWN_FRAMES, DISTRACTION_FRAMES,
    RIGHT_EYE_CALC, LEFT_EYE_CALC, LIP_CALC,
    RIGHT_EYE_INDICES, LEFT_EYE_INDICES, LIP_INDICES
)
from modules.audio import speak_warning, play_beep
from modules.vision import calculate_ear, calculate_mar, estimate_head_pose
from modules.ui import enhance_night_vision
from modules.alerts import send_emergency_alerts

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.json')
LIVE_STATS_PATH = os.path.join(os.path.dirname(__file__), 'live_stats.json')

def update_db(username, metric):
    db = {}
    if os.path.exists(DB_PATH):
        with open(DB_PATH, 'r') as f:
            try:
                db = json.load(f)
            except:
                pass
    if username not in db:
        db[username] = {"drowsy_count": 0, "yawn_count": 0, "distraction_count": 0, "trips": 0}
    
    db[username][metric] += 1
    with open(DB_PATH, 'w') as f:
        json.dump(db, f)

def write_live_stats(ear, mar, head_pos, state):
    stats = {
        "ear": round(float(ear), 3),
        "mar": round(float(mar), 3),
        "head_pos": head_pos,
        "state": state,
        "timestamp": time.time()
    }
    with open(LIVE_STATS_PATH, 'w') as f:
        json.dump(stats, f)


class DrowsinessDetector:
    def __init__(self, username):
        self.username = username
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.frame_counter_ear = 0
        self.frame_counter_mar = 0
        self.distraction_start_time = None
        
        # Event Latches so we only log an incident once per active occurrence
        self.drowsy_logged = False
        self.yawn_logged = False
        self.distraction_logged_warning = False
        self.distraction_logged_critical = False
        self.emergency_logged = False
        
        # Log a new trip initialization
        update_db(self.username, "trips")

    def process_frame(self, image):
        h, w, _ = image.shape
        
        # --- FEATURE 3: Low-Light/Night Vision Enhancement ---
        image = enhance_night_vision(image)
        
        image.flags.writeable = False
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(image_rgb)
        image.flags.writeable = True
        
        state = "AWAKE"
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                landmarks = np.array([(lm.x * w, lm.y * h) for lm in face_landmarks.landmark])
                
                # --- FEATURE 2: Head Pose Estimation ---
                is_distracted, head_pos = estimate_head_pose(face_landmarks, w, h)

                right_eye = landmarks[RIGHT_EYE_CALC]
                left_eye = landmarks[LEFT_EYE_CALC]
                lips = landmarks[LIP_CALC]
                
                avg_ear = (calculate_ear(right_eye) + calculate_ear(left_eye)) / 2.0
                mar = calculate_mar(lips)
                
                is_drowsy = False
                is_yawning = False
                
                # Check for Critical Eye Closure
                if avg_ear < EAR_THRESHOLD:
                    self.frame_counter_ear += 1
                    if self.frame_counter_ear >= DROWSINESS_FRAMES:
                        is_drowsy = True
                        state = "DROWSY"
                        if not self.drowsy_logged:
                            update_db(self.username, "drowsy_count")
                            self.drowsy_logged = True
                        speak_warning("Critical Drowsiness! Wake up immediately!")

                        if self.frame_counter_ear >= CRITICAL_DROWSY_LIMIT and not self.emergency_logged:
                            print(f"!!! DISPATCHING EMERGENCY ALERT !!!")
                            send_emergency_alerts(self.username)
                            self.emergency_logged = True
                else:
                    self.frame_counter_ear = 0
                    self.drowsy_logged = False
                    self.emergency_logged = False
                
                # Check for Pre-Fatigue Yawning
                if mar > MAR_THRESHOLD and not is_drowsy:
                    self.frame_counter_mar += 1
                    if self.frame_counter_mar >= YAWN_FRAMES:
                        is_yawning = True
                        state = "YAWNING"
                        if not self.yawn_logged:
                            update_db(self.username, "yawn_count")
                            self.yawn_logged = True
                        speak_warning("Yawning detected. You are showing signs of fatigue.")
                else:
                    self.frame_counter_mar = 0
                    self.yawn_logged = False
                
                # Check for Distraction
                if is_distracted and not is_drowsy:
                    if self.distraction_start_time is None:
                        self.distraction_start_time = time.time()
                    
                    elapsed_distraction = time.time() - self.distraction_start_time
                    
                    if elapsed_distraction >= 5.0:
                        state = "DISTRACTED"
                        if not self.distraction_logged_critical:
                            update_db(self.username, "distraction_count")
                            self.distraction_logged_critical = True
                        speak_warning("Distraction detected. Keep your eyes on the road.")
                    elif elapsed_distraction >= 2.0:
                        state = "DISTRACTED_WARNING"
                        if not self.distraction_logged_warning:
                            self.distraction_logged_warning = True
                        play_beep()
                else:
                    self.distraction_start_time = None
                    self.distraction_logged_warning = False
                    self.distraction_logged_critical = False
                
                # Update Live Stats for Dashboard only
                write_live_stats(avg_ear, mar, head_pos, state)

                # --- TECH OVERLAY: HIGH-FIDELITY FACIAL GRAPH ---
                # Colors: Electric Blue/Cyan and Safety Green
                target_cyan = (255, 229, 0) 
                safety_green = (0, 255, 100)
                
                # Render Detailed Eye Polygons (Outer boundaries)
                for eye_indices in [LEFT_EYE_INDICES, RIGHT_EYE_INDICES]:
                    eye_pts = landmarks[eye_indices].astype(np.int32)
                    # Draw a semi-transparent glow effect by drawing twice
                    cv2.polylines(image, [eye_pts], True, safety_green, 1, cv2.LINE_AA)
                    for pt in eye_pts:
                        cv2.circle(image, tuple(pt), 1, target_cyan, -1)

                # Render Entire Mouth Area (Outer lips)
                mouth_pts = landmarks[LIP_INDICES].astype(np.int32)
                cv2.polylines(image, [mouth_pts], True, safety_green, 1, cv2.LINE_AA)
                for pt in mouth_pts:
                    cv2.circle(image, tuple(pt), 1, target_cyan, -1)

                # Add Telemetry Text
                cv2.putText(image, f"STATE: {state}", (20, 40), 
                            cv2.FONT_HERSHEY_DUPLEX, 0.7, target_cyan, 1, cv2.LINE_AA)
                    
        else:
            self.frame_counter_ear = 0
            self.frame_counter_mar = 0
            self.distraction_start_time = None
            write_live_stats(0.0, 0.0, "None", "NO_FACE")

        return image

    def close(self):
        self.face_mesh.close()


def main(username):
    detector = DrowsinessDetector(username)
    cap = cv2.VideoCapture(0)
    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break
            
        image = cv2.flip(image, 1)
        processed_image = detector.process_frame(image)
        
        cv2.imshow('Drowsiness Detector', processed_image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    detector.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', type=str, default='Driver', help='Username for DB logging')
    args = parser.parse_args()
    
    main(args.user)
