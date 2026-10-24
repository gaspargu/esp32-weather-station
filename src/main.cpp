#include <Arduino.h>
#include <DHT.h>

constexpr uint8_t DHT_PIN = 4;
constexpr unsigned long READ_INTERVAL_MS = 5000;

DHT dht(DHT_PIN, DHT22);

void setup()
{
  Serial.begin(115200);
  delay(1000);
  dht.begin();
  Serial.println("ESP32-S3 started. DHT22 on GPIO4.");
  // Allow the sensor to stabilize before the first reading.
  delay(2000);
}

void loop()
{
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

  delay(READ_INTERVAL_MS);
}
