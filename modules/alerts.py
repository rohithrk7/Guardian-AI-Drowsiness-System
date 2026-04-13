import geocoder
import requests
from .config import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
)

def get_current_location():
    """
    Simulates GPS tracking using IP geolocation. 
    """
    try:
        g = geocoder.ip('me')
        if g.latlng:
            return {
                "lat": g.latlng[0],
                "lon": g.latlng[1],
                "address": g.address
            }
        return None
    except Exception as e:
        print(f"Error fetching location: {e}")
        return None

def send_telegram_alert(message_body):
    """
    Sends an instant push notification via Telegram Bot.
    """
    if not TELEGRAM_BOT_TOKEN or "YOUR_" in TELEGRAM_BOT_TOKEN:
        return False, "Telegram Token missing."
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message_body,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return True, "Telegram Alert Sent."
        return False, f"Telegram Error: {response.text}"
    except Exception as e:
        return False, f"Telegram Connection Failed: {e}"

def send_emergency_alerts(username="Driver"):
    """
    Dispatches a critical alert through Telegram.
    """
    # 1. Fetch Location Data
    location = get_current_location()
    
    if location:
        lat, lon = location["lat"], location["lon"]
        address = location["address"]
        maps_link = f"https://www.google.com/maps?q={lat},{lon}"
        
        message_body = (
            f"🆘 [DDDS ALERT] Driver '{username}' is showing UNRESPONSIVE drowsiness!\n"
            f"📍 Location: {address}\n"
            f"🗺️ View Map: {maps_link}"
        )
    else:
        message_body = f"🆘 [DDDS ALERT] Driver '{username}' is unresponsive. Location tracking failed! Check immediately!"

    # 2. Trigger Telegram
    tg_status, tg_msg = send_telegram_alert(message_body)
    print(f" > Telegram: {tg_msg}")
    
    return tg_status, tg_msg

