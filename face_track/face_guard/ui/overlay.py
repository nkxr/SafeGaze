# ui/overlay.py
import cv2
import numpy as np

class HUD:
    def __init__(self, width, height):
        self.W = width
        self.H = height
        self.C_GREEN = (0, 255, 0)
        self.C_RED = (0, 0, 255)
        self.C_YELLOW = (0, 255, 255)
        self.C_WHITE = (255, 255, 255)
        self.C_BG = (0, 0, 0)

    def draw_info_panel(self, frame, score, blink_count, drive_time, level_text, level_color):
        """แถบข้อมูลด้านบน (Top Bar)"""
        # แถบพื้นหลังสีดำด้านบน
        cv2.rectangle(frame, (0, 0), (self.W, 80), self.C_BG, -1)
        
        # 1. Fatigue Score (ซ้าย)
        cv2.putText(frame, "FATIGUE SCORE", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.C_WHITE, 1)
        cv2.putText(frame, f"{score}", (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.2, level_color, 3)
        
        # 2. Status Level (กลางซ้าย)
        cv2.putText(frame, f"STATUS: {level_text}", (200, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, level_color, 2)

        # 3. Drive Time (ขวา)
        hrs = int(drive_time // 3600)
        mins = int((drive_time % 3600) // 60)
        time_str = f"DRIVE: {hrs:02}h {mins:02}m"
        
        # จัดตำแหน่งชิดขวา
        time_size = cv2.getTextSize(time_str, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        cv2.putText(frame, time_str, (self.W - time_size[0] - 30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.C_WHITE, 2)
        
        blink_str = f"BLINKS: {blink_count}"
        blink_size = cv2.getTextSize(blink_str, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
        cv2.putText(frame, blink_str, (self.W - blink_size[0] - 30, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.C_WHITE, 1)

    def draw_bar(self, frame, label, value, max_val, index, color):
        """
        วาดหลอดพลัง (Bottom Left)
        index: ลำดับหลอด (0, 1, 2, ...)
        """
        bar_w = 250
        bar_h = 20
        gap = 40
        
        # คำนวณตำแหน่ง Y จากด้านล่างจอขึ้นมา
        start_y = self.H - 50 - (index * gap)
        x = 30
        
        # ชื่อหลอด
        cv2.putText(frame, label, (x, start_y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.C_WHITE, 1)
        
        # พื้นหลังหลอด
        cv2.rectangle(frame, (x, start_y), (x + bar_w, start_y + bar_h), (80, 80, 80), -1)
        
        # เนื้อหลอด
        ratio = min(max(value / max_val, 0.0), 1.0)
        fill_w = int(bar_w * ratio)
        cv2.rectangle(frame, (x, start_y), (x + fill_w, start_y + bar_h), color, -1)

    # ui/overlay.py (แก้เฉพาะฟังก์ชัน draw_debug)

    def draw_debug(self, frame, ear, mar, pitch, yaw, fps, nose_var): # <--- รับค่า nose_var เพิ่ม
        x = 30
        y = 150 
        color = (200, 200, 200)
        
        lines = [
            f"FPS:   {int(fps)}",
            f"EAR:   {ear:.2f}",
            f"MAR:   {mar:.2f}",
            f"PITCH: {int(pitch)}",
            f"YAW:   {int(yaw)}",
            f"VAR:   {nose_var:.2f}" # <--- โชว์ค่าความนิ่ง (ถ้าต่ำกว่า 15.0 = นิ่ง)
        ]
        
        for line in lines:
            cv2.putText(frame, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
            y += 25

    def draw_calibration(self, frame, progress):
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.W, self.H), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        cx, cy = self.W // 2, self.H // 2
        
        cv2.putText(frame, "CALIBRATION", (cx - 140, cy - 80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, self.C_YELLOW, 3)
        cv2.putText(frame, "Look Straight & Stay Still", (cx - 180, cy - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.C_WHITE, 1)
        
        # Progress Bar
        bar_w = 400
        start_x = cx - (bar_w // 2)
        cv2.rectangle(frame, (start_x, cy + 20), (start_x + bar_w, cy + 50), (100, 100, 100), -1)
        cv2.rectangle(frame, (start_x, cy + 20), (start_x + int(bar_w * progress), cy + 50), self.C_GREEN, -1)

    def draw_rest_screen(self, frame, rest_time):
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.W, self.H), (20, 50, 20), -1)
        cv2.addWeighted(overlay, 0.9, frame, 0.1, 0, frame)
        
        cx, cy = self.W // 2, self.H // 2
        mins = int(rest_time // 60)
        secs = int(rest_time % 60)
        
        cv2.putText(frame, "REST MODE", (cx - 150, cy - 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, self.C_WHITE, 3)
        cv2.putText(frame, f"{mins:02}:{secs:02}", (cx - 100, cy + 40), cv2.FONT_HERSHEY_SIMPLEX, 3.0, self.C_GREEN, 5)
        cv2.putText(frame, "Press 'r' to Resume", (cx - 120, cy + 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.C_YELLOW, 1)

    def draw_warning(self, frame, text, subtext=""):
        cx, cy = self.W // 2, self.H // 2
        
        # กล่องแดง
        cv2.rectangle(frame, (cx - 300, cy - 100), (cx + 300, cy + 100), (0, 0, 255), -1)
        cv2.rectangle(frame, (cx - 300, cy - 100), (cx + 300, cy + 100), (255, 255, 255), 4)
        
        # ตัวหนังสือ
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 2.0, 5)[0]
        tx = cx - (text_size[0] // 2)
        cv2.putText(frame, text, (tx, cy + 10), cv2.FONT_HERSHEY_SIMPLEX, 2.0, self.C_WHITE, 5)
        
        if subtext:
            sub_size = cv2.getTextSize(subtext, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
            sx = cx - (sub_size[0] // 2)
            cv2.putText(frame, subtext, (sx, cy + 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2)