import os
import requests
from machine import reset

def update_file(url, target_filename=None):
    clean_url = url.split("?")[0]
    print(f"clean_url: {clean_url}")   

    # 2\. Automatischer Umbau von normalen GitHub-Links zu RAW-Links
    if "github.com" in clean_url and "/blob/" in clean_url: 
        clean_url = clean_url.replace( "github.com", "raw.githubusercontent.com" ).replace("/blob/", "/") 
        print(f"🔄 GitHub-Link auf RAW umgestellt: {clean_url}")

    if not target_filename:
        
        target_filename = clean_url.split("/")[-1]
        print(f"target_filename: {target_filename}")

    temp_filename = target_filename + ".tmp"
    print(f"📥 OTA: Lade '{target_filename}' von '{url}' herunter..." )

    try:
        response = requests.get(clean_url)

        if response.status_code == 200:
            with open(temp_filename, "w") as f:
                f.write(response.text)

            response.close()
            print("✅ Download abgeschlossen. Ersetze Datei...")

            try:
                os.remove(target_filename)
            except OSError:
                pass

            os.rename(temp_filename, target_filename)

            print("🔄 OTA erfolgreich! Controller startet in 2 Sekunden neu...") 
            import time

            time.sleep(2)
            reset()

        else:
            print(f"❌ OTA Fehler: HTTP Status Code {response.status_code}") 
            response.close()

    except Exception as e:
        print(f"❌ OTA-Update fehlgeschlagen: {e}")
        try:
            os.remove(temp_filename)
        except OSError:
            pass
                
