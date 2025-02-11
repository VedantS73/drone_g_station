from dronekit import connect, VehicleMode
import time

def establishConnection():
    baud_rate = 57600
    vehicle = connect('/dev/ttyAMA0', wait_ready=True, baud=baud_rate)
    return vehicle

def arm(vehicle):
    print("Preparing to arm...")
    
    vehicle.mode = VehicleMode("STABILIZE")  # Switch to STABILIZE mode for indoor flying
    vehicle.armed = True
    while not vehicle.armed:
        print("Waiting for drone to become armed...")
        time.sleep(1)

    print("Vehicle is now armed.")
    print("Props are spinning. CAUTION!")

def set_rc_channel_pwm(vehicle, channel_id, pwm=1500):
    """ Set RC channel pwm value
    Args:
        channel_id (int): Channel ID
        pwm (int, optional): Channel pwm value 1100-1900
    """
    if channel_id < 1 or channel_id > 8:
        print("Channel does not exist.")
        return
    
    # Set the channel override
    vehicle.channels.overrides[channel_id] = pwm

def clear_rc_override(vehicle, channel_id):
    """ Clear the RC channel override
    Args:
        channel_id (int): Channel ID
    """
    if channel_id < 1 or channel_id > 8:
        print("Channel does not exist.")
        return
    
    # Clear the channel override
    vehicle.channels.overrides[channel_id] = None

def indoor_flight(vehicle, duration):
    print(f"Attempting indoor flight for {duration} seconds...")
    
    # Increase throttle to take off
    set_rc_channel_pwm(vehicle, 3, 1600)  # Throttle channel (usually channel 3)
    
    flight_start = time.time()
    while time.time() - flight_start < duration:
        # You can add more control inputs here if needed
        print(f"Flight time: {time.time() - flight_start:.1f}s")
        time.sleep(1)
    
    # Gradually reduce throttle to land
    print("Landing...")
    set_rc_channel_pwm(vehicle, 3, 1450)  # Slightly below hover throttle
    time.sleep(2)
    set_rc_channel_pwm(vehicle, 3, 1400)  # Further reduce throttle
    time.sleep(2)
    set_rc_channel_pwm(vehicle, 3, 1300)  # Continue reducing
    time.sleep(2)
    
    # Cut throttle
    set_rc_channel_pwm(vehicle, 3, 1000)
    
    # Clear the override
    clear_rc_override(vehicle, 3)
    
    print("Flight complete")

def disarm(vehicle):
    print("Disarming...")
    vehicle.armed = False
    while vehicle.armed:
        print("Waiting for disarming...")
        time.sleep(1)
    print("Vehicle disarmed")

def main():
    vehicle = establishConnection()
    arm(vehicle)
    indoor_flight(vehicle, duration=15)  # 15 seconds of flight
    disarm(vehicle)
    vehicle.close()
    print("Mission complete.")

if __name__ == "__main__":
    main()