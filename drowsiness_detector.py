import cv2
import mediapipe as mp
import numpy as np
import time
import argparse
import json
import os

# Import our custom modules
from modules.config import (
    EAR_THRESHOLD, DROWSINESS_FRAMES,
    MAR_THRESHOLD, YAWN_FRAMES, DISTRACTION_FRAMES,
    RIGHT_EYE_INDICES, LEFT_EYE_INDICES, LIP_INDICES
)
from modules.audio import speak_warning, play_beep
from modules.vision import calculate_ear, calculate_mar, estimate_head_pose
from modules.ui import enhance_night_vision, draw_styled_landmarks

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.json')

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

def main(username):
    # Log a new trip initialization
    update_db(username, "trips")
    
    # Mediapipe configuration
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    cap = cv2.VideoCapture(0)
    
    frame_counter_ear = 0
    frame_counter_mar = 0
    distraction_start_time = None
    
    # Event Latches so we only log an incident once per active occurrence
    drowsy_logged = False
    yawn_logged = False
    distraction_logged_warning = False
    distraction_logged_critical = False
    
    # Setup Window
    cv2.namedWindow('Premium Driver Safety System [Night-Vision Active]', cv2.WINDOW_NORMAL)
    
    while cap.isOpened():
        success, image = cap.read()
        if not success: 
            break
            
        image = cv2.flip(image, 1)
        h, w, _ = image.shape
        
        # --- FEATURE 3: Low-Light/Night Vision Enhancement ---
        image = enhance_night_vision(image)
        
        image.flags.writeable = False
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(image_rgb)
        image.flags.writeable = True
        
        # Transparent UI background panel
        overlay = image.copy()
        cv2.rectangle(overlay, (0, 0), (w, 110), (30, 30, 30), -1)
        cv2.addWeighted(overlay, 0.7, image, 0.3, 0, image)
        
        state = "AWAKE"
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                landmarks = np.array([(lm.x * w, lm.y * h) for lm in face_landmarks.landmark])
                
                # --- FEATURE 2: Head Pose Estimation ---
                is_distracted, head_pos = estimate_head_pose(face_landmarks, w, h)

                right_eye = landmarks[RIGHT_EYE_INDICES]
                left_eye = landmarks[LEFT_EYE_INDICES]
                lips = landmarks[LIP_INDICES]
                
                avg_ear = (calculate_ear(right_eye) + calculate_ear(left_eye)) / 2.0
                mar = calculate_mar(lips) # --- FEATURE 1: MAR calculation ---
                
                is_drowsy = False
                is_yawning = False
                
                # Check for Critical Eye Closure
                if avg_ear < EAR_THRESHOLD:
                    frame_counter_ear += 1
                    if frame_counter_ear >= DROWSINESS_FRAMES:
                        is_drowsy = True
                        state = "DROWSY"
                        if not drowsy_logged:
                            update_db(username, "drowsy_count")
                            drowsy_logged = True
                        speak_warning("Critical Drowsiness! Wake up immediately!")
                else:
                    frame_counter_ear = 0
                    drowsy_logged = False
                
                # Check for Pre-Fatigue Yawning
                if mar > MAR_THRESHOLD and not is_drowsy:
                    frame_counter_mar += 1
                    if frame_counter_mar >= YAWN_FRAMES:
                        is_yawning = True
                        state = "YAWNING"
                        if not yawn_logged:
                            update_db(username, "yawn_count")
                            yawn_logged = True
                        speak_warning("Yawning detected. You are showing signs of fatigue.")
                else:
                    frame_counter_mar = 0
                    yawn_logged = False
                
                # Check for Distraction
                if is_distracted and not is_drowsy:
                    if distraction_start_time is None:
                        distraction_start_time = time.time()
                    
                    elapsed_distraction = time.time() - distraction_start_time
                    
                    if elapsed_distraction >= 5.0:
                        state = "DISTRACTED"
                        if not distraction_logged_critical:
                            update_db(username, "distraction_count")
                            distraction_logged_critical = True
                        speak_warning("Distraction detected. Keep your eyes on the road.")
                    elif elapsed_distraction >= 2.0:
                        state = "DISTRACTED_WARNING"
                        if not distraction_logged_warning:
                            distraction_logged_warning = True
                        play_beep()
                else:
                    distraction_start_time = None
                    distraction_logged_warning = False
                    distraction_logged_critical = False
                
                # Draw dynamic styled facial geometries
                draw_styled_landmarks(image, right_eye, left_eye, lips, state)
                
                # Colors based on state
                ear_color = (0, 0, 255) if is_drowsy else (0, 255, 255)
                mar_color = (0, 165, 255) if is_yawning else (0, 255, 255)
                
                head_color = (0, 255, 255)
                if state == "DISTRACTED":
                    head_color = (0, 0, 255)
                elif state == "DISTRACTED_WARNING":
                    head_color = (0, 165, 255)
                
                # Dynamic Numeric Text Metrics
                cv2.putText(image, f"EAR: {avg_ear:.3f}", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.7, ear_color, 2)
                cv2.putText(image, f"MAR: {mar:.3f} (Yawn)", (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.7, mar_color, 2)
                cv2.putText(image, f"HEAD: {head_pos}", (20, 125), cv2.FONT_HERSHEY_SIMPLEX, 0.7, head_color, 2)
                
                max_bar = 150
                # Render Eye Closure Bar Graph
                bar_w_ear = max(min(int((avg_ear / 0.40) * max_bar), max_bar), 0)
                cv2.rectangle(image, (230, 25), (230 + max_bar, 50), (50, 50, 50), -1)
                cv2.rectangle(image, (230, 25), (230 + bar_w_ear, 50), ear_color, -1)
                
                # Render Yawn Opening Bar Graph
                bar_w_mar = max(min(int((mar / 0.80) * max_bar), max_bar), 0)
                cv2.rectangle(image, (230, 65), (230 + max_bar, 90), (50, 50, 50), -1)
                cv2.rectangle(image, (230, 65), (230 + bar_w_mar, 90), mar_color, -1)
                
                # Extreme Alert Centered Output
                if state == "DROWSY":
                    cv2.putText(image, "CRITICAL: SLEEPING!", (w // 2 - 200, h // 2), 
                                cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 255), 3)
                elif state == "YAWNING":
                    cv2.putText(image, "WARNING: YAWNING!", (w // 2 - 200, h // 2), 
                                cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 165, 255), 3)
                elif state == "DISTRACTED":
                    cv2.putText(image, "CRITICAL: LOOK FORWARD!", (w // 2 - 250, h // 2), 
                                cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 255), 3)
                elif state == "DISTRACTED_WARNING":
                    cv2.putText(image, "WARNING: DISTRACTION BEEP", (w // 2 - 250, h // 2), 
                                cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 165, 255), 3)
                    
        else:
            cv2.putText(image, "No Face Detected", (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 3)
            frame_counter_ear = 0
            frame_counter_mar = 0
            distraction_start_time = None
            
        cv2.putText(image, "Night Vision Active - Controlled via Dashboard", (w - 350, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        cv2.imshow('Premium Driver Safety System [Night-Vision Active]', image)
        cv2.waitKey(5)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', type=str, default='Driver', help='Username for DB logging')
    args = parser.parse_args()
    
    main(args.user)
