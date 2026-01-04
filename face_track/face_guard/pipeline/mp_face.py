# pipeline/mp_face.py
import mediapipe as mp
import cv2
import numpy as np
from src.config import MAX_FACES, REFINE_LANDMARKS, MIN_DETECTION_CONFIDENCE, MIN_TRACKING_CONFIDENCE

class FaceMeshDetector:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=MAX_FACES,
            refine_landmarks=REFINE_LANDMARKS,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE
        )

    def process(self, frame):
        # MediaPipe ต้องการภาพ RGB แต่ OpenCV ให้มาเป็น BGR
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # ประมวลผลหาจุดต่าง ๆ บนใบหน้า
        rgb_frame.flags.writeable = False # Performance trick
        results = self.face_mesh.process(rgb_frame)
        rgb_frame.flags.writeable = True
        
        return results