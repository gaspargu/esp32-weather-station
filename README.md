# ESP32 Weather Station

A local temperature and humidity monitoring system: an ESP32-S3 reads an AM2302 (DHT22) sensor, sends readings to FastAPI, and displays them in a responsive React dashboard.

## Architecture

```text
AM2302 / DHT22 → ESP32-S3 → Wi-Fi / HTTP → FastAPI → SQLite
                                            ↑
                                      React dashboard
```

During development, Vite serves the dashboard and forwards its API requests to FastAPI. The computer hosting these services must remain running to receive and display new readings.

## Current features

- Read temperature and humidity every 5 seconds, with serial output and failed-reading reports.
- Connect to 2.4 GHz Wi-Fi and retry unavailable connections every 30 seconds.
- Send a fresh valid reading to the API every 30 seconds when configured and connected.
- Validate and persist readings in SQLite, with UTC timestamps and per-device queries.
- Display a device card with temperature, humidity, measurement time, reception time, and freshness.
- Browse the latest 100 readings in a responsive English-language dashboard, refreshed every 30 seconds.

## Getting started

1. Follow the [hardware and firmware guide](docs/hardware.md) to wire the sensor, configure Wi-Fi, and upload the firmware.
2. Follow the [backend guide](backend/README.md) to install dependencies and start FastAPI in LAN mode to receive ESP32 readings.
3. [Configure delivery on the ESP32](docs/hardware.md#send-readings-to-the-backend) using the computer's LAN address, then upload again.
4. Follow the [frontend guide](frontend/README.md) to start the dashboard on your computer or view it from a phone on the same network.

The API and dashboard can also be tested without connected hardware; see their guides for requests and automated tests.

## Documentation

| Guide | Contents |
| --- | --- |
| [Hardware and firmware](docs/hardware.md) | Components, wiring, PlatformIO, Wi-Fi, API delivery, and sensor troubleshooting |
| [Backend](backend/README.md) | Python setup, local/LAN server modes, API, timestamps, SQLite, networking, and tests |
| [Frontend](frontend/README.md) | Node setup, Vite proxy, desktop/mobile access, dashboard behavior, build, and tests |
| [Documentation images](docs/images/README.md) | Where to store hardware photos and dashboard screenshots, and how to embed them |

## Repository structure

```text
src/          ESP32 firmware
include/      Firmware configuration and local Wi-Fi credentials
backend/      FastAPI application and backend tests
frontend/     React dashboard and frontend tests
docs/         Hardware guide and documentation images
```

## Security and limitations

This version is intended for a **trusted local network only**. There is no authentication, authorization, or TLS. Do not expose the API or development dashboard to the Internet or forward their ports on your router. Device filtering is not access control.

Wi-Fi credentials belong only in the ignored `include/secrets.h`; never commit credentials or share firmware binaries containing them. See the component guides for network configuration and timestamp limitations.

## Roadmap

- [x] Read temperature and humidity over serial.
- [x] Connect to a 2.4 GHz Wi-Fi network.
- [x] Send readings to a FastAPI backend over HTTP.
- [x] Store measurement history in the backend.
- [x] Build a responsive React monitoring dashboard.
- [ ] Add charts.
- [ ] Add authentication and device permissions.
- [ ] Add secure Internet deployment.
