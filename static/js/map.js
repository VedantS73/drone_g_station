// Initialize map
const map = L.map('map').setView([0, 0], 2);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

let droneMarker = null;

function updateMapMarker(latitude, longitude) {
    if (latitude && longitude) {
        const position = [latitude, longitude];
        if (!droneMarker) {
            droneMarker = L.marker(position).addTo(map);
            map.setView(position, 18);
        } else {
            droneMarker.setLatLng(position);
            map.panTo(position);
        }
    }
}