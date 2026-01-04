import time

class EventTimer:
    def __init__(self, limit_seconds):
        self.limit = limit_seconds
        self.start_time = None
        self.progress = 0.0 # 0.0 ถึง 1.0
        self.triggered = False

    def update(self, condition_met):
        """
        condition_met: True ถ้ากำลังเกิดเหตุการณ์ (เช่น หลับตาอยู่)
        return: (is_triggered, progress)
        """
        if condition_met:
            if self.start_time is None:
                self.start_time = time.time()
            
            # คำนวณเวลาที่ผ่านไป
            elapsed = time.time() - self.start_time
            self.progress = min(elapsed / self.limit, 1.0)
            
            if elapsed >= self.limit:
                self.triggered = True
        else:
            # รีเซ็ตถ้ายกเลิกเงื่อนไข
            self.start_time = None
            self.progress = 0.0
            self.triggered = False
            
        return self.triggered, self.progress