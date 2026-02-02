import json
import os

# Имя файла во внутренней памяти ESP32
CONFIG_FILE = "device_settings.json"

# Настройки по умолчанию
_defaults = {
    "DEVICE_NAME": "Vector_Sensor",
    "NUM_LEDS": 200,      # Твои текущие 200 диодов
    "LED_PIN": 4,
    "I2C_SDA": 21,
    "I2C_SCL": 22,
    "ENS_ADDR": 0x53,     # Твой живой датчик
    "BRIGHTNESS": 1.0     # От 0.0 до 1.0
}

def load_config():
    """Загружает конфиг из файла или создает его из дефолтов"""
    try:
        if CONFIG_FILE in os.listdir():
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                # Проверяем, что все ключи из дефолта есть в файле
                for key in _defaults:
                    if key not in data:
                        data[key] = _defaults[key]
                return data
        else:
            # Если файла нет, создаем его с дефолтными настройками
            print("📝 Создаю новый файл настроек...")
            save_config(_defaults)
            return _defaults
    except Exception as e:
        print(f"⚠️ Ошибка конфига (вероятно, файл поврежден): {e}")
        return _defaults

def save_config(new_data):
    """Обновляет и сохраняет конфиг во Flash память"""
    try:
        # Всегда берем актуальное состояние перед обновлением
        if CONFIG_FILE in os.listdir():
            with open(CONFIG_FILE, "r") as f:
                current = json.load(f)
        else:
            current = _defaults.copy()
            
        current.update(new_data)
        
        with open(CONFIG_FILE, "w") as f:
            json.dump(current, f)
        print("💾 Настройки сохранены!")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return False

# Инициализация при импорте модуля
_current = load_config()

# Экспорт переменных для main.py и led_manager.py
DEVICE_NAME = _current["DEVICE_NAME"]
NUM_LEDS    = _current["NUM_LEDS"]
LED_PIN     = _current["LED_PIN"]
I2C_SDA     = _current["I2C_SDA"]
I2C_SCL     = _current["I2C_SCL"]
ENS_ADDR    = _current["ENS_ADDR"]
BRIGHTNESS  = _current["BRIGHTNESS"]