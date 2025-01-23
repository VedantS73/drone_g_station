function armMotors() {
    fetch('/arm', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) alert('Motors armed!');
            else alert('Failed to arm motors');
        });
}

function takeoff() {
    fetch('/takeoff', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ altitude: 5 })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) alert('Taking off!');
        else alert('Takeoff failed');
    });
}

function move(direction) {
    fetch('/move', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ direction, speed: 2 })
    });
}

function setAltitudeMode() {
    const altitudeInput = document.getElementById('altitude-input');
    const altitude = parseFloat(altitudeInput.value);

    // Validate altitude input
    if (isNaN(altitude) || altitude < 0 || altitude > 100) {
        alert('Please enter a valid altitude between 0 and 100 meters.');
        return;
    }

    // Send altitude mode request to the server
    fetch('/set_altitude', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ altitude: altitude })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Altitude mode set to ${altitude} meters`);
            // Optional: You might want to update some UI element to show current altitude mode
        } else {
            alert('Failed to set altitude mode: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Altitude mode error:', error);
        alert('Error setting altitude mode');
    });
}