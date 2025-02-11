from dronekit import connect, VehicleMode
import time

def establishConnection():
    baud_rate = 57600
    vehicle = connect('/dev/ttyAMA0', wait_ready=False, baud=baud_rate)
    return vehicle

def bypass_checks_and_arm():
    """
    Bypass pre-arm checks and arm the vehicle.
    """
    print("Disabling all safety checks and forcing arming...")

    # Set mode to STABILIZE to avoid GPS and other sensor dependencies
    vehicle.mode = VehicleMode("STABILIZE")

    # Arm the motors immediately
    vehicle.armed = True

    # Confirm the vehicle is armed
    while not vehicle.armed:
        print(" Waiting for arming...")
        time.sleep(1)

    print("Vehicle armed! Motors should be spinning now.")

def spin_motors_for_seconds(throttle_value, duration):
    """
    Spin motors at the specified throttle value (1500) for a set duration (seconds).
    Throttle is typically controlled via RC Channel 3.
    """
    print(f"Spinning motors at throttle {throttle_value} for {duration} seconds.")

    # Set RC3 (throttle) to the specified throttle_value (1500 for mid-throttle)
    vehicle.channels.overrides['3'] = throttle_value

    # Wait for the specified duration
    time.sleep(duration)

    # After spinning, reset the RC3 override (return control to the autopilot)
    vehicle.channels.overrides['3'] = None
    print("Throttle override cleared, motors stopped.")

# Establish connection
vehicle = establishConnection()

# Bypass checks and arm the motors
bypass_checks_and_arm()

# Spin motors at throttle 1500 for X seconds (e.g., 5 seconds)
spin_motors_for_seconds(1500, 15)

# Disarm the vehicle after spinning
vehicle.armed = False
print("Vehicle disarmed. End of script.")
