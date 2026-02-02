import json
import os

CONFIG_FILE = "vector_settings.json"

default_settings = {
    "DEVICE_NAME": "Vector_Sensor",
    "NUM_LEDS": 200,
    "LED_PIN": 4,
    "ENS_ADDR": 0x53,
    "danger_co2": 1000,
    "send_interval": 1000,
    "brightness": 1.0
}

class ConfigManager:
    def __init__(self):
        self.data = default_settings.copy()
        self.load()

    def load(self):
        try:
            if CONFIG_FILE in os.listdir():
                with open(CONFIG_FILE, "r") as f:
                    saved = json.load(f)
                    self.data.update(saved)
            else:
                self.save()
        except:
            self.data = default_settings.copy()

    def save(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.data, f)
        except:
            pass

    def update(self, new_data):
        self.data.update(new_data)
        self.save()
        
    def get(self, key):
        return self.data.get(key, default_settings.get(key))

settings = ConfigManager()