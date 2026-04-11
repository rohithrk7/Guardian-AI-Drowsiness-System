import cv2
import numpy as np

def enhance_night_vision(image):
    """Applies CLAHE (Contrast Limited Adaptive Histogram Equalization) for low-light"""
    # Convert image to LAB color space
    lab_img = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab_img)
    
    # Apply CLAHE to L-channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    
    # Merge and convert back to BGR
    updated_lab_img = cv2.merge((cl, a, b))
    enhanced_img = cv2.cvtColor(updated_lab_img, cv2.COLOR_LAB2BGR)
    return enhanced_img

def draw_styled_landmarks(image, right_eye, left_eye, lips, state):
    """Draws tracking landmarks representing state via dynamic color"""
    color = (0, 255, 0) # Green for AWAKE
    if state == "DROWSY" or state == "DISTRACTED": 
        color = (0, 0, 255) # Red for critical
    elif state == "YAWNING" or state == "DISTRACTED_WARNING": 
        color = (0, 165, 255) # Orange for pre-warning
    
    # Draw eyes
    for pt in right_eye: cv2.circle(image, tuple(pt.astype(np.int32)), 2, color, -1)
    cv2.polylines(image, [right_eye.astype(np.int32)], True, color, 1)

    for pt in left_eye: cv2.circle(image, tuple(pt.astype(np.int32)), 2, color, -1)
    cv2.polylines(image, [left_eye.astype(np.int32)], True, color, 1)
    
    # Draw lips
    for pt in lips: cv2.circle(image, tuple(pt.astype(np.int32)), 2, color, -1)
    cv2.polylines(image, [lips.astype(np.int32)], True, color, 1)
