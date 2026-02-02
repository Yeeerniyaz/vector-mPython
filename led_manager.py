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
        """1. Тұрақты түс"""
        for i in range(self.count):
            self.np[i] = (r, g, b)
        self.np.write()

    def clear(self):
        """Өшіру"""
        self.fill(0, 0, 0)

    # --- ЭФФЕКТЫ ---

    def rainbow(self):
        """2. Кемпірқосақ (Жылжымалы)"""
        # Тек бір қадам жасаймыз, цикл main.py-да болады
        self.rainbow_step = getattr(self, 'rainbow_step', 0) + 3
        for i in range(self.count):
            idx = (i * 256 // self.count) + self.rainbow_step
            self.np[i] = self._wheel(idx & 255)
        self.np.write()

    def fire(self):
        """3. Алау (От)"""
        for i in range(self.count):
            flicker = random.randint(0, 50)
            r = 255 - flicker
            g = 90 - flicker
            if g < 0: g = 0
            self.np[i] = (r, g, 0)
        self.np.write()
        time.sleep(random.uniform(0.01, 0.05))

    def meteor(self, r, g, b, tail_size=10, decay=0.75):
        """4. Метеор (Комета)"""
        # Тазалау (Fade out)
        for j in range(self.count):
            curr = self.np[j]
            if curr[0] > 10 or curr[1] > 10 or curr[2] > 10: # Егер жанып тұрса
                self.np[j] = (int(curr[0]*decay), int(curr[1]*decay), int(curr[2]*decay))
            else:
                self.np[j] = (0,0,0)
        
        # Метеор басының позициясы
        self.meteor_pos = getattr(self, 'meteor_pos', 0) + 1
        if self.meteor_pos >= self.count: self.meteor_pos = 0

        # Басын жағу
        for i in range(tail_size):
            if 0 <= self.meteor_pos - i < self.count:
                # Басы ашық, құйрығы сөніңкі
                fade = 1.0 - (i / tail_size)
                self.np[self.meteor_pos - i] = (int(r*fade), int(g*fade), int(b*fade))
        
        self.np.write()

    def police(self):
        """5. Полиция (Қызыл-Көк жыпылықтау)"""
        self.police_step = getattr(self, 'police_step', 0) + 1
        
        # Жартысы қызыл, жартысы көк
        mid = self.count // 2
        
        if self.police_step % 10 < 5: # 5 кадр Қызыл
            for i in range(0, mid): self.np[i] = (255, 0, 0)
            for i in range(mid, self.count): self.np[i] = (0, 0, 0)
        else: # 5 кадр Көк
            for i in range(0, mid): self.np[i] = (0, 0, 0)
            for i in range(mid, self.count): self.np[i] = (0, 0, 255)
            
        self.np.write()
        time.sleep(0.05)

    def strobe(self, r, g, b):
        """6. Стробоскоп (Дискотека)"""
        self.fill(r, g, b)
        time.sleep(0.05)
        self.clear()
        time.sleep(0.05)

    def breathe(self, r, g, b):
        """7. Дем алу (Плавная пульсация)"""
        self.breath_val = getattr(self, 'breath_val', 0)
        self.breath_dir = getattr(self, 'breath_dir', 1)
        
        # Жарықтықты өзгертеміз (0-100)
        self.breath_val += (2 * self.breath_dir)
        if self.breath_val >= 100: self.breath_dir = -1
        if self.breath_val <= 5: self.breath_dir = 1
        
        k = self.breath_val / 100.0
        self.fill(int(r*k), int(g*k), int(b*k))
        time.sleep(0.01)

    def sparkle(self, r, g, b):
        """8. Жұлдыздар (Sparkle)"""
        # Кездейсоқ пикселді жағамыз
        pixel = random.randint(0, self.count - 1)
        self.np[pixel] = (r, g, b)
        self.np.write()
        # Және тез өшіреміз (келесі кадрда)
        self.np[pixel] = (0, 0, 0)
        time.sleep(0.01)

    def random_color(self):
        """9. Рандом түстер (Хаос)"""
        for i in range(self.count):
            self.np[i] = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        self.np.write()
        time.sleep(0.2)

    def scanner(self, r, g, b):
        """10. Сканер (KITT / Cylon)"""
        self.scan_pos = getattr(self, 'scan_pos', 0)
        self.scan_dir = getattr(self, 'scan_dir', 1)
        
        self.clear()
        self.np[self.scan_pos] = (r, g, b)
        
        # Құйрық қосуға болады (қарапайым болу үшін бір пиксел)
        if self.scan_pos > 0: 
            self.np[self.scan_pos-1] = (int(r*0.3), int(g*0.3), int(b*0.3))
            
        self.np.write()
        
        self.scan_pos += self.scan_dir
        if self.scan_pos >= self.count - 1: self.scan_dir = -1
        if self.scan_pos <= 0: self.scan_dir = 1
        time.sleep(0.02)

    def _wheel(self, pos):
        if pos < 85: return (pos * 3, 255 - pos * 3, 0)
        elif pos < 170: return (255 - (pos-85) * 3, 0, (pos-85) * 3)
        else: return (0, (pos-170) * 3, 255 - (pos-170) * 3)