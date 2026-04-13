# Alert parameters
EAR_THRESHOLD = 0.22         # Adjust if necessary
DROWSINESS_FRAMES = 15       # Consecutive frames EAR must be below threshold

MAR_THRESHOLD = 0.55         # Yawn threshold
YAWN_FRAMES = 15             # Consecutive frames to register a yawn

DISTRACTION_FRAMES = 15      # Frames for head pose distraction

# Standard EAR calculation indices based on MediaPipe Face Mesh
RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]

# MAR indices for Yawn Detection
LIP_INDICES = [78, 308, 13, 14] 

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

