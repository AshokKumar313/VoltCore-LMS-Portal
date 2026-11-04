---
name: "ESP32-WROOM-32D Dual-Core MCU"
partNumber: "ESP32-WROOM-32D"
category: "Microcontroller"
operatingVoltage: "3.3V DC (2.7V - 3.6V)"
currentDraw: "Active: 80-240 mA, Deep Sleep: 10 uA"
interfaces:
  - "SPI"
  - "I2C"
  - "UART"
  - "PWM"
  - "ADC"
  - "DAC"
  - "GPIO"
  - "Wi-Fi 802.11 b/g/n"
  - "BLE 4.2"
pinout:
  - pin: 5
    name: "GPIO 5 (VSPI CS0)"
    type: "Chip Select"
    description: "Hardware SPI Chip Select for MFRC522 RFID reader"
  - pin: 18
    name: "GPIO 18 (VSPI CLK)"
    type: "Bus Clock"
    description: "Hardware SPI Clock line rated up to 80 MHz"
  - pin: 19
    name: "GPIO 19 (VSPI MISO)"
    type: "Bus Data"
    description: "Master In Slave Out data line from peripherals"
  - pin: 23
    name: "GPIO 23 (VSPI MOSI)"
    type: "Bus Data"
    description: "Master Out Slave In data line to peripherals"
  - pin: 21
    name: "GPIO 21 (I2C SDA)"
    type: "Bus Data"
    description: "Standard I2C Data line for SSD1306 OLED display"
  - pin: 22
    name: "GPIO 22 (I2C SCL)"
    type: "Bus Clock"
    description: "Standard I2C Clock line for SSD1306 OLED display"
  - pin: 2
    name: "GPIO 2 (LED)"
    type: "Digital I/O"
    description: "Onboard Blue/Green status indicator LED"
datasheetUrl: "https://www.espressif.com/sites/default/files/documentation/esp32-wroom-32d_esp32-wroom-32u_datasheet_en.pdf"
wokwiPartId: "board-esp32-devkit-c-v4"
architecture: "Xtensa Dual-Core 32-bit LX6 Microprocessor"
clockSpeed: "Up to 240 MHz (600 DMIPS)"
description: "High-performance Wi-Fi + Bluetooth + BLE MCU module targeting low-power IoT sensing nodes and real-time edge processing."
labLocation: "MIT Chromepet Embedded Systems Lab - Locker B-04"
---

# ESP32-WROOM-32D Hardware Specifications

The **ESP32-WROOM-32D** is the foundational embedded microcontroller for the Anna University MIT Campus IoT Laboratory. Equipped with dual Xtensa LX6 cores, it enables concurrent execution of network stacks (Wi-Fi, FreeRTOS, HTTP client) on Core 0 while executing deterministic sensor sampling on Core 1.

