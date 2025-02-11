from picamera2 import Picamera2
import time

def initialize_camera():
    """Initialize the camera with some basic settings"""
    try:
        # Initialize camera
        picam2 = Picamera2()
        
        # Configure the camera
        config = picam2.create_preview_configuration()
        picam2.configure(config)
        
        # Start the camera
        picam2.start()
        
        # Wait for camera to warm up
        time.sleep(2)
        
        return picam2
    except Exception as e:
        print(f"Error initializing camera: {e}")
        return None

def main():
    # Initialize camera
    camera = initialize_camera()
    if camera is None:
        print("Failed to initialize camera. Please check if:")
        print("1. PiCamera is properly connected")
        print("2. Camera is enabled in raspi-config")
        print("3. You have the necessary permissions")
        return

    try:
        # Capture a single image
        print("Capturing image...")
        camera.capture_file("test_photo.jpg")
        print("Image saved as 'test_photo.jpg'")
        
        # Capture a sequence of 3 images
        print("\nCapturing sequence of images...")
        for i in range(3):
            camera.capture_file(f"sequence_{i}.jpg")
            print(f"Captured sequence_{i}.jpg")
            time.sleep(1)
            
    except Exception as e:
        print(f"Error during capture: {e}")
    
    finally:
        # Clean up
        camera.close()
        print("\nCamera cleaned up and closed")

if __name__ == "__main__":
    main()
