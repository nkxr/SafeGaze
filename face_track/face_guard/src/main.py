import sys
import os
import cv2
import time
from collections import deque # ใช้เก็บประวัติเวลา blink

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import WINDOW_NAME, FRAME_WIDTH, FRAME_HEIGHT, TIME_TO_SLEEP, TIME_TO_YAWN, TIME_TO_DISTRACT, SLEEP_RECOVERY_TIME, BLINK_FREQ_THRESHOLD
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
from ui.overlay import HUD

def main():
    cam = Camera()
    detector = FaceMeshDetector()
    
    # Init Objects
    s_ear, s_mar = SmoothValue(0.3), SmoothValue(0.3)
    s_yaw, s_pitch = SmoothValue(0.3), SmoothValue(0.3)

    calibrator = Calibrator()
    timer_sleep = EventTimer(TIME_TO_SLEEP)
    timer_yawn = EventTimer(TIME_TO_YAWN)
    timer_distract = EventTimer(TIME_TO_DISTRACT)
    
    # Timer สำหรับกู้คืนสถานะหลับ (ต้องลืมตาต่อเนื่อง)
    timer_recovery = EventTimer(SLEEP_RECOVERY_TIME)
    
    score_mgr = ScoreManager()
    hud = HUD(FRAME_WIDTH, FRAME_HEIGHT)

    # State Variables
    mode = "IDLE"
    is_eye_closed_prev = False
    
    # Blink Rate Variables
    blink_timestamps = deque(maxlen=20) # เก็บเวลา blink 20 ครั้งล่าสุด
    
    # Sleep Lock Variables
    is_sleep_locked = False # สถานะว่าตอนนี้โดนล็อคว่าหลับอยู่หรือไม่

    # Display Options
    show_mesh = True
    
    prev_frame_time = 0

    print("System Ready. Keys: 'c'=Calibrate, 'm'=Toggle Mesh, 'q'=Quit")

    while True:
        success, frame = cam.get_frame()
        if not success: break
        
        # FPS Calculation
        new_frame_time = time.time()
        fps = 1 / (new_frame_time - prev_frame_time) if prev_frame_time > 0 else 0
        prev_frame_time = new_frame_time

        results = detector.process(frame)
        
        # 3. Toggle Mesh (วาดเฉพาะตอนเปิด)
        if show_mesh:
            draw_face_mesh(frame, results)

        if results.multi_face_landmarks:
            lm = results.multi_face_landmarks[0].landmark
            
            # --- Calculation ---
            raw_ear = calculate_ear(lm, FRAME_WIDTH, FRAME_HEIGHT)
            raw_mar = calculate_mar(lm, FRAME_WIDTH, FRAME_HEIGHT)
            p, y, r = calculate_head_pose(lm, FRAME_WIDTH, FRAME_HEIGHT)
            iris_pos = get_iris_position(lm, FRAME_WIDTH, FRAME_HEIGHT)

            ear = s_ear.update(raw_ear)
            mar = s_mar.update(raw_mar)
            yaw = s_yaw.update(y)
            pitch = s_pitch.update(p)

            if mode == "CALIBRATING":
                calibrator.update(ear, mar, pitch, yaw)
                hud.draw_calibration(frame, calibrator.get_progress())
                if calibrator.is_finished: mode = "RUNNING"

            elif mode == "RUNNING":
                # ==========================
                # 1. BLINK RATE LOGIC
                # ==========================
                is_eye_closed_now = (ear < calibrator.thresh_ear)
                
                # นับ Blink เมื่อเปลี่ยนจาก ลืม -> หลับ
                if is_eye_closed_now and not is_eye_closed_prev:
                    blink_timestamps.append(time.time())
                
                # ลบ Blink ที่เก่าเกิน 10 วินาทีทิ้ง (คิด Rate ในรอบ 10 วิ)
                current_time = time.time()
                while blink_timestamps and current_time - blink_timestamps[0] > 10.0:
                    blink_timestamps.popleft()
                
                # เช็คว่ากระพริบตาถี่เกินไหม?
                blink_rate = len(blink_timestamps)
                is_rapid_blink = blink_rate >= 8 # (เช่น 8 ครั้งใน 10 วิ ถือว่าเริ่มถี่ผิดปกติ)

                # ==========================
                # 2. SLEEP LOCK LOGIC
                # ==========================
                # เช็คเงื่อนไขหลับปกติ (กันเงยหน้า)
                is_bad_angle = (pitch - calibrator.base_pitch) < -10 or (pitch - calibrator.base_pitch) > 25
                is_sleeping_raw = (not is_bad_angle) and is_eye_closed_now
                
                # Update Timer ปกติ
                trig_sleep, prog_sleep = timer_sleep.update(is_sleeping_raw)
                
                # ถ้าหลอดเต็ม -> สั่ง Lock
                if trig_sleep:
                    is_sleep_locked = True
                
                # ถ้ากำลัง Lock อยู่ -> ต้องลืมตาต่อเนื่องเพื่อปลดล็อค
                if is_sleep_locked:
                    # ถ้าลืมตาอยู่ -> เริ่มนับเวลา Recovery
                    is_recovering = (not is_sleeping_raw)
                    unlocked, recovery_prog = timer_recovery.update(is_recovering)
                    
                    if unlocked: # กู้คืนสำเร็จ
                        is_sleep_locked = False
                    
                    # บังคับให้สถานะหลับยังคงอยู่ (เต็มหลอด) ระหว่างที่ยังกู้คืนไม่เสร็จ
                    final_is_sleeping = True
                    display_prog_sleep = 1.0 # หลอดค้างเต็ม
                else:
                    # สถานะปกติ
                    timer_recovery.update(False) # รีเซ็ตตัวกู้คืน
                    final_is_sleeping = is_sleeping_raw
                    display_prog_sleep = prog_sleep

                is_eye_closed_prev = is_eye_closed_now

                # ==========================
                # 3. OTHER LOGIC (Yawn & Distract)
                # ==========================
                is_yawning = mar > calibrator.thresh_mar
                trig_yawn, prog_yawn = timer_yawn.update(is_yawning)

                diff_yaw = abs(yaw - calibrator.base_yaw)
                diff_pitch = abs(pitch - calibrator.base_pitch)
                is_distracted = False
                # เดิมอาจจะตั้งไว้ 30 -> ลองขยับเป็น 35 หรือ 40
                # เพื่อเผื่อระยะเวลาเรา "ยิ้ม" แล้วค่ามันแกว่ง
                if diff_yaw > 40 or diff_pitch > 25: is_distracted = True
                elif diff_yaw > 15 and ((yaw < calibrator.base_yaw and iris_pos == 'LEFT') or (yaw > calibrator.base_yaw and iris_pos == 'RIGHT')):
                     is_distracted = True

                trig_distract, prog_distract = timer_distract.update(is_distracted)

                # ==========================
                # 4. SCORING & UI
                # ==========================
                # can_heal จะเป็น True ก็ต่อเมื่อ ไม่ได้ถูก Lock สถานะหลับอยู่
                can_heal = not is_sleep_locked

                curr_score = score_mgr.update(final_is_sleeping, is_yawning, is_distracted, is_rapid_blink, can_heal)
                lvl_text, lvl_color = score_mgr.get_level()

                # Draw UI
                hud.draw_info_panel(frame, curr_score, len(blink_timestamps), lvl_text, lvl_color)
                
                # แสดง Alert กระพริบตาถี่ (ซ้อนตรง Yawn)
                if is_rapid_blink:
                     hud.draw_bar(frame, f"Rapid Blink ({blink_rate})", 1.0, 1.0, 30, 440, (0, 0, 255))
                else:
                     c_yawn = (0, 0, 255) if is_yawning else (0, 255, 0)
                     hud.draw_bar(frame, "Yawn", prog_yawn, 1.0, 30, 440, c_yawn)

                c_sleep = (0, 0, 255) if final_is_sleeping else (0, 255, 0)
                hud.draw_bar(frame, "Sleep", display_prog_sleep, 1.0, 30, 400, c_sleep)
                
                c_dist = (0, 0, 255) if is_distracted else (0, 255, 0)
                hud.draw_bar(frame, f"Focus ({iris_pos})", prog_distract, 1.0, 30, 480, c_dist)

                # 4. Debug Info (ตามที่ขอ)
                hud.draw_debug(frame, ear, mar, pitch, yaw, iris_pos, fps)

                # Warnings
                if is_sleep_locked:
                    # โชว์หลอด Recovery แทนว่าเหลืออีกกี่วิถึงจะหาย
                    rec_p = int(timer_recovery.progress * 100)
                    hud.draw_warning(frame, f"OPEN EYES! {rec_p}%")
                elif trig_yawn: hud.draw_warning(frame, "TAKE A BREAK")
                elif trig_distract: hud.draw_warning(frame, "EYES ON ROAD")
                elif is_rapid_blink: hud.draw_warning(frame, "TIRED EYES?")

            else:
                cv2.putText(frame, "Press 'c' to Start", (200, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow(WINDOW_NAME, frame)
        key = cv2.waitKey(5) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c') and mode == "IDLE":
            mode = "CALIBRATING"
            calibrator.start()
        elif key == ord('m'): # Toggle Mesh
            show_mesh = not show_mesh

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()