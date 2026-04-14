# 🛡️ DDDS - Driver Drowsiness Detection System v2.4.0

![Python](https://img.shields.io/badge/Python-3.8+-3776ab?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-5c3ee8?style=for-the-badge&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Latest-00e5ff?style=for-the-badge&logo=google&logoColor=white)

**DDDS** is a hyper-advanced, real-time AI safety protocol designed to prevent road accidents caused by driver fatigue and distraction. Featuring a premium **Glassmorphism UI** and industry-grade Computer Vision, DDDS provides a complete 360° safety monitoring dashboard for single-vehicle or fleet operations.

---

## 🔥 Key Features

*   **⚡ Real-Time Fatigue Speedometer**: A composite circular gauge (0-100) that calculates drowsiness risk by combining EAR, MAR, and Head Pose.
*   **👁️ High-Fidelity Facial Graph**: Detailed 468-point landmark tracking with specific green-cyan visualizations for the eyes and mouth.
*   **🚨 Multi-Stage Alert System**:
    *   **Level 1 (Warning)**: Voice prompts for signs of fatigue (yawning).
    *   **Level 2 (Critical)**: High-pitched alarm for eye closure (>1.5s).
    *   **Level 3 (Emergency)**: Automatic Telegram alerts with **GPS Coordinates** and Google Maps links.
*   **📱 Mobile-First Dashboard**: Fully responsive layout optimized for monitoring from any smartphone or tablet while in the vehicle.
*   **👤 Dynamic Driver Profiles**: Premium login system that tracks Name, Vehicle Plate, and Phone number across sessions.
*   **📍 Emergency Contact Panel**: Manual override with "SOS" button and live GPS display.

---

## 🛠️ Installation Guide

Choose one of the two methods below to get started.

### Method A: Cloning via Git (Recommended)
1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/mithunj7999-cyber/DDDS.git
    ```
2.  **Navigate to Directory**:
    ```bash
    cd DDDS
    ```
3.  **Setup Virtual Environment (Optional but Recommended)**:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```
4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Method B: Manual Installation (Zip File)
1.  **Download & Extract**: Download the `.zip` file from the repository and extract the folder to your Desktop.
2.  **Open Cwd**: Open the extracted `DDDS` folder.
3.  **Launch Terminal**: Click on the address bar at the top of the folder window, type `cmd`, and press **Enter**.
4.  **Install Packages**:
    ```bash
    pip install -r requirements.txt
    ```

---

## 🚀 Running the Application

1.  **Start the Server**:
    ```bash
    python app.py
    ```
2.  **Access the Dashboard**:
    *   **Desktop**: Go to `http://localhost:8080`
    *   **Mobile**: Go to `http://YOUR_IP_ADDRESS:8080` (Ensure both devices are on the same Wi-Fi).
3.  **Login**: Enter your Name, Plate Number, and Age.
4.  **Initialize**: Click "START MONITORING" to activate the AI.

---

## ⚙️ Telegram Configuration

To receive emergency alerts on your phone:
1.  Open `modules/config.py`.
2.  Create a Bot with [@BotFather](https://t.me/botfather) and paste the `TELEGRAM_BOT_TOKEN`.
3.  Get your Chat ID from [@userinfobot](https://t.me/userinfobot) and paste it into `TELEGRAM_CHAT_ID`.

---

## 📦 Requirements

*   **OS**: Windows 10/11 (Preferred)
*   **Camera**: Integrated Webcam or USB External Camera.
*   **Python**: 3.8.x - 3.11.x
*   **Key Libraries**:
    *   Flask (Web Server)
    *   OpenCV-Python (Video Processing)
    *   MediaPipe (Face Mesh AI)
    *   Pyttsx3 (Text-to-Speech)
    *   Requests (Alerts API)

---

## 📁 Project Structure

```text
DDDS/
├── app.py                 # Primary Flask Web Server
├── drowsiness_detector.py # AI Engine & Frame Processor
├── modules/               # Core Logic Modules
│   ├── alerts.py          # Telegram & GPS Alerts
│   ├── config.py          # Thresholds & API Keys
│   └── vision.py          # EAR/MAR Math Logic
├── frontend/              # Dynamic UI Files
│   ├── index.html         # Dashboard Structure
│   ├── style.css          # Premium Styling
│   └── script.js          # Live-Data & Charts
└── requirements.txt       # Dependencies List
```

---
*© 2026 Driver Drowsiness Detection System (DDDS). All rights reserved.*
