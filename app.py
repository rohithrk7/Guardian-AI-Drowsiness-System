from flask import Flask, request, jsonify
import subprocess
import os
import json

# Initialize Flask App, pointing to our frontend directory for HTML/CSS/Images
app = Flask(__name__, static_folder='frontend', static_url_path='/')

camera_process = None

@app.route('/')
def serve_index():
    # Send the main HTML file when someone visits the homepage
    return app.send_static_file('index.html')

@app.route('/start_camera', methods=['POST'])
def start_camera():
    """
    This endpoint is triggered by the HTML Dashboard when the user clicks 'INITIALIZE CAMERA'.
    It launches the drowsiness_detector.py machine learning script asynchronously.
    """
    global camera_process
    try:
        data = request.get_json() or {}
        username = data.get('username', 'Driver')
        
        # Locate the exact path of the python file
        script_path = os.path.join(os.path.dirname(__file__), 'drowsiness_detector.py')
        
        if camera_process is not None:
            camera_process.terminate()
            camera_process.wait()
            
        # Launch the camera script as an independent background process
        camera_process = subprocess.Popen(['python', script_path, '--user', username])
        
        return jsonify({
            "status": "success", 
            "message": "AI Camera successfully launched."
        })
        
    except Exception as e:
        print(f"Failed to start camera: {e}")
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    """
    Triggered to cleanly terminate the background AI Camera.
    """
    global camera_process
    try:
        if camera_process is not None:
            camera_process.terminate()
            camera_process.wait()
            camera_process = None
            
        return jsonify({
            "status": "success", 
            "message": "AI Camera successfully stopped."
        })
    except Exception as e:
        print(f"Failed to stop camera: {e}")
        return jsonify({
            "status": "error", 
            "message": str(e)
        }), 500

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
        
    user_data = db.get(username, {
        "drowsy_count": 0, "yawn_count": 0, "distraction_count": 0, "trips": 0
    })
    
    # Calculate a simple safety score 100 - (penalties)
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


if __name__ == '__main__':
    print("==============================================")
    print("   DRIVER SAFETY WEB PROTOCOL ACTIVE          ")
    print("   Open your browser to: http://localhost:8080")
    print("==============================================")
    
    # Run the server on port 8080
    app.run(debug=True, port=8080, use_reloader=False)
