#include <Arduino.h>
#include <DHT.h>
#include <WiFi.h>

#include "secrets.h"

constexpr uint8_t DHT_PIN = 4;
constexpr unsigned long READ_INTERVAL_MS = 5000;
constexpr unsigned long WIFI_RETRY_INTERVAL_MS = 30000;

DHT dht(DHT_PIN, DHT22);
unsigned long lastSensorRead = 0;
unsigned long lastWiFiAttempt = 0;
bool wasWiFiConnected = false;

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

  if (isnan(humidity) || isnan(temperature))
  {
    Serial.println("Failed to read DHT22. Check power, wiring, and OUT connected to GPIO4.");
  }
  else
  {
    Serial.print("Temperature: ");
    Serial.print(temperature, 1);
    Serial.print(" °C | Humidity: ");
    Serial.print(humidity, 1);
    Serial.println(" %");
  }

}
