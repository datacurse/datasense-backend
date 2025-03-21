import RPi.GPIO as GPIO
import time

# Define GPIO pins
TRIGPIN = 17  # GPIO 11
ECHOPIN = 27  # GPIO 10

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIGPIN, GPIO.OUT)
GPIO.setup(ECHOPIN, GPIO.IN)

def measure_distance():
    # Set the trigger pin LOW and wait for 2 microseconds
    GPIO.output(TRIGPIN, False)
    time.sleep(2e-6)  # 2 microseconds

    # Set the trigger pin HIGH and wait for 20 microseconds
    GPIO.output(TRIGPIN, True)
    time.sleep(20e-6)  # 20 microseconds
    GPIO.output(TRIGPIN, False)

    # Measure the width of the incoming pulse
    while GPIO.input(ECHOPIN) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHOPIN) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start

    # Calculate distance: distance = (duration / 2) * 0.343 (in mm)
    distance = (pulse_duration / 2) * 34300  # Convert to millimeters

    return distance

try:
    while True:
        dist = measure_distance()
        print(f"Distance: {dist:.2f} mm")
        time.sleep(0.1)  # Delay before next measurement

except KeyboardInterrupt:
    print("Measurement stopped by user")
    GPIO.cleanup()  # Clean up GPIO pins
