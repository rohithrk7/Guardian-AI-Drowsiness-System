# Premium Driver Drowsiness Detection System (DDDS)

A hyper-advanced, web-hosted AI Safety System that detects driver fatigue, yawning, and head distraction in real-time. Designed with an ultra-premium glassmorphism UI.

## Getting Started (Quick Setup)

Follow these exact steps to run this project seamlessly on any Windows laptop/PC using the Flask Web framework.

### Prerequisites
Make sure you have [Python](https://www.python.org/downloads/) installed (Python 3.8 to 3.11 recommended). Check the box that says **"Add Python to PATH"** during installation.

### Step 1: Extract the Folder
Make sure the `DDDS` project folder is completely extracted (e.g., placing the `DDDS` folder on the fresh computer's local desktop).

### Step 2: Open Terminal / Command Prompt
Open the Terminal or Command prompt exactly where your folder is located:
1. Open the inner `DDDS` folder. 
2. Click on the folder address bar at the very top.
3. Type `cmd` and press **Enter**.

### Step 3: Install the AI Packages
Run the following standard Python command. This will download all the necessary heavy machine learning and computer vision libraries:
```bash
pip install -r requirements.txt
```
*(Note: Be patient, as `opencv` and `mediapipe` are somewhat large packages).*

### Step 4: Boot the Flask Server
Turn on the primary command server by typing:
```bash
python app.py
```
You should see red/white text in your console stating: `"DRIVER SAFETY WEB PROTOCOL ACTIVE -> Open your browser to: http://localhost:8080"`

### Step 5: Start the Simulation
1. Once the Flask server is running, open a web browser (Chrome/Edge preferably).
2. Go to **http://localhost:8080**
3. Log in with any username. This registers your name in the local database.
4. Click the glowing **INITIALIZE CAMERA** button and physically test the AI triggers:
   * **Shut your eyes** (Drowsiness).
   * **Yawn widely** (Fatigue).
   * **Turn your head away from the laptop bounds for 2+ seconds** (Distraction).

To stop safely, hit **TERMINATE AI FEED** on the dashboard. Do not blindly close the camera window.
