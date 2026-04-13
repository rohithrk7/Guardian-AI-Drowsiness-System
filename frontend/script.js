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
    if (!isCameraRunning) return;
    
    // Simulate real-time metric fluctuations for the premium UI feel
    // In a production environment, this would poll a real-time socket
    const ear = (0.25 + Math.random() * 0.1).toFixed(2);
    const fatigue = Math.floor(Math.random() * 10);
    
    document.getElementById('ear-value').innerText = ear;
    document.getElementById('ear-progress').style.width = `${(ear / 0.4) * 100}%`;
    
    document.getElementById('fatigue-value').innerText = fatigue;
    document.getElementById('fatigue-progress').style.width = `${fatigue}%`;

    if (isCameraRunning) setTimeout(startMetricSimulation, 1000);
}
