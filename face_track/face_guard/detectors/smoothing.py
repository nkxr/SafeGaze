class SmoothValue:
    def __init__(self, alpha=0.5):
        """
        alpha: ค่าความหน่วง (0.1 = หน่วงมาก/ลื่นมาก, 0.9 = ไวมาก/สั่น)
        """
        self.alpha = alpha
        self.value = None

    def update(self, new_value):
        if self.value is None:
            self.value = new_value
        else:
            # สูตร Exponential Moving Average
            self.value = (self.alpha * new_value) + ((1 - self.alpha) * self.value)
        return self.value