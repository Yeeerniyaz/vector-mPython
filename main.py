import bluetooth
import time
import json
from config import settings #
from led_manager import LedManager

print(f"\n{'='*30}\n💎 VECTOR: SUPER CONTROLLER\n{'='*30}")

# --- НАСТРОЙКИ ---
PIN_LED = settings.get("LED_PIN")
NUM_LEDS = settings.get("NUM_LEDS")
DEVICE_NAME = "Vector_Party"

# Лентаны қосамыз
leds = LedManager(PIN_LED, NUM_LEDS)

# --- BLUETOOTH ---
ble = bluetooth.BLE()
ble.active(True)
UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
TX_UUID   = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")
RX_UUID   = bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")

# Ағымдағы режим
current_mode = "RAINBOW" 
custom_color = (255, 255, 255) # Дефолт түс (ақ)

conn_handle = None

def ble_irq(event, data):
    global conn_handle, current_mode, custom_color
    if event == 1:
        conn_handle = data[0]
        print("🔵 Connected")
    elif event == 2:
        conn_handle = None
        print("⚪ Disconnected")
        advertise()
    elif event == 3: # Команда келді
        _, attr_handle = data
        try:
            msg = ble.gatts_read(attr_handle).decode().strip()
            print(f"📥 CMD: {msg}")
            
            # Егер JSON келсе (Түсті таңдау үшін) -> {"color": [255, 0, 100]}
            if msg.startswith("{"):
                try:
                    data = json.loads(msg)
                    if "color" in data:
                        c = data["color"]
                        custom_color = (c[0], c[1], c[2])
                        current_mode = "SOLID" # Тұрақты түс режиміне өтеміз
                except: pass
            
            # Егер ТЕКСТ келсе (Режимдер)
            else:
                cmd = msg.upper()
                # Тексеру: Бұл режим бе әлде түс пе?
                if cmd in ["RED", "GREEN", "BLUE", "WHITE", "ORANGE", "PINK"]:
                    current_mode = "SOLID"
                    if cmd == "RED": custom_color = (255, 0, 0)
                    if cmd == "GREEN": custom_color = (0, 255, 0)
                    if cmd == "BLUE": custom_color = (0, 0, 255)
                    if cmd == "WHITE": custom_color = (255, 255, 255)
                    if cmd == "ORANGE": custom_color = (255, 100, 0)
                    if cmd == "PINK": custom_color = (255, 0, 100)
                else:
                    current_mode = cmd # FIRE, RAINBOW, POLICE...
                    leds.clear()

        except Exception as e:
            print(f"Error parsing: {e}")

def setup_ble():
    ((tx, rx),) = ble.gatts_register_services((
        (UART_UUID, ((TX_UUID, bluetooth.FLAG_NOTIFY), (RX_UUID, bluetooth.FLAG_WRITE),)),
    ))
    ble.irq(ble_irq)
    advertise()

def advertise():
    name = bytes(DEVICE_NAME, 'UTF-8')
    adv = bytearray(b'\x02\x01\x06') + bytearray((len(name)+1, 0x09)) + name
    ble.gap_advertise(100, adv)

# --- ГЛАВНЫЙ ЦИКЛ ---
def run():
    setup_ble()
    print("🚀 Ready to Party! Send commands...")
    
    while True:
        try:
            # Режимдерді ойнату
            if current_mode == "SOLID":
                leds.fill(custom_color[0], custom_color[1], custom_color[2])
                time.sleep(0.1) # Процессорды қыздырмау үшін

            elif current_mode == "RAINBOW":
                leds.rainbow() # Шексіз айналады

            elif current_mode == "FIRE":
                leds.fire()

            elif current_mode == "METEOR":
                leds.meteor(0, 200, 255) # Көгілдір метеор

            elif current_mode == "METEOR_RED":
                leds.meteor(255, 50, 0) # Отты метеор

            elif current_mode == "POLICE":
                leds.police()

            elif current_mode == "STROBE":
                leds.strobe(255, 255, 255) # Ақ стробоскоп

            elif current_mode == "BREATHE":
                leds.breathe(custom_color[0], custom_color[1], custom_color[2]) # Таңдалған түспен дем алу

            elif current_mode == "SPARKLE":
                leds.sparkle(255, 255, 255) # Ақ жұлдыздар

            elif current_mode == "SCANNER":
                leds.scanner(255, 0, 0) # Қызыл KITT

            elif current_mode == "RANDOM":
                leds.random_color()

            elif current_mode == "OFF":
                leds.clear()
                time.sleep(0.1)
                
            else:
                # Егер белгісіз команда болса -> Rainbow
                leds.rainbow()

        except Exception as e:
            print(f"Loop Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        run()
    except:
        pass