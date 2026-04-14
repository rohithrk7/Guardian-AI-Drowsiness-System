from flask import Flask, request, jsonify, Response
import threading
import time
import os
import json
import cv2

# Import detector helper to keep stats and video in-sync
from drowsiness_detector import DrowsinessDetector
from modules.alerts import send_emergency_alerts, get_current_location

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

@app.route('/start_camera', methods=['POST'])
def start_camera():
    global camera_thread, camera_active, current_username
    try:
        data = request.get_json() or {}
        username = data.get('username', 'Driver')
        current_username = username

        if camera_active:
            return jsonify({"status": "success", "message": "Camera is already running."})

        camera_stop_event.clear()
        camera_thread = threading.Thread(target=camera_loop, args=(username,), daemon=True)
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
        while camera_active:
            with camera_lock:
                frame = current_frame
            if frame is None:
                time.sleep(0.02)
                continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
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


def camera_loop(username):
    global current_frame
    detector = None
    cap = cv2.VideoCapture(0)

    try:
        detector = DrowsinessDetector(username)
        while not camera_stop_event.is_set():
            success, frame = cap.read()
            if not success:
                time.sleep(0.05)
                continue

            frame = cv2.flip(frame, 1)
            processed_frame = detector.process_frame(frame)
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            if not ret:
                continue

            with camera_lock:
                current_frame = buffer.tobytes()
            time.sleep(0.03)
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
