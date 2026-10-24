# ESP32 Weather Station

A temperature and humidity monitoring project using an ESP32-S3 and an AM2302 (DHT22) sensor, built with PlatformIO and the Arduino framework.

## Current features

- Read temperature in Celsius and relative humidity every 5 seconds.
- Display readings in the serial monitor at 115200 baud.
- Report failed sensor readings.

Wi-Fi connectivity, a FastAPI backend, and a React dashboard are planned but not implemented yet.

## Hardware

- ESP32-S3 development board with an N16R8 module.
- AM2302 (DHT22) sensor module with `+`, `-`, and `OUT` terminals.
- USB data cable and jumper wires.

### Wiring

Disconnect USB and any other power source before changing connections. Follow the terminal labels on your sensor module; their physical order may vary.

| Sensor terminal | ESP32-S3 pin |
| --- | --- |
| `+` | `3V3` |
| `-` | `GND` |
| `OUT` | `GPIO4` |

GPIO4 means the pin labeled `4` or `IO4`, not the fourth physical pin. ESP32 GPIOs are not 5 V tolerant.

## Getting started

1. Install [Visual Studio Code](https://code.visualstudio.com/) and the [PlatformIO IDE extension](https://platformio.org/install/ide?install=vscode).
2. Open this project folder in VS Code.
3. Connect the sensor as shown above, then connect the board by USB.
4. Run **PlatformIO: Upload** to build and upload the firmware. PlatformIO automatically installs the libraries declared in `platformio.ini`.
5. Run **PlatformIO: Serial Monitor** at **115200 baud**.

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

## Configuration

- `platformio.ini`: board, Arduino framework, serial speed, and library dependencies.
- `src/main.cpp`: sensor type (`DHT22`), data pin (`DHT_PIN`), and reading interval (`READ_INTERVAL_MS`).

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
- [ ] Connect to a 2.4 GHz Wi-Fi network.
- [ ] Send readings to a FastAPI backend over HTTP.
- [ ] Store measurement history.
- [ ] Build a responsive React monitoring dashboard.

## Commit messages

Use English commit messages with a type prefix, for example:

```text
feat: add Wi-Fi connectivity
fix: handle failed sensor readings
docs: update wiring instructions
chore: update dependencies
```
