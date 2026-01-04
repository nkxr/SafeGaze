import cv2
import numpy as np

def calculate_head_pose(landmarks, width, height):
    """
    คำนวณมุมหน้า (Pitch, Yaw, Roll)
    return: (pitch, yaw, roll) ในหน่วยองศา
    """
    # 1. จุดบนหน้า 2D (จาก MediaPipe)
    face_2d = []
    points_idx = [1, 152, 33, 263, 61, 291]
    
    for idx in points_idx:
        lm = landmarks[idx]
        face_2d.append([lm.x * width, lm.y * height])
    
    face_2d = np.array(face_2d, dtype=np.float64)

    # 2. จุดบนหน้า 3D มาตรฐาน
    face_3d = np.array([
        [0.0, 0.0, 0.0],          # Nose tip
        [0.0, -330.0, -65.0],     # Chin
        [-225.0, 170.0, -135.0],  # Left eye left corner
        [225.0, 170.0, -135.0],   # Right eye right corner
        [-150.0, -150.0, -125.0], # Left Mouth corner
        [150.0, -150.0, -125.0]   # Right mouth corner
    ], dtype=np.float64)

    # 3. ตั้งค่ากล้อง
    focal_length = 1 * width
    cam_matrix = np.array([
        [focal_length, 0, width / 2],
        [0, focal_length, height / 2],
        [0, 0, 1]
    ])
    dist_matrix = np.zeros((4, 1), dtype=np.float64)

    # 4. Solve PnP
    success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)

    if not success:
        return 0, 0, 0

    # 5. แปลงเป็น Euler Angles
    rmat, jac = cv2.Rodrigues(rot_vec)
    
    # --- แก้ไขตรงนี้ (รับค่าแค่ 6 ตัว) ---
    angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

    # ค่าที่ได้เป็นองศาอยู่แล้ว ไม่ต้องคูณ 360
    pitch = angles[0] 
    yaw = angles[1] 
    roll = angles[2]
    
    return pitch, yaw, roll