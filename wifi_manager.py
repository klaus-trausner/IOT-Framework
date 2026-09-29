import network
import asyncio
import wdt_manager
import config

try: 
    import webrepl 
    WEBREPL_AVAILABLE = True 
except ImportError: 
    WEBREPL_AVAILABLE = False

# Globale Events  &  Status
wifi_connected_event = asyncio.Event()
IP_adress = None

async def connect_wifi(ssid, password, check_interval=5):
    global IP_adress
    wlan = network.WLAN(network.STA_IF)

    # 1\. Hostname setzen (für neuere MicroPython-Versionen ab v1.20
    try: 
        network.hostname(config.DEVICE_HOSTNAME) 
    except (AttributeError, TypeError): 
        pass

    wlan.active(True)

    print("📶 WLAN Manager gestartet...")

    while True:
        wdt_manager.feed_task("wifi_manager")
        if not wlan.isconnected():
            wifi_connected_event.clear()
            print(f"🔗 Verbinde mit WLAN '{ssid}'...")

            wlan.connect(ssid, password)

            timeout = 10
            while not wlan.isconnected() and timeout > 0:
                wdt_manager.feed_task("wifi_manager")
                await asyncio.sleep(1)
                timeout -= 1

            if wlan.isconnected():
                IP_adress = wlan.ifconfig()[0]
                print(f"✅ WLAN verbunden! IP: {IP_adress}")
                
                wifi_connected_event.set()

                # WebREPL-Server über WLAN starten 
                if WEBREPL_AVAILABLE: 
                    try: 
                        webrepl.start() 
                        print("🌐 WebREPL gestartet!") 
                    except Exception as e: 
                        print(f"⚠️ WebREPL Start-Fehler: {e}")


            else:
                print("❌ WLAN-Verbindung fehlgeschlagen. Nächster Versuch in Kürze...")

                
        wdt_manager.feed_task("wifi_manager")
        await asyncio.sleep(check_interval)
        
        