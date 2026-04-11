import numpy as np
import cv2
from modules.config import HEAD_POSE_INDICES

def calculate_ear(eye_landmarks):
    """Calculate Eye Aspect Ratio"""
    v1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
    v2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
    h = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
    # Avoid zero division
    ear = (v1 + v2) / (2.0 * h) if h != 0 else 0 
    return ear

def calculate_mar(lip_landmarks):
    """Calculate Mouth Aspect Ratio for yawns"""
    # Inner lips: 0=left corner, 1=right corner, 2=upper, 3=lower
    h = np.linalg.norm(lip_landmarks[0] - lip_landmarks[1])
    v = np.linalg.norm(lip_landmarks[2] - lip_landmarks[3])
    if h == 0: return 0
    return v / h

def estimate_head_pose(face_landmarks, w, h):
    """Estimates head pose (pitch, yaw, roll) using solvePnP"""
    face_2d = []
    face_3d = []
    
    for idx, lm in enumerate(face_landmarks.landmark):
        if idx in HEAD_POSE_INDICES:
            x, y = int(lm.x * w), int(lm.y * h)
            face_2d.append([x, y])
            face_3d.append([x, y, lm.z])
            
    face_2d = np.array(face_2d, dtype=np.float64)
    face_3d = np.array(face_3d, dtype=np.float64)
    
    focal_length = 1 * w
    cam_matrix = np.array([[focal_length, 0, w / 2],
                           [0, focal_length, h / 2],
                           [0, 0, 1]])
    dist_matrix = np.zeros((4, 1), dtype=np.float64)
    
    success_pnp, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)
    rmat, _ = cv2.Rodrigues(rot_vec)
    angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
    
    x_angle = angles[0] * 360
    y_angle = angles[1] * 360
    
    is_distracted = False
    head_pos = "Forward"
    if y_angle < -10:
        head_pos = "Looking Left"
        is_distracted = True
    elif y_angle > 10:
        head_pos = "Looking Right"
        is_distracted = True
    elif x_angle < -10:
        head_pos = "Looking Down"
        is_distracted = True
    elif x_angle > 15:
        head_pos = "Looking Up"
        is_distracted = True
        
    return is_distracted, head_pos
