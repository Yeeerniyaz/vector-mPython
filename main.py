import bluetooth
import time
import json
import micropython
from config import settings
from led_manager import LedManager

# 1. Қателерді ұстау үшін буфер бөлеміз (Crash болса себебін көру үшін)
micropython.alloc_emergency_exception_buf(100)

print(f"\n{'='*30}\n💎 VECTOR: STABLE v2.1\n{'='*30}")

# --- НАСТРОЙКИ ---
PIN_LED = settings.get("LED_PIN")
NUM_LEDS = settings.get("NUM_LEDS") 
DEVICE_NAME = "Vector_Party"

# LED менеджерді іске қосу
leds = LedManager(PIN_LED, NUM_LEDS)

# --- BLUETOOTH БАПТАУЛАРЫ ---
ble = bluetooth.BLE()
ble.active(True)

UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
TX_UUID   = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")
RX_UUID   = bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")

# Глобалды айнымалылар (күйді сақтау үшін)
current_mode = "RAINBOW" 
custom_color = (255, 255, 255)
conn_handle = None

# ⚠️ ФЛАГТАР (IRQ мен Main Loop арасында сөйлесу үшін)
# IRQ ішінде тек осыларды өзгертеміз, ауыр код жазбаймыз!
ble_state = {
    "connected": False,
    "new_msg": False,
    "buffer": None
}

def ble_irq(event, data):
    global conn_handle
    
    # 1. ҚОСЫЛДЫ (_IRQ_CENTRAL_CONNECT)
    if event == 1: 
        conn_handle = data[0]
        ble_state["connected"] = True
        # Мұнда print() ЖОҚ!
        
    # 2. ҮЗІЛДІ (_IRQ_CENTRAL_DISCONNECT)
    elif event == 2: 
        conn_handle = None
        ble_state["connected"] = False
        # Жарнаманы қайта қосуды main loop-та жасаймыз
        
    # 3. КОМАНДА КЕЛДІ (_IRQ_GATTS_WRITE)
    elif event == 3: 
        conn_h, attr_handle = data
        try:
            # Деректерді оқимыз да, буферге саламыз
            ble_state["buffer"] = ble.gatts_read(attr_handle)
            ble_state["new_msg"] = True
        except:
            pass

def setup_ble():
    ((tx, rx),) = ble.gatts_register_services((
        (UART_UUID, ((TX_UUID, bluetooth.FLAG_NOTIFY), (RX_UUID, bluetooth.FLAG_WRITE),)),
    ))
    ble.irq(ble_irq)

# Жарнама пакетін алдын-ала дайындаймыз
name_bytes = bytes(DEVICE_NAME, 'UTF-8')
adv_data = bytearray(b'\x02\x01\x06') + bytearray((len(name_bytes)+1, 0x09)) + name_bytes

def advertise():
    # 100ms интервалмен жарнамалау
    ble.gap_advertise(100000, adv_data)

# --- ГЛАВНЫЙ ЦИКЛ ---
def run():
    setup_ble()
    advertise()
    print("🚀 Ready. Waiting for connection...")
    
    # Күйді бақылау үшін (консольге қайта-қайта шығармау үшін)
    prev_connected = False
    last_adv_time = 0
    
    while True:
        try:
            now = time.ticks_ms()

            # ---------------------------------------
            # 1. БАЙЛАНЫС КҮЙІН ӨҢДЕУ
            # ---------------------------------------
            if ble_state["connected"]:
                if not prev_connected:
                    print("🔵 Connected! (Stable)")
                    prev_connected = True
                    # Қосылған соң 3 секунд тұрақталуын күтеміз (қалауың бойынша)
                    time.sleep(0.5) 
            else:
                if prev_connected:
                    print("⚪ Disconnected. Restarting Adv...")
                    prev_connected = False
                    advertise() # Қайта жарнамалау
                
                # Сақтандыру: Егер үзілген болса, әр 5 секунд сайын жарнаманы тексереміз
                if time.ticks_diff(now, last_adv_time) > 5000:
                    advertise()
                    last_adv_time = now

            # ---------------------------------------
            # 2. ХАБАРЛАМАЛАРДЫ ӨҢДЕУ (Парсинг)
            # ---------------------------------------
            if ble_state["new_msg"]:
                ble_state["new_msg"] = False # Флагты түсіреміз
                raw_data = ble_state["buffer"]
                
                if raw_data:
                    try:
                        msg = raw_data.decode().strip()
                        print(f"📥 CMD: {msg}") # Енді print жасауға болады!

                        # JSON тексеру
                        if msg.startswith("{"):
                            try:
                                data = json.loads(msg)
                                if "color" in data:
                                    c = data["color"]
                                    custom_color = (c[0], c[1], c[2])
                                    global current_mode
                                    current_mode = "SOLID"
                            except:
                                print("JSON Error")
                        
                        # ТЕКСТ тексеру
                        else:
                            cmd = msg.upper()
                            COLOR_MAP = {
                                "RED": (255, 0, 0), "GREEN": (0, 255, 0), "BLUE": (0, 0, 255),
                                "WHITE": (255, 255, 255), "ORANGE": (255, 100, 0), "PINK": (255, 0, 100)
                            }
                            if cmd in COLOR_MAP:
                                current_mode = "SOLID"
                                custom_color = COLOR_MAP[cmd]
                            elif cmd == "OFF":
                                current_mode = "OFF"
                            else:
                                # Егер белгісіз команда болса, режим деп қабылдаймыз
                                current_mode = cmd
                                leds.clear()
                                
                    except Exception as e:
                        print(f"Msg Error: {e}")

            # ---------------------------------------
            # 3. LED ЭФФЕКТІЛЕРІ
            # ---------------------------------------
            if current_mode == "SOLID":
                leds.fill(custom_color[0], custom_color[1], custom_color[2])
                time.sleep(0.05) # Процессорды демалдыру
            
            elif current_mode == "RAINBOW":
                leds.rainbow()
            
            elif current_mode == "FIRE": 
                leds.fire()
            
            elif current_mode == "METEOR":
                 leds.meteor(0, 200, 255)
            
            elif current_mode == "POLICE":
                 leds.police()
            
            elif current_mode == "OFF": 
                leds.clear()
                time.sleep(0.1)
            
            else:
                # Default
                leds.rainbow()
            
            # Циклдің тым жылдам айналмауы үшін кішкене кідіріс
            time.sleep(0.01)

        except Exception as e:
            print(f"Main Loop Crash: {e}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(f"Fatal: {e}")