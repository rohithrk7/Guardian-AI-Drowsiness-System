let isSignupMode = false;
let currentUser = 'Driver';
let incidentChartInstance = null;

function toggleMode() {
    isSignupMode = !isSignupMode;
    
    const title = document.getElementById('auth-title');
    const registerFields = document.getElementById('register-fields');
    const btnText = document.getElementById('btn-text');
    const toggleWrap = document.getElementById('toggle-wrap');
    const licenseInput = document.getElementById('license-plate');

    if (isSignupMode) {
        // Switch to Register Mode
        title.innerHTML = 'Register <span>Profile</span>';
        registerFields.classList.add('open');
        licenseInput.setAttribute('required', 'true');
        btnText.innerText = 'Create Profile';
        toggleWrap.innerHTML = `Already registered? <span onclick="toggleMode()">Login</span>`;
    } else {
        // Switch to Login Mode
        title.innerHTML = 'Driver <span>Login</span>';
        registerFields.classList.remove('open');
        licenseInput.removeAttribute('required');
        btnText.innerText = 'Authenticate System';
        toggleWrap.innerHTML = `New Fleet Driver? <span onclick="toggleMode()">Register Here</span>`;
    }
}

function handleAuth(e) {
    e.preventDefault();
    
    // Show loading animation
    const btnText = document.getElementById('btn-text');
    const spinner = document.getElementById('btn-spinner');
    
    btnText.style.display = 'none';
    spinner.style.display = 'block';

    // Simulate network delay for premium feel
    setTimeout(() => {
        btnText.style.display = 'block';
        spinner.style.display = 'none';
        
        currentUser = document.getElementById('username').value || 'Driver';
        document.getElementById('dash-username').innerText = currentUser;
        
        // Fetch User History
        fetch(`/api/stats/${currentUser}`)
            .then(res => res.json())
            .then(data => {
                document.getElementById('score-text').innerText = `${data.score}/100`;
                document.getElementById('score-text').style.color = data.score > 80 ? '#00ffaa' : (data.score > 50 ? '#ffb033' : '#ff3366');
                document.getElementById('trips-text').innerText = data.trips;
                
                renderChart(data);
            });
        
        // Switch Views
        document.getElementById('auth-view').classList.remove('active');
        document.getElementById('dashboard-view').classList.add('active');
        
    }, 1200);
}

function renderChart(data) {
    const ctx = document.getElementById('incidentChart').getContext('2d');
    
    if (incidentChartInstance) {
        incidentChartInstance.destroy();
    }
    
    Chart.defaults.color = "#aaaaaa";
    Chart.defaults.font.family = "'Outfit', sans-serif";
    
    incidentChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['EAR Drowsiness', 'MAR Yawns', 'Head Distraction'],
            datasets: [{
                label: 'Total Incident Triggers',
                data: [data.drowsy_count, data.yawn_count, data.distraction_count],
                backgroundColor: [
                    'rgba(255, 51, 102, 0.7)',  // Red
                    'rgba(0, 165, 255, 0.7)',   // Orange
                    'rgba(0, 230, 255, 0.7)'    // Cyan
                ],
                borderColor: [
                    '#ff3366',
                    '#00a5ff',
                    '#00e6ff'
                ],
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255,255,255,0.05)' }
                },
                x: {
                    grid: { display: false }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function logout() {
    document.getElementById('dashboard-view').classList.remove('active');
    
    // Wait for fade out, then show login again
    setTimeout(() => {
        document.getElementById('auth-view').classList.add('active');
        document.getElementById('auth-form').reset();
        if(isSignupMode) toggleMode(); // reset to login
    }, 500);
}

let isCameraRunning = false;

async function toggleCamera() {
    const btn = document.getElementById('camera-btn');
    const statusText = document.getElementById('camera-status-text');
    
    if (!isCameraRunning) {
        // -> START SEQUENCE
        btn.style.boxShadow = "0 0 40px rgba(255, 51, 102, 0.8)";
        btn.style.borderColor = "#ff3366";
        btn.style.color = "#ff3366";
        btn.innerText = "TERMINATE AI FEED";
        statusText.innerHTML = "<span style='color:#00ffaa;'>Connecting AI Model... Look at the webcam.</span>";
        
        try {
            const response = await fetch('/start_camera', { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: currentUser })
            });
            const result = await response.json();
            
            if(result.status === 'success') {
                statusText.innerHTML = "<span style='color:#00ffaa;'>AI Camera Feed active on your desktop window.</span>";
                isCameraRunning = true;
            }
        } catch (error) {
            statusText.innerHTML = "<span style='color:#ff3366;'>Error: Could not reach Python Backend Server.</span>";
            btn.style.borderColor = "var(--primary)";
            btn.style.color = "var(--primary)";
            btn.innerText = "INITIALIZE CAMERA";
            btn.style.boxShadow = "0 0 20px rgba(0, 230, 255, 0.2), inset 0 0 10px rgba(0, 230, 255, 0.1)";
            isCameraRunning = false;
        }
    } else {
        // -> STOP SEQUENCE
        try {
            const response = await fetch('/stop_camera', { method: 'POST' });
            const result = await response.json();
            
            if(result.status === 'success') {
                btn.style.boxShadow = "0 0 20px rgba(0, 230, 255, 0.2), inset 0 0 10px rgba(0, 230, 255, 0.1)";
                btn.style.borderColor = "var(--primary)";
                btn.style.color = "var(--primary)";
                btn.innerText = "INITIALIZE CAMERA";
                statusText.innerHTML = "<span style='color:#aaa;'>Network secured. Ready for deployment.</span>";
                isCameraRunning = false;
            }
        } catch (error) {
            statusText.innerHTML = "<span style='color:#ff3366;'>Error: Failed to stop camera process.</span>";
        }
    }
}
