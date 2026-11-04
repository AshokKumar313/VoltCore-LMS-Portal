---
title: "EC8702: Embedded Systems & Real-Time Operating Systems Architecture"
code: "EC8702"
semester: 7
regulation: "Anna University R2021"
department: "Department of Electronics Engineering, MIT Campus"
credits: 4
order: 1
description: "Master embedded C development, FreeRTOS multi-tasking, memory-mapped I/O, SPI/I2C peripheral drivers, and low-power ESP32 IoT nodes tailored for Anna University standards."
difficulty: "Advanced"
author: "MIT Campus Embedded Systems Faculty"
publishDate: 2026-08-15
prerequisites:
  - "Digital Electronics & Microprocessors (8086 / 8051)"
  - "Data Structures and Algorithms in C/C++"
  - "Computer Architecture & Assembly Basics"
learningOutcomes:
  - "Architect preemptive multi-tasking applications using FreeRTOS task queues, semaphores, and mutexes."
  - "Implement high-throughput SPI/I2C communication pipelines with Direct Memory Access (DMA)."
  - "Design secure, power-efficient IoT telemetry nodes transmitting over 802.11 b/g/n and BLE 4.2."
  - "Analyze priority inversion and configure priority inheritance protocols on dual-core Xtensa microcontrollers."
hardwareKit:
  - "ESP32-WROOM-32D Dual-Core MCU"
  - "MFRC522 13.56MHz RFID Reader Module"
  - "SSD1306 0.96 inch 128x64 OLED (I2C)"
  - "FTDI USB-UART Serial Bridge"
tags:
  - "Embedded Systems"
  - "FreeRTOS"
  - "ESP32"
  - "IoT Architecture"
  - "Anna University R2021"
syllabusUnits:
  - unit: 1
    title: "Introduction to Embedded Computing & ARM Cortex Architecture"
    topics:
      - "Complex Systems and Microprocessors"
      - "ARM Cortex-M Memory Map and Registers"
      - "Instruction Pipelining and Interrupt Latency"
    labHours: 6
  - unit: 2
    title: "Real-Time Operating Systems (RTOS) & Task Scheduling"
    topics:
      - "FreeRTOS Kernel Architecture"
      - "Rate Monotonic Scheduling (RMS) vs Earliest Deadline First (EDF)"
      - "Inter-Task Communication with Queues and Event Groups"
    labHours: 8
  - unit: 3
    title: "Communication Protocols & Hardware Peripherals"
    topics:
      - "SPI Master-Slave Arbitration and Clock Polarity (CPOL/CPHA)"
      - "I2C Bus Arbitration, Clock Stretching, and SCL/SDA Pull-ups"
      - "UART FIFO Buffering and DMA Descriptors"
    labHours: 8
ieeeReference: "IEEE Transactions on Industrial Informatics, Vol. 19, No. 4, pp. 3201-3212"
xpReward: 350
---

# EC8702: Embedded Systems & Real-Time Operating Systems Architecture

Welcome to the Anna University / MIT Campus syllabus for **EC8702**. This advanced module covers the bridge between silicon physics, register abstractions, and real-time deterministic software.

## Key Laboratory Directives
- **Hardware Target**: ESP32-WROOM-32 DevKit v4
- **Security Standard**: PBKDF2-HMAC-SHA256 authenticated telemetry
- **Simulation**: Wokwi Zero-Latency Circuit Simulator

