# ESP32 Weather Station

A temperature and humidity monitoring project using an ESP32-S3 and an AM2302 (DHT22) sensor, built with PlatformIO and the Arduino framework.

## Current features

- Read temperature in Celsius and relative humidity every 5 seconds.
- Display readings in the serial monitor at 115200 baud.
- Report failed sensor readings.
- Connect to a 2.4 GHz Wi-Fi network and display the assigned IP address.
- Retry Wi-Fi connections every 30 seconds while continuing sensor readings.
- Receive and store readings with a FastAPI + SQLite backend, including UTC timestamps.

- Send a fresh valid reading to FastAPI over HTTP every 30 seconds when configured.

A responsive React dashboard displays device values, reception freshness, and the latest 100 readings. See [frontend/README.md](frontend/README.md) for setup, LAN access, and tests. Authentication and Internet deployment are not implemented yet.

## Backend

See [backend/README.md](backend/README.md) for virtual environment setup, API usage, timestamp semantics, and tests.

### Send ESP32 readings to the backend

**Choose the correct server mode:** `--host 127.0.0.1` is for tests and clients on the server computer only. **Use `--host 0.0.0.0` to receive ESP32 readings** or connect from another device. See [backend run instructions](backend/README.md#run) for complete PowerShell, CMD, and Linux commands.

1. Start FastAPI with `--host 0.0.0.0 --port 8000` (see the backend README). Keep the computer running and connect it to the same trusted LAN as the ESP32.
2. Find your computer's LAN IPv4 address using `ipconfig` on Windows or `ip -4 addr` on Linux.
3. Edit `include/config.h`, replacing the example IP with your computer's address:

   ```cpp
   constexpr char BACKEND_READINGS_URL[] = "http://192.168.1.50:8000/api/readings";
   constexpr char DEVICE_ID[] = "esp32-01";
   ```

4. Upload the firmware again, then open the serial monitor. The first send is attempted after approximately 30 seconds. A successful send prints `Reading saved by backend (HTTP 201).`
5. Open `http://127.0.0.1:8000/docs` on the server computer and query `/api/readings/latest` or `/api/readings` to verify storage.

Use your computer's address, not the ESP32's IP, `localhost`, or `0.0.0.0`. If necessary, allow inbound TCP port 8000 from your trusted LAN through the firewall without disabling it. If your computer's address changes, update the URL and upload again.

`0.0.0.0` tells the server where to listen; it is never the URL's destination address. Even in this mode you can still open `http://127.0.0.1:8000/docs` on the server computer. To test LAN access, open `http://<computer-lan-ip>:8000/health` from another device on the same network.

An empty URL disables delivery. Invalid readings and readings taken while offline are not queued; the firmware tries a fresh reading at the next 30-second interval. HTTP calls are synchronous with 2-second connect and read timeouts, so sensor readings may be briefly delayed during a request. The firmware omits `measured_at` until its clock is synchronized; the backend generates `received_at` in UTC.

This HTTP setup has no authentication or encryption: use it only on a trusted local network and do not expose the server to the Internet. `config.h` contains no credentials and is tracked by Git; never add passwords or tokens there.

## Hardware

- ESP32-S3 development board with an N16R8 module.
- AM2302 (DHT22) sensor module with `+`, `-`, and `OUT` terminals.
- USB data cable and jumper wires.

### Wiring

Disconnect USB and any other power source before changing connections. Follow the terminal labels on your sensor module; their physical order may vary.

| Sensor terminal | ESP32-S3 pin |
| --------------- | ------------ |
| `+`             | `3V3`        |
| `-`             | `GND`        |
| `OUT`           | `GPIO4`      |

GPIO4 means the pin labeled `4` or `IO4`, not the fourth physical pin. ESP32 GPIOs are not 5 V tolerant.

## Getting started

1. Install [Visual Studio Code](https://code.visualstudio.com/) and the [PlatformIO IDE extension](https://platformio.org/install/ide?install=vscode).
2. Open this project folder in VS Code.
   Copy `include/secrets.example.h` to `include/secrets.h` if it does not exist, then enter your Wi-Fi credentials as described below.
3. Connect the sensor as shown above, then connect the board by USB.
4. This board has two USB ports labeled USB and COM. The COM port was used successfully for uploading and serial monitoring.
5. Run **PlatformIO: Upload** to build and upload the firmware. PlatformIO automatically installs the libraries declared in `platformio.ini`.
6. Run **PlatformIO: Serial Monitor** at **115200 baud**.

Expected output:

```text
ESP32-S3 started. DHT22 on GPIO4.
Temperature: 24.3 °C | Humidity: 58.2 %
```

Allow a few seconds after startup for the first reading.

### Wi-Fi setup

Edit `include/secrets.h` locally:

```cpp
#pragma once

constexpr char WIFI_SSID[] = "YOUR_NETWORK_NAME";
constexpr char WIFI_PASSWORD[] = "YOUR_NETWORK_PASSWORD";
```

Use a **2.4 GHz** network; the ESP32-S3 does not support 5 GHz Wi-Fi. Upload the firmware again after changing credentials.

`include/secrets.h` is excluded from Git. Never put real credentials in `include/secrets.example.h`. Credentials are compiled into the firmware, so do not share firmware binaries containing them.

When connected, the serial monitor prints:

```text
Connecting to Wi-Fi...
Wi-Fi connected. IP address: 192.168.1.100
```

If the network is unavailable, the firmware retries every 30 seconds. Sensor readings continue independently. An empty SSID disables connection attempts. Wi-Fi connectivity alone does not send readings to a server or confirm Internet access.

### PlatformIO CLI

From a terminal where the PlatformIO CLI is available:

```sh
pio run
pio run --target upload
pio device monitor --baud 115200
```

## Configuration

- `platformio.ini`: board, Arduino framework, serial speed, and library dependencies.
- `src/main.cpp`: sensor type (`DHT22`), data pin (`DHT_PIN`), and reading interval (`READ_INTERVAL_MS`).
- `include/secrets.h`: local Wi-Fi credentials (not committed).
- `include/config.h`: backend readings URL and device identifier.

The project currently uses the `esp32-s3-devkitc-1` board definition. It does not configure the full 16 MB flash or enable the 8 MB PSRAM of the N16R8 module; neither is required for this initial sensor test.

## Troubleshooting

If the firmware reports `Failed to read DHT22`:

- Confirm that the sensor is an AM2302/DHT22.
- Check `+` to `3V3`, `-` to `GND`, and `OUT` to GPIO4.
- Use short wires and check for loose connections.
- Disconnect power before changing wiring or measuring continuity.
- Check whether the sensor module includes a data pull-up resistor; bare sensors require an external one.

## Roadmap

- [x] Read temperature and humidity over serial.
- [x] Connect to a 2.4 GHz Wi-Fi network.
- [x] Send readings to a FastAPI backend over HTTP.
- [x] Store measurement history in the backend.
- [x] Build a responsive React monitoring dashboard.
- [ ] Add charts, authentication, and secure Internet deployment.
