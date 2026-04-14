# Alert parameters
EAR_THRESHOLD = 0.22         # Adjust if necessary
DROWSINESS_FRAMES = 15       # Consecutive frames EAR must be below threshold

MAR_THRESHOLD = 0.55         # Yawn threshold
YAWN_FRAMES = 15             # Consecutive frames to register a yawn

DISTRACTION_FRAMES = 15      # Frames for head pose distraction

# EAR/MAR Calculation Indices (Legacy/Accurate)
RIGHT_EYE_CALC = [33, 160, 158, 133, 153, 144]
LEFT_EYE_CALC = [362, 385, 387, 263, 373, 380]
LIP_CALC = [78, 308, 13, 14]

# Visualization Indices (Full Contours)
RIGHT_EYE_INDICES = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
LEFT_EYE_INDICES = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
LIP_INDICES = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267, 0, 37, 39, 40, 185] 

# Indices for Head Pose Estimation
HEAD_POSE_INDICES = [33, 263, 1, 61, 291, 199]

# --- Emergency Alert Configuration ---
# Number of frames for critical drowsiness (Emergency Response)
CRITICAL_DROWSY_LIMIT = 45   # Roughly 2-3 seconds of closed eyes

# --- Telegram Alert Configuration (Recommended) ---
# 1. Get Token from @BotFather
# 2. Get ID from @userinfobot
TELEGRAM_BOT_TOKEN = "8678903058:AAE-s48dA91Wldt-EZ4OMeIF_bCf2Y59K_c"
TELEGRAM_CHAT_ID = "668854268"

