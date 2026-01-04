# src/config.py

# Camera Settings
CAMERA_INDEX = 0  # ปกติ 0 คือกล้อง Webcam ในเครื่อง, 1 คือกล้องตัวที่สอง
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FPS = 30

# Window Settings
WINDOW_NAME = "Face Guard Prototype"

# Face Mesh Settings
MAX_FACES = 1
REFINE_LANDMARKS = True # เปิดเพื่อให้จับจุดรูม่านตา (Iris) ได้ละเอียดขึ้น (จำเป็นสำหรับเฟสต่อไป)
MIN_DETECTION_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5

# src/config.py (Add these lines)

# --- Timing Thresholds (Seconds) ---
TIME_TO_SLEEP = 1.5     # หลับตาเกินนี้ = หลับ
TIME_TO_YAWN = 3.0      # อ้าปากค้างเกินนี้ = หาว
TIME_TO_DISTRACT = 2.5  # หันหน้านานเกินนี้ = เหม่อ

# --- Calibration Settings ---
CALIBRATION_TIME = 3.0  # เวลาที่ใช้เก็บค่าหน้าปกติ (วินาที)

# src/config.py (ต่อท้ายของเดิม)

# --- Recovery & Advanced ---
SLEEP_RECOVERY_TIME = 2.0  # ต้องลืมตาต่อเนื่องกี่วิ ถึงจะหยุดเตือนหลับ
BLINK_FREQ_THRESHOLD = 5  # ถ้ากระพริบตาเกิน 5 ครั้งใน 10 วิ (ถี่ไป) = เหนื่อย