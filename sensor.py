#!/usr/bin/env python3
import smbus
from time import sleep


def read_calibration(bus):
    """Read calibration values from 0x88 to 0x9F."""
    cal = []
    # Read T1-T3, P1-P9 calibration values
    for addr in range(0x88, 0x9F, 2):
        val = bus.read_word_data(0x76, addr)
        # Convert to negative number if needed (except for T1 and P1)
        if addr not in [0x88, 0x8E] and val > 32767:
            val -= 65536
        cal.append(val)
    return cal


def read_raw_data(bus):
    """Read raw temperature and pressure data."""
    d = [bus.read_byte_data(0x76, reg) for reg in [0xFA, 0xFB, 0xFC]]
    temp = ((d[0] << 16) | (d[1] << 8) | d[2]) >> 4

    d = [bus.read_byte_data(0x76, reg) for reg in [0xF7, 0xF8, 0xF9]]
    pres = ((d[0] << 16) | (d[1] << 8) | d[2]) >> 4

    return temp, pres


def calculate_temp(adc_T, cal):
    """Calculate temperature using calibration values."""
    var1 = (((adc_T >> 3) - (cal[0] << 1)) * cal[1]) >> 11
    var2 = (((((adc_T >> 4) - cal[0]) * ((adc_T >> 4) - cal[0])) >> 12) * cal[2]) >> 14
    t_fine = var1 + var2
    temp = (t_fine * 5 + 128) >> 8
    return temp / 100, t_fine


def calculate_pressure(adc_P, t_fine, cal):
    """Calculate pressure using calibration values."""
    var1 = t_fine - 128000
    var2 = var1 * var1 * cal[6]
    var2 = var2 + ((var1 * cal[5]) << 17)
    var2 = var2 + (cal[4] << 35)

    var1 = ((var1 * var1 * cal[3]) >> 8) + ((var1 * cal[4]) << 12)
    var1 = ((1 << 47) + var1) * cal[3] >> 33

    if var1 == 0:
        return 0

    p = 1048576 - adc_P
    p = (((p << 31) - var2) * 3125) // var1

    var1 = (cal[9] * (p >> 13) * (p >> 13)) >> 25
    var2 = (cal[8] * p) >> 19

    p = ((p + var1 + var2) >> 8) + (cal[7] << 4)
    return p / 25600


def main():
    """Initialize sensor and continuously read values."""
    try:
        bus = smbus.SMBus(1)
        # Initialize sensor settings
        bus.write_byte_data(0x76, 0xF5, (5 << 5))
        bus.write_byte_data(0x76, 0xF4, ((5 << 5) | (5 << 2) | (3 << 0)))
        sleep(0.1)

        cal = read_calibration(bus)
        print("BMP280 Sensor - Press Ctrl+C to exit\n")

        while True:
            adc_T, adc_P = read_raw_data(bus)
            temp, t_fine = calculate_temp(adc_T, cal)
            pres = calculate_pressure(adc_P, t_fine, cal)

            print(f"Temperature: {temp:0.1f}°C")
            print(f"Pressure: {pres:0.1f} hPa")
            print("-" * 30)
            sleep(1)

    except KeyboardInterrupt:
        print("\nExiting gracefully")


if __name__ == "__main__":
    main()

