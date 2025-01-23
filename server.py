import asyncio
import datetime
from fastapi import FastAPI
import socketio
from sensors.bmp280 import BMP280

# Initialize FastAPI
app = FastAPI()

# Initialize Socket.IO server
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app = socketio.ASGIApp(sio, other_asgi_app=app)

# Initialize BMP280 sensor
bmp280 = BMP280(bus_number=1, i2c_addr=0x76)
bmp280.set_config(t_sb="1000ms", filter="16")
bmp280.set_ctrl_meas(osrs_t="x16", osrs_p="x16", mode="normal")


@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    await sio.emit("message", {"data": "Connected to sensor"}, room=sid)


async def send_sensor_data():
    while True:
        try:
            data = {
                "temperature": bmp280.read_temperature(),
                "pressure": bmp280.read_pressure(),
                "timestamp": datetime.datetime.now().isoformat(),
            }
            await sio.emit("sensor_data", data)
            print(
                f"Sent sensor data: Temp={data['temperature']:.1f}°C, "
                f"Pressure={data['pressure'] / 100:.1f}hPa"
            )
        except Exception as e:
            print(f"Error reading sensor data: {e}")
            await sio.emit("error", {"message": "Error reading sensor data"})
        await asyncio.sleep(1)


if __name__ == "__main__":
    import uvicorn

    loop = asyncio.get_event_loop()
    loop.create_task(send_sensor_data())
    uvicorn.run(app, host="localhost", port=5000)

