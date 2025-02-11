from dronekit import connect, VehicleMode, APIException
import time
import argparse

# def connectMyCopter():
#     parser = argparse.ArgumentParser(description="commands")
#     parser.add_argument('--connect')
#     args = parser.parse_args()

#     connection_string = args.connect
#     baud_rate = 57600

#     vehicle = connect(connection_string, baud=baud_rate, wait_ready=True)
#     return vehicle

def establishConnection():
    baud_rate = 57600
    vehicle = connect('/dev/ttyAMA0', wait_ready=True, baud=baud_rate)

    return vehicle

def set_home_location():
    """
    Check and set the home location for the vehicle.
    """
    while not vehicle.home_location:
        print("Waiting for home location to be set...")
        cmds = vehicle.commands
        cmds.download()
        cmds.wait_ready()
        time.sleep(1)

    # If home location is still not set, set it manually to current location
    if not vehicle.home_location:
        print("Setting home location to the current location...")
        vehicle.home_location = vehicle.location.global_frame

    print(f"Home Location: {vehicle.home_location}")

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
    vehicle.mode = VehicleMode("LAND")
    print("Landing...")
    
def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    print("Basic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print(" Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode    = VehicleMode("GUIDED")
    vehicle.armed   = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print(" Altitude: ", vehicle.location.global_relative_frame.alt)
        #Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

# vehicle = connectMyCopter()
vehicle = establishConnection()
set_home_location()
arm_and_takeoff(2)
# arm()
# takeoff_and_spin(5)  # Hover for 5 seconds
# manual_throttle(1500, 5)
land()
print("End of script.")
