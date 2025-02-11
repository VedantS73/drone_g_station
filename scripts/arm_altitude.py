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

def land():
    vehicle.mode = VehicleMode("LAND")
    print("Landing...")

vehicle = establishConnection()
arm()
takeoff_and_spin(15)
land()
print("End of script.")
