import asyncio
import wifi_manager
import mqtt_manager
import config
import wdt_manager
import time

def handle_incoming_mqtt(topic, msg): 
    """Wird aufgerufen, wenn eine abonnierte Nachricht eintrifft.""" 
    print(f"🔔 MAIN verarbeitet Nachricht: {topic} -&gt; {msg}")

async def test_sender():
    zaehler = 0
    while True:
        await mqtt_manager.mqtt_connected_event.wait()
        zaehler += 1
        payload = f"Messung Nr.: {zaehler}"

        await mqtt_manager.publish("test", payload)
        wdt_manager.feed_task("test_sender")
        await asyncio.sleep(5)
        wdt_manager.feed_task("test_sender")

async def heartbeat():
    """Zeigt, dass das System unbeeindruckt weiterläuft.""" 
    while True: 
        print("💓 System läuft lokal weiter...") 
        await asyncio.sleep(2)
        wdt_manager.feed_task("heartbeat")
        # time.sleep(10)

async def main():
    mqtt_manager.on_message_handler = handle_incoming_mqtt

    wdt_manager.register_task("wifi_manager")
    asyncio.create_task(wifi_manager.connect_wifi(config.WIFI_SSID, config.WIFI_PASS))

    wdt_manager.register_task("mqtt_manager")
    asyncio.create_task(mqtt_manager.start_mqtt(
        server=config.MQTT_BROKER,
        client_id=config.MQTT_Client_ID,
        user=config.MQTT_USER,
        password=config.MQTT_PASS,
        subscriptions=config.SUBSCRIPTIONS,
    ))

    wdt_manager.register_task("test_sender")
    asyncio.create_task(test_sender())

    wdt_manager.register_task("heartbeat")
    asyncio.create_task(heartbeat())

    # Projekttasks ....

    asyncio.create_task(
        wdt_manager.start_watchdog(timeout_ms=8000, max_task_delay_s=10)
    )

    while True:
        await asyncio.sleep(1)

asyncio.run(main())