import cv2
import numpy as np

class HUD:
    def __init__(self, width, height):
        self.W = width
        self.H = height
        
        # สี (B, G, R)
        self.C_GREEN = (0, 255, 0)
        self.C_RED = (0, 0, 255)
        self.C_YELLOW = (0, 255, 255)
        self.C_WHITE = (255, 255, 255)
        self.C_BG = (50, 50, 50) # สีเทาเข้มพื้นหลัง

    def draw_info_panel(self, frame, score, blink_count, level_text, level_color):
        """วาดแผงคะแนนด้านบน"""
        # สร้างแถบดำด้านบน
        cv2.rectangle(frame, (0, 0), (self.W, 80), (0, 0, 0), -1)
        
        # 1. Fatigue Score (ซ้าย)
        cv2.putText(frame, "FATIGUE SCORE", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.C_WHITE, 1)
        cv2.putText(frame, f"{score}", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.2, level_color, 3)
        
        # 2. Status Level (กลาง)
        cv2.putText(frame, f"STATUS: {level_text}", (200, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, level_color, 2)

        # 3. Blinks (ขวา)
        cv2.putText(frame, f"BLINKS: {blink_count}", (self.W - 180, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.C_WHITE, 2)

    def draw_bar(self, frame, label, value, max_val, x, y, color):
        """วาดหลอดพลัง (Progress Bar)"""
        bar_w = 200
        bar_h = 20
        
        # ชื่อหลอด
        cv2.putText(frame, label, (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.C_WHITE, 1)
        
        # พื้นหลังหลอด (สีเทา)
        cv2.rectangle(frame, (x, y), (x + bar_w, y + bar_h), (100, 100, 100), -1)
        
        # เนื้อหลอด (สีตามสถานะ)
        ratio = value / max_val
        fill_w = int(bar_w * ratio)
        cv2.rectangle(frame, (x, y), (x + fill_w, y + bar_h), color, -1)

    def draw_calibration(self, frame, progress):
        """หน้าจอตอน Calibrate"""
        # ทำให้ภาพมืดลงหน่อย
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.W, self.H), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

        # ข้อความกลางจอ
        cx, cy = self.W // 2, self.H // 2
        cv2.putText(frame, "CALIBRATING...", (cx - 150, cy - 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, self.C_YELLOW, 2)
        cv2.putText(frame, "Look at the camera & Stay still", (cx - 200, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.8, self.C_WHITE, 1)
        
        # หลอดโหลด
        cv2.rectangle(frame, (cx - 150, cy + 50), (cx - 150 + int(300 * progress), cy + 80), self.C_GREEN, -1)
        cv2.rectangle(frame, (cx - 150, cy + 50), (cx + 150, cy + 80), self.C_WHITE, 2)

    def draw_warning(self, frame, text):
        """กล่องแจ้งเตือนสีแดงกลางจอ"""
        cx, cy = self.W // 2, self.H // 2
        cv2.rectangle(frame, (cx - 200, cy - 60), (cx + 200, cy + 60), (0, 0, 255), -1)
        cv2.rectangle(frame, (cx - 200, cy - 60), (cx + 200, cy + 60), (255, 255, 255), 2)
        
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
        text_x = cx - text_size[0] // 2
        text_y = cy + text_size[1] // 2
        
        cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        
    # ui/overlay.py (เพิ่ม method นี้ใน class HUD)

    def draw_debug(self, frame, ear, mar, pitch, yaw, iris_pos, fps):
        """แสดงค่าตัวเลขแบบละเอียด"""
        x, y = 30, 180
        color = (200, 200, 200) # สีเทาอ่อนๆ ไม่แย่งซีน
        
        lines = [
            f"FPS: {int(fps)}",
            f"EAR: {ear:.2f}",
            f"MAR: {mar:.2f}",
            f"Pitch: {int(pitch)}",
            f"Yaw: {int(yaw)}",
            f"Iris: {iris_pos}"
        ]
        
        for line in lines:
            cv2.putText(frame, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            y += 20