import geocoder
import requests
from twilio.rest import Client
from .config import (
    TWILIO_SID, TWILIO_TOKEN, TWILIO_NUMBER, EMERGENCY_CONTACT,
    BITRIX24_WEBHOOK_URL, BITRIX24_USER_ID,
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
)

def get_current_location():
    """
    Simulates GPS tracking using IP geolocation. 
    In a real car, this would use a hardware GPS module (like Serial NMEA data).
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

def send_bitrix24_notification(message_body):
    """
    Sends an instant message alert to the Bitrix24 CRM dashboard.
    """
    if not BITRIX24_WEBHOOK_URL or "YOUR_" in BITRIX24_WEBHOOK_URL:
        return False, "Bitrix24 URL missing."
    
    try:
        # Construct the API endpoint for sending a private message
        # Ensure the trailing slash handling
        base_url = BITRIX24_WEBHOOK_URL.rstrip('/')
        endpoint = f"{base_url}/im.message.add.json"
        
        payload = {
            "DIALOG_ID": BITRIX24_USER_ID,
            "MESSAGE": message_body
        }
        
        response = requests.post(endpoint, json=payload)
        if response.status_code == 200:
            return True, "Bitrix24 Notification Sent."
        return False, f"Bitrix24 Error: {response.text}"
    except Exception as e:
        return False, f"Bitrix24 Connection Failed: {e}"

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
    Dispatches a critical alert through all connected channels (SMS, CRM, etc.)
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

    # 2. Trigger Telegram (Most Reliable & Free)
    tg_status, tg_msg = send_telegram_alert(message_body)
    print(f" > Telegram: {tg_msg}")

    # 3. Trigger Bitrix24 (CRM Alert)
    bt_status, bt_msg = send_bitrix24_notification(message_body)
    print(f" > Bitrix24: {bt_msg}")

    # 4. Trigger Twilio SMS (Conditional on valid credentials)
    if all([TWILIO_SID, TWILIO_TOKEN, TWILIO_NUMBER]) and "YOUR_" not in TWILIO_SID:
        try:
            client = Client(TWILIO_SID, TWILIO_TOKEN)
            client.messages.create(
                body=message_body,
                from_=TWILIO_NUMBER,
                to=EMERGENCY_CONTACT
            )
            return True, "Emergency SMS Sent Successfully."
        except Exception as e:
            return False, f"SMS Dispatch Error: {e}"
    else:
        # Fallback for development (If keys are not set)
        print("\n" + "="*50)
        print(" [DEVELOPMENT ALERT - SMS SIMULATION] ")
        print(f" To: {EMERGENCY_CONTACT}")
        print(f" Content: {message_body}")
        print("="*50 + "\n")
        return True, "SMS Simulated (Authentication keys missing)."
