# logic/scoring.py
import time

class ScoreManager:
    def __init__(self):
        self.score = 0.0
        self.max_score = 100
        self.last_update = time.time()
        
        self.PENALTY_SLEEP = 20.0   # เพิ่มความรุนแรง
        self.PENALTY_YAWN = 5.0
        self.PENALTY_DISTRACT = 8.0
        self.PENALTY_BLINK = 10.0    # โทษฐานกระพริบตาถี่
        self.HEAL_RATE = 2.0

    def update(self, is_sleeping, is_yawning, is_distracted, is_rapid_blink, can_heal):
        now = time.time()
        dt = now - self.last_update
        self.last_update = now

        # เพิ่มคะแนนตามความผิด
        if is_sleeping:
            self.score += self.PENALTY_SLEEP * dt
        elif is_yawning:
            self.score += self.PENALTY_YAWN * dt
        elif is_distracted:
            self.score += self.PENALTY_DISTRACT * dt
        elif is_rapid_blink:
            self.score += self.PENALTY_BLINK * dt
        
        # ถ้าไม่มีความผิด และ "อนุญาตให้ฮีลได้" (can_heal) ค่อยลดคะแนน
        elif can_heal:
            self.score -= self.HEAL_RATE * dt

        self.score = max(0.0, min(self.score, self.max_score))
        return int(self.score)

    def get_level(self):
        if self.score < 20: return "FRESH", (0, 255, 0)
        elif self.score < 50: return "TIRED", (0, 255, 255)
        elif self.score < 80: return "DROWSY", (0, 165, 255)
        else: return "DANGER", (0, 0, 255)