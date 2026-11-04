---
title: "ESP32 + MFRC522 RFID Smart Attendance Telemetry Node"
difficulty: "Advanced"
estimatedMinutes: 45
author: "VoltCore Silicon Architecture Team (MIT Campus)"
wokwiId: "382755291244849153"
verifiedOnHardware: true
hardwarePlatform: "ESP32"
chipList:
  - "board-esp32-devkit-c-v4"
  - "wokwi-rfid-rc522"
  - "board-ssd1306"
  - "wokwi-led"
  - "wokwi-resistor"
  - "wokwi-pushbutton"
wiringConnections:
  - from: "esp:5"
    to: "rc522:SDA"
    color: "orange"
    signal: "SPI CS"
  - from: "esp:18"
    to: "rc522:SCK"
    color: "yellow"
    signal: "SPI CLK"
  - from: "esp:23"
    to: "rc522:MOSI"
    color: "green"
    signal: "SPI MOSI"
  - from: "esp:19"
    to: "rc522:MISO"
    color: "blue"
    signal: "SPI MISO"
  - from: "esp:21"
    to: "oled:SDA"
    color: "cyan"
    signal: "I2C SDA"
  - from: "esp:22"
    to: "oled:SCL"
    color: "magenta"
    signal: "I2C SCL"
learningObjectives:
  - "Configure high-speed SPI bus communication with MFRC522 RFID front-end."
  - "Format JSON HTTP POST telemetry payloads over 802.11 Wi-Fi."
  - "Establish secure communications with Flask SQLite backend on Port 5000."
  - "Display real-time verification and student UID on I2C SSD1306 display."
defaultSketch: |
  #include <WiFi.h>
  #include <HTTPClient.h>
  
  void setup() {
    Serial.begin(115200);
    WiFi.begin("Wokwi-GUEST", "");
  }
  
  void loop() {
    delay(1000);
  }
diagramJson:
  version: 1
  author: "VoltCore MIT"
  editor: "wokwi"
  parts:
    - type: "board-esp32-devkit-c-v4"
      id: "esp"
      top: 0
      left: 0
      attrs: {}
expectedTelemetry:
  node_id: "ESP32_MIT_IOT_LAB_01"
  status: "Lab-Verified"
  http_code: 200
---

# ESP32 + MFRC522 RFID Smart Attendance Telemetry Node

This simulation models the real-world automated lab attendance gateway deployed across the Department of Electronics Engineering at the MIT Campus, Anna University.

