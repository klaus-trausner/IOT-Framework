import asyncio
from machine import WDT, reset
import time

wdt = None
_registered_tasks = {}

def register_task(name):
    _registered_tasks[name] = time.time()

def feed_task(name):
    if name in _registered_tasks:
        _registered_tasks[name] = time.time()


async def start_watchdog(timeout_ms=8000, max_task_delay_s=10):
    global wdt
    print(f"🐕 Smart-Watchdog gestartet ({len(_registered_tasks)} Tasks überwacht)...")
    wdt = WDT(timeout=timeout_ms)

    while True:
        now = time.time()
        all_healthy = True

        for task_name, last_seen in _registered_tasks.items():
            if now - last_seen > max_task_delay_s:
                print( f"⚠️ CRITICAL: Task '{task_name}' reagiert nicht mehr! (Inaktiv seit {now - last_seen}s)" ) 
                all_healthy = False

        if all_healthy:
            wdt.feed()
        else: 
            print("🚨 Watchdog verweigert das Füttern! System-Reset droht...") 
            # Optional: Man kann direkt \`reset()\` ausführen oder den WDT ablaufen lassen 
        
        await asyncio.sleep(2)