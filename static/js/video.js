const socket = io();
let videoActive = false;

function startVideo() {
    if (!videoActive) {
        socket.emit('start_video');
        videoActive = true;
    } else {
        // Add stop video functionality if needed
        videoActive = false;
    }
}

socket.on('video_frame', (data) => {
    const videoFeed = document.getElementById('video-feed');
    const blob = new Blob([data.frame], { type: 'image/jpeg' });
    const url = URL.createObjectURL(blob);
    videoFeed.style.backgroundImage = `url(${url})`;
});