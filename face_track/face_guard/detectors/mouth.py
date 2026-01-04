import numpy as np

# จุดอ้างอิงปาก (ริมฝีปากใน)
MOUTH = [13, 312, 317, 14, 87, 82, 78, 308] 
# 13=บน, 14=ล่าง, 78=มุมซ้าย, 308=มุมขวา

def calculate_mar(landmarks, width, height):
    """
    คำนวณค่า Mouth Aspect Ratio (MAR)
    return: ค่าความกว้างปาก (ยิ่งมาก = ยิ่งอ้ากว้าง)
    """
    try:
        # จุดบน vs ล่าง
        top = np.array([landmarks[13].x * width, landmarks[13].y * height])
        bottom = np.array([landmarks[14].x * width, landmarks[14].y * height])
        
        # จุดมุมซ้าย vs มุมขวา
        left = np.array([landmarks[78].x * width, landmarks[78].y * height])
        right = np.array([landmarks[308].x * width, landmarks[308].y * height])

        # คำนวณระยะ
        vertical_dist = np.linalg.norm(top - bottom)
        horizontal_dist = np.linalg.norm(left - right)

        # สูตร MAR
        if horizontal_dist == 0: return 0
        return vertical_dist / horizontal_dist
    except:
        return 0.0