from gpiozero import Device
from gpiozero.pins.rpigpio import RPiGPIOFactory
import time
from datetime import datetime

# Set up GPIO factory
Device.pin_factory = RPiGPIOFactory()


class GPIOMonitor:
    def __init__(self):
        self.pin_info = {
            1: {"type": "POWER", "voltage": "3.3V"},
            2: {"type": "POWER", "voltage": "5V"},
            3: {
                "type": "GPIO",
                "gpio": 2,
                "alt_function": "I2C",
                "function_name": "SDA",
            },
            4: {"type": "POWER", "voltage": "5V"},
            5: {
                "type": "GPIO",
                "gpio": 3,
                "alt_function": "I2C",
                "function_name": "SCL",
            },
            6: {"type": "GROUND"},
            7: {"type": "GPIO", "gpio": 4},
            8: {
                "type": "GPIO",
                "gpio": 14,
                "alt_function": "UART",
                "function_name": "TXD",
            },
            9: {"type": "GROUND"},
            10: {
                "type": "GPIO",
                "gpio": 15,
                "alt_function": "UART",
                "function_name": "RXD",
            },
            11: {"type": "GPIO", "gpio": 17},
            12: {
                "type": "GPIO",
                "gpio": 18,
                "alt_function": "PCM",
                "function_name": "CLK",
            },
            13: {"type": "GPIO", "gpio": 27},
            14: {"type": "GROUND"},
            15: {"type": "GPIO", "gpio": 22},
            16: {"type": "GPIO", "gpio": 23},
            17: {"type": "POWER", "voltage": "3.3V"},
            18: {"type": "GPIO", "gpio": 24},
            19: {
                "type": "GPIO",
                "gpio": 10,
                "alt_function": "SPI",
                "function_name": "MOSI",
            },
            20: {"type": "GROUND"},
            21: {
                "type": "GPIO",
                "gpio": 9,
                "alt_function": "SPI",
                "function_name": "MISO",
            },
            22: {"type": "GPIO", "gpio": 25},
            23: {
                "type": "GPIO",
                "gpio": 11,
                "alt_function": "SPI",
                "function_name": "SCLK",
            },
            24: {
                "type": "GPIO",
                "gpio": 8,
                "alt_function": "SPI",
                "function_name": "CE0",
            },
            25: {"type": "GROUND"},
            26: {
                "type": "GPIO",
                "gpio": 7,
                "alt_function": "SPI",
                "function_name": "CE1",
            },
            27: {"type": "ID", "function_name": "SD"},
            28: {"type": "ID", "function_name": "SC"},
            29: {"type": "GPIO", "gpio": 5},
            30: {"type": "GROUND"},
            31: {"type": "GPIO", "gpio": 6},
            32: {"type": "GPIO", "gpio": 12},
            33: {"type": "GPIO", "gpio": 13},
            34: {"type": "GROUND"},
            35: {
                "type": "GPIO",
                "gpio": 19,
                "alt_function": "PCM",
                "function_name": "FS",
            },
            36: {"type": "GPIO", "gpio": 16},
            37: {"type": "GPIO", "gpio": 26},
            38: {
                "type": "GPIO",
                "gpio": 20,
                "alt_function": "PCM",
                "function_name": "DIN",
            },
            39: {"type": "GROUND"},
            40: {
                "type": "GPIO",
                "gpio": 21,
                "alt_function": "PCM",
                "function_name": "DOUT",
            },
        }

    def get_pin_display_info(self, pin_num, pin_info, state):
        """Format pin information for display"""
        if pin_info["type"] == "GPIO":
            gpio_num = str(pin_info["gpio"])
            if "alt_function" in pin_info:
                pin_function = f"{pin_info['alt_function']} {pin_info['function_name']}"
            else:
                pin_function = ""
        elif pin_info["type"] == "POWER":
            gpio_num = "N/A"
            pin_function = pin_info["voltage"]
        elif pin_info["type"] == "ID":
            gpio_num = "N/A"
            pin_function = f"ID_{pin_info['function_name']}"
        else:  # GROUND
            gpio_num = "N/A"
            pin_function = ""

        return {
            "pin": pin_num,
            "type": pin_info["type"],
            "gpio": gpio_num,
            "function": pin_function,
            "value": state["value"],
            "mode": state["mode"],
            "active": state["active"],
        }

    def read_pin_states(self):
        """Read current state of all pins"""
        current_states = {}

        for pin in self.pin_info.keys():
            pin_info = self.pin_info[pin]

            if pin_info["type"] == "GPIO":
                try:
                    device = Device.pin_factory.pin(pin_info["gpio"])
                    current_states[pin] = {
                        "value": device.state,
                        "mode": "INPUT" if device.direction == "input" else "OUTPUT",
                        "active": device.state == 1,
                    }
                except Exception as e:
                    current_states[pin] = {
                        "value": None,
                        "mode": "UNAVAILABLE",
                        "active": False,
                    }
            else:
                current_states[pin] = {
                    "value": "N/A",
                    "mode": pin_info["type"],
                    "active": "N/A",
                }

        return current_states

    def monitor_pins(self, show_power_ground=True):
        """Continuously monitor and display pin states

        Args:
            show_power_ground (bool): If False, hide power and ground pins from display
        """
        try:
            while True:
                states = self.read_pin_states()
                print("\033[2J\033[H")  # Clear screen
                print(
                    f"Raspberry Pi Pin States at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                print("-" * 85)
                print(
                    "PIN | TYPE    | GPIO | FUNCTION    | VALUE | MODE        | ACTIVE"
                )
                print("-" * 85)

                for pin in sorted(self.pin_info.keys()):
                    pin_info = self.pin_info[pin]
                    # Skip power and ground pins if show_power_ground is False
                    if not show_power_ground and pin_info["type"] in [
                        "POWER",
                        "GROUND",
                        "ID",
                    ]:
                        continue

                    display_info = self.get_pin_display_info(pin, pin_info, states[pin])
                    print(
                        f"{display_info['pin']:3} | "
                        f"{display_info['type']:<7} | "
                        f"{display_info['gpio']:<4} | "
                        f"{display_info['function']:<11} | "
                        f"{display_info['value']!s:5} | "
                        f"{display_info['mode']:<10} | "
                        f"{display_info['active']!s}"
                    )

                return
                time.sleep(1)

        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        except Exception as e:
            print(f"Error during monitoring: {e}")


if __name__ == "__main__":
    monitor = GPIOMonitor()
    # Set to False to hide power and ground pins
    monitor.monitor_pins(show_power_ground=False)
