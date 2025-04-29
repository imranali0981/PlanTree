#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"

// WiFi credentials
const char* ssid = "Imran";     //Muaaz Replace with your WiFi SSID
const char* password = "essafamily123"; //ammad317gb Replace with your WiFi Password

// Server details
const char* serverUrl = "https://plan-tree-amber.vercel.app/sensor-data"; //http://192.168.100.94:3000/sensor-data Replace with your Node.js server IP and endpoint

// DHT11 pin and type
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// MQ135 analog pin
#define MQ135_PIN 34

void setup() {
  // Start the Serial communication
  Serial.begin(115200);

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Initialize DHT sensor
  dht.begin();
}

void loop() {
  // Check if WiFi is connected
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    // Reading from DHT11 sensor
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    // Reading from MQ135 sensor
    int mq135Value = analogRead(MQ135_PIN);

    // Check if reading is valid
    if (!isnan(temperature) && !isnan(humidity)) {
      // Prepare the JSON payload

      Serial.print("Sending Temperature: ");
      Serial.println(temperature);
      Serial.print("Sending Humidity: ");
      Serial.println(humidity);
      Serial.print("Sending Air Quality: ");
      Serial.println(mq135Value);

      String payload = "{\"location\":\"New Karachi\","
                       "\"temperature\":" + String(temperature) + 
                       ",\"humidity\":" + String(humidity) + 
                       ",\"mq135\":" + String(mq135Value) + "}";

      // Make the POST request to the server
      http.begin(serverUrl);
      http.addHeader("Content-Type", "application/json");
      int httpResponseCode = http.POST(payload);
      Serial.println("Trying Sending Data");

      if (httpResponseCode > 0) {
        Serial.println("Data sent successfully");
      } else {
        Serial.print("Error on sending POST: ");
        Serial.println(httpResponseCode);
      }
      
      http.end();
    }
  }

  // Delay for 5 minutes before sending again
  delay(300000);
}
