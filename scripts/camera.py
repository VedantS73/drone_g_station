from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput
import socket
import time
import signal
import sys

class StreamingServer:
    def __init__(self, host='0.0.0.0', port=8000):
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((host, port))
        self.server_socket.listen(0)
        self.connection = None
        self.stream_output = None
        
    def start(self):
        print(f"Waiting for connection on port 8000...")
        self.connection = self.server_socket.accept()[0].makefile('wb')
        return self.connection
    
    def cleanup(self):
        if self.connection:
            self.connection.close()
        self.server_socket.close()
        print("\nStreaming server cleaned up")

def setup_camera():
    """Initialize and configure the camera for video streaming"""
    picam2 = Picamera2()
    video_config = picam2.create_video_configuration(
        main={"size": (640, 480)},
        buffer_count=4,
        encode="main"
    )
    picam2.configure(video_config)
    return picam2

def signal_handler(sig, frame):
    """Handle graceful shutdown on CTRL+C"""
    print("\nShutting down gracefully...")
    cleanup()
    sys.exit(0)

def cleanup():
    """Cleanup function to be called before exit"""
    try:
        if 'picam2' in globals():
            picam2.stop_encoder()
            picam2.close()
        if 'server' in globals():
            server.cleanup()
    except Exception as e:
        print(f"Error during cleanup: {e}")

def main():
    global picam2, server
    
    # Setup signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Initialize the streaming server
        server = StreamingServer()
        
        # Setup the camera
        picam2 = setup_camera()
        
        # Create H264 encoder
        encoder = H264Encoder(bitrate=1000000)  # 1Mbps
        
        # Start the camera
        picam2.start()
        print("Camera started, waiting 2 seconds for warmup...")
        time.sleep(2)
        
        # Wait for client connection
        connection = server.start()
        print("Client connected, starting stream...")
        
        # Create output for the encoder
        output = FileOutput(connection)
        
        # Start the encoder with the file output
        picam2.start_encoder(encoder, output)
        
        print("Streaming... Press CTRL+C to stop.")
        
        # Keep the stream running
        while True:
            time.sleep(1)
            
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    main()
