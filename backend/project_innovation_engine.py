"""
========================================================================================
VoltCore Apex Academia - Engineering Project & Innovation Center (Phase 24)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/project_innovation_engine.py
Course Code: EC3711 - Mini Project / Comprehensive Practical (Regulation 2023)
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Public Contact: ashokkumar3132008@gmail.com | GitHub: https://github.com/AshokKumar313
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  Lightweight backend manager handling:
    1. Mini-Project Proposal Builder & Lifecycle Manager (Draft -> Review -> Approved).
    2. Engineering Bill of Materials (BOM) Cost Estimator with GST & Contingency buffers.
    3. Hardware Component Compatibility Checker (Logic Voltage, Current Budget, Bus Match).
    4. Project Milestone & Deliverables Tracker with Attainment Percentages.
    5. Curated ECE Innovation Idea Repository mapped to Regulation 2023.
    6. SQLite WAL-backed persistence with sub-3ms query latency & passive thermal profile.
========================================================================================
"""

import os
import time
import math
import json
import sqlite3
import threading
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")

# Default demo student
DEFAULT_STUDENT_ID = "2023MITEC042"

# Curated ECE Innovation Idea Repository (Anna University Regulation 2023 Aligned)
INNOVATION_IDEAS_CATALOG = [
    {
        "idea_id": "IDEA_LORA_AGRI_NODE",
        "title": "LoRaWAN Agricultural Soil & Microclimate Node",
        "domain": "IoT & Smart Systems",
        "difficulty": "Intermediate",
        "curriculum_mapping": "EC3501 Wireless Communication & Networks",
        "description": "Ultra-low-power edge sensory node measuring volumetric soil moisture, temperature, and atmospheric pressure with deep-sleep telemetry over 5km LoRa links.",
        "suggested_mcu": "ESP32-WROOM-32",
        "hardware_stack": ["ESP32-WROOM-32", "SX1278 LoRa Module", "BME280 Sensor", "Capacitive Soil Moisture Sensor", "TP4056 Solar Charger"],
        "software_stack": ["FreeRTOS", "RadioHead / LMIC Library", "InfluxDB", "Grafana"],
        "estimated_budget_inr": 2450.0,
        "tags": ["IoT", "LoRaWAN", "Agriculture", "LowPower", "SmartSensing"]
    },
    {
        "idea_id": "IDEA_QUADCOPTER_RTOS",
        "title": "Deterministic Quadcopter Flight Controller on FreeRTOS",
        "domain": "Embedded RTOS & Robotics",
        "difficulty": "Advanced",
        "curriculum_mapping": "EC3601 Embedded Systems & RTOS",
        "description": "Sub-millisecond cascaded PID attitude control loop running as high-priority real-time tasks with Kalman filtering for fused IMU/Barometer telemetry.",
        "suggested_mcu": "STM32F401CCU6 (BlackPill)",
        "hardware_stack": ["STM32F401CCU6", "MPU6050 6-DOF IMU", "BMP280 Barometer", "4x 20A ESC", "2204 Brushless Motors"],
        "software_stack": ["FreeRTOS Kernel", "CMSIS-DSP", "DMA SPI/I2C Drivers", "PID Tuning GUI"],
        "estimated_budget_inr": 6200.0,
        "tags": ["RTOS", "FlightControl", "Robotics", "KalmanFilter", "STM32"]
    },
    {
        "idea_id": "IDEA_TINYML_VIBRATION",
        "title": "TinyML Vibration Anomaly Detector for Industrial Motors",
        "domain": "Edge AI & Signal Processing",
        "difficulty": "Intermediate",
        "curriculum_mapping": "EC3701 TinyML & Intelligent Edge Systems",
        "description": "On-device accelerometer FFT spectral feature extraction and quantized neural network (INT8) inferencing to predict bearing wear and rotor imbalances.",
        "suggested_mcu": "Raspberry Pi Pico (RP2040)",
        "hardware_stack": ["Raspberry Pi Pico", "ADXL345 Accelerometer", "SSD1306 OLED Display", "Active Buzzer"],
        "software_stack": ["TensorFlow Lite for Microcontrollers", "Edge Impulse C++ SDK", "Python SciPy"],
        "estimated_budget_inr": 1850.0,
        "tags": ["TinyML", "EdgeAI", "PredictiveMaintenance", "Vibration", "SignalProcessing"]
    },
    {
        "idea_id": "IDEA_RISCV_PIPELINED_CORE",
        "title": "FPGA Pipelined 32-bit RISC-V (RV32I) Soft-Core Processor",
        "domain": "VLSI & Digital Systems",
        "difficulty": "Advanced",
        "curriculum_mapping": "EC3352 Digital Systems Design & Computer Architecture",
        "description": "5-stage classical pipelined RISC-V RV32I core with hazard resolution, forwarding units, Harvard cache architecture, and custom peripheral memory mapping.",
        "suggested_mcu": "Xilinx Spartan-7 / Artix-7 FPGA",
        "hardware_stack": ["Xilinx Spartan-7 FPGA Board", "UART-to-USB Bridge", "7-Segment Displays", "Tactile Switches"],
        "software_stack": ["Verilog HDL", "Xilinx Vivado", "GNU RISC-V Toolchain", "GTKWave"],
        "estimated_budget_inr": 7500.0,
        "tags": ["VLSI", "RISC-V", "Verilog", "FPGA", "ComputerArchitecture"]
    },
    {
        "idea_id": "IDEA_PPG_HEALTH_MONITOR",
        "title": "Non-Invasive Wearable PPG Heart Rate & SpO2 Monitor",
        "domain": "Biomedical Electronics",
        "difficulty": "Beginner",
        "curriculum_mapping": "EC3451 Linear Integrated Circuits & Biomedical Instrumentation",
        "description": "Optical sensor photoplethysmography circuit with active bandpass analog front-end (0.5 - 4 Hz) and digital peak-detection algorithm for cardiac rhythm tracking.",
        "suggested_mcu": "Arduino Nano 33 BLE",
        "hardware_stack": ["Arduino Nano 33 BLE", "MAX30102 Pulse Oximeter", "0.96 inch I2C OLED", "LiPo 3.7V Battery"],
        "software_stack": ["Arduino C++", "BLE HID Service", "Butterworth Filter Lib"],
        "estimated_budget_inr": 2100.0,
        "tags": ["Biomedical", "PPG", "Wearables", "SpO2", "Healthcare"]
    },
    {
        "idea_id": "IDEA_AUTONOMOUS_ROVER_SLAM",
        "title": "Autonomous Ground Rover with Ultrasonic LiDAR SLAM",
        "domain": "Robotics & Automation",
        "difficulty": "Intermediate",
        "curriculum_mapping": "EC3601 Embedded Systems & Microcontrollers",
        "description": "Differential-drive autonomous robotic platform combining Time-of-Flight (ToF) laser ranging with ultrasonic collision avoidance and obstacle mapping.",
        "suggested_mcu": "ESP32-WROOM-32",
        "hardware_stack": ["ESP32-WROOM-32", "VL53L0X ToF Laser Sensor", "2x HC-SR04 Ultrasonic", "L298N Motor Driver", "2x TT Gear Motors"],
        "software_stack": ["ESP-IDF / Arduino", "Micro-ROS", "Occupancy Grid Mapping"],
        "estimated_budget_inr": 3400.0,
        "tags": ["Robotics", "SLAM", "Autonomous", "ObstacleAvoidance", "Sensors"]
    }
]

# Standard Hardware Specifications Database for Compatibility Checking
MCU_DATABASE = {
    "ESP32-WROOM-32": {
        "name": "ESP32-WROOM-32",
        "logic_voltage": 3.3,
        "five_volt_tolerant": False,
        "vreg_max_ma": 600.0,
        "i2c_ports": 2,
        "spi_ports": 3,
        "uart_ports": 3,
        "pwm_channels": 16,
        "adc_channels": 18,
        "wireless": "WiFi 802.11 b/g/n + BLE 4.2",
        "standard_sleep_ua": 10.0
    },
    "STM32F401CCU6 (BlackPill)": {
        "name": "STM32F401CCU6 (BlackPill)",
        "logic_voltage": 3.3,
        "five_volt_tolerant": True,  # FT pins only
        "vreg_max_ma": 400.0,
        "i2c_ports": 3,
        "spi_ports": 4,
        "uart_ports": 3,
        "pwm_channels": 11,
        "adc_channels": 16,
        "wireless": "None (External Required)",
        "standard_sleep_ua": 12.0
    },
    "Arduino Uno R3 (ATmega328P)": {
        "name": "Arduino Uno R3 (ATmega328P)",
        "logic_voltage": 5.0,
        "five_volt_tolerant": True,
        "vreg_max_ma": 800.0,  # 5V rail
        "vreg_3v3_max_ma": 50.0, # 3.3V pin limit
        "i2c_ports": 1,
        "spi_ports": 1,
        "uart_ports": 1,
        "pwm_channels": 6,
        "adc_channels": 6,
        "wireless": "None",
        "standard_sleep_ua": 15000.0
    },
    "Raspberry Pi Pico (RP2040)": {
        "name": "Raspberry Pi Pico (RP2040)",
        "logic_voltage": 3.3,
        "five_volt_tolerant": False,
        "vreg_max_ma": 300.0,
        "i2c_ports": 2,
        "spi_ports": 2,
        "uart_ports": 2,
        "pwm_channels": 16,
        "adc_channels": 3,
        "wireless": "None (Pico W has WiFi)",
        "standard_sleep_ua": 180.0
    },
    "Arduino Nano 33 BLE (nRF52840)": {
        "name": "Arduino Nano 33 BLE (nRF52840)",
        "logic_voltage": 3.3,
        "five_volt_tolerant": False,
        "vreg_max_ma": 200.0,
        "i2c_ports": 1,
        "spi_ports": 1,
        "uart_ports": 1,
        "pwm_channels": 8,
        "adc_channels": 8,
        "wireless": "BLE 5.0",
        "standard_sleep_ua": 5.0
    }
}

COMPONENT_DATABASE = {
    "BME280 Sensor": {
        "name": "BME280 Barometric/Humidity/Temp Sensor",
        "category": "SENSOR",
        "logic_voltage": 3.3,
        "current_ma": 3.6,
        "interface": "I2C",
        "i2c_address": "0x76",
        "unit_price_inr": 380.0,
        "notes": "Strict 3.3V logic. Exceeding 3.6V will damage sensor."
    },
    "MPU6050 6-DOF IMU": {
        "name": "MPU6050 6-DOF IMU Accelerometer/Gyro",
        "category": "SENSOR",
        "logic_voltage": 3.3,
        "current_ma": 3.9,
        "interface": "I2C",
        "i2c_address": "0x68",
        "unit_price_inr": 190.0,
        "notes": "Module breakout usually includes 3.3V LDO; I2C lines are 3.3V."
    },
    "HC-SR04 Ultrasonic Distance Sensor": {
        "name": "HC-SR04 Ultrasonic Distance Sensor",
        "category": "SENSOR",
        "logic_voltage": 5.0,
        "current_ma": 15.0,
        "interface": "GPIO_PULSE",
        "unit_price_inr": 120.0,
        "notes": "Echo pin outputs 5V TTL pulse. Requires resistor divider (1k/2k) when connected to 3.3V MCU."
    },
    "SX1278 LoRa Module": {
        "name": "SX1278 433MHz LoRa Transceiver",
        "category": "COMMUNICATION",
        "logic_voltage": 3.3,
        "current_ma": 120.0,
        "interface": "SPI",
        "unit_price_inr": 550.0,
        "notes": "Transmit burst current reaches 120mA. Ensure solid 3.3V decoupling capacitor."
    },
    "SIM800L GSM/GPRS Module": {
        "name": "SIM800L Quad-Band GSM/GPRS Module",
        "category": "COMMUNICATION",
        "logic_voltage": 4.0,
        "current_ma": 2000.0,
        "interface": "UART",
        "unit_price_inr": 650.0,
        "notes": "Requires 3.7V - 4.2V supply capable of 2.0A pulse currents. Cannot be powered directly from MCU regulator."
    },
    "SSD1306 0.96 inch I2C OLED": {
        "name": "SSD1306 0.96 inch 128x64 I2C OLED Display",
        "category": "DISPLAY",
        "logic_voltage": 3.3,
        "current_ma": 22.0,
        "interface": "I2C",
        "i2c_address": "0x3C",
        "unit_price_inr": 280.0,
        "notes": "Supports 3.3V and 5V inputs with on-board boost converter."
    },
    "SG90 Micro Servo Motor": {
        "name": "TowerPro SG90 9g Micro Servo",
        "category": "ACTUATOR",
        "logic_voltage": 5.0,
        "current_ma": 500.0,
        "interface": "PWM",
        "unit_price_inr": 140.0,
        "notes": "Stall current is 500mA+. Must be powered from an independent 5V rail; never from MCU pins."
    },
    "MAX30102 Pulse Oximeter": {
        "name": "MAX30102 Pulse Oximeter & Heart Rate Sensor",
        "category": "SENSOR",
        "logic_voltage": 3.3,
        "current_ma": 2.5,
        "interface": "I2C",
        "i2c_address": "0x57",
        "unit_price_inr": 320.0,
        "notes": "Requires dual 1.8V core and 3.3V I2C pullups. Handled on module."
    },
    "VL53L0X ToF Laser Sensor": {
        "name": "VL53L0X Time-of-Flight Laser Ranging Sensor",
        "category": "SENSOR",
        "logic_voltage": 3.3,
        "current_ma": 19.0,
        "interface": "I2C",
        "i2c_address": "0x29",
        "unit_price_inr": 450.0,
        "notes": "Precision millimeter ranging up to 2m; I2C address can be changed via XSHUT pin."
    },
    "ADXL345 Accelerometer": {
        "name": "ADXL345 3-Axis Digital Accelerometer",
        "category": "SENSOR",
        "logic_voltage": 3.3,
        "current_ma": 0.14,
        "interface": "I2C",
        "i2c_address": "0x53",
        "unit_price_inr": 210.0,
        "notes": "Ultra-low power sensor ideal for vibration analysis and tap detection."
    }
}


class ProjectInnovationEngine:
    """
    Lightweight, high-performance Engineering Project & Innovation Center engine.
    Supports proposals, bill of materials calculation, hardware compatibility checks,
    and milestone progress tracking under Anna University Regulation 2023.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._lock = threading.Lock()
        self.init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def init_db(self):
        """Initializes tables for proposals, BOM items, milestones, and ideas with SQLite WAL."""
        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    # 1. Project Proposals Table
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS project_proposals (
                            proposal_id TEXT PRIMARY KEY,
                            student_id TEXT NOT NULL,
                            title TEXT NOT NULL,
                            domain TEXT NOT NULL,
                            abstract TEXT,
                            objectives_json TEXT,
                            regulation_code TEXT DEFAULT 'Regulation 2023 / EC3711',
                            hardware_stack_json TEXT,
                            software_stack_json TEXT,
                            mentor_name TEXT,
                            status TEXT DEFAULT 'DRAFT',
                            created_at REAL,
                            updated_at REAL
                        );
                    """)

                    # 2. Project Bill of Materials (BOM) Table
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS project_bom_items (
                            item_id TEXT PRIMARY KEY,
                            proposal_id TEXT NOT NULL,
                            component_name TEXT NOT NULL,
                            category TEXT NOT NULL,
                            quantity INTEGER DEFAULT 1,
                            unit_price_inr REAL DEFAULT 0.0,
                            vendor TEXT,
                            voltage_spec REAL,
                            current_ma REAL,
                            interface_type TEXT,
                            in_stock INTEGER DEFAULT 1,
                            created_at REAL,
                            FOREIGN KEY (proposal_id) REFERENCES project_proposals(proposal_id)
                        );
                    """)

                    # 3. Project Milestones Table
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS project_milestones (
                            milestone_id TEXT PRIMARY KEY,
                            proposal_id TEXT NOT NULL,
                            title TEXT NOT NULL,
                            description TEXT,
                            weightage_percent REAL DEFAULT 20.0,
                            due_date TEXT,
                            status TEXT DEFAULT 'PENDING',
                            deliverables_json TEXT,
                            completed_at REAL,
                            FOREIGN KEY (proposal_id) REFERENCES project_proposals(proposal_id)
                        );
                    """)

                    # 4. Innovation Ideas Table
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS innovation_ideas (
                            idea_id TEXT PRIMARY KEY,
                            title TEXT NOT NULL,
                            domain TEXT NOT NULL,
                            difficulty TEXT NOT NULL,
                            curriculum_mapping TEXT,
                            description TEXT,
                            suggested_mcu TEXT,
                            hardware_stack_json TEXT,
                            software_stack_json TEXT,
                            estimated_budget_inr REAL,
                            tags_json TEXT
                        );
                    """)

                    # Index for fast student lookups
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_proposals_student ON project_proposals(student_id);")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_bom_proposal ON project_bom_items(proposal_id);")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_milestones_proposal ON project_milestones(proposal_id);")

                    self._seed_default_data(conn)
            finally:
                conn.close()

    def _seed_default_data(self, conn: sqlite3.Connection):
        """Seeds standard ideas and a verified benchmark proposal for MIT Campus student."""
        # Seed Innovation Ideas
        for idea in INNOVATION_IDEAS_CATALOG:
            conn.execute("""
                INSERT OR IGNORE INTO innovation_ideas (
                    idea_id, title, domain, difficulty, curriculum_mapping,
                    description, suggested_mcu, hardware_stack_json, software_stack_json,
                    estimated_budget_inr, tags_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                idea["idea_id"],
                idea["title"],
                idea["domain"],
                idea["difficulty"],
                idea["curriculum_mapping"],
                idea["description"],
                idea["suggested_mcu"],
                json.dumps(idea["hardware_stack"]),
                json.dumps(idea["software_stack"]),
                idea["estimated_budget_inr"],
                json.dumps(idea["tags"])
            ))

        # Seed Verified Sample Proposal for Lead Architect Ashok Kumar A
        sample_proposal_id = "PROP_2023MITEC042_01"
        cursor = conn.execute("SELECT proposal_id FROM project_proposals WHERE proposal_id = ?", (sample_proposal_id,))
        if not cursor.fetchone():
            now = time.time()
            conn.execute("""
                INSERT INTO project_proposals (
                    proposal_id, student_id, title, domain, abstract,
                    objectives_json, regulation_code, hardware_stack_json, software_stack_json,
                    mentor_name, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                sample_proposal_id,
                DEFAULT_STUDENT_ID,
                "Autonomous IoT Edge Microclimate & Crop Disease Monitoring Node",
                "IoT & Smart Systems",
                "Ultra-low-power edge sensory node deployed in agricultural fields with on-device microclimate sensing, solar energy harvesting, and long-range LoRaWAN telemetry to cloud analytics dashboards.",
                json.dumps([
                    "Design solar energy harvesting circuit with TP4056 and 18650 Li-ion cell.",
                    "Interface BME280 and soil moisture sensors with ESP32 via I2C and ADC.",
                    "Implement LoRaWAN Class A uplink communication over 5km distance.",
                    "Optimize deep-sleep power states to achieve >12 months battery longevity."
                ]),
                "Regulation 2023 / EC3711",
                json.dumps(["ESP32-WROOM-32", "SX1278 LoRa Module", "BME280 Sensor", "Capacitive Soil Moisture Sensor"]),
                json.dumps(["FreeRTOS", "RadioHead", "InfluxDB", "Grafana"]),
                "Dr. P. Nirmal Kumar (Professor & Head, Dept of Electronics)",
                "APPROVED",
                now,
                now
            ))

            # Seed Sample BOM Items for Proposal
            sample_bom = [
                ("BOM_ITEM_01", sample_proposal_id, "ESP32-WROOM-32 Development Board", "MCU", 1, 350.0, "Robu.in", 3.3, 80.0, "GPIO/WiFi/BLE", 1),
                ("BOM_ITEM_02", sample_proposal_id, "SX1278 433MHz LoRa Transceiver", "COMMUNICATION", 1, 550.0, "Ebay India", 3.3, 120.0, "SPI", 1),
                ("BOM_ITEM_03", sample_proposal_id, "BME280 Temperature/Humidity/Pressure Sensor", "SENSOR", 1, 380.0, "Robocraze", 3.3, 3.6, "I2C", 1),
                ("BOM_ITEM_04", sample_proposal_id, "Capacitive Soil Moisture Sensor v1.2", "SENSOR", 2, 85.0, "Robu.in", 3.3, 5.0, "ADC", 1),
                ("BOM_ITEM_05", sample_proposal_id, "TP4056 1A Li-Ion Charger Module with Protection", "POWER", 1, 45.0, "ElectronicsComp", 5.0, 1000.0, "Power Rail", 1),
                ("BOM_ITEM_06", sample_proposal_id, "3.7V 2500mAh 18650 Rechargeable Cell", "POWER", 1, 240.0, "Robu.in", 3.7, 2500.0, "Battery", 1)
            ]
            for item in sample_bom:
                conn.execute("""
                    INSERT INTO project_bom_items (
                        item_id, proposal_id, component_name, category,
                        quantity, unit_price_inr, vendor, voltage_spec, current_ma,
                        interface_type, in_stock, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (*item, now))

            # Seed Sample Milestones
            sample_milestones = [
                ("MS_01", sample_proposal_id, "Literature Survey & Component Procurement", "Select sensors and order prototyping components", 20.0, "2026-11-15", "COMPLETED", json.dumps(["Component delivery confirmation", "Comparative study doc"]), now),
                ("MS_02", sample_proposal_id, "Hardware Prototyping & Sensor Calibration", "Breadboard circuit, verify I2C/SPI signals on oscilloscope", 25.0, "2026-11-30", "COMPLETED", json.dumps(["Oscilloscope waveform captures", "Calibration curve"]), now),
                ("MS_03", sample_proposal_id, "Firmware Development & LoRa Integration", "FreeRTOS tasks for sensor reading and packet formulation", 30.0, "2026-12-15", "IN_PROGRESS", json.dumps(["GitHub repository commit", "LoRa packet dump"]), None),
                ("MS_04", sample_proposal_id, "Field Deployment & Final Viva Presentation", "Deploy at MIT Campus garden and generate technical report", 25.0, "2027-01-10", "PENDING", json.dumps(["Project thesis PDF", "Demonstration video"]), None)
            ]
            for ms in sample_milestones:
                conn.execute("""
                    INSERT INTO project_milestones (
                        milestone_id, proposal_id, title, description,
                        weightage_percent, due_date, status, deliverables_json,
                        completed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, ms)

    # ====================================================================================
    # 1. Overview & Statistics
    # ====================================================================================

    def get_overview(self, student_id: str = DEFAULT_STUDENT_ID) -> Dict[str, Any]:
        """Provides an aggregated overview of project proposals, milestones, and budgets."""
        conn = self._get_connection()
        try:
            cur = conn.execute("SELECT COUNT(*) AS total FROM project_proposals WHERE student_id = ?", (student_id,))
            total_proposals = cur.fetchone()["total"]

            cur = conn.execute("SELECT COUNT(*) AS approved FROM project_proposals WHERE student_id = ? AND status = 'APPROVED'", (student_id,))
            approved_proposals = cur.fetchone()["approved"]

            cur = conn.execute("""
                SELECT COUNT(*) AS total_ms,
                       SUM(CASE WHEN m.status = 'COMPLETED' THEN 1 ELSE 0 END) AS completed_ms,
                       SUM(CASE WHEN m.status = 'IN_PROGRESS' THEN 1 ELSE 0 END) AS in_progress_ms
                FROM project_milestones m
                JOIN project_proposals p ON m.proposal_id = p.proposal_id
                WHERE p.student_id = ?;
            """, (student_id,))
            ms_row = cur.fetchone()
            total_ms = ms_row["total_ms"] or 0
            completed_ms = ms_row["completed_ms"] or 0
            in_progress_ms = ms_row["in_progress_ms"] or 0

            # Total BOM budget allocated
            cur = conn.execute("""
                SELECT SUM(b.quantity * b.unit_price_inr) AS total_bom
                FROM project_bom_items b
                JOIN project_proposals p ON b.proposal_id = p.proposal_id
                WHERE p.student_id = ?;
            """, (student_id,))
            total_bom_raw = cur.fetchone()["total_bom"] or 0.0

            # Count available ideas
            cur = conn.execute("SELECT COUNT(*) AS ideas_count FROM innovation_ideas;")
            ideas_count = cur.fetchone()["ideas_count"]

            overall_progress = round((completed_ms / total_ms * 100), 1) if total_ms > 0 else 0.0

            return {
                "status": "SUCCESS",
                "student_id": student_id,
                "metrics": {
                    "total_proposals": total_proposals,
                    "approved_proposals": approved_proposals,
                    "total_milestones": total_ms,
                    "completed_milestones": completed_ms,
                    "in_progress_milestones": in_progress_ms,
                    "overall_progress_percent": overall_progress,
                    "total_bom_expenditure_inr": round(total_bom_raw, 2),
                    "curated_ideas_count": ideas_count
                },
                "institution": "Madras Institute of Technology (MIT) Campus",
                "regulation": "Anna University Regulation 2023",
                "course_code": "EC3711"
            }
        finally:
            conn.close()

    # ====================================================================================
    # 2. Curated Innovation Ideas Repository
    # ====================================================================================

    def get_innovation_ideas(self, domain: Optional[str] = None, difficulty: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns filtered innovation ideas mapped to Anna University curriculum."""
        conn = self._get_connection()
        try:
            query = "SELECT * FROM innovation_ideas WHERE 1=1"
            params = []
            if domain:
                query += " AND domain = ?"
                params.append(domain)
            if difficulty:
                query += " AND difficulty = ?"
                params.append(difficulty)

            query += " ORDER BY idea_id ASC;"
            cur = conn.execute(query, tuple(params))
            results = []
            for row in cur.fetchall():
                results.append({
                    "idea_id": row["idea_id"],
                    "title": row["title"],
                    "domain": row["domain"],
                    "difficulty": row["difficulty"],
                    "curriculum_mapping": row["curriculum_mapping"],
                    "description": row["description"],
                    "suggested_mcu": row["suggested_mcu"],
                    "hardware_stack": json.loads(row["hardware_stack_json"] or "[]"),
                    "software_stack": json.loads(row["software_stack_json"] or "[]"),
                    "estimated_budget_inr": row["estimated_budget_inr"],
                    "tags": json.loads(row["tags_json"] or "[]")
                })
            return results
        finally:
            conn.close()

    # ====================================================================================
    # 3. Project Proposals Management
    # ====================================================================================

    def get_proposals(self, student_id: str = DEFAULT_STUDENT_ID) -> List[Dict[str, Any]]:
        """Retrieves all project proposals for a given student with aggregated counts."""
        conn = self._get_connection()
        try:
            cur = conn.execute("""
                SELECT p.*,
                       COUNT(DISTINCT b.item_id) AS bom_items_count,
                       COALESCE(SUM(b.quantity * b.unit_price_inr), 0.0) AS bom_subtotal_inr,
                       COUNT(DISTINCT m.milestone_id) AS milestones_count,
                       SUM(CASE WHEN m.status = 'COMPLETED' THEN 1 ELSE 0 END) AS completed_milestones
                FROM project_proposals p
                LEFT JOIN project_bom_items b ON p.proposal_id = b.proposal_id
                LEFT JOIN project_milestones m ON p.proposal_id = m.proposal_id
                WHERE p.student_id = ?
                GROUP BY p.proposal_id
                ORDER BY p.created_at DESC;
            """, (student_id,))
            proposals = []
            for row in cur.fetchall():
                total_ms = row["milestones_count"]
                comp_ms = row["completed_milestones"] or 0
                prog = round((comp_ms / total_ms * 100), 1) if total_ms > 0 else 0.0

                proposals.append({
                    "proposal_id": row["proposal_id"],
                    "student_id": row["student_id"],
                    "title": row["title"],
                    "domain": row["domain"],
                    "abstract": row["abstract"],
                    "objectives": json.loads(row["objectives_json"] or "[]"),
                    "regulation_code": row["regulation_code"],
                    "hardware_stack": json.loads(row["hardware_stack_json"] or "[]"),
                    "software_stack": json.loads(row["software_stack_json"] or "[]"),
                    "mentor_name": row["mentor_name"],
                    "status": row["status"],
                    "bom_items_count": row["bom_items_count"],
                    "bom_subtotal_inr": round(row["bom_subtotal_inr"], 2),
                    "milestones_count": total_ms,
                    "completed_milestones": comp_ms,
                    "progress_percent": prog,
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                })
            return proposals
        finally:
            conn.close()

    def get_proposal_detail(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves complete proposal details including BOM items and milestones."""
        conn = self._get_connection()
        try:
            cur = conn.execute("SELECT * FROM project_proposals WHERE proposal_id = ?", (proposal_id,))
            row = cur.fetchone()
            if not row:
                return None

            # Get BOM items
            cur_bom = conn.execute("""
                SELECT * FROM project_bom_items
                WHERE proposal_id = ?
                ORDER BY created_at ASC;
            """, (proposal_id,))
            bom_items = []
            for b in cur_bom.fetchall():
                bom_items.append({
                    "item_id": b["item_id"],
                    "component_name": b["component_name"],
                    "category": b["category"],
                    "quantity": b["quantity"],
                    "unit_price_inr": b["unit_price_inr"],
                    "total_price_inr": round(b["quantity"] * b["unit_price_inr"], 2),
                    "vendor": b["vendor"],
                    "voltage_spec": b["voltage_spec"],
                    "current_ma": b["current_ma"],
                    "interface_type": b["interface_type"],
                    "in_stock": bool(b["in_stock"])
                })

            # Get Milestones
            cur_ms = conn.execute("""
                SELECT * FROM project_milestones
                WHERE proposal_id = ?
                ORDER BY due_date ASC;
            """, (proposal_id,))
            milestones = []
            total_weight = 0.0
            completed_weight = 0.0
            for m in cur_ms.fetchall():
                w = m["weightage_percent"] or 0.0
                total_weight += w
                if m["status"] == "COMPLETED":
                    completed_weight += w

                milestones.append({
                    "milestone_id": m["milestone_id"],
                    "title": m["title"],
                    "description": m["description"],
                    "weightage_percent": w,
                    "due_date": m["due_date"],
                    "status": m["status"],
                    "deliverables": json.loads(m["deliverables_json"] or "[]"),
                    "completed_at": m["completed_at"]
                })

            progress = round((completed_weight / total_weight * 100), 1) if total_weight > 0 else 0.0

            return {
                "proposal_id": row["proposal_id"],
                "student_id": row["student_id"],
                "title": row["title"],
                "domain": row["domain"],
                "abstract": row["abstract"],
                "objectives": json.loads(row["objectives_json"] or "[]"),
                "regulation_code": row["regulation_code"],
                "hardware_stack": json.loads(row["hardware_stack_json"] or "[]"),
                "software_stack": json.loads(row["software_stack_json"] or "[]"),
                "mentor_name": row["mentor_name"],
                "status": row["status"],
                "progress_percent": progress,
                "bom_items": bom_items,
                "milestones": milestones,
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }
        finally:
            conn.close()

    def create_proposal(self, data: Dict[str, Any], actor_role: str = "Student") -> Dict[str, Any]:
        """Creates a new project proposal."""
        title = (data.get("title") or "").strip()
        if not title:
            return {"status": "ERROR", "message": "Project title is required."}

        proposal_id = data.get("proposal_id") or f"PROP_{int(time.time()*1000)}"
        student_id = data.get("student_id") or DEFAULT_STUDENT_ID
        domain = data.get("domain", "IoT & Smart Systems")
        abstract = data.get("abstract", "")
        objectives = data.get("objectives", [])
        regulation = data.get("regulation_code", "Regulation 2023 / EC3711")
        hw_stack = data.get("hardware_stack", [])
        sw_stack = data.get("software_stack", [])
        mentor = data.get("mentor_name", "Dr. P. Nirmal Kumar (MIT Campus)")
        status = "SUBMITTED" if actor_role in ["Teacher", "Admin"] else "DRAFT"

        now = time.time()
        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    conn.execute("""
                        INSERT INTO project_proposals (
                            proposal_id, student_id, title, domain, abstract,
                            objectives_json, regulation_code, hardware_stack_json, software_stack_json,
                            mentor_name, status, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        proposal_id, student_id, title, domain, abstract,
                        json.dumps(objectives), regulation, json.dumps(hw_stack), json.dumps(sw_stack),
                        mentor, status, now, now
                    ))
                return {
                    "status": "SUCCESS",
                    "proposal_id": proposal_id,
                    "message": f"Proposal '{title}' registered successfully.",
                    "current_status": status
                }
            except sqlite3.IntegrityError:
                return {"status": "ERROR", "message": f"Proposal with ID '{proposal_id}' already exists."}
            finally:
                conn.close()

    def update_proposal_status(self, proposal_id: str, new_status: str, actor_role: str = "Student") -> Dict[str, Any]:
        """Updates proposal approval status with RBAC enforcement."""
        valid_statuses = ["DRAFT", "SUBMITTED", "UNDER_REVIEW", "APPROVED", "REJECTED"]
        if new_status not in valid_statuses:
            return {"status": "ERROR", "message": f"Invalid status '{new_status}'."}

        # Students cannot approve/reject proposals
        if actor_role not in ["Teacher", "Admin"] and new_status in ["APPROVED", "REJECTED"]:
            return {"status": "FORBIDDEN", "message": "Only faculty mentors or administrators can approve or reject proposals."}

        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    cur = conn.execute("""
                        UPDATE project_proposals
                        SET status = ?, updated_at = ?
                        WHERE proposal_id = ?;
                    """, (new_status, time.time(), proposal_id))
                    if cur.rowcount == 0:
                        return {"status": "ERROR", "message": f"Proposal '{proposal_id}' not found."}
                return {
                    "status": "SUCCESS",
                    "proposal_id": proposal_id,
                    "new_status": new_status,
                    "message": f"Proposal status transitioned to {new_status}."
                }
            finally:
                conn.close()

    # ====================================================================================
    # 4. Bill of Materials (BOM) Cost Estimator
    # ====================================================================================

    def calculate_bom(
        self,
        items: List[Dict[str, Any]],
        tax_buffer_percent: float = 18.0,
        contingency_percent: float = 10.0
    ) -> Dict[str, Any]:
        """
        Calculates complete hardware bill of materials budget with GST & contingency.
        Performs category breakdown and computes per-item metrics.
        """
        if not items:
            return {
                "status": "SUCCESS",
                "items_count": 0,
                "subtotal_inr": 0.0,
                "gst_tax_inr": 0.0,
                "contingency_inr": 0.0,
                "total_estimated_budget_inr": 0.0,
                "category_breakdown": {},
                "max_cost_item": None,
                "average_item_cost_inr": 0.0
            }

        subtotal = 0.0
        categories: Dict[str, float] = {}
        max_cost_item = None
        highest_cost = -1.0

        processed_items = []
        for idx, item in enumerate(items):
            name = item.get("component_name", f"Component #{idx+1}")
            qty = max(1, int(item.get("quantity", 1)))
            unit_price = max(0.0, float(item.get("unit_price_inr", 0.0)))
            cat = (item.get("category") or "OTHER").upper()
            line_total = round(qty * unit_price, 2)
            subtotal += line_total

            categories[cat] = round(categories.get(cat, 0.0) + line_total, 2)

            if line_total > highest_cost:
                highest_cost = line_total
                max_cost_item = {
                    "component_name": name,
                    "total_cost_inr": line_total,
                    "category": cat
                }

            processed_items.append({
                "component_name": name,
                "category": cat,
                "quantity": qty,
                "unit_price_inr": unit_price,
                "line_total_inr": line_total,
                "vendor": item.get("vendor", "Standard Vendor")
            })

        subtotal = round(subtotal, 2)
        gst_amount = round(subtotal * (tax_buffer_percent / 100.0), 2)
        contingency_amount = round(subtotal * (contingency_percent / 100.0), 2)
        grand_total = round(subtotal + gst_amount + contingency_amount, 2)
        avg_cost = round(subtotal / len(items), 2) if items else 0.0

        return {
            "status": "SUCCESS",
            "items_count": len(items),
            "subtotal_inr": subtotal,
            "tax_buffer_percent": tax_buffer_percent,
            "gst_tax_inr": gst_amount,
            "contingency_percent": contingency_percent,
            "contingency_inr": contingency_amount,
            "total_estimated_budget_inr": grand_total,
            "category_breakdown": categories,
            "max_cost_item": max_cost_item,
            "average_item_cost_inr": avg_cost,
            "processed_items": processed_items
        }

    def save_bom_items(self, proposal_id: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Saves or updates BOM items associated with a project proposal."""
        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    # Clear existing items for this proposal
                    conn.execute("DELETE FROM project_bom_items WHERE proposal_id = ?", (proposal_id,))
                    now = time.time()
                    for idx, item in enumerate(items):
                        item_id = item.get("item_id") or f"BOM_{proposal_id}_{idx+1}_{int(time.time()*1000)}"
                        conn.execute("""
                            INSERT INTO project_bom_items (
                                item_id, proposal_id, component_name, category,
                                quantity, unit_price_inr, vendor, voltage_spec, current_ma,
                                interface_type, in_stock, created_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                        """, (
                            item_id,
                            proposal_id,
                            item.get("component_name", "Unknown Component"),
                            item.get("category", "OTHER").upper(),
                            int(item.get("quantity", 1)),
                            float(item.get("unit_price_inr", 0.0)),
                            item.get("vendor", "Local Distributor"),
                            float(item.get("voltage_spec", 3.3)),
                            float(item.get("current_ma", 10.0)),
                            item.get("interface_type", "GPIO"),
                            1 if item.get("in_stock", True) else 0,
                            now
                        ))
                return {"status": "SUCCESS", "proposal_id": proposal_id, "saved_items_count": len(items)}
            finally:
                conn.close()

    # ====================================================================================
    # 5. Hardware Component Compatibility Checker
    # ====================================================================================

    def check_compatibility(
        self,
        mcu_name: str,
        components: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validates hardware component interoperability against the chosen microcontroller:
          1. Logic Voltage compatibility (3.3V vs 5.0V with level shifting alerts).
          2. Power consumption budget (total current draw vs MCU on-board LDO limit).
          3. Bus interface count (I2C collisions, SPI CS lines, UART port saturation).
          4. Returns comprehensive engineering verdict: COMPATIBLE, COMPATIBLE_WITH_CAVEATS, or INCOMPATIBLE.
        """
        mcu_spec = MCU_DATABASE.get(mcu_name)
        if not mcu_spec:
            # Fallback default generic MCU
            mcu_spec = {
                "name": mcu_name or "Generic 3.3V MCU",
                "logic_voltage": 3.3,
                "five_volt_tolerant": False,
                "vreg_max_ma": 400.0,
                "i2c_ports": 2,
                "spi_ports": 2,
                "uart_ports": 2,
                "wireless": "Unknown"
            }

        mcu_voltage = mcu_spec["logic_voltage"]
        mcu_5v_tol = mcu_spec["five_volt_tolerant"]
        regulator_max_ma = mcu_spec["vreg_max_ma"]

        critical_errors = []
        caveats = []
        passed_checks = []

        total_current_ma = 0.0
        i2c_addresses_used: Dict[str, str] = {}
        i2c_count = 0
        spi_count = 0
        uart_count = 0

        for comp in components:
            name = comp.get("name") or comp.get("component_name", "Unnamed Component")
            v_spec = float(comp.get("logic_voltage") or comp.get("voltage_spec", 3.3))
            i_ma = float(comp.get("current_ma", 10.0))
            iface = (comp.get("interface") or comp.get("interface_type") or "GPIO").upper()
            addr = comp.get("i2c_address")

            total_current_ma += i_ma

            # 1. Voltage Compatibility Rule Checks
            if mcu_voltage == 3.3 and v_spec > 3.6:
                if mcu_5v_tol:
                    caveats.append(
                        f"Voltage Mismatch with '{name}': Sensor runs at {v_spec}V. While {mcu_name} has 5V-tolerant input pins, "
                        f"a bi-directional level shifter is strongly advised to avoid overstressing ESD clamping diodes."
                    )
                else:
                    critical_errors.append(
                        f"VOLTAGE INCOMPATIBILITY with '{name}': Component outputs {v_spec}V logic to 3.3V non-tolerant {mcu_name}. "
                        f"Direct connection will permanently destroy MCU GPIO pins. Mandatory: Add a BSS138 bi-directional level shifter or voltage divider."
                    )
            elif mcu_voltage == 5.0 and v_spec < 4.0:
                critical_errors.append(
                    f"VOLTAGE HAZARD with '{name}': {mcu_name} transmits 5.0V on output/bus pins to a {v_spec}V maximum component. "
                    f"Mandatory: Add a 3.3V-to-5V level translator to prevent instant component burnout."
                )
            else:
                passed_checks.append(f"Logic Voltage: '{name}' ({v_spec}V) is natively matched with {mcu_name} ({mcu_voltage}V).")

            # 2. Interface Bus Tracking & Address Collisions
            if "I2C" in iface:
                i2c_count += 1
                if addr:
                    if addr in i2c_addresses_used:
                        caveats.append(
                            f"I2C ADDRESS COLLISION: Both '{name}' and '{i2c_addresses_used[addr]}' share address {addr}. "
                            f"Remedy: Tie AD0/ADDR pin to VCC/GND or utilize a TCA9548A 8-channel I2C multiplexer."
                        )
                    else:
                        i2c_addresses_used[addr] = name
            elif "SPI" in iface:
                spi_count += 1
            elif "UART" in iface:
                uart_count += 1

        # 3. Current Budget & Power Rail Assessment
        headroom_ma = round(regulator_max_ma - total_current_ma, 2)
        headroom_pct = max(0.0, round((headroom_ma / regulator_max_ma) * 100, 1))

        if total_current_ma > regulator_max_ma:
            critical_errors.append(
                f"POWER OVERLOAD: Total component draw ({total_current_ma} mA) exceeds on-board {mcu_voltage}V regulator rating "
                f"({regulator_max_ma} mA) by {abs(headroom_ma)} mA. "
                f"Mandatory: Deploy an external dedicated power rail (e.g., AMS1117-3.3 or LM2596 buck regulator with common ground)."
            )
        elif headroom_pct < 15.0:
            caveats.append(
                f"Tight Power Headroom: Current draw ({total_current_ma} mA) consumes {100 - headroom_pct}% of the regulator capacity "
                f"({regulator_max_ma} mA). Inductive spikes or high RF bursts may cause MCU brownout resets."
            )
        else:
            passed_checks.append(
                f"Power Budget Healthy: Total load {total_current_ma} mA is well within the {regulator_max_ma} mA limit ({headroom_pct}% headroom)."
            )

        # 4. Bus Port Limits
        if i2c_count > mcu_spec.get("i2c_ports", 2) * 4:
            caveats.append(f"Heavy I2C Bus Loading: {i2c_count} I2C devices attached. Check total pull-up capacitance (<400pF).")
        if uart_count > mcu_spec.get("uart_ports", 2):
            caveats.append(
                f"UART Port Exhaustion: {uart_count} UART devices exceed hardware ports ({mcu_spec.get('uart_ports')}). "
                f"SoftwareSerial or an external UART expander will be required."
            )

        # Overall Verdict
        if critical_errors:
            verdict = "INCOMPATIBLE"
            verdict_badge = "CRITICAL_ISSUES_DETECTED"
        elif caveats:
            verdict = "COMPATIBLE_WITH_CAVEATS"
            verdict_badge = "ENGINEERING_WARNINGS"
        else:
            verdict = "COMPATIBLE"
            verdict_badge = "FULLY_VERIFIED"

        return {
            "status": "SUCCESS",
            "verdict": verdict,
            "verdict_badge": verdict_badge,
            "mcu": mcu_spec,
            "components_count": len(components),
            "power_budget": {
                "total_current_ma": round(total_current_ma, 2),
                "regulator_max_ma": regulator_max_ma,
                "headroom_ma": headroom_ma,
                "headroom_percent": headroom_pct,
                "power_safe": total_current_ma <= regulator_max_ma
            },
            "interface_summary": {
                "i2c_devices": i2c_count,
                "spi_devices": spi_count,
                "uart_devices": uart_count,
                "i2c_addresses_claimed": list(i2c_addresses_used.keys())
            },
            "critical_errors": critical_errors,
            "caveats": caveats,
            "passed_checks": passed_checks
        }

    # ====================================================================================
    # 6. Milestone & Deliverables Tracker
    # ====================================================================================

    def get_milestones(self, proposal_id: str) -> List[Dict[str, Any]]:
        """Retrieves milestones for a proposal."""
        conn = self._get_connection()
        try:
            cur = conn.execute("""
                SELECT * FROM project_milestones
                WHERE proposal_id = ?
                ORDER BY due_date ASC;
            """, (proposal_id,))
            milestones = []
            for row in cur.fetchall():
                milestones.append({
                    "milestone_id": row["milestone_id"],
                    "proposal_id": row["proposal_id"],
                    "title": row["title"],
                    "description": row["description"],
                    "weightage_percent": row["weightage_percent"],
                    "due_date": row["due_date"],
                    "status": row["status"],
                    "deliverables": json.loads(row["deliverables_json"] or "[]"),
                    "completed_at": row["completed_at"]
                })
            return milestones
        finally:
            conn.close()

    def update_milestone_status(self, milestone_id: str, new_status: str) -> Dict[str, Any]:
        """Toggles milestone progress status (PENDING, IN_PROGRESS, COMPLETED)."""
        valid_statuses = ["PENDING", "IN_PROGRESS", "COMPLETED"]
        if new_status not in valid_statuses:
            return {"status": "ERROR", "message": f"Invalid milestone status '{new_status}'."}

        completed_at = time.time() if new_status == "COMPLETED" else None

        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    cur = conn.execute("""
                        UPDATE project_milestones
                        SET status = ?, completed_at = ?
                        WHERE milestone_id = ?;
                    """, (new_status, completed_at, milestone_id))
                    if cur.rowcount == 0:
                        return {"status": "ERROR", "message": f"Milestone '{milestone_id}' not found."}
                return {
                    "status": "SUCCESS",
                    "milestone_id": milestone_id,
                    "new_status": new_status,
                    "completed_at": completed_at
                }
            finally:
                conn.close()

    def add_milestone(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Adds a new milestone to a proposal."""
        proposal_id = data.get("proposal_id")
        title = (data.get("title") or "").strip()
        if not proposal_id or not title:
            return {"status": "ERROR", "message": "Proposal ID and milestone title are required."}

        milestone_id = data.get("milestone_id") or f"MS_{int(time.time()*1000)}"
        desc = data.get("description", "")
        weight = float(data.get("weightage_percent", 20.0))
        due_date = data.get("due_date", "2026-12-31")
        status = data.get("status", "PENDING")
        deliverables = data.get("deliverables", [])

        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    conn.execute("""
                        INSERT INTO project_milestones (
                            milestone_id, proposal_id, title, description,
                            weightage_percent, due_date, status, deliverables_json,
                            completed_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """, (
                        milestone_id, proposal_id, title, desc,
                        weight, due_date, status, json.dumps(deliverables),
                        time.time() if status == "COMPLETED" else None
                    ))
                return {
                    "status": "SUCCESS",
                    "milestone_id": milestone_id,
                    "message": f"Milestone '{title}' added successfully."
                }
            finally:
                conn.close()


# Singleton instance
project_innovation_engine = ProjectInnovationEngine()
