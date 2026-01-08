# src/config.py
import cv2

# --- Camera & Display ---
CAMERA_INDEX = 0
WINDOW_NAME = "SafeGaze V.2 (HD)"
FRAME_WIDTH = 1280  # ปรับเป็น HD
FRAME_HEIGHT = 720  # ปรับเป็น HD

# --- MediaPipe Settings ---
MAX_FACES = 1
REFINE_LANDMARKS = True
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5

# --- Colors (B, G, R) ---
GREEN = (0, 255, 0)
YELLOW = (0, 255, 255)
RED = (0, 0, 255)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)

# --- Timing Thresholds (Seconds) ---
TIME_TO_SLEEP = 1.5
TIME_TO_YAWN = 2.5
TIME_TO_DISTRACT = 2.0

# --- Recovery & Advanced ---
SLEEP_RECOVERY_TIME = 2.0
BLINK_FREQ_THRESHOLD = 15

# --- V.2 New Configs ---
MAX_DRIVE_TIME = 7200
REST_TIME_REQUIRED = 900

# --- STATIC / LIVENESS CHECK (รวมระบบ) ---
# ความแปรปรวนรวม (ยอมให้ขยับได้นิดหน่อยเผื่อรถสั่น)
STATIC_VAR_THRESH = 15.0  
# เวลานับถอยหลัง Blink (วินาที)
BLINK_WAIT_TIME = 5.0

# --- Calibration Settings ---
CALIBRATION_TIME = 3.0