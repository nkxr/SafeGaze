import numpy as np

# จุดอ้างอิงของตา (MediaPipe Indices)
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

# จุดตาดำ (Iris)
# 468 คือจุดกึ่งกลางตาดำข้างขวา (มุมมองคนขับ)
RIGHT_IRIS_CENTER = 468 
RIGHT_EYE_IN = 33   # หัวตาขวา
RIGHT_EYE_OUT = 133 # หางตาขวา

def calculate_ear(landmarks, width, height):
    """
    คำนวณค่า Eye Aspect Ratio (EAR)
    """
    def get_coords(indices):
        coords = []
        for idx in indices:
            lm = landmarks[idx]
            coords.append([lm.x * width, lm.y * height])
        return np.array(coords)

    def eye_aspect_ratio(eye_points):
        A = np.linalg.norm(eye_points[1] - eye_points[5])
        B = np.linalg.norm(eye_points[2] - eye_points[4])
        C = np.linalg.norm(eye_points[0] - eye_points[3])
        ear = (A + B) / (2.0 * C)
        return ear

    try:
        left_points = get_coords(LEFT_EYE)
        right_points = get_coords(RIGHT_EYE)

        left_ear = eye_aspect_ratio(left_points)
        right_ear = eye_aspect_ratio(right_points)

        return (left_ear + right_ear) / 2.0
    except:
        return 0.0

def get_iris_position(landmarks, width, height):
    """
    ตรวจสอบว่าตาดำมองไปทางไหน (CENTER, LEFT, RIGHT)
    โดยเช็คจากตาขวา (Right Eye) เป็นหลัก
    """
    try:
        # ดึงพิกัดแนวนอน (x)
        p_in = landmarks[RIGHT_EYE_IN].x * width
        p_out = landmarks[RIGHT_EYE_OUT].x * width
        p_iris = landmarks[RIGHT_IRIS_CENTER].x * width
        
        # ระยะทั้งหมดของดวงตา (จากหัวตาไปหางตา)
        eye_width = p_out - p_in
        if eye_width == 0: return "CENTER"
        
        # ระยะจากหัวตาถึงตาดำ
        dist_to_iris = p_iris - p_in
        
        # คำนวณอัตราส่วน (0.0 - 1.0)
        # 0.5 คือตรงกลาง
        # น้อยกว่า 0.4 คือมองขวา (หันไปทางขวาของตัวเอง)
        # มากกว่า 0.6 คือมองซ้าย (หันไปทางซ้ายของตัวเอง)
        ratio = dist_to_iris / eye_width
        
        if ratio < 0.42:
            return "RIGHT"
        elif ratio > 0.58:
            return "LEFT"
        else:
            return "CENTER"
    except:
        return "CENTER"