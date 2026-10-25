#include <Arduino.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <HTTPClient.h>
#include <WiFi.h>

#include "config.h"
#include "secrets.h"

constexpr uint8_t DHT_PIN = 4;
constexpr unsigned long READ_INTERVAL_MS = 5000;
constexpr unsigned long WIFI_RETRY_INTERVAL_MS = 30000;
constexpr unsigned long SEND_INTERVAL_MS = 30000;
constexpr int32_t HTTP_CONNECT_TIMEOUT_MS = 2000;
constexpr uint16_t HTTP_READ_TIMEOUT_MS = 2000;

DHT dht(DHT_PIN, DHT22);
unsigned long lastSensorRead = 0;
unsigned long lastWiFiAttempt = 0;
unsigned long lastSendAttempt = 0;
bool wasWiFiConnected = false;

void sendReading(float temperature, float humidity)
{
  if (WiFi.status() != WL_CONNECTED)
  {
    Serial.println("Reading not sent: Wi-Fi is disconnected.");
    return;
  }

  WiFiClient client;
  HTTPClient http;
  http.setConnectTimeout(HTTP_CONNECT_TIMEOUT_MS);
  http.setTimeout(HTTP_READ_TIMEOUT_MS);
  if (!http.begin(client, BACKEND_READINGS_URL))
  {
    Serial.println("Failed to initialize HTTP request. Check include/config.h.");
    return;
  }
  http.addHeader("Content-Type", "application/json");

  JsonDocument reading;
  reading["device_id"] = DEVICE_ID;
  reading["temperature_c"] = temperature;
  reading["humidity_pct"] = humidity;
  // Omit measured_at until the device clock is synchronized.
  String body;
  serializeJson(reading, body);

  const int statusCode = http.POST(body);
  if (statusCode == HTTP_CODE_CREATED)
  {
    Serial.println("Reading saved by backend (HTTP 201).");
  }
  else if (statusCode > 0)
  {
    Serial.printf("Backend rejected reading (HTTP %d). Check the API logs and configuration.\n", statusCode);
  }
  else
  {
    Serial.printf("HTTP request failed: %s\n", HTTPClient::errorToString(statusCode).c_str());
  }
  http.end();
}

void connectWiFi()
{
  Serial.println("Connecting to Wi-Fi...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  lastWiFiAttempt = millis();
}

void maintainWiFi()
{
  if (WIFI_SSID[0] == '\0')
  {
    return;
  }

  const bool isConnected = WiFi.status() == WL_CONNECTED;
  if (isConnected && !wasWiFiConnected)
  {
    Serial.print("Wi-Fi connected. IP address: ");
    Serial.println(WiFi.localIP());
  }
  else if (!isConnected && wasWiFiConnected)
  {
    Serial.println("Wi-Fi disconnected. Sensor readings will continue.");
  }
  wasWiFiConnected = isConnected;

  if (!isConnected && millis() - lastWiFiAttempt >= WIFI_RETRY_INTERVAL_MS)
  {
    Serial.println("Wi-Fi unavailable. Retrying connection.");
    connectWiFi();
  }
}

void setup()
{
  Serial.begin(115200);
  delay(1000);
  dht.begin();
  Serial.println("ESP32-S3 started. DHT22 on GPIO4.");
  if (BACKEND_READINGS_URL[0] == '\0')
  {
    Serial.println("HTTP delivery disabled. Set BACKEND_READINGS_URL in include/config.h.");
  }
  if (WIFI_SSID[0] == '\0')
  {
    Serial.println("Wi-Fi not configured. Set credentials in include/secrets.h.");
  }
  else
  {
    WiFi.mode(WIFI_STA);
    // Handle retries explicitly while keeping sensor readings independent.
    WiFi.setAutoReconnect(false);
    connectWiFi();
  }
  // Allow the sensor to stabilize before the first reading.
  delay(2000);
  lastSensorRead = millis() - READ_INTERVAL_MS;
}

void loop()
{
  maintainWiFi();

  const unsigned long now = millis();
  if (now - lastSensorRead < READ_INTERVAL_MS)
  {
    delay(10);
    return;
  }
  lastSensorRead = now;

  const float humidity = dht.readHumidity();
  const float temperature = dht.readTemperature();
  const bool shouldSend = BACKEND_READINGS_URL[0] != '\0' &&
                          now - lastSendAttempt >= SEND_INTERVAL_MS;
  if (shouldSend)
  {
    // Failed or skipped sends are not queued; try a fresh reading next interval.
    lastSendAttempt = now;
  }

  if (isnan(humidity) || isnan(temperature))
  {
    Serial.println("Failed to read DHT22. Check power, wiring, and OUT connected to GPIO4.");
    if (shouldSend)
    {
      Serial.println("Reading not sent: sensor data is invalid.");
    }
  }
  else
  {
    Serial.print("Temperature: ");
    Serial.print(temperature, 1);
    Serial.print(" °C | Humidity: ");
    Serial.print(humidity, 1);
    Serial.println(" %");
    if (shouldSend)
    {
      sendReading(temperature, humidity);
    }
  }

}
