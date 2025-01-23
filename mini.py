from aiohttp import web
import socketio
from sensors.bmp280 import BMP280

sio = socketio.AsyncServer(async_mode="aiohttp")
app = web.Application()
sio.attach(app)

bmp280 = BMP280(bus_number=1, i2c_addr=0x76)


async def sensor_task():
    while True:
        bmp280.set_config(t_sb="1000ms", filter="16")
        bmp280.set_ctrl_meas(osrs_t="x16", osrs_p="x16", mode="normal")
        # Read fresh values each iteration
        temperature = round(bmp280.read_temperature(), 2)
        pressure = round(bmp280.read_pressure(), 2)
        print(temperature, pressure)

        # Send both values in a single emit
        await sio.emit(
            "sensor_data", {"temperature": temperature, "pressure": pressure}
        )

        await sio.sleep(1)  # Wait 1 second between readings


@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")


@sio.event
def disconnect(sid, reason):
    print(f"Client disconnected: {sid}")


async def init_app():
    sio.start_background_task(sensor_task)
    return app


if __name__ == "__main__":
    web.run_app(init_app(), port=8080)
