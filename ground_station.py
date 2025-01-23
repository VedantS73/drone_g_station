# ground_station.py
import dronekit_patch
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import paramiko
from collections.abc import MutableMapping
# from dronekit import connect, VehicleMode
from dronekit import connect as dronekit_connect
from dronekit import VehicleMode
import cv2
import numpy as np
import threading
import time
import json
import socket

app = Flask(__name__)
socketio = SocketIO(app)

class DroneController:
    def __init__(self):
        self.vehicle = None
        self.ssh_client = None
        self.video_stream = None
        self.streaming = False
        self.mavlink_port = 5760  # Default MAVLink port
    
    def connect_ssh(self, hostname="raspberrypi.local", username="pi", password="raspberry"):
        """Establish SSH connection to Raspberry Pi"""
        try:
            print(f"Attempting SSH connection to {hostname}...")
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(hostname, username=username, password=password, timeout=10)
            print("SSH connection successful")
            
            # Check if MAVProxy is running
            stdin, stdout, stderr = self.ssh_client.exec_command('pgrep -f mavproxy.py')
            if not stdout.read():
                print("Starting MAVProxy...")
                # Start MAVProxy if it's not running
                # Adjust the serial port (/dev/ttyAMA0) according to your Pixhawk connection
                cmd = f'mavproxy.py --master=/dev/ttyAMA0 --out=tcpin:0.0.0.0:{self.mavlink_port}'
                stdin, stdout, stderr = self.ssh_client.exec_command(f'nohup {cmd} > /dev/null 2>&1 &')
                time.sleep(5)  # Wait for MAVProxy to start
            
            return True
        except Exception as e:
            print(f"SSH Connection failed with error: {str(e)}")
            return False
    
    def connect_drone(self):
        """Connect to drone via MAVLink"""
        try:
            # Get the IP address from the SSH connection
            remote_ip = self.ssh_client.get_transport().getpeername()[0]
            connection_string = f'tcp:{remote_ip}:{self.mavlink_port}'
            print(f"Attempting to connect to drone at {connection_string}")
            
            # Try to establish connection
            self.vehicle = dronekit_connect(connection_string)
            
            # Manually wait for parameters to be ready
            print("Waiting for vehicle parameters...")
            while not self.vehicle.is_armable:
                print(f"System status: {self.vehicle.system_status.state}")
                print(f"Is armable: {self.vehicle.is_armable}")
                print("Waiting for vehicle initialization...")
                print(f"GPS fix type: {self.vehicle.gps_0.fix_type}")
                print(f"Number of satellites: {self.vehicle.gps_0.satellites_visible}")
                # print(f"Battery voltage: {self.vehicle.battery.voltage}")
                # print(f"Battery level: {self.vehicle.battery.level}")
                print('----------------------------EOF---------------------------------')

                time.sleep(1)
            
            print("Successfully connected to the drone!")
            return True

        except socket.timeout:
            print("Timeout while connecting to drone. Check if MAVProxy is running and port is correct.")
            return False
        except Exception as e:
            print(f"Drone connection failed with error: {str(e)}")
            return False
    
    def get_telemetry(self):
        """Get current drone telemetry data"""
        if self.vehicle:
            try:
                return {
                    'latitude': self.vehicle.location.global_relative_frame.lat if hasattr(self.vehicle.location, 'global_relative_frame') else None,
                    'longitude': self.vehicle.location.global_relative_frame.lon if hasattr(self.vehicle.location, 'global_relative_frame') else None,
                    'altitude': self.vehicle.location.global_relative_frame.alt if hasattr(self.vehicle.location, 'global_relative_frame') else None,
                    'battery': self.vehicle.battery.level if hasattr(self.vehicle, 'battery') and self.vehicle.battery else None,
                    'mode': self.vehicle.mode.name if hasattr(self.vehicle, 'mode') and self.vehicle.mode else None,
                    'armed': self.vehicle.armed if hasattr(self.vehicle, 'armed') else None,
                    'system_status': self.vehicle.system_status.state if hasattr(self.vehicle, 'system_status') and self.vehicle.system_status else None
                }
            except Exception as e:
                print(f"Error getting telemetry: {str(e)}")
                return None
        return None

    def arm_motors(self):
        """Arm the drone motors"""
        if not self.vehicle:
            return False
        try:
            print("Attempting to arm motors...")
            self.vehicle.armed = True
            time.sleep(1)
            return self.vehicle.armed
        except Exception as e:
            print(f"Error arming motors: {str(e)}")
            return False
    
    def takeoff(self, target_altitude):
        """Take off to specified altitude"""
        if not self.vehicle:
            return False
        try:
            if not self.vehicle.armed:
                print("Cannot takeoff - motors not armed")
                return False
            print(f"Taking off to altitude: {target_altitude}m")
            self.vehicle.simple_takeoff(target_altitude)
            return True
        except Exception as e:
            print(f"Takeoff failed: {str(e)}")
            return False
    
    def move(self, direction, speed):
        """Move drone in specified direction"""
        if not self.vehicle or not self.vehicle.armed:
            return False
        try:    
            # Create movement command based on direction
            if direction == 'forward':
                self.vehicle.send_mavlink(self.vehicle.message_factory.set_position_target_local_ned_encode(
                    0, 0, 0, 1, 0b0000111111000111,
                    0, speed, 0, 0, 0, 0, 0, 0, 0, 0, 0))
            # Add other directions as needed
            return True
        except Exception as e:
            print(f"Movement failed: {str(e)}")
            return False

    def start_video_stream(self):
        """Start video streaming from RPi camera"""
        if not self.ssh_client:
            return False
        try:    
            stdin, stdout, stderr = self.ssh_client.exec_command('raspivid -t 0 -w 640 -h 480 -fps 25 -b 2000000 -o -')
            self.video_stream = stdout.read(1024)
            self.streaming = True
            return True
        except Exception as e:
            print(f"Video streaming failed: {str(e)}")
            return False

drone_controller = DroneController()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('index2.html')

@app.route('/connect', methods=['POST'])
def connect():
    data = request.json
    print(f"Connecting to {data.get('hostname', 'raspberrypi.local')}...")
    
    ssh_success = drone_controller.connect_ssh(
        hostname=data.get('hostname', 'raspberrypi.local'),
        username=data.get('username', 'pi'),
        password=data.get('password', 'raspberry')
    )
    
    if ssh_success:
        print("SSH connected, attempting drone connection...")
        drone_success = drone_controller.connect_drone()
        return jsonify({
            'success': drone_success,
            'message': 'Connected to drone' if drone_success else 'Failed to connect to drone'
        })
    return jsonify({'success': False, 'message': 'SSH connection failed'})

@app.route('/telemetry')
def telemetry():
    data = drone_controller.get_telemetry()
    return jsonify(data if data else {'error': 'No telemetry data available'})

@app.route('/arm', methods=['POST'])
def arm():
    success = drone_controller.arm_motors()
    return jsonify({'success': success})

@app.route('/takeoff', methods=['POST'])
def takeoff():
    altitude = request.json.get('altitude', 1)  # Default 5 meters
    success = drone_controller.takeoff(altitude)
    return jsonify({'success': success})

@app.route('/move', methods=['POST'])
def move():
    direction = request.json.get('direction')
    speed = request.json.get('speed', 1)  # Default 2 m/s
    success = drone_controller.move(direction, speed)
    return jsonify({'success': success})

@app.route('/set_altitude', methods=['POST'])
def set_altitude():
    if not drone_controller.vehicle:
        return jsonify({'success': False, 'message': 'Drone not connected'})
    
    data = request.json
    altitude = data.get('altitude')
    
    if altitude is None or not isinstance(altitude, (int, float)) or altitude < 0 or altitude > 100:
        return jsonify({'success': False, 'message': 'Invalid altitude'})
    
    try:
        # Store current mode to revert back later
        original_mode = drone_controller.vehicle.mode
        
        # Ensure the vehicle is armed before changing mode
        if not drone_controller.vehicle.armed:
            drone_controller.arm_motors()
        
        # Change to ALT_HOLD mode
        drone_controller.vehicle.mode = VehicleMode("ALT_HOLD")
        
        print("Hovering and spinning propellers...")
        target_altitude = altitude
        drone_controller.vehicle.simple_takeoff(target_altitude)
        
        # Wait for 15 seconds
        time.sleep(15)
        
        print(f"Landing after spinning for {15} seconds.")
        drone_controller.vehicle.mode = VehicleMode("LAND")
        
        return jsonify({
            'success': True,
            'message': f'ALT_HOLD mode set for 15 seconds at {altitude} meters'
        })
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Error setting altitude hold: {str(e)}'
        })

@socketio.on('start_video')
def handle_video_stream():
    if drone_controller.start_video_stream():
        while drone_controller.streaming:
            if drone_controller.video_stream:
                emit('video_frame', {'frame': drone_controller.video_stream})
            time.sleep(0.04)  # 25 FPS

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)