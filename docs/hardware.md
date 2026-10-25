# Hardware and Firmware

[Project overview](../README.md) · [Backend guide](../backend/README.md) · [Frontend guide](../frontend/README.md)

The firmware uses PlatformIO with the Arduino framework. It reads the AM2302 (DHT22) every 5 seconds and, when configured and connected to Wi-Fi, sends a fresh valid reading to FastAPI every 30 seconds.

Paths in this guide are relative to the repository root. Run CLI commands from that directory.

## Components

- ESP32-S3 development board with an N16R8 module.
- AM2302 (DHT22) sensor module with `+`, `-`, and `OUT` terminals.
- USB data cable and jumper wires.

## Wiring

Disconnect USB and any other power source before changing connections. Follow the terminal labels on your sensor module; their physical order may vary.

| Sensor terminal | ESP32-S3 pin |
| --- | --- |
| `+` | `3V3` |
| `-` | `GND` |
| `OUT` | `GPIO4` |

GPIO4 means the pin labeled `4` or `IO4`, not the fourth physical pin. ESP32 GPIOs are not 5 V tolerant.

## Build and upload

1. Install [Visual Studio Code](https://code.visualstudio.com/) and the [PlatformIO IDE extension](https://platformio.org/install/ide?install=vscode).
2. Open the repository folder in VS Code.
3. Copy `include/secrets.example.h` to `include/secrets.h` if it does not exist, then enter your Wi-Fi credentials as described in [Wi-Fi setup](#wi-fi-setup).
4. Connect the sensor as shown above, then connect the board by USB. This board has two USB ports labeled USB and COM; the COM port was used successfully for uploading and serial monitoring.
5. Run **PlatformIO: Upload**. PlatformIO automatically installs the libraries declared in `platformio.ini`.
6. Run **PlatformIO: Serial Monitor** at **115200 baud**.

Expected output:

```text
ESP32-S3 started. DHT22 on GPIO4.
Temperature: 24.3 °C | Humidity: 58.2 %
```

Allow a few seconds after startup for the first reading.

### PlatformIO CLI

From a terminal where the PlatformIO CLI is available:

```sh
pio run
pio run --target upload
pio device monitor --baud 115200
```

## Wi-Fi setup

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

## Send readings to the backend

1. [Start FastAPI in LAN mode](../backend/README.md#receive-readings-from-the-esp32-normal-station-operation). Keep the computer running and connected to the same trusted LAN as the ESP32. Loopback-only mode cannot receive ESP32 readings.
2. Find the computer's LAN IPv4 address using `ipconfig` on Windows or `ip -4 addr` on Linux. Choose the Wi-Fi/Ethernet interface connected to the ESP32's network, not a VPN or container interface.
3. Edit `include/config.h`, replacing the example IP with the computer's address:

   ```cpp
   constexpr char BACKEND_READINGS_URL[] = "http://192.168.1.50:8000/api/readings";
   constexpr char DEVICE_ID[] = "esp32-01";
   ```

4. Upload the firmware again, then open the serial monitor. The first send is attempted after approximately 30 seconds. A successful send prints `Reading saved by backend (HTTP 201).`
5. Open `http://127.0.0.1:8000/docs` on the server computer and query `/api/readings/latest` or `/api/readings` to verify storage. Start the [dashboard](../frontend/README.md#run-locally) to view the readings; its configured device ID must match the firmware's.

Use the computer's address, not the ESP32's IP, `localhost`, or `0.0.0.0`. If the computer's address changes, update the URL and upload again. See the [backend networking instructions](../backend/README.md#receive-readings-from-the-esp32-normal-station-operation) for listening addresses, firewall configuration, and LAN connectivity checks.

An empty URL disables delivery. Invalid readings and readings taken while offline are not queued; the firmware tries a fresh reading at the next 30-second interval. HTTP calls are synchronous with 2-second connect and read timeouts, so sensor readings may be briefly delayed during a request.

The firmware currently has no clock synchronization and omits `measured_at`. The backend generates `received_at` in UTC; see [API timestamp semantics](../backend/README.md#endpoints). Reception time is not necessarily measurement time.

This HTTP setup has no authentication or encryption: use it only on a trusted local network and do not expose the server to the Internet. `config.h` contains no credentials and is tracked by Git; never add passwords or tokens there.

## Configuration reference

- `platformio.ini`: board, Arduino framework, serial speed, and library dependencies.
- `src/main.cpp`: sensor type (`DHT22`), data pin (`DHT_PIN`), and reading interval (`READ_INTERVAL_MS`).
- `include/secrets.h`: local Wi-Fi credentials (not committed).
- `include/config.h`: backend readings URL and device identifier.

The project currently uses the `esp32-s3-devkitc-1` board definition. It does not configure the full 16 MB flash or enable the 8 MB PSRAM of the N16R8 module; neither is required for the current firmware.

## Troubleshooting

If the firmware reports `Failed to read DHT22`:

- Confirm that the sensor is an AM2302/DHT22.
- Check `+` to `3V3`, `-` to `GND`, and `OUT` to GPIO4.
- Use short wires and check for loose connections.
- Disconnect power before changing wiring or measuring continuity.
- Check whether the sensor module includes a data pull-up resistor; bare sensors require an external one.

If sensor readings work but HTTP delivery fails, follow the [backend LAN checks](../backend/README.md#receive-readings-from-the-esp32-normal-station-operation). For photos of the setup, use the [documentation image folders](images/README.md).
