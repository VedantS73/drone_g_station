from dronekit import connect, VehicleMode, APIException
import time
import argparse

def establishConnection():
    baud_rate = 57600
    vehicle = connect('/dev/ttyAMA0', wait_ready=True, baud=baud_rate)

    return vehicle

def arm():
    print("Yoooo vehicle is now armable")
    print("")
    
    vehicle.mode = VehicleMode("ALT_HOLD")  # Switch to ALT_HOLD mode
    vehicle.armed = True
    while vehicle.armed == False:
        print("Waiting for drone to become armed...")
        time.sleep(1)

    print("Vehicle is now armed.")
    print("OMG props are spinning. LOOK OUT!!!!!")

    return None

def takeoff_and_spin(duration):
    print("Hovering and spinning propellers...")
    
    # We don't need to take off to a high altitude, since we are in ALT_HOLD mode
    target_altitude = 1  # This sets the hover altitude to a low level
    vehicle.simple_takeoff(target_altitude)

    time.sleep(duration)  # Let the drone hover and spin for the specified duration

    print(f"Landing after spinning for {duration} seconds.")
    vehicle.mode = VehicleMode("LAND")  # Set mode to LAND after hovering

def manual_throttle(throttle_value, duration):
    print(f"Setting throttle to {throttle_value} for {duration} seconds...")
    
    # Throttle is on channel 3 in RC (1000-2000 microseconds)
    vehicle.channels.overrides['3'] = throttle_value
    
    time.sleep(duration)
    
    # Clear the override after duration
    vehicle.channels.overrides['3'] = None
    print("Throttle override cleared")

def land():
    print("Switching to LAND mode...")
    vehicle.mode = VehicleMode("LAND")
    
    # Wait until the vehicle is on the ground
    while vehicle.armed:
        print("Waiting for the vehicle to land...")
        time.sleep(1)

    print("Vehicle has landed and disarmed.")
    vehicle.armed = False  # Ensure that the vehicle disarms after landing

vehicle = establishConnection()
arm()

# Increase throttle for hover and motor testing
manual_throttle(1900, 20)

# Land the drone safely
land()

print("End of script.")
