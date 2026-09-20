import network
import asyncio
import wdt_manager

# Globale Events  &  Status
wifi_connected_event = asyncio.Event()

async def connect_wifi(ssid, password, check_interval=5):
    wlan = network.WLAN(network.STA_IF)
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
                print(f"✅ WLAN verbunden! IP: {wlan.ifconfig()[0]}")
                wifi_connected_event.set()
            else:
                print("❌ WLAN-Verbindung fehlgeschlagen. Nächster Versuch in Kürze...")

                
        wdt_manager.feed_task("wifi_manager")
        await asyncio.sleep(check_interval)
        
        