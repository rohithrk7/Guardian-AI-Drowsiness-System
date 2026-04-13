let currentUser = 'Driver';
let incidentChartInstance = null;

// Auto-initialize Dashboard on page load
window.addEventListener('DOMContentLoaded', () => {
    loadDashboardData('Driver');
});

function loadDashboardData(user) {
    currentUser = user;
    // Initial fetch to populate any existing history if needed
    fetch(`/api/stats/${currentUser}`)
        .then(res => res.json())
        .then(data => {
            addLogItem("System diagnostic complete. All sensors active.");
        });
}

function addLogItem(message, type = 'normal') {
    const logs = document.getElementById('incident-logs');
    const li = document.createElement('li');
    li.className = `log-item ${type}`;
    li.innerText = `${new Date().toLocaleTimeString()} - ${message}`;
    logs.prepend(li);
    
    // Keep only last 10 logs
    if (logs.children.length > 10) logs.removeChild(logs.lastChild);
}

let isCameraRunning = false;

async function toggleCamera() {
    const btn = document.getElementById('camera-btn');
    const statusText = document.getElementById('camera-status-text');
    const badge = document.getElementById('feed-status-badge');
    const alarmCard = document.getElementById('alarm-card');
    
    if (!isCameraRunning) {
        // -> START SEQUENCE
        btn.innerText = "TERMINATE MONITORING";
        btn.style.background = "linear-gradient(to right, #ff3366, #ff8000)";
        statusText.innerHTML = "AI Camera Feed active on desktop.";
        badge.innerText = "LIVE";
        badge.className = "badge active";
        addLogItem("AI Monitoring initiated.", "success");
        
        try {
            const response = await fetch('/start_camera', { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: currentUser })
            });
            isCameraRunning = true;
            
            // Start simulated real-time metrics for UI feel
            startMetricSimulation();

        } catch (error) {
            addLogItem("Failed to connect to AI server.", "alert");
            resetUI();
        }
    } else {
        // -> STOP SEQUENCE
        try {
            await fetch('/stop_camera', { method: 'POST' });
            resetUI();
            addLogItem("Monitoring session terminated manually.");
        } catch (error) {
            addLogItem("Error stopping camera.", "alert");
        }
    }
}

function resetUI() {
    const btn = document.getElementById('camera-btn');
    const statusText = document.getElementById('camera-status-text');
    const badge = document.getElementById('feed-status-badge');
    
    btn.innerText = "START MONITORING";
    btn.style.background = "var(--btn-cyan)";
    statusText.innerHTML = "Camera is currently OFF";
    badge.innerText = "STANDBY";
    badge.className = "badge standby";
    isCameraRunning = false;
    
    document.getElementById('ear-value').innerText = "0.00";
    document.getElementById('ear-progress').style.width = "0%";
    document.getElementById('fatigue-value').innerText = "0";
    document.getElementById('fatigue-progress').style.width = "0%";
    document.getElementById('alarm-status').innerText = "OFF";
    document.body.classList.remove('alert-active');
}

function startMetricSimulation() {
    pollLiveStats();
}

async function pollLiveStats() {
    if (!isCameraRunning) {
        document.getElementById('alarm-status').innerText = "STANDBY";
        document.getElementById('alarm-status').style.color = "var(--text-muted)";
        document.getElementById('emergency-overlay').style.display = 'none';
        return;
    }
    
    try {
        const res = await fetch('/api/live_stats');
        const data = await res.json();
        
        // Update Metrics
        document.getElementById('ear-value').innerText = data.ear.toFixed(3);
        document.getElementById('ear-progress').style.width = `${Math.min((data.ear / 0.4) * 100, 100)}%`;
        
        document.getElementById('mar-value').innerText = data.mar.toFixed(3);
        document.getElementById('mar-progress').style.width = `${Math.min((data.mar / 0.8) * 100, 100)}%`;
        
        document.getElementById('head-value').innerText = data.head_pos;
        document.getElementById('alarm-status').innerText = data.state;

        // EMERGENCY OVERLAY LOGIC
        const overlay = document.getElementById('emergency-overlay');
        const warnText = document.getElementById('warning-text');
        
        if (data.state !== "AWAKE" && data.state !== "NO_FACE" && data.state !== "STANDBY") {
            overlay.style.display = 'block';
            document.body.classList.add('alert-active');
            
            if (data.state === "DROWSY") {
                warnText.innerText = "CRITICAL: WAKE UP IMMEDIATELY!";
                overlay.style.background = "rgba(255, 0, 0, 0.95)";
            } else if (data.state === "YAWNING") {
                warnText.innerText = "WARNING: SIGNS OF FATIGUE DETECTED";
                overlay.style.background = "rgba(255, 100, 0, 0.95)";
            } else if (data.state.includes("DISTRACTED")) {
                warnText.innerText = "CAUTION: KEEP EYES ON ROAD";
                overlay.style.background = "rgba(255, 50, 0, 0.95)";
            }
        } else {
            overlay.style.display = 'none';
            document.body.classList.remove('alert-active');
            
            if (data.state === "NO_FACE") {
                document.getElementById('alarm-status').style.color = "#ffaa00";
            } else {
                document.getElementById('alarm-status').style.color = "#00ffaa";
            }
        }

    } catch (e) {
        console.error("Live fetch error:", e);
    }
    
    if (isCameraRunning) setTimeout(pollLiveStats, 200);
}

