from gpiozero import LED
from time import sleep

"""
Wiring setup:
- Red wire: GPIO17 -> 220Ω resistor -> LED longer leg (+)
- Black wire: LED shorter leg (-) -> GND (Pin 6, 9, 14, 20, 25, 30, 34, or 39)
"""

# Initialize LED on GPIO17
led = LED(17)

try:
    while True:
        # Test pattern: on for 1 second, off for 1 second
        print("LED turning ON")
        led.on()
        sleep(1)

        print("LED turning OFF")
        led.off()
        sleep(1)

except KeyboardInterrupt:
    # Clean up when user presses CTRL+C
    print("\nCleaning up...")
    led.close()

