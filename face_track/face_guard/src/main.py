import sys
import os
import cv2
import time
import numpy as np  # Import numpy ที่หัวไฟล์ให้ถูกต้อง
from collections import deque

# Setup paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import *
from pipeline.camera import Camera
from pipeline.mp_face import FaceMeshDetector
from ui.draw_utils import draw_face_mesh

from detectors.eye import calculate_ear, get_iris_position
from detectors.mouth import calculate_mar
from detectors.attention import calculate_head_pose
from detectors.smoothing import SmoothValue

from logic.calibration import Calibrator
from logic.timers import EventTimer
from logic.scoring import ScoreManager
from logic.liveness import ActivityDetector
from ui.overlay import HUD

def main():
    # 1. Initialize System Components
    cam = Camera()
    detector = FaceMeshDetector()
    
    s_ear = SmoothValue(0.3)
    s_mar = SmoothValue(0.3)
    s_yaw = SmoothValue(0.3)
    s_pitch = SmoothValue(0.3)
    
    calibrator = Calibrator()
    liveness = ActivityDetector()
    hud = HUD(FRAME_WIDTH, FRAME_HEIGHT)
    score_mgr = ScoreManager()

    # 2. Timers
    timer_sleep = EventTimer(TIME_TO_SLEEP)
    timer_yawn = EventTimer(TIME_TO_YAWN)
    timer_distract = EventTimer(TIME_TO_DISTRACT)
    timer_recovery = EventTimer(SLEEP_RECOVERY_TIME)

    # 3. State Variables
    mode = "IDLE"  # IDLE, CALIBRATING, RUNNING, RESTING
    
    blink_timestamps = deque(maxlen=20)
    is_eye_closed_prev = False
    is_sleep_locked = False
    show_mesh = True  # Toggle Face Mesh
    
    drive_start_time = None
    rest_start_time = None
    
    prev_frame_time = 0
    fps = 0
    
    # ตัวแปรสำหรับ Debug ค่าความนิ่ง
    current_nose_var = 100.0

    print(f"SafeGaze V.2 Ready on Camera Index {CAMERA_INDEX}")
    print("Controls: 'c'=Calibrate, 'r'=Rest, 'm'=Toggle Mesh, 'q'=Quit")

    while True:
        # --- Frame Capture & FPS ---
        success, frame = cam.get_frame()
        if not success: break
        
        new_frame_time = time.time()
        if prev_frame_time > 0:
            fps = 1 / (new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time

        # --- MODE: RESTING (พักรถ) ---
        if mode == "RESTING":
            if rest_start_time is None: rest_start_time = time.time()
            elapsed_rest = time.time() - rest_start_time
            
            hud.draw_rest_screen(frame, elapsed_rest)
            cv2.imshow(WINDOW_NAME, frame)
            
            key = cv2.waitKey(5) & 0xFF
            if key == ord('r'): 
                mode = "IDLE" # กลับไปหน้าแรก (บังคับ Calibrate ใหม่)
                drive_start_time = None
                rest_start_time = None
                print("Resuming... Please Calibrate.")
            elif key == ord('q'): break
            continue

        # --- FACE PROCESSING ---
        results = detector.process(frame)
        
        if show_mesh:
            draw_face_mesh(frame, results)

        if results.multi_face_landmarks:
            lm = results.multi_face_landmarks[0].landmark
            
            # 1. Raw Calculations
            raw_ear = calculate_ear(lm, FRAME_WIDTH, FRAME_HEIGHT)
            raw_mar = calculate_mar(lm, FRAME_WIDTH, FRAME_HEIGHT)
            p, y, r = calculate_head_pose(lm, FRAME_WIDTH, FRAME_HEIGHT)
            iris_pos = get_iris_position(lm, FRAME_WIDTH, FRAME_HEIGHT)
            
            # 2. Update Liveness Data (Head & Iris)
            liveness.update_nose(lm[1], FRAME_WIDTH, FRAME_HEIGHT)
            liveness.update_iris(lm[468], FRAME_WIDTH, FRAME_HEIGHT)

            # 3. Smoothing
            ear = s_ear.update(raw_ear)
            mar = s_mar.update(raw_mar)
            yaw = s_yaw.update(y)
            pitch = s_pitch.update(p)

            # --- MODE SWITCHING ---
            if mode == "CALIBRATING":
                calibrator.update(ear, mar, pitch, yaw)
                hud.draw_calibration(frame, calibrator.get_progress())
                
                if calibrator.is_finished:
                    mode = "RUNNING"
                    drive_start_time = time.time()
                    print("Calibration Done. Drive Safe!")

            elif mode == "RUNNING":
                # =========================================================
                #  A. BLINK TRACKING
                # =========================================================
                is_eye_closed_now = (ear < calibrator.thresh_ear)
                if is_eye_closed_now and not is_eye_closed_prev:
                    blink_timestamps.append(time.time())
                
                # ลบ blink ที่เก่าเกิน 10 วินาที
                curr_time = time.time()
                while blink_timestamps and curr_time - blink_timestamps[0] > 10.0:
                    blink_timestamps.popleft()
                
                blink_rate = len(blink_timestamps)
                is_rapid_blink = blink_rate >= BLINK_FREQ_THRESHOLD
                is_eye_closed_prev = is_eye_closed_now

                # =========================================================
                #  B. STATIC CHECK (กันรูปถ่าย + กันหลับใน)
                # =========================================================
                
                # คำนวณค่า Variance เพื่อโชว์บนหน้าจอ (Debug)
                if len(liveness.nose_history) > 10:
                    data = np.array(liveness.nose_history)
                    # คำนวณความแปรปรวนของแกน X และ Y รวมกัน
                    current_nose_var = np.var(data[:, 0]) + np.var(data[:, 1])

                # ตรวจสอบความนิ่ง
                is_static = liveness.check_static(blink_rate)
                
                if is_static:
                    # 1. แจ้งเตือนให้กระพริบตา
                    hud.draw_warning(frame, "PLEASE BLINK", "Verifying Driver...")
                    
                    # 2. แสดงค่า Debug (ส่งค่า current_nose_var ไปด้วย)
                    hud.draw_debug(frame, ear, mar, pitch, yaw, fps, current_nose_var)
                    
                    # 3. แสดงสถานะ System Paused
                    hud.draw_bar(frame, "System Paused", 1.0, 1.0, 0, (100,100,100))
                    
                    # 4. หยุดการประมวลผลส่วนที่เหลือ (ไม่คิดคะแนน)
                    cv2.imshow(WINDOW_NAME, frame)
                    key = cv2.waitKey(5) & 0xFF
                    if key == ord('q'): break
                    elif key == ord('m'): show_mesh = not show_mesh
                    continue 

                # =========================================================
                #  C. NORMAL DROWSINESS DETECTION
                # =========================================================
                
                # 1. Drive Time Check
                drive_duration = time.time() - drive_start_time
                is_overtime = drive_duration > MAX_DRIVE_TIME

                # 2. Sleep Logic (ตาปิด)
                is_bad_angle = (pitch - calibrator.base_pitch) < -10 or (pitch - calibrator.base_pitch) > 25
                is_sleeping_raw = (not is_bad_angle) and is_eye_closed_now
                
                trig_sleep, prog_sleep = timer_sleep.update(is_sleeping_raw)
                if trig_sleep: is_sleep_locked = True
                
                if is_sleep_locked:
                    unlocked, _ = timer_recovery.update(not is_sleeping_raw)
                    if unlocked: is_sleep_locked = False
                    final_is_sleeping = True
                    prog_sleep = 1.0
                else:
                    timer_recovery.update(False)
                    final_is_sleeping = is_sleeping_raw

                # 3. Yawn Logic
                is_yawning = mar > calibrator.thresh_mar
                trig_yawn, prog_yawn = timer_yawn.update(is_yawning)

                # 4. Distraction Logic
                diff_yaw = abs(yaw - calibrator.base_yaw)
                is_distracted = False
                
                if diff_yaw > 35 or abs(pitch - calibrator.base_pitch) > 25: 
                    is_distracted = True
                elif diff_yaw > 15:
                    if (yaw < calibrator.base_yaw and iris_pos == 'LEFT') or \
                       (yaw > calibrator.base_yaw and iris_pos == 'RIGHT'):
                        is_distracted = True

                trig_distract, prog_distract = timer_distract.update(is_distracted)

                # =========================================================
                #  D. PRIORITY WARNING SYSTEM
                # =========================================================
                warning_msg = ""
                warning_sub = ""
                
                # Priority 1: Sleep (อันตรายสุด)
                if is_sleep_locked:
                    warning_msg = "WAKE UP!"
                    warning_sub = "Drowsiness Detected"
                    score_mgr.update(True, False, False, False, False)
                
                # Priority 2: Distraction
                elif trig_distract:
                    warning_msg = "EYES ON ROAD"
                    score_mgr.update(False, False, True, False, False)

                # Priority 3: Yawn
                elif trig_yawn:
                    warning_msg = "TAKE A BREAK"
                    warning_sub = "Yawning"
                    score_mgr.update(False, True, False, False, False)
                
                # Priority 4: Overtime
                elif is_overtime:
                    warning_msg = "TIME TO REST"

                # Update Score (Normal case)
                if not (is_sleep_locked or trig_distract or trig_yawn):
                     curr_score = score_mgr.update(False, False, False, is_rapid_blink, True)
                else:
                     curr_score = score_mgr.score

                # =========================================================
                #  E. DRAW UI
                # =========================================================
                lvl_text, lvl_color = score_mgr.get_level()
                
                # Info Panel
                hud.draw_info_panel(frame, int(curr_score), blink_rate, drive_duration, lvl_text, lvl_color)
                
                # Status Bars
                c_sleep = (0,0,255) if final_is_sleeping else (0,255,0)
                hud.draw_bar(frame, "Sleep", prog_sleep, 1.0, 0, c_sleep)
                
                c_yawn = (0,0,255) if is_yawning else (0,255,0)
                hud.draw_bar(frame, "Yawn", prog_yawn, 1.0, 1, c_yawn)
                
                c_dist = (0,0,255) if is_distracted else (0,255,0)
                hud.draw_bar(frame, f"Focus ({iris_pos})", prog_distract, 1.0, 2, c_dist)
                
                if is_rapid_blink:
                    hud.draw_bar(frame, "Rapid Blink!", 1.0, 1.0, 3, (0,165,255))

                # Warning Overlay
                if warning_msg:
                    hud.draw_warning(frame, warning_msg, warning_sub)

                # Debug Info (ส่งค่า current_nose_var ไปแสดงผล)
                hud.draw_debug(frame, ear, mar, pitch, yaw, fps, current_nose_var)

            else: # IDLE Screen
                cv2.putText(frame, "Press 'c' to Calibrate", (FRAME_WIDTH//2 - 200, FRAME_HEIGHT//2), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)

        cv2.imshow(WINDOW_NAME, frame)
        key = cv2.waitKey(5) & 0xFF
        if key == ord('q'): break
        elif key == ord('c') and mode == "IDLE":
            mode = "CALIBRATING"
            calibrator.start()
        elif key == ord('r') and mode == "RUNNING":
            mode = "RESTING"
            rest_start_time = time.time()
        elif key == ord('m'):
            show_mesh = not show_mesh

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()