import time
from machine import I2C

class AHT21:
    def __init__(self, i2c, addr=0x38):
        self.i2c = i2c
        self.addr = addr
        try:
            self.i2c.writeto(self.addr, b'\xBA') # Soft Reset
            time.sleep(0.02)
            self.i2c.writeto(self.addr, b'\xBE\x08\x00') # Calibrate
            time.sleep(0.01)
        except: pass

    def read(self):
        try:
            self.i2c.writeto(self.addr, b'\xAC\x33\x00')
            time.sleep(0.08)
            data = self.i2c.readfrom(self.addr, 7)
            if data[0] & 0x80: return None, None 
            hum = ((data[1] << 12) | (data[2] << 4) | (data[3] >> 4)) * 100 / 0x100000
            temp = (((data[3] & 0xF) << 16) | (data[4] << 8) | data[5]) * 200 / 0x100000 - 50
            return round(temp, 1), round(hum, 1)
        except: return None, None

class ENS160:
    def __init__(self, i2c, addr=0x53):
        self.i2c = i2c
        self.addr = addr
        self._init_sensor()

    def _init_sensor(self):
        try:
            # 1. Сброс и IDLE
            self.i2c.writeto_mem(self.addr, 0x10, b'\x00') # IDLE
            time.sleep(0.1)
            self.i2c.writeto_mem(self.addr, 0x10, b'\xF0') # RESET
            time.sleep(0.2)
            self.i2c.writeto_mem(self.addr, 0x10, b'\x00') # IDLE
            time.sleep(0.1)
            
            # 2. Обязательно "обманываем" датчик нормальной погодой для старта
            # (25C, 50%) - это нужно, чтобы он не выдавал 0
            t_val = int((25.0 + 273.15) * 64)
            h_val = int(50.0 * 512)
            env = bytearray([t_val & 0xFF, (t_val >> 8) & 0xFF, h_val & 0xFF, (h_val >> 8) & 0xFF])
            self.i2c.writeto_mem(self.addr, 0x13, env)
            
            # 3. Запуск Standard Mode
            self.i2c.writeto_mem(self.addr, 0x10, b'\x02') 
            time.sleep(0.5)
        except: pass

    def set_env(self, temp, hum):
        try:
            t_data = int((temp + 273.15) * 64)
            h_data = int(hum * 512)
            buf = bytearray([t_data & 0xFF, (t_data >> 8) & 0xFF, h_data & 0xFF, (h_data >> 8) & 0xFF])
            self.i2c.writeto_mem(self.addr, 0x13, buf)
        except: pass

    def read(self):
        try:
            status = self.i2c.readfrom_mem(self.addr, 0x20, 1)[0]
            # Проверяем бит "New Data" (бит 0)
            if status & 1:
                data = self.i2c.readfrom_mem(self.addr, 0x21, 5)
                aqi = data[0]
                tvoc = data[1] | (data[2] << 8)
                eco2 = data[3] | (data[4] << 8)
                return eco2, tvoc, aqi
            return None, None, None
        except: return None, None, None
