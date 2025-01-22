import smbus
from time import sleep


def p(x, *funcs):
    for f in funcs:
        x = f(x)
    return x


def set_config(t_sb="1000ms", filter="off", spi3w="disable"):
    _t_sb = {
        "0.5ms": 0b000,
        "62.5ms": 0b001,
        "125ms": 0b010,
        "250ms": 0b011,
        "500ms": 0b100,
        "1000ms": 0b101,
        "2000ms": 0b110,
        "4000ms": 0b111,
    }
    _filter = {"off": 0b000, "2": 0b001, "4": 0b010, "8": 0b011, "16": 0b100}
    _spi3w = {"disable": 0b0, "enable": 0b1}

    value = (_t_sb[t_sb] << 5) | (_filter[filter] << 2) | (_spi3w[spi3w])
    wbd(0xF5, value)


def set_ctrl_meas(osrs_t="x16", osrs_p="x16", mode="normal"):
    _osrs_t = {
        "skip": 0b000,
        "x1": 0b001,
        "x2": 0b010,
        "x4": 0b011,
        "x8": 0b100,
        "x16": 0b101,
    }
    _osrs_p = {
        "skip": 0b000,
        "x1": 0b001,
        "x2": 0b010,
        "x4": 0b011,
        "x8": 0b100,
        "x16": 0b101,
    }
    _mode = {"sleep": 0b00, "forced": 0b01, "normal": 0b11}
    value = (_osrs_t[osrs_t] << 5) | (_osrs_p[osrs_p] << 2) | _mode[mode]
    wbd(0xF4, value)


bus = smbus.SMBus(1)
i2c_addr = 0x76


def rbd(register):
    return bus.read_byte_data(i2c_addr, register)


def wbd(register, value):
    bus.write_byte_data(i2c_addr, register, value)


def rwd(register):
    return bus.read_word_data(i2c_addr, register)


def sign(value):
    return value - 65536 if value > 32767 else value


set_config(t_sb="1000ms", filter="16")
set_ctrl_meas(osrs_t="x16", osrs_p="x16", mode="normal")

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
    var2 = (((((adc_T >> 4) - dig_T1) * ((adc_T >> 4) - dig_T1)) >> 12) * dig_T3) >> 14
    t_fine = var1 + var2
    temp = (t_fine * 5 + 128) >> 8
    temp /= 100
    return temp, t_fine


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
    p /= 25600
    return p


def read_raw_temperature():
    temp_msb = rbd(0xFA) << 12
    temp_lsb = rbd(0xFB) << 4
    temp_xlsb = rbd(0xFC) >> 4
    adc_T = temp_msb + temp_lsb + temp_xlsb
    return adc_T


def read_raw_pressure():
    press_msb = rbd(0xF7) << 12
    press_lsb = rbd(0xF8) << 4
    press_xlsb = rbd(0xF9) >> 4
    adc_P = press_msb + press_lsb + press_xlsb
    return adc_P


def read_temperature():
    adc_T = read_raw_temperature()
    temp, _ = calculate_temp(adc_T)
    return temp


def read_pressure():
    adc_T = read_raw_temperature()
    adc_P = read_raw_pressure()
    _, t_fine = calculate_temp(adc_T)
    press = calculate_pressure(
        adc_P,
        t_fine,
    )
    return press


def main():
    try:
        while True:
            temperature = read_temperature()
            pressure = read_pressure()
            print(f"Temperature: {temperature:0.1f}°C")
            print(f"Pressure: {pressure:0.1f} hPa")
            print("-" * 30)
            sleep(1)

    except KeyboardInterrupt:
        print("\nExiting gracefully")


if __name__ == "__main__":
    main()

