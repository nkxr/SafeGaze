import time
import numpy as np
from src.config import CALIBRATION_TIME

class Calibrator:
    def __init__(self):
        self.data_ear = []
        self.data_mar = []
        self.data_yaw = []
        self.data_pitch = []
        
        self.start_time = None
        self.is_calibrating = False
        self.is_finished = False
        
        # ผลลัพธ์ (Thresholds)
        self.thresh_ear = 0.25 # ค่า default เผื่อไว้
        self.thresh_mar = 0.5
        self.base_yaw = 0
        self.base_pitch = 0

    def start(self):
        self.is_calibrating = True
        self.start_time = time.time()
        self.data_ear = []
        self.data_mar = []
        self.data_yaw = []
        self.data_pitch = []
        print("Starting Calibration... Keep face neutral.")

    def update(self, ear, mar, pitch, yaw):
        if not self.is_calibrating:
            return

        # เก็บข้อมูลใส่ List
        self.data_ear.append(ear)
        self.data_mar.append(mar)
        self.data_yaw.append(yaw)
        self.data_pitch.append(pitch)

        # เช็คเวลา
        elapsed = time.time() - self.start_time
        if elapsed >= CALIBRATION_TIME:
            self._calculate_thresholds()
            self.is_calibrating = False
            self.is_finished = True
            print(f"Calibration Done! EAR: {self.thresh_ear:.2f}, MAR: {self.thresh_mar:.2f}")

    def get_progress(self):
        if not self.is_calibrating or self.start_time is None:
            return 0.0
        return min((time.time() - self.start_time) / CALIBRATION_TIME, 1.0)

    def _calculate_thresholds(self):
        avg_ear = np.mean(self.data_ear)
        avg_mar = np.mean(self.data_mar)
        
        # แก้ตรงนี้: จาก 0.8 เป็น 0.6
        # ความหมาย: ค่า EAR ต้องต่ำกว่า 60% ของตอนลืมตา ถึงจะนับว่าหลับ
        # (ช่วยแก้เรื่องหรี่ตาแล้วโดนจับได้ชะงัดนัก)
        self.thresh_ear = avg_ear * 0.6  
        
        # ปากเอาเหมือนเดิม เพราะดีอยู่แล้ว
        self.thresh_mar = avg_mar + 0.3  
        
        self.base_yaw = np.mean(self.data_yaw)
        self.base_pitch = np.mean(self.data_pitch)