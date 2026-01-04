# pipeline/camera.py
import cv2
from src.config import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT

class Camera:
    def __init__(self):
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        # ตั้งค่าความละเอียด
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera index {CAMERA_INDEX}")

    def get_frame(self):
        success, frame = self.cap.read()
        if not success:
            return False, None
        
        # กลับด้านภาพ (Mirror) ให้เหมือนกระจกเงา จะได้ไม่งงซ้ายขวา
        frame = cv2.flip(frame, 1)
        return True, frame

    def release(self):
        self.cap.release()