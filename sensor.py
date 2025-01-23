from time import sleep
from sensors.bmp280 import BMP280


def main() -> None:
    bmp280 = BMP280(bus_number=1, i2c_addr=0x76)
    bmp280.set_config(t_sb="1000ms")
    bmp280.set_ctrl_meas(osrs_t="x16", osrs_p="x16", mode="normal")
    try:
        while True:
            temperature = bmp280.read_temperature()
            pressure = bmp280.read_pressure()
            print(f"Temperature: {temperature:0.1f}°C")
            print(f"Pressure: {pressure:0.1f} hPa")
            print("-" * 30)
            sleep(1)
    except KeyboardInterrupt:
        print("\nExiting gracefully")


if __name__ == "__main__":
    main()
