import geocoder
import requests
import time
from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

# ✅ Cache location to avoid repeated API calls
cached_location = None
last_fetch_time = 0

# ⏱️ Fetch location only every 5 minutes (300 sec)
LOCATION_REFRESH_INTERVAL = 300  


def get_current_location():
    """
    Fetch location using IP (with caching to prevent 429 errors)
    """
    global cached_location, last_fetch_time

    current_time = time.time()

    # ✅ Use cached location if within interval
    if cached_location and (current_time - last_fetch_time < LOCATION_REFRESH_INTERVAL):
        return cached_location

    try:
        g = geocoder.ip('me')

        if g.latlng:
            cached_location = {
                "lat": g.latlng[0],
                "lon": g.latlng[1],
                "address": g.address if g.address else "Unknown Location"
            }
            last_fetch_time = current_time
            return cached_location

        return None

    except Exception as e:
        print(f"Error fetching location: {e}")
        return cached_location  # fallback to last known location


def get_chat_id_from_username(target_username):
    """
    Crawls bot updates to find the numeric Chat ID for a given @username.
    The user MUST have sent at least one message to the bot first.
    """
    if not target_username: return None
    
    # Clean username
    target_username = target_username.strip().replace("@", "").lower()
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            updates = response.json().get('result', [])
            # Search from newest to oldest
            for update in reversed(updates):
                msg = update.get('message')
                if not msg: continue
                
                user_info = msg.get('from', {})
                username = user_info.get('username', '').lower()
                
                if username == target_username:
                    return user_info.get('id')
        return None
    except Exception as e:
        print(f"Error resolving username: {e}")
        return None

def send_telegram_alert(message_body, chat_id=None):
    """
    Sends alert via Telegram with dynamic recipient support
    """
    if not TELEGRAM_BOT_TOKEN or "YOUR_" in TELEGRAM_BOT_TOKEN:
        return False, "Telegram Token missing."

    # Use custom chat_id if provided, otherwise fallback to global config
    target_chat_id = chat_id if chat_id else TELEGRAM_CHAT_ID

    if not target_chat_id:
        return False, "No recipient Chat ID provided."

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": target_chat_id,
        "text": message_body,
        "parse_mode": "HTML"
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # ✅ Retry logic
    for attempt in range(3):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=5)

            if response.status_code == 200:
                return True, "Telegram Alert Sent."

            elif response.status_code == 429:
                time.sleep(2)
            else:
                return False, f"Telegram Error: {response.text}"

        except Exception as e:
            time.sleep(2)

    return False, "Telegram Failed after retries"


def send_emergency_alerts(username="Driver", chat_id=None):
    """
    Sends drowsiness alert with location (targeted)
    """

    # ✅ Get location
    location = get_current_location()

    if location:
        lat, lon = location["lat"], location["lon"]
        address = location["address"]

        maps_link = f"https://www.google.com/maps?q={lat},{lon}"

        message_body = (
            f"🆘 <b>[SAFE-DRIVE ALERT]</b>\n"
            f"Drowsiness detected!\n\n"
            f"👤 <b>Driver:</b> {username}\n"
            f"📍 <b>Location:</b> {address}\n"
            f"🗺️ <a href='{maps_link}'>View Driver Location</a>\n\n"
            f"⚠️ <i>Please check on the driver immediately.</i>"
        )
    else:
        message_body = (
            f"🆘 <b>[SAFE-DRIVE ALERT]</b>\n"
            f"Driver '<b>{username}</b>' has triggered an SOS!\n"
            f"⚠️ Location unavailable. Contact driver now!"
        )

    # ✅ Send alert
    tg_status, tg_msg = send_telegram_alert(message_body, chat_id=chat_id)

    print(f"> Telegram Support ({username}): {tg_msg}")

    return tg_status, tg_msg