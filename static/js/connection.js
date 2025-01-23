function updateConnectionStatus(connected) {
    const statusIndicator = document.getElementById('connection-status');
    const statusText = document.getElementById('connection-text');
    
    if (connected) {
        statusIndicator.className = 'status-indicator status-connected';
        statusText.textContent = 'Connected';
    } else {
        statusIndicator.className = 'status-indicator status-disconnected';
        statusText.textContent = 'Disconnected';
    }
}

function connect() {
    const connectionData = {
        hostname: document.getElementById('hostname').value,
        username: document.getElementById('username').value,
        password: document.getElementById('password').value
    };

    fetch('/connect', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(connectionData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateConnectionStatus(true);
            startTelemetry();
        } else {
            updateConnectionStatus(false);
            alert('Connection failed: ' + data.message);
        }
    });
}

function startTelemetry() {
    telemetryInterval = setInterval(() => {
        fetch('/telemetry')
            .then(response => response.json())
            .then(data => {
                // Update telemetry values
                document.getElementById('lat').textContent = data.latitude?.toFixed(6) || '--';
                document.getElementById('lon').textContent = data.longitude?.toFixed(6) || '--';
                document.getElementById('alt').textContent = data.altitude?.toFixed(2) + ' m' || '--';
                document.getElementById('battery-level').textContent = data.battery ? data.battery + '%' : '--';
                document.getElementById('flight-mode').textContent = data.mode || '--';

                // Update map marker
                updateMapMarker(data.latitude, data.longitude);
            });
    }, 1000);
}

// Initialize with disconnected status
updateConnectionStatus(false);