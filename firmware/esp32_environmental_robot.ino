/**
 * ESP32 Environmental Monitoring Robot Firmware
 * Invention: Environmental Monitoring Robot with Wireless Sensor Telemetry and Real-Time Dashboard
 * Patent Reference: Darft-3.pdf (Form 2, The Patents Act 1970)
 *
 * Hardware Peripherals & Pin Mappings:
 * 1. Chassis & Motors (101, 102): 2x DC Geared Motors driven via L298N Dual H-Bridge (103)
 *    - IN1: GPIO 18 (Left Motor Forward)
 *    - IN2: GPIO 19 (Left Motor Reverse)
 *    - IN3: GPIO 22 (Right Motor Forward)
 *    - IN4: GPIO 23 (Right Motor Reverse)
 *    - ENA: GPIO 25 (Left PWM Speed)
 *    - ENB: GPIO 26 (Right PWM Speed)
 * 2. Optical Wheel Encoders (204): 20-slot disc (n_cpr = 20), D_wheel = 0.065m
 *    - Left Wheel Encoder: GPIO 34 (Interrupt input)
 *    - Right Wheel Encoder: GPIO 35 (Interrupt input)
 * 3. Environmental Sensor (201): DHT22 Digital Air Temperature & Humidity Sensor
 *    - Data Pin: GPIO 4
 * 4. Satellite Positioning Receiver (202): NEO-6M GPS Module
 *    - GPS RX: GPIO 16 (ESP32 RX2)
 *    - GPS TX: GPIO 17 (ESP32 TX2)
 * 5. Ultrasonic Proximity Sensor (203): HC-SR04
 *    - Trig: GPIO 13
 *    - Echo: GPIO 14
 * 6. Power Subsystem (104): 2S 18650 Li-ion Cells (Nominal 7.4V) via resistive voltage divider
 *    - Battery ADC Pin: GPIO 36 (ADC1_CH0)
 *
 * Telemetry Protocol:
 * - JSON Telemetry Packet (303) transmitted over Wi-Fi uplink (302) via HTTP POST
 *   to /api/v1/telemetry/packet on the remote server (400).
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <TinyGPS++.h>
#include <HardwareSerial.h>

// Wi-Fi Configuration
const char* WIFI_SSID     = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SERVER_URL    = "http://192.168.1.100:8000/api/v1/telemetry/packet";
const char* ROBOT_ID      = "dav_robot_01";

// Pin Assignments
#define PIN_MOTOR_IN1    18
#define PIN_MOTOR_IN2    19
#define PIN_MOTOR_IN3    22
#define PIN_MOTOR_IN4    23
#define PIN_MOTOR_ENA    25
#define PIN_MOTOR_ENB    26

#define PIN_ENCODER_LEFT  34
#define PIN_ENCODER_RIGHT 35

#define PIN_DHT22        4
#define PIN_US_TRIG      13
#define PIN_US_ECHO      14
#define PIN_BATTERY_ADC  36

// Sensor & Peripheral Definitions
#define DHTTYPE DHT22
DHT dht(PIN_DHT22, DHTTYPE);

TinyGPSPlus gps;
HardwareSerial gpsSerial(2); // UART2 (pins 16, 17)

// Wheel & Odometry Parameters (Patent Section 4.5.11 & Equation 1)
const float WHEEL_DIAMETER_M = 0.065; // 65mm
const int COUNTS_PER_REV     = 20;    // 20-slot optical encoder disc
volatile unsigned long leftEncoderCount = 0;
volatile unsigned long rightEncoderCount = 0;

// Reporting & Power Management (Section 4.5.9, 4.5.11)
unsigned long defaultReportingIntervalMs = 60000; // 60s
unsigned long lowBatteryIntervalMs     = 180000; // 180s when battery is low
unsigned long lastTelemetryMillis      = 0;
const float LOW_BATTERY_THRESHOLD_V    = 6.8;

// Encoder ISRs
void IRAM_ATTR isrLeftEncoder() {
  leftEncoderCount++;
}

void IRAM_ATTR isrRightEncoder() {
  rightEncoderCount++;
}

// Distance Calculation: Equation 1: d = (n_pulse * pi * D_wheel) / n_cpr
float calculateTravelledDistance() {
  unsigned long avgPulses = (leftEncoderCount + rightEncoderCount) / 2;
  return (float(avgPulses) * 3.14159265 * WHEEL_DIAMETER_M) / float(COUNTS_PER_REV);
}

// Battery Voltage Reader
float readBatteryVoltage() {
  // 12-bit ADC: 0-4095. Voltage divider: R1=100k, R2=47k -> multiplier ~ 3.127
  int raw = analogRead(PIN_BATTERY_ADC);
  float pinVoltage = (raw / 4095.0) * 3.3;
  float batteryVoltage = pinVoltage * ((100.0 + 47.0) / 47.0);
  return batteryVoltage;
}

// Ultrasonic Obstacle Distance (HC-SR04)
float readObstacleDistanceCm() {
  digitalWrite(PIN_US_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_US_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_US_TRIG, LOW);

  long duration = pulseIn(PIN_US_ECHO, HIGH, 30000); // 30ms timeout (~5m)
  if (duration == 0) return -1.0; // No echo
  return duration * 0.034 / 2.0;
}

// Manual Motor Movement Handler (Patent Section 4.5.2: Safe non-autonomous control)
void stopMotors() {
  digitalWrite(PIN_MOTOR_IN1, LOW);
  digitalWrite(PIN_MOTOR_IN2, LOW);
  digitalWrite(PIN_MOTOR_IN3, LOW);
  digitalWrite(PIN_MOTOR_IN4, LOW);
  ledcWrite(0, 0);
  ledcWrite(1, 0);
}

void setup() {
  Serial.begin(115200);
  Serial.println("[DAV] Initializing Environmental Monitoring Robot...");

  // Motor Driver Setup - DEFAULT SAFELY TO STOPPED
  pinMode(PIN_MOTOR_IN1, OUTPUT);
  pinMode(PIN_MOTOR_IN2, OUTPUT);
  pinMode(PIN_MOTOR_IN3, OUTPUT);
  pinMode(PIN_MOTOR_IN4, OUTPUT);
  pinMode(PIN_MOTOR_ENA, OUTPUT);
  pinMode(PIN_MOTOR_ENB, OUTPUT);
  stopMotors();

  // Encoder Inputs with Interrupts
  pinMode(PIN_ENCODER_LEFT, INPUT_PULLUP);
  pinMode(PIN_ENCODER_RIGHT, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_ENCODER_LEFT), isrLeftEncoder, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_ENCODER_RIGHT), isrRightEncoder, RISING);

  // Ultrasonic Pins
  pinMode(PIN_US_TRIG, OUTPUT);
  pinMode(PIN_US_ECHO, INPUT);

  // DHT22 Setup
  dht.begin();

  // NEO-6M GPS UART2 Setup (9600 baud standard for NEO-6M)
  gpsSerial.begin(9600, SERIAL_8N1, 16, 17);

  // Connect Wi-Fi
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("[DAV] Connecting to Wi-Fi...");
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[DAV] Wi-Fi Connected. IP: " + WiFi.localIP().toString());
  } else {
    Serial.println("\n[DAV] Wi-Fi connection timed out. Will retry during telemetry cycle.");
  }
}

void loop() {
  // Feed GPS serial stream
  while (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read());
  }

  // Periodic Telemetry Dispatch
  float batteryVoltage = readBatteryVoltage();
  unsigned long currentInterval = (batteryVoltage < LOW_BATTERY_THRESHOLD_V && batteryVoltage > 3.0)
    ? lowBatteryIntervalMs
    : defaultReportingIntervalMs;

  if (millis() - lastTelemetryMillis >= currentInterval) {
    lastTelemetryMillis = millis();

    // Sample DHT22
    float temp = dht.readTemperature();
    float hum  = dht.readHumidity();

    // Ultrasonic
    float obstacleCm = readObstacleDistanceCm();

    // Encoder Distance
    float dist = calculateTravelledDistance();
    unsigned long pulses = (leftEncoderCount + rightEncoderCount) / 2;

    // Build Telemetry JSON Document
    StaticJsonDocument<384> doc;
    doc["robot_id"] = ROBOT_ID;
    
    if (!isnan(temp) && temp >= -40.0 && temp <= 80.0) {
      doc["temperature_c"] = temp;
    } else {
      doc["temperature_c"] = nullptr;
    }

    if (!isnan(hum) && hum >= 0.0 && hum <= 100.0) {
      doc["humidity_pct"] = hum;
    } else {
      doc["humidity_pct"] = nullptr;
    }

    // GPS Status - Honest preservation of fix (Patent Claim 7)
    if (gps.location.isValid()) {
      doc["gps_fix"] = true;
      doc["latitude"] = gps.location.lat();
      doc["longitude"] = gps.location.lng();
    } else {
      doc["gps_fix"] = false;
      doc["latitude"] = nullptr;
      doc["longitude"] = nullptr;
    }

    doc["encoder_pulses"] = pulses;
    doc["distance_m"] = dist;
    doc["battery_voltage"] = batteryVoltage;
    if (obstacleCm > 0.0) {
      doc["obstacle_distance_cm"] = obstacleCm;
    } else {
      doc["obstacle_distance_cm"] = nullptr;
    }
    doc["source"] = "live_hardware";

    String jsonPayload;
    serializeJson(doc, jsonPayload);

    // Send HTTP POST Telemetry Packet
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(SERVER_URL);
      http.addHeader("Content-Type", "application/json");
      int httpCode = http.POST(jsonPayload);
      if (httpCode > 0) {
        Serial.printf("[DAV] Telemetry dispatched successfully: HTTP %d\n", httpCode);
      } else {
        Serial.printf("[DAV] HTTP POST failed, error: %s\n", http.errorToString(httpCode).c_str());
      }
      http.end();
    } else {
      Serial.println("[DAV] Wi-Fi disconnected. Reconnecting...");
      WiFi.reconnect();
    }
  }
}
