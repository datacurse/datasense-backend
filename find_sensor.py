from smbus2 import SMBus
import time


def find_sensor_address():
    for addr in [0x76, 0x77]:
        try:
            bus = SMBus(1)
            bus.read_byte(addr)
            print(f"Found sensor at address 0x{addr:02x}")
            return addr
        except Exception as e:
            print(f"Nothing at address 0x{addr:02x}: {str(e)}")
            continue
    print("No sensor found")
    return None


# Add initial delay to let sensor boot up
print("Waiting for sensor to initialize...")
time.sleep(2)

# Try to find the sensor
address = find_sensor_address()
if address:
    print(f"Use this address in your main script: 0x{address:02x}")
