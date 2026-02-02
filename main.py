import bluetooth
import time
import json
from config import settings
from led_manager import LedManager

print(f"\n{'='*30}\n💎 VECTOR: SMART CONNECT\n{'='*30}")

# --- НАСТРОЙКИ ---
PIN_LED = settings.get("LED_PIN")
# Егер 200 диод болса, BLE-ге өте ауыр! Бастапқыда 20-50 қылып көр.
NUM_LEDS = settings.get("NUM_LEDS") 
DEVICE_NAME = "Vector_Party"

leds = LedManager(PIN_LED, NUM_LEDS)

# --- BLUETOOTH ---
ble = bluetooth.BLE()
ble.active(True)
UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
TX_UUID   = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")
RX_UUID   = bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")

current_mode = "RAINBOW" 
custom_color = (255, 255, 255)

# БАЙЛАНЫС СТАТУСЫ
conn_handle = None
# Жаңа қосылғанда диодтарды тоқтатып тұру үшін таймер
connection_start_time = 0 

def ble_irq(event, data):
    global conn_handle, connection_start_time, current_mode, custom_color
    
    # 1. ҚОСЫЛДЫ
    if event == 1:
        conn_handle = data[0]
        # Қосылған сәтте уақытты белгілейміз
        connection_start_time = time.ticks_ms()
        print("🔵 Connected! (PAUSING LEDs for stability...)")
        
    # 2. ҮЗІЛДІ
    elif event == 2:
        conn_handle = None
        print("⚪ Disconnected. Restarting Adv...")
        advertise()
        
    # 3. КОМАНДА КЕЛДІ
    elif event == 3:
        _, attr_handle = data
        try:
            msg = ble.gatts_read(attr_handle).decode().strip()
            print(f"📥 CMD: {msg}")
            
            if msg.startswith("{"):
                try:
                    data = json.loads(msg)
                    if "color" in data:
                        c = data["color"]
                        custom_color = (c[0], c[1], c[2])
                        current_mode = "SOLID" 
                except: pass
            else:
                cmd = msg.upper()
                COLOR_MAP = {
                    "RED": (255, 0, 0), "GREEN": (0, 255, 0), "BLUE": (0, 0, 255),
                    "WHITE": (255, 255, 255), "ORANGE": (255, 100, 0), "PINK": (255, 0, 100)
                }
                if cmd in COLOR_MAP:
                    current_mode = "SOLID"
                    custom_color = COLOR_MAP[cmd]
                else:
                    current_mode = cmd
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
    # 100ms интервал (ең тұрақтысы)
    ble.gap_advertise(100000, adv)

# --- ГЛАВНЫЙ ЦИКЛ ---
def run():
    setup_ble()
    print("🚀 Ready. Waiting for connection...")
    
    while True:
        try:
            # === МАҢЫЗДЫ ЛОГИКА ===
            # Егер жаңа ғана қосылсақ (алғашқы 3 секунд), 
            # LED-ке тиіспейміз! Bluetooth сервистерін жіберіп алсын.
            if conn_handle is not None:
                if time.ticks_diff(time.ticks_ms(), connection_start_time) < 3000:
                    # 3 секунд тыныштық
                    time.sleep(0.1)
                    continue 

            # Қалыпты режим
            if current_mode == "SOLID":
                leds.fill(custom_color[0], custom_color[1], custom_color[2])
                time.sleep(0.1) 

            elif current_mode == "RAINBOW":
                leds.rainbow()
                
            elif current_mode == "FIRE": leds.fire()
            elif current_mode == "METEOR": leds.meteor(0, 200, 255)
            elif current_mode == "POLICE": leds.police()
            elif current_mode == "OFF": 
                leds.clear()
                time.sleep(0.2)
            else:
                leds.rainbow()

            # Bluetooth-қа уақыт бөлу
            time.sleep(0.05) 

        except Exception as e:
            print(f"Loop Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        run()
    except:
        pass