from flask import Flask, request, jsonify, Response
import threading
import time
import os
import json
import cv2
import numpy as np

# Import detector helper to keep stats and video in-sync
from drowsiness_detector import DrowsinessDetector
from modules.alerts import send_emergency_alerts, get_current_location, get_chat_id_from_username, send_telegram_alert

# Initialize Flask App, pointing to our frontend directory for HTML/CSS/Images
app = Flask(__name__, static_folder='frontend', static_url_path='/')

camera_thread = None
camera_active = False
camera_lock = threading.Lock()
camera_stop_event = threading.Event()
current_frame = None
current_username = 'Driver'

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/admin')
def serve_admin():
    return app.send_static_file('admin.html')

# --- Database Persistence (SQLite) ---
DB_SQLITE = os.path.join(os.path.dirname(__file__), 'guardian.db')

def init_db():
    import sqlite3
    conn = sqlite3.connect(DB_SQLITE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS drivers 
                 (username TEXT PRIMARY KEY, 
                  phone TEXT, 
                  vehicle TEXT, 
                  age TEXT, 
                  license TEXT, 
                  telegram_id TEXT,
                  drowsy_count INTEGER DEFAULT 0, 
                  yawn_count INTEGER DEFAULT 0, 
                  distraction_count INTEGER DEFAULT 0, 
                  trips INTEGER DEFAULT 0, 
                  last_login TEXT)''')
    conn.commit()
    conn.close()

def save_driver_to_db(details):
    import sqlite3
    init_db()
    conn = sqlite3.connect(DB_SQLITE)
    c = conn.cursor()
    
    username = details.get('username', 'Unknown')
    phone = details.get('phone', 'N/A')
    vehicle = details.get('vehicle', 'N/A')
    age = details.get('age', 'N/A')
    license = details.get('license', 'N/A')
    tg_input = details.get('tg_id', 'N/A') # This behaves as username now
    
    # Try to resolve username to chat_id
    telegram_id = get_chat_id_from_username(tg_input)
    if not telegram_id:
        # Fallback to the input itself if it's already a numeric ID
        telegram_id = tg_input if tg_input.isdigit() else "PENDING_AUTH"
    
    now = time.ctime()

    # Check if exists
    c.execute("SELECT trips FROM drivers WHERE username=?", (username,))
    row = c.fetchone()
    if row is None:
        c.execute("INSERT INTO drivers (username, phone, vehicle, age, license, telegram_id, trips, last_login) VALUES (?,?,?,?,?,?,?,?)",
                  (username, phone, vehicle, age, license, telegram_id, 1, now))
    else:
        c.execute("UPDATE drivers SET phone=?, vehicle=?, age=?, license=?, telegram_id=?, trips=trips+1, last_login=? WHERE username=?",
                  (phone, vehicle, age, license, telegram_id, now, username))
    
    conn.commit()
    conn.close()
    return telegram_id

@app.route('/api/admin/data')
def get_admin_data():
    import sqlite3
    if not os.path.exists(DB_SQLITE): return jsonify({})
    conn = sqlite3.connect(DB_SQLITE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM drivers")
    rows = c.fetchall()
    data = {}
    for r in rows:
        data[r['username']] = {
            "details": {
                "phone": r['phone'],
                "vehicle": r['vehicle'],
                "age": r['age'],
                "license": r['license']
            },
            "drowsy_count": r['drowsy_count'],
            "yawn_count": r['yawn_count'],
            "distraction_count": r['distraction_count'],
            "trips": r['trips'],
            "last_login": r['last_login']
        }
    conn.close()
    return jsonify(data)

@app.route('/api/admin/delete_driver', methods=['POST'])
def delete_driver():
    try:
        data = request.get_json() or {}
        username = data.get('username')
        if not username: return jsonify({"status": "error", "message": "Username missing"}), 400
        
        import sqlite3
        conn = sqlite3.connect(DB_SQLITE)
        c = conn.cursor()
        c.execute("DELETE FROM drivers WHERE username=?", (username,))
        conn.commit()
        conn.close()
        
        print(f"DEBUG: Admin deleted driver: {username}")
        return jsonify({"status": "success", "message": f"Driver {username} deleted."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/admin/test_driver_tg', methods=['POST'])
def test_driver_tg():
    try:
        data = request.get_json() or {}
        username = data.get('username')
        tg_input = data.get('telegram_id') # Could be handle or ID
        
        if not tg_input: return jsonify({"status": "error", "message": "No Telegram handle linked."}), 400
        
        # Resolve if needed
        chat_id = get_chat_id_from_username(tg_input) if not str(tg_input).isdigit() else tg_input
        
        if not chat_id or chat_id == "PENDING_AUTH":
            return jsonify({"status": "error", "message": "User hasn't messaged the bot yet."}), 400
            
        test_msg = f"🔔 <b>GUARDIAN AI: Connection Test</b>\n\nHello {username}, this is a test from the fleet dashboard to verify your alert connection."
        status, msg = send_telegram_alert(test_msg, chat_id=chat_id)
        
        if status:
            return jsonify({"status": "success", "message": "Test successful! Alert sent."})
        else:
            return jsonify({"status": "error", "message": msg}), 500
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/start_camera', methods=['POST'])
def start_camera():
    global camera_thread, camera_active, current_username
    try:
        data = request.get_json() or {}
        username = data.get('username', 'Driver')
        telegram_id = data.get('tg_id', '')
        current_username = username

        if camera_active:
            return jsonify({"status": "success", "message": "Camera is already running."})

        # Persist driver info (don't block for TG resolution here)
        save_driver_to_db(data)
        
        print(f"DEBUG: Starting camera for user {username}")
        camera_stop_event.clear()
        
        # Pass the input username/id to the thread, let thread resolve if needed
        tg_input = data.get('tg_id', 'PENDING_AUTH')
        camera_thread = threading.Thread(target=camera_loop, args=(username, tg_input), daemon=True)
        camera_thread.start()
        camera_active = True

        return jsonify({"status": "success", "message": "AI Camera successfully launched."})

    except Exception as e:
        print(f"Failed to start camera: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    global camera_active
    try:
        if camera_active:
            camera_stop_event.set()
            camera_active = False

        return jsonify({"status": "success", "message": "AI Camera successfully stopped."})
    except Exception as e:
        print(f"Failed to stop camera: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/video_feed')
def video_feed():
    def generate():
        # Wait up to 5 seconds for camera to actually start
        timeout = 50
        while not camera_active and timeout > 0:
            time.sleep(0.1)
            timeout -= 1
            
        while camera_active:
            with camera_lock:
                frame = current_frame
            
            if frame is None:
                time.sleep(0.1)
                continue
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            time.sleep(0.04)
        return

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/stats/<username>', methods=['GET'])
def get_stats(username):
    db_path = os.path.join(os.path.dirname(__file__), 'database.json')
    if os.path.exists(db_path):
        with open(db_path, 'r') as f:
            try:
                db = json.load(f)
            except json.JSONDecodeError:
                db = {}
    else:
        db = {}

    user_data = db.get(username, {"drowsy_count": 0, "yawn_count": 0, "distraction_count": 0, "trips": 0})
    penalties = (user_data["drowsy_count"] * 10) + (user_data["yawn_count"] * 2) + (user_data["distraction_count"] * 3)
    score = max(0, 100 - penalties)
    user_data["score"] = score

    return jsonify(user_data)

@app.route('/api/live_stats', methods=['GET'])
def live_stats():
    live_path = os.path.join(os.path.dirname(__file__), 'live_stats.json')
    if os.path.exists(live_path):
        try:
            with open(live_path, 'r') as f:
                data = json.load(f)
            return jsonify(data)
        except:
            return jsonify({"status": "error", "message": "Failed to read stats"}), 500
    return jsonify({"ear": 0, "mar": 0, "head_pos": "None", "state": "STANDBY"})

@app.route('/api/manual_alert', methods=['POST'])
def manual_alert():
    try:
        data = request.get_json() or {}
        username = data.get('username', 'Driver')
        send_emergency_alerts(username)
        return jsonify({"status": "success", "message": "Manual alert dispatched."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/location', methods=['GET'])
def get_location():
    loc = get_current_location()
    if loc:
        return jsonify(loc)
    return jsonify({"lat": 0, "lon": 0, "address": "Unknown"})


def camera_loop(username, telegram_id):
    global current_frame, camera_active
    detector = None
    print("DEBUG: Attempting to open camera. Testing indices [0, 1, 2]...")
    cap = None
    for index in [0, 1, 2]:
        print(f"DEBUG: Trying VideoCapture({index}) with CAP_DSHOW...")
        cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
        if cap.isOpened():
            print(f"DEBUG: Success! Camera found at index {index}")
            break
        print(f"DEBUG: Index {index} failed.")
        
    if not cap or not cap.isOpened():
        print("DEBUG: FALLBACK - All CAP_DSHOW attempts failed. Trying default indices...")
        for index in [0, 1]:
            cap = cv2.VideoCapture(index)
            if cap.isOpened():
                print(f"DEBUG: Success! Camera found at default index {index}")
                break

    if not cap or not cap.isOpened():
        print("DEBUG: FATAL ERROR - No camera detected on any index.")
        camera_active = False
        return

    # Fast warm-up
    print("DEBUG: Quick warm-up for camera sensor...")
    time.sleep(0.5)

    # Resolve ID in background (non-blocking)
    resolved_id = telegram_id
    if telegram_id and not str(telegram_id).isdigit():
        resolved_id = get_chat_id_from_username(telegram_id) or "PENDING_AUTH"

    try:
        detector = DrowsinessDetector(username, resolved_id)
        print(f"DEBUG: DrowsinessDetector initialized with ID: {resolved_id}")
        while not camera_stop_event.is_set():
            try:
                success, frame = cap.read()
                if not success:
                    print("DEBUG: WARNING - Failed to read frame from camera.")
                    time.sleep(0.05)
                    continue

                frame = cv2.flip(frame, 1)
                processed_frame = detector.process_frame(frame)
                
                # Check for black frame
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness = np.mean(gray)
                if brightness < 5:
                    print(f"DEBUG: WARNING - Camera frame is very dark/black (Avg: {brightness}). Check camera privacy shutter!")
                
                ret, buffer = cv2.imencode('.jpg', processed_frame)
                if not ret:
                    continue

                with camera_lock:
                    current_frame = buffer.tobytes()
                time.sleep(0.01) # Small sleep to yield to other threads
            except Exception as loop_e:
                print(f"DEBUG: Error in camera loop step: {loop_e}")
                time.sleep(0.1)
    except Exception as init_e:
        print(f"DEBUG: Failed to initialize detector or loop: {init_e}")
    finally:
        cap.release()
        if detector:
            detector.close()


if __name__ == '__main__':
    print("==============================================")
    print("   DRIVER SAFETY WEB PROTOCOL ACTIVE          ")
    print("   Open your browser to: http://localhost:8080")
    print("   Mobile view: http://<your-ip>:8080")
    print("==============================================")
    app.run(debug=True, host='0.0.0.0', port=8080, use_reloader=False)
