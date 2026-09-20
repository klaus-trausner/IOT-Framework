import asyncio
from umqtt.simple import MQTTClient
import wifi_manager
import wdt_manager


# Globale Variablen
client = None
mqtt_connected_event = asyncio.Event()

# Callback Funktion
on_message_handler = None



def _internal_callback(topic, msg):
    topic_str = topic.decode("utf-8")
    msg_str = msg.decode("utf-8")
    print(f"📩 MQTT empfangen [{topic_str}]: {msg_str}")

    if on_message_handler:
        on_message_handler(topic_str, msg_str)


async def start_mqtt(server, client_id, port=1883, user=None, password=None, subscriptions= []):
    global client

    while True:
        await wifi_manager.wifi_connected_event.wait()
        mqtt_connected_event.clear()

        print(f"🔌 Verbinde mit MQTT-Broker '{server}'...")

        try:
            client = MQTTClient(
                client_id=client_id,
                server=server,
                port=port,
                user=user if user else None,
                password=password if password else None,
                keepalive=60,
            )
            client.set_callback(_internal_callback)
            client.connect()

            print("✅ MQTT erfolgreich verbunden!")
            mqtt_connected_event.set()

            # Abonniere Topics
            for topic in subscriptions:
                client.subscribe(topic)
                print(f"📥 Topic abonniert: {topic}")

            # Empfangsschleife
            while wifi_manager.wifi_connected_event.is_set():
                try:
                    client.check_msg()
                except Exception as e:
                    print(f"⚠️ MQTT Verbindungsverlust: {e}") 
                    break

                wdt_manager.feed_task("mqtt_manager")    
                await asyncio.sleep(0.1)

        except Exception as e:
            print(f"❌ MQTT Fehler beim Verbinden: {e}")


        mqtt_connected_event.clear()
        print("🔄 Versuche MQTT-Verbindung in 5 Sekunden erneut...") 
        await asyncio.sleep(5)
        


async def publish(topic, payload, retain=False):
    global client
    if mqtt_connected_event.is_set() and client is not None:
        try:
            client.publish(topic, str(payload), retain=retain)
            print(f"📤 MQTT gesendet [{topic}]: {payload}")
        except Exception as e:
            print(f"⚠️ Fehler beim Senden der MQTT-Nachricht: {e}")
    else:
        print(f"⚠️ MQTT nicht verbunden. Nachricht verworfen: [{topic}]")


