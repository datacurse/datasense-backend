import smbus
from toolz import pipe
from ctypes import c_int16


def sign(value: int) -> int:
    return c_int16(value).value


class BMP280:
    """
    Description:
    The BMP280 is an absolute barometric pressure sensor,
    which is especially feasible for mobile applications.
    Its small dimensions and its low power consumption
    allow for the implementation in battery-powered devices
    such as mobile phones, GPS modules or watches.

    Datasheet link:
    https://cdn-shop.adafruit.com/datasheets/BST-BMP280-DS001-11.pdf
    """

    T_SB = {
        "0.5ms": 0,
        "62.5ms": 1,
        "125ms": 2,
        "250ms": 3,
        "500ms": 4,
        "1000ms": 5,
        "2000ms": 6,
        "4000ms": 7,
    }
    FILTER = {"off": 0, "2": 1, "4": 2, "8": 3, "16": 4}
    SPI3W = {"disable": 0, "enable": 1}
    OSRS_T = {"skip": 0, "x1": 1, "x2": 2, "x4": 3, "x8": 4, "x16": 5}
    OSRS_P = {"skip": 0, "x1": 1, "x2": 2, "x4": 3, "x8": 4, "x16": 5}
    MODE = {"sleep": 0, "forced": 1, "normal": 2}

    def __init__(self, bus_number: int = 1, i2c_addr: int = 0x76) -> None:
        self.bus = smbus.SMBus(bus_number)
        self.i2c_addr = i2c_addr

    def set_config(
        self, t_sb: str = "1000ms", filter: str = "off", spi3w: str = "disable"
    ) -> None:
        value = (self.T_SB[t_sb] << 5) | (self.FILTER[filter] << 2) | self.SPI3W[spi3w]
        self.wbd(0xF5, value)

    def set_ctrl_meas(
        self, osrs_t: str = "x16", osrs_p: str = "x16", mode: str = "normal"
    ) -> None:
        value = (
            (self.OSRS_T[osrs_t] << 5) | (self.OSRS_P[osrs_p] << 2) | self.MODE[mode]
        )
        self.wbd(0xF4, value)

    def rbd(self, register: int) -> int:
        return self.bus.read_byte_data(self.i2c_addr, register)

    def wbd(self, register: int, value: int) -> None:
        self.bus.write_byte_data(self.i2c_addr, register, value)

    def rwd(self, register: int) -> int:
        return self.bus.read_word_data(self.i2c_addr, register)

    def read_raw_temperature(self) -> int:
        temp_msb = self.rbd(0xFA) << 12
        temp_lsb = self.rbd(0xFB) << 4
        temp_xlsb = self.rbd(0xFC) >> 4
        return temp_msb + temp_lsb + temp_xlsb

    def read_raw_pressure(self) -> int:
        press_msb = self.rbd(0xF7) << 12
        press_lsb = self.rbd(0xF8) << 4
        press_xlsb = self.rbd(0xF9) >> 4
        return press_msb + press_lsb + press_xlsb

    def calculate_temperature(self, adc_T: int) -> tuple[float, int]:
        dig_T1 = pipe(0x88, self.rwd)
        dig_T2 = pipe(0x8A, self.rwd, sign)
        dig_T3 = pipe(0x8C, self.rwd, sign)

        var1 = (((adc_T >> 3) - (dig_T1 << 1)) * dig_T2) >> 11
        var2 = (
            ((((adc_T >> 4) - dig_T1) * ((adc_T >> 4) - dig_T1)) >> 12) * dig_T3
        ) >> 14
        t_fine = var1 + var2
        temp = (t_fine * 5 + 128) >> 8
        temp /= 100

        return temp, t_fine

    def calculate_pressure(self, adc_P: int, t_fine: int) -> float:
        dig_P1 = pipe(0x8E, self.rwd)
        dig_P2 = pipe(0x90, self.rwd, sign)
        dig_P3 = pipe(0x92, self.rwd, sign)
        dig_P4 = pipe(0x94, self.rwd, sign)
        dig_P5 = pipe(0x96, self.rwd, sign)
        dig_P6 = pipe(0x98, self.rwd, sign)
        dig_P7 = pipe(0x9A, self.rwd, sign)
        dig_P8 = pipe(0x9C, self.rwd, sign)
        dig_P9 = pipe(0x9E, self.rwd, sign)

        var1 = t_fine - 128000
        var2 = var1 * var1 * dig_P6
        var2 = var2 + ((var1 * dig_P5) << 17)
        var2 = var2 + (dig_P4 << 35)
        var1 = ((var1 * var1 * dig_P3) >> 8) + ((var1 * dig_P2) << 12)
        var1 = ((1 << 47) + var1) * dig_P1 >> 33
        if var1 == 0:
            return 0.0
        p = 1048576 - adc_P
        p = (((p << 31) - var2) * 3125) // var1
        var1 = (dig_P9 * (p >> 13) * (p >> 13)) >> 25
        var2 = (dig_P8 * p) >> 19
        p = ((p + var1 + var2) >> 8) + (dig_P7 << 4)
        p /= 25600

        return p

    def read_temperature(self) -> float:
        adc_T = self.read_raw_temperature()
        temp, _ = self.calculate_temperature(adc_T)
        return temp

    def read_pressure(self) -> float:
        adc_T = self.read_raw_temperature()
        _, t_fine = self.calculate_temperature(adc_T)
        adc_P = self.read_raw_pressure()
        return self.calculate_pressure(adc_P, t_fine)
