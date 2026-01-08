# logic/liveness.py
import numpy as np
from collections import deque
from src.config import STATIC_VAR_THRESH

class ActivityDetector:
    def __init__(self):
        self.nose_history = deque(maxlen=60) 
        self.iris_history = deque(maxlen=60)
        
    def update_nose(self, nose_landmark, width, height):
        x = nose_landmark.x * width
        y = nose_landmark.y * height
        self.nose_history.append((x, y))

    def update_iris(self, iris_landmark, width, height):
        if iris_landmark:
            x = iris_landmark.x * width
            y = iris_landmark.y * height
            self.iris_history.append((x, y))

    def check_static(self, blink_count_recent):
        """
        รวมระบบ: ตรวจสอบความนิ่ง (Static)
        เงื่อนไข: (หัวนิ่ง หรือ ตานิ่ง) AND (ไม่กระพริบตาเลย)
        """
        # ข้อมูลต้องพอประมาณ (20 เฟรม)
        if len(self.nose_history) < 20: return False
        
        # 1. คำนวณความนิ่งจมูก
        nose_data = np.array(self.nose_history)
        nose_var = np.var(nose_data[:, 0]) + np.var(nose_data[:, 1])
        
        # 2. คำนวณความนิ่งตา (ถ้ามีข้อมูล)
        iris_var = 100 # ค่าเริ่มต้นสูงๆ
        if len(self.iris_history) > 20:
            iris_data = np.array(self.iris_history)
            iris_var = np.var(iris_data[:, 0]) + np.var(iris_data[:, 1])
        
        # 3. เช็คความนิ่ง (ใช้อันใดอันหนึ่งที่นิ่งผิดปกติ)
        # เราใช้ STATIC_VAR_THRESH (เช่น 0.08)
        # ถ้านิ่งกว่าเกณฑ์ คือ น่าสงสัย
        is_still = (nose_var < STATIC_VAR_THRESH) or (iris_var < STATIC_VAR_THRESH)
        
        # 4. ตัวตัดสินคือ "การกระพริบตา"
        has_blinked = blink_count_recent > 0
        
        # ถ้านิ่ง และ ไม่กระพริบตา = Lock ระบบ
        return is_still and (not has_blinked)