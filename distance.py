import RPi.GPIO as GPIO
import os
import time

# Define GPIO to use on Pi
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO_TRIGGER = 23
GPIO_ECHO = 24

TRIGGER_TIME = 0.00001
MAX_TIME = 0.004  # max time waiting for response in case something is missed
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)  # Trigger
GPIO.setup(GPIO_ECHO, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Echo

GPIO.output(GPIO_TRIGGER, False)

# This function measures a distance


def measure():
    print("Starting measurement...")

    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(TRIGGER_TIME)
    GPIO.output(GPIO_TRIGGER, False)

    start = time.time()
    timeout = start + MAX_TIME

    # Wait for Echo to go HIGH (signal start)
    while GPIO.input(GPIO_ECHO) == 0 and start <= timeout:
        start = time.time()

    if start > timeout:
        print("⚠️ Echo never went HIGH (Timeout waiting for echo start)")
        return -1

    print("✔ Echo detected, measuring...")

    stop = time.time()
    timeout = stop + MAX_TIME

    # Wait for Echo to go LOW (signal end)
    while GPIO.input(GPIO_ECHO) == 1 and stop <= timeout:
        stop = time.time()

    if stop > timeout:
        print("⚠️ Echo never went LOW (Stuck HIGH)")
        return -1

    elapsed = stop - start
    distance = (elapsed * 34300) / 2.0
    print(f"📏 Measured distance: {distance:.1f} cm")
    return distance


if __name__ == "__main__":
    try:
        while True:
            distance = measure()
            if distance > -1:
                print("Measured Distance = %.1f cm" % distance)
            else:
                print("#")
            time.sleep(0.5)
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
