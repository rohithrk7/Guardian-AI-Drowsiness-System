# 🛡️ Guardian AI: Driver Drowsiness Detection System

Guardian AI is a sophisticated, real-time safety monitoring system designed for transport fleets. Using Computer Vision (MediaPipe) and Flask, it monitors driver fatigue through eye closure and yawning patterns, sending instant SOS alerts via Telegram including live GPS location.

---

## ✨ Key Features
*   🚀 **AI Monitoring**: Real-time EAR (Eye Aspect Ratio) and MAR (Mouth Aspect Ratio) analysis.
*   📱 **Personalized Telegram Alerts**: Multi-driver support where alerts are routed to each driver's specific Telegram handle.
*   📊 **Fleet Admin Dashboard**: A centralized panel for managers to track safety metrics, view location, and audit historical data.
*   🗄️ **Persistent SQLite Backend**: Robust storage for driver metadata, performance scores, and session history.
*   📄 **PDF Performance Reports**: Generate and download professional safety dossiers for individual drivers.
*   🛡️ **Secure Credentials**: Multi-level password protection for Drivers and Administration.

---

## 🛠️ Getting Started (Beginner Friendly)

Follow these steps to run the project on your local machine:

### 1. Prerequisites
Make sure you have **Python 3.8 or higher** installed. You can download it from [python.org](https://www.python.org/).

### 2. Clone the Repository
Open your terminal (or CMD) and run:
```bash
git clone https://github.com/YOUR_USERNAME/DDDS.git
cd DDDS
```

### 3. Install Dependencies
Install the required libraries using the provided requirements file:
```bash
pip install flask opencv-python mediapipe requests geocoder numpy
```

### 4. Configure Telegram Bot (Optional but Recommended)
To receive alerts on your phone:
1.  Message [@BotFather](https://t.me/botfather) on Telegram to create a bot and get your **API Token**.
2.  Open `modules/config.py` and paste your token.
3.  Message your new bot and click **START**.

### 5. Run the Application
Start the server:
```bash
python app.py
```
After running, open your browser and go to:
*   🛡️ **Driver View**: `http://localhost:8080`
*   📊 **Admin View**: `http://localhost:8080/admin`

---

## 🔑 Default Credentials
| Portal | Password |
| :--- | :--- |
| **Driver Login** | `guardian2026` |
| **Admin Panel** | `admin_guardian_2026` |

---

## 👤 For Drivers
1. Enter your Name, Phone, and **Telegram Username** (e.g., @yourname).
2. Click **START MONITORING**.
3. If the system detects drowsiness, it will play a loud alarm and send an SOS message to your Telegram account instantly.

---

## 📊 For Admins
1. Click the **🔒 Admin Panel** button (Top-Left).
2. Enter the admin password.
3. Use the **📄 REPORT** button to download a PDF of any driver's history.
4. Use the **🗑️ DELETE** button to remove old records.
5. Use the **🔔 TEST TG** button to verify if a driver's Telegram is correctly linked.

---

## 📜 Technology Stack
*   **Backend**: Python, Flask, SQLite
*   **Engine**: OpenCV, MediaPipe FaceMesh
*   **Frontend**: HTML5, CSS3 (Glassmorphism), Vanilla JavaScript
*   **Utilities**: jsPDF (Reporting), Geocoder (GPS Location)

---

## 🤝 Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any safety-critical improvements.

---
*Created with ❤️ for Safer Roads.*
