let currentUser = 'Driver';
let incidentChartInstance = null;

// Auto-initialize Dashboard on page load
window.addEventListener('DOMContentLoaded', () => {
    // We wait for login now
    setupLogin();
});

function setupLogin() {
    const loginForm = document.getElementById('login-form');
    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const details = {
            name: document.getElementById('login-name').value,
            phone: document.getElementById('login-phone').value,
            vehicle: document.getElementById('login-vehicle').value,
            age: document.getElementById('login-age').value,
            license: document.getElementById('login-license').value || "N/A"
        };
        
        currentUser = details.name;
        updateProfileDisplay(details);
        
        // Hide Login
        document.getElementById('login-screen').classList.add('login-hidden');
        
        // Init Dashboard
        addLogItem(`Driver ${currentUser} logged in. System ready.`, "success");
    });
}

function updateProfileDisplay(data) {
    document.getElementById('disp-name').innerText = data.name;
    document.getElementById('disp-phone').innerText = data.phone;
    document.getElementById('disp-vehicle').innerText = data.vehicle;
    document.getElementById('disp-age').innerText = data.age;
    document.getElementById('disp-license').innerText = data.license;
}

function addLogItem(message, type = 'normal') {
    const logs = document.getElementById('incident-logs');
    const li = document.createElement('li');
    li.className = `log-item ${type}`;
    li.innerText = `${new Date().toLocaleTimeString()} - ${message}`;
    logs.prepend(li);
    
    // Keep only last 12 logs
    if (logs.children.length > 12) logs.removeChild(logs.lastChild);
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

        // SHOW VIDEO FEED
        const feed = document.getElementById('main-feed');
        const placeholder = document.getElementById('placeholder-content');
        feed.src = "/video_feed";
        feed.style.display = "block";
        placeholder.classList.add('hidden');
        
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
    
    // HIDE VIDEO FEED
    const feed = document.getElementById('main-feed');
    const placeholder = document.getElementById('placeholder-content');
    feed.src = "";
    feed.style.display = "none";
    placeholder.classList.remove('hidden');
    
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

        // UPDATE STATUS PULSE AND BADGE
        updateStatusDisplay(data.state);

        // COMPUTE FATIGUE SCORE (0-100)
        const earScore = Math.max(0, (0.32 - data.ear) * 300); // Higher if eyes closed
        const marScore = Math.max(0, (data.mar - 0.5) * 150);  // Higher if yawning
        const distractScore = (data.head_pos !== "Forward") ? 25 : 0;
        
        let totalScore = Math.round(earScore + marScore + distractScore);
        totalScore = Math.min(Math.max(totalScore, 0), 100);
        
        updateFatigueGauge(totalScore);

    } catch (e) {
        console.error("Live fetch error:", e);
    }
    
    if (isCameraRunning) setTimeout(pollLiveStats, 200);
}

function updateFatigueGauge(score) {
    const gauge = document.getElementById('fatigue-gauge');
    const valueDisp = document.getElementById('total-fatigue-value');
    const msgDisp = document.getElementById('fatigue-msg');
    
    // SVG Circumference for R=45 is ~282.7
    const circumference = 2 * Math.PI * 45;
    const offset = circumference - (score / 100) * circumference;
    
    gauge.style.strokeDashoffset = offset;
    valueDisp.innerText = `${score}%`;
    
    if (score < 30) {
        gauge.style.stroke = "#00ffaa";
        msgDisp.innerText = "STABLE / ALERT";
        msgDisp.style.color = "#00ffaa";
    } else if (score < 60) {
        gauge.style.stroke = "#ffaa00";
        msgDisp.innerText = "MILD FATIGUE";
        msgDisp.style.color = "#ffaa00";
    } else {
        gauge.style.stroke = "#ff3366";
        msgDisp.innerText = "CRITICAL FATIGUE";
        msgDisp.style.color = "#ff3366";
    }
}

function updateStatusDisplay(state) {
    const pulse = document.getElementById('status-pulse');
    const badge = document.getElementById('feed-status-badge');
    
    // Reset classes
    pulse.classList.remove('pulse-active', 'pulse-warning', 'pulse-critical');
    
    if (state === "AWAKE") {
        pulse.classList.add('pulse-active');
        badge.innerText = "ACTIVE";
    } else if (state === "DROWSY" || state === "CRITICAL") {
        pulse.classList.add('pulse-critical');
        badge.innerText = "CRITICAL";
    } else if (state === "YAWNING" || state.includes("DISTRACTED")) {
        pulse.classList.add('pulse-warning');
        badge.innerText = "WARNING";
    } else if (state === "NO_FACE") {
        pulse.classList.add('pulse-warning');
        badge.innerText = "SEARCHING...";
    } else {
        pulse.classList.add('pulse-active');
        badge.innerText = "LIVE";
    }
}

// EMERGENCY CONTACT LOGIC
function toggleContactEdit() {
    const editDiv = document.getElementById('contact-edit');
    editDiv.classList.toggle('hidden');
}

function saveContact() {
    const name = document.getElementById('edit-contact-name').value;
    const phone = document.getElementById('edit-contact-phone').value;
    
    if (name) document.getElementById('contact-name-display').innerText = name;
    if (phone) document.getElementById('contact-phone-display').innerText = phone;
    
    toggleContactEdit();
    addLogItem("Emergency contact updated.");
}

async function sendManualAlert() {
    addLogItem("Manual Emergency Alert triggered!", "alert");
    try {
        const res = await fetch('/api/manual_alert', { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: currentUser })
        });
        const data = await res.json();
        if (data.status === "success") {
            addLogItem("Emergency Dispatch notified via Telegram.", "success");
        }
    } catch (e) {
        addLogItem("Failed to send manual alert.", "alert");
    }
}

// Fetch GPS
async function updateGPS() {
    try {
        const res = await fetch('/api/location');
        const data = await res.json();
        if (data.lat) {
            document.getElementById('gps-display').innerText = `${data.lat.toFixed(4)}, ${data.lon.toFixed(4)}`;
        }
    } catch (e) {}
    
    setTimeout(updateGPS, 30000); // Update every 30s
}
updateGPS();

