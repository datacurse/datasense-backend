import smbus
from time import sleep


def main():
    """Initialize sensor and continuously read values."""
    try:
        bus = smbus.SMBus(1)
        i2c_addr = 0x76

        # Initialize sensor settings
        bus.write_byte_data(i2c_addr, 0xF5, (5 << 5))
        bus.write_byte_data(i2c_addr, 0xF4, ((5 << 5) | (5 << 2) | (3 << 0)))
        sleep(0.1)

        def rwd(register):
            return bus.read_word_data(i2c_addr, register)

        def sign(value):
            return value - 65536 if value > 32767 else value

        def p(x, *funcs):
            for f in funcs:
                x = f(x)
            return x

        dig_T1 = p(0x88, rwd)
        dig_T2 = p(0x8A, rwd, sign)
        dig_T3 = p(0x8C, rwd, sign)
        dig_P1 = p(0x8E, rwd)
        dig_P2 = p(0x90, rwd, sign)
        dig_P3 = p(0x92, rwd, sign)
        dig_P4 = p(0x94, rwd, sign)
        dig_P5 = p(0x96, rwd, sign)
        dig_P6 = p(0x98, rwd, sign)
        dig_P7 = p(0x9A, rwd, sign)
        dig_P8 = p(0x9C, rwd, sign)
        dig_P9 = p(0x9E, rwd, sign)

        def calculate_temp(adc_T):
            var1 = (((adc_T >> 3) - (dig_T1 << 1)) * dig_T2) >> 11
            var2 = (
                ((((adc_T >> 4) - dig_T1) * ((adc_T >> 4) - dig_T1)) >> 12) * dig_T3
            ) >> 14
            t_fine = var1 + var2
            temp = (t_fine * 5 + 128) >> 8
            return temp / 100, t_fine

        def calculate_pressure(adc_P, t_fine):
            var1 = t_fine - 128000
            var2 = var1 * var1 * dig_P6
            var2 = var2 + ((var1 * dig_P5) << 17)
            var2 = var2 + (dig_P4 << 35)

            var1 = ((var1 * var1 * dig_P3) >> 8) + ((var1 * dig_P2) << 12)
            var1 = ((1 << 47) + var1) * dig_P1 >> 33

            if var1 == 0:
                return 0

            p = 1048576 - adc_P
            p = (((p << 31) - var2) * 3125) // var1

            var1 = (dig_P9 * (p >> 13) * (p >> 13)) >> 25
            var2 = (dig_P8 * p) >> 19

            p = ((p + var1 + var2) >> 8) + (dig_P7 << 4)
            return p / 25600

        def rbd(register):
            return bus.read_byte_data(i2c_addr, register)

        while True:
            temp_msb = rbd(0xFA) << 12
            temp_lsb = rbd(0xFB) << 4
            temp_xlsb = rbd(0xFC) >> 4
            adc_T = temp_msb + temp_lsb + temp_xlsb

            press_msb = rbd(0xF7) << 12
            press_lsb = rbd(0xF8) << 4
            press_xlsb = rbd(0xF9) >> 4
            adc_P = press_msb + press_lsb + press_xlsb

            temp, t_fine = calculate_temp(adc_T)
            pres = calculate_pressure(
                adc_P,
                t_fine,
            )

            print(f"Temperature: {temp:0.1f}°C")
            print(f"Pressure: {pres:0.1f} hPa")
            print("-" * 30)
            sleep(1)

    except KeyboardInterrupt:
        print("\nExiting gracefully")


if __name__ == "__main__":
    main()

