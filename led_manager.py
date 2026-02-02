import time
import math
import random
from machine import Pin
from neopixel import NeoPixel

class LedManager:
    def __init__(self, pin, count):
        self.np = NeoPixel(Pin(pin), count)
        self.count = count

    def fill(self, r, g, b):
        """Заливка всей ленты"""
        for i in range(self.count):
            self.np[i] = (r, g, b)
        self.np.write()

    def clear(self):
        """Полное выключение"""
        self.fill(0, 0, 0)

    # --- ЭФФЕКТЫ ИСКР ---

    def sparks(self, r=255, g=255, b=255, count=2, wait=0.03):
        """Белые искры ПОВЕРХ текущего цвета (не стирая фон)"""
        original = [self.np[i] for i in range(self.count)]
        indices = [random.randint(0, self.count - 1) for _ in range(count)]
        for idx in indices: self.np[idx] = (r, g, b)
        self.np.write()
        time.sleep(wait)
        for idx in indices: self.np[idx] = original[idx]
        self.np.write()

    def sparks_on_black(self, count=2, wait=0.05):
        """Искры на полностью ВЫКЛЮЧЕННОЙ ленте"""
        self.clear() # Сначала всё тушим
        indices = [random.randint(0, self.count - 1) for _ in range(count)]
        for idx in indices:
            self.np[idx] = (255, 255, 255) # Ярко-белый
        self.np.write()
        time.sleep(wait)
        for idx in indices:
            self.np[idx] = (0, 0, 0) # Снова тушим
        self.np.write()

    # --- ОСТАЛЬНЫЕ ЭФФЕКТЫ ---

    def show_status(self, co2):
        """Стандартный режим CO2"""
        if co2 == 0:    self.fill(0, 0, 50)    # Синий
        elif co2 < 800: self.fill(0, 255, 0)   # Зеленый
        elif co2 < 1100: self.fill(255, 100, 0) # Оранжевый
        else:           self.fill(255, 0, 0)   # Красный

    def breathe(self, r, g, b):
        """Плавное дыхание"""
        for i in range(50):
            s = (math.sin(i * 0.12) + 1) / 2
            self.fill(int(r*s), int(g*s), int(b*s))
            time.sleep(0.02)

    def meteor(self, r, g, b, size=4, speed=0.05):
        """Пролетающий метеор"""
        for i in range(self.count + size):
            for j in range(self.count):
                curr = self.np[j]
                self.np[j] = (int(curr[0]*0.6), int(curr[1]*0.6), int(curr[2]*0.6))
            for j in range(size):
                if 0 <= i - j < self.count:
                    self.np[i - j] = (r, g, b)
            self.np.write()
            time.sleep(speed)

    def fire(self):
        """Мерцание огня"""
        r = random.randint(200, 255)
        g = random.randint(50, 100)
        self.fill(r, g, 0)
        time.sleep(random.uniform(0.05, 0.15))

    def scanner(self, r, g, b, speed=0.04):
        """Бегущий блик туда-сюда"""
        for i in range(self.count):
            self.clear(); self.np[i] = (r,g,b); self.np.write(); time.sleep(speed)
        for i in range(self.count-2, 0, -1):
            self.clear(); self.np[i] = (r,g,b); self.np.write(); time.sleep(speed)

    def rainbow(self, wait=0.01):
        """Радуга"""
        for j in range(255):
            for i in range(self.count):
                idx = (i * 256 // self.count) + j
                self.np[i] = self._wheel(idx & 255)
            self.np.write()
            time.sleep(wait)

    def _wheel(self, pos):
        if pos < 85: return (pos * 3, 255 - pos * 3, 0)
        elif pos < 170: return (255 - (pos-85) * 3, 0, (pos-85) * 3)
        else: return (0, (pos-170) * 3, 255 - (pos-170) * 3)