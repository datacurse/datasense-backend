import os
import glob
import time

# Load one-wire communication modules
os.system("modprobe w1-gpio")
os.system("modprobe w1-therm")

# Define the base directory for the one-wire sensor
base_dir = "/sys/bus/w1/devices/"
device_folder = glob.glob(base_dir + "28*")[0]
device_file = device_folder + "/w1_slave"


def read_temp_raw():
    with open(device_file, "r") as f:
        lines = f.readlines()
    return lines


def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != "YES":
        time.sleep(0.2)
        lines = read_temp_raw()

    equals_pos = lines[1].find("t=")
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2 :]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f


# Continuous temperature reading loop
while True:
    temperature_celsius, temperature_fahrenheit = read_temp()
    print(f"Temperature: {temperature_celsius:.2f} °C")
    print(f"Temperature: {temperature_fahrenheit:.2f} °F")
    time.sleep(1)

