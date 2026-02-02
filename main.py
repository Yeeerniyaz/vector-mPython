from machine import I2C, Pin
import time
import struct

# --- НАСТРОЙКИ ---
PIN_SDA = 21
PIN_SCL = 22
ENS_ADDR = 0x53

def test_missing_part():
    print(f"\n{'='*40}\n🩹 ТЕСТ ПОСЛЕ АВАРИИ\n{'='*40}")
    
    # Пробуем инициализировать шину
    try:
        i2c = I2C(0, scl=Pin(PIN_SCL), sda=Pin(PIN_SDA), freq=100000)
    except:
        print("❌ Ошибка I2C шины (возможно, отвалился резистор подтяжки)")
        return

    # Сканируем
    print("🔎 Ищем выживших...")
    devices = i2c.scan()
    
    if len(devices) == 0:
        print("❌ Никого нет. Похоже, отвалилась важная деталь (SDA/SCL или питание).")
        return
    else:
        print(f"✅ НАЙДЕНЫ УСТРОЙСТВА: {[hex(d) for d in devices]}")
        if ENS_ADDR in devices:
            print("🎉 ENS160 НА СВЯЗИ! (Тебе повезло, деталь была лишней)")
            
            # Контрольный выстрел: читаем ID
            try:
                part_id = i2c.readfrom_mem(ENS_ADDR, 0x00, 2)
                print(f"🆔 ID Чипа: {hex(struct.unpack('<H', part_id)[0])}")
            except: 
                print("⚠️ Вижу, но читать не могу.")
        else:
            print(f"⚠️ Вижу кого-то другого, но не ENS160 ({hex(ENS_ADDR)})")

if __name__ == "__main__":
    test_missing_part()