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


def send_telegram_alert(message_body):
    """
    Sends alert via Telegram with basic retry handling
    """
    if not TELEGRAM_BOT_TOKEN or "YOUR_" in TELEGRAM_BOT_TOKEN:
        return False, "Telegram Token missing."

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_body,
        "parse_mode": "HTML"
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # ✅ Retry logic (prevents temporary failures)
    for attempt in range(3):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=5)

            if response.status_code == 200:
                return True, "Telegram Alert Sent."

            elif response.status_code == 429:
                print("⚠️ Telegram rate limit hit. Retrying...")
                time.sleep(2)

            else:
                return False, f"Telegram Error: {response.text}"

        except Exception as e:
            print(f"Retry {attempt+1}: {e}")
            time.sleep(2)

    return False, "Telegram Failed after retries"


def send_emergency_alerts(username="Driver"):
    """
    Sends drowsiness alert with location (optimized)
    """

    # ✅ Get location (cached, no spamming API)
    location = get_current_location()

    if location:
        lat, lon = location["lat"], location["lon"]
        address = location["address"]

        maps_link = f"https://www.google.com/maps?q={lat},{lon}"

        message_body = (
            f"🆘 <b>[DDDS ALERT]</b>\n"
            f"Driver '<b>{username}</b>' is <b>UNRESPONSIVE (Drowsy)</b>!\n\n"
            f"📍 <b>Location:</b> {address}\n"
            f"🗺️ <a href='{maps_link}'>View Live Location</a>"
        )
    else:
        message_body = (
            f"🆘 <b>[DDDS ALERT]</b>\n"
            f"Driver '<b>{username}</b>' is unresponsive!\n"
            f"⚠️ Location unavailable. Check immediately!"
        )

    # ✅ Send alert
    tg_status, tg_msg = send_telegram_alert(message_body)

    print(f"> Telegram: {tg_msg}")

    return tg_status, tg_msg