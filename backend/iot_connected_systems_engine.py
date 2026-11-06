"""
========================================================================================
VoltCore Apex Academia - Phase G: IoT & Connected Systems (Features 271–280)
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Features:
  - Feature 271: IoT Architecture Diagram Builder (Perception, Edge, Network, Cloud, App)
  - Feature 272: MQTT Message Structure Explorer (Fixed/Variable Headers, QoS 0/1/2 Handshakes)
  - Feature 273: Sensor Data Dashboard with Anomaly Detection (Z-Score & Thresholds)
  - Feature 274: IoT Device Registry (ESP32, STM32-LoRa, RP2040, nRF52 Inventory)
  - Feature 275: Virtual Sensor Calibration Tool (2-Point Linear, Temp Compensation)
  - Feature 276: MQTT Topic Structure Designer (Hierarchical Paths & Wildcard Matcher)
  - Feature 277: IoT Packet History Ledger (CONNECT, PUBLISH, SUBSCRIBE, RSSI, SNR)
  - Feature 278: Device Status Timeline Generator (Boot, Wi-Fi, MQTT Handshake, Sleep)
  - Feature 279: Smart Home / Industrial Automation Rule Engine (IF-THEN Trigger Engine)
  - Feature 280: IoT Network Topology Visualizer & Link Budget (Star, Mesh, Path Loss)
Hardware Safe: Zero background polling loops, SQLite WAL mode, passive CPU footprint.
========================================================================================
"""

import os
import math
import json
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_telemetry.db")

# Standard 5-Tier IoT Architecture Model (Feature 271)
IOT_ARCHITECTURE_TIERS: List[Dict[str, Any]] = [
    {
        "tier_id": 1,
        "name": "Perception Layer",
        "tamil_name": "உணர்வி அடுக்கு (சென்சார்கள்)",
        "role": "Physical signal acquisition & actuation",
        "protocols": ["I2C", "SPI", "UART", "1-Wire", "GPIO", "ADC"],
        "hardware": ["BME280 (Temp/Hum/Press)", "MPU6050 (IMU)", "MQ-135 (Air Quality)", "Solid-State Relay"],
        "color": "emerald"
    },
    {
        "tier_id": 2,
        "name": "Edge / Gateway Layer",
        "tamil_name": "எட்ஜ் / கேட்வே அடுக்கு",
        "role": "Local aggregation, protocol translation & edge filtering",
        "protocols": ["ESP-NOW", "Modbus-RTU", "BLE Mesh", "CAN Bus"],
        "hardware": ["ESP32-S3 Edge Gateway", "Raspberry Pi 4 CM4", "STM32F4 Gateway"],
        "color": "cyan"
    },
    {
        "tier_id": 3,
        "name": "Network & Transport Layer",
        "tamil_name": "நெட்வொர்க் மற்றும் பரிமாற்ற அடுக்கு",
        "role": "Long-range and local wireless telemetry data routing",
        "protocols": ["Wi-Fi (802.11 b/g/n)", "LoRaWAN (865-867 MHz IN865)", "NB-IoT", "ZigBee (802.15.4)"],
        "hardware": ["SX1276 LoRa Transceiver", "SIM7080G Cellular Modem", "CC2530 ZigBee"],
        "color": "indigo"
    },
    {
        "tier_id": 4,
        "name": "Middleware & Cloud Broker Layer",
        "tamil_name": "கிளவுட் தரவுத்தரகர் அடுக்கு",
        "role": "Message brokering, queuing, time-series storage & analytics",
        "protocols": ["MQTT 3.1.1/5.0", "CoAP", "HTTP/2 REST", "WebSockets"],
        "hardware": ["Mosquitto MQTT Broker", "SQLite WAL Telemetry Store", "EMQX Enterprise Cluster"],
        "color": "purple"
    },
    {
        "tier_id": 5,
        "name": "Application & Business Layer",
        "tamil_name": "பயன்பாட்டு மற்றும் முடிவெடுக்கும் அடுக்கு",
        "role": "User dashboards, automation rule firing, alerts & predictive maintenance",
        "protocols": ["HTTPS", "WSS", "WebPush", "SMTP", "SMS Webhook"],
        "hardware": ["VoltCore Apex Dashboard", "Grafana Panels", "Automated Relays"],
        "color": "amber"
    }
]


class IoTConnectedSystemsEngine:
    """
    Backend computational & simulation engine for Phase G (Features 271–280):
    - Multi-tier IoT architecture validation & topology planning
    - MQTT packet encoding/decoding, binary header & QoS handshake flows
    - Sensor data generation, statistics & Z-score anomaly detection
    - Device registry inventory management with SQLite WAL persistence
    - Two-point linear & temperature-compensated sensor calibration
    - Hierarchical MQTT topic validation & '+' / '#' wildcard matching
    - Telemetry packet logging and historical query engine
    - Node lifecycle state timeline generation
    - Conditional IF-THEN automation rule engine
    - RF link budget, free-space path loss & RSSI calculations
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_db(self) -> None:
        with self._lock:
            conn = self._get_connection()
            try:
                # 1. IoT Device Registry
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS iot_device_registry (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        node_id TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        platform TEXT NOT NULL,
                        mac_address TEXT NOT NULL,
                        ip_address TEXT NOT NULL,
                        firmware_version TEXT NOT NULL,
                        status TEXT NOT NULL,
                        battery_percent INTEGER NOT NULL,
                        created_at TEXT NOT NULL,
                        last_seen TEXT NOT NULL
                    );
                """)

                # 2. IoT Telemetry Packets Ledger
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS iot_telemetry_packets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        node_id TEXT NOT NULL,
                        topic TEXT NOT NULL,
                        packet_type TEXT NOT NULL,
                        qos INTEGER NOT NULL,
                        payload TEXT NOT NULL,
                        rssi_dbm REAL NOT NULL,
                        snr_db REAL NOT NULL,
                        created_at TEXT NOT NULL
                    );
                """)

                # 3. Smart Automation Rules Ledger
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS automation_rules (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id TEXT NOT NULL,
                        rule_name TEXT NOT NULL,
                        metric TEXT NOT NULL,
                        operator TEXT NOT NULL,
                        threshold REAL NOT NULL,
                        action_type TEXT NOT NULL,
                        target_device TEXT NOT NULL,
                        is_enabled INTEGER NOT NULL DEFAULT 1,
                        created_at TEXT NOT NULL
                    );
                """)

                # Seed demo records if registry is empty
                cur = conn.execute("SELECT id FROM iot_device_registry LIMIT 1")
                if not cur.fetchone():
                    now = datetime.now(timezone.utc).isoformat()
                    demo_devices = [
                        ("NODE-MIT-LAB304-01", "Ambient Environmental Node", "ESP32-WROOM-32", "24:6F:28:1A:BC:01", "192.168.1.101", "v2.4.1", "ONLINE", 98, now, now),
                        ("NODE-MIT-LAB304-02", "Precision Vibration Sensor", "STM32F4-LORA", "00:80:E1:15:2B:02", "192.168.1.102", "v1.9.0", "ONLINE", 85, now, now),
                        ("NODE-MIT-ROOF-03", "Solar Micro-Weather Station", "RP2040-WIFI", "D8:3A:DD:C4:4E:03", "192.168.1.103", "v2.1.0", "SLEEPING", 72, now, now),
                        ("NODE-MIT-SMART-04", "Industrial Relay Controller", "ESP32-S3", "30:AE:A4:07:9F:04", "192.168.1.104", "v3.0.2", "ONLINE", 100, now, now)
                    ]
                    for d in demo_devices:
                        conn.execute("""
                            INSERT INTO iot_device_registry (
                                node_id, name, platform, mac_address, ip_address, firmware_version, status, battery_percent, created_at, last_seen
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, d)

                    # Seed demo telemetry packets
                    demo_packets = [
                        ("NODE-MIT-LAB304-01", "voltcore/mit/ece/lab304/node01/ambient", "PUBLISH", 1, json.dumps({"temp": 26.4, "humidity": 58.2, "pressure": 1013.2}), -62.0, 9.5, now),
                        ("NODE-MIT-LAB304-02", "voltcore/mit/ece/lab304/node02/vibration", "PUBLISH", 2, json.dumps({"accel_g": 0.04, "freq_hz": 120.0}), -55.0, 11.2, now),
                        ("NODE-MIT-ROOF-03", "voltcore/mit/ece/roof/node03/weather", "PUBLISH", 0, json.dumps({"temp": 32.1, "lux": 85000, "wind_speed": 4.2}), -78.0, 6.1, now)
                    ]
                    for p in demo_packets:
                        conn.execute("""
                            INSERT INTO iot_telemetry_packets (
                                node_id, topic, packet_type, qos, payload, rssi_dbm, snr_db, created_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, p)

                    # Seed demo automation rule
                    conn.execute("""
                        INSERT INTO automation_rules (
                            student_id, rule_name, metric, operator, threshold, action_type, target_device, is_enabled, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, ("2023MITEC042", "High Temperature Lab Vent", "temperature", ">", 32.0, "RELAY_CONTROL", "NODE-MIT-SMART-04", 1, now))

                conn.commit()
            finally:
                conn.close()

    # =========================================================================
    # Feature 271: IoT Architecture Tier Model
    # =========================================================================
    def get_architecture_tiers(self) -> List[Dict[str, Any]]:
        """Returns the 5 standard layers of the IoT Connected Systems Architecture."""
        return IOT_ARCHITECTURE_TIERS

    # =========================================================================
    # Feature 272: MQTT Message Structure & Handshake Protocol Explorer
    # =========================================================================
    def parse_mqtt_packet(
        self,
        packet_type: str = "PUBLISH",
        topic: str = "voltcore/mit/ece/lab304/node01/temperature",
        qos: int = 1,
        retain: int = 0,
        payload_data: Optional[Dict[str, Any]] = None,
        packet_id: int = 1042
    ) -> Dict[str, Any]:
        """
        Synthesizes and breaks down an MQTT 3.1.1 protocol packet:
        - Fixed header byte 1: [Packet Type (4 bits) | DUP (1 bit) | QoS (2 bits) | RETAIN (1 bit)]
        - Remaining length byte(s)
        - Variable header: Topic length + Topic string + Packet Identifier (if QoS > 0)
        - Payload: Encoded JSON payload
        - Complete hex byte sequence and QoS handshake sequence steps
        """
        type_codes = {
            "CONNECT": 1, "CONNACK": 2, "PUBLISH": 3, "PUBACK": 4,
            "PUBREC": 5, "PUBREL": 6, "PUBCOMP": 7, "SUBSCRIBE": 8,
            "SUBACK": 9, "PINGREQ": 12, "PINGRESP": 13, "DISCONNECT": 14
        }
        pt_upper = packet_type.upper()
        code = type_codes.get(pt_upper, 3)

        qos_safe = max(0, min(2, int(qos)))
        retain_safe = 1 if retain else 0
        dup_safe = 0

        # Fixed Header Byte 1
        fixed_header_byte1 = (code << 4) | (dup_safe << 3) | (qos_safe << 1) | retain_safe

        # Variable Header
        topic_bytes = topic.encode("utf-8")
        topic_len = len(topic_bytes)

        var_header_bytes = bytearray()
        if pt_upper == "PUBLISH":
            # Topic length (2 bytes MSB-LSB) + Topic bytes
            var_header_bytes.extend([(topic_len >> 8) & 0xFF, topic_len & 0xFF])
            var_header_bytes.extend(topic_bytes)
            # Packet ID required for QoS 1 and 2
            if qos_safe > 0:
                var_header_bytes.extend([(packet_id >> 8) & 0xFF, packet_id & 0xFF])
        elif pt_upper == "PUBACK":
            var_header_bytes.extend([(packet_id >> 8) & 0xFF, packet_id & 0xFF])

        # Payload
        payload_dict = payload_data or {"temp": 28.5, "unit": "C", "ts": 1730900000}
        payload_bytes = json.dumps(payload_dict).encode("utf-8")

        remaining_length = len(var_header_bytes) + len(payload_bytes)

        # Variable byte length encoding for remaining length
        rem_len_bytes = bytearray()
        val = remaining_length
        while True:
            digit = val % 128
            val //= 128
            if val > 0:
                digit |= 0x80
            rem_len_bytes.append(digit)
            if val <= 0:
                break

        # Assemble Full Packet
        full_packet = bytearray([fixed_header_byte1])
        full_packet.extend(rem_len_bytes)
        full_packet.extend(var_header_bytes)
        full_packet.extend(payload_bytes)

        # Handshake sequence explanation based on QoS
        handshake_flows = {
            0: [
                {"step": 1, "from": "Client (Node)", "to": "Broker", "packet": "PUBLISH (QoS 0)", "guarantee": "At most once (Fire & Forget, No ACK)"}
            ],
            1: [
                {"step": 1, "from": "Client (Node)", "to": "Broker", "packet": f"PUBLISH (QoS 1, PacketID={packet_id})", "guarantee": "At least once"},
                {"step": 2, "from": "Broker", "to": "Client (Node)", "packet": f"PUBACK (PacketID={packet_id})", "guarantee": "Acknowledgment confirmed"}
            ],
            2: [
                {"step": 1, "from": "Client (Node)", "to": "Broker", "packet": f"PUBLISH (QoS 2, PacketID={packet_id})", "guarantee": "Exactly once initiation"},
                {"step": 2, "from": "Broker", "to": "Client (Node)", "packet": f"PUBREC (PacketID={packet_id})", "guarantee": "Publish received & held"},
                {"step": 3, "from": "Client (Node)", "to": "Broker", "packet": f"PUBREL (PacketID={packet_id})", "guarantee": "Publish release authorized"},
                {"step": 4, "from": "Broker", "to": "Client (Node)", "packet": f"PUBCOMP (PacketID={packet_id})", "guarantee": "Publish complete (4-way handshake)"}
            ]
        }

        return {
            "packet_type": pt_upper,
            "type_code": code,
            "qos": qos_safe,
            "retain": retain_safe,
            "remaining_length": remaining_length,
            "fixed_header_hex": f"0x{fixed_header_byte1:02X}",
            "full_packet_hex": full_packet.hex().upper(),
            "packet_size_bytes": len(full_packet),
            "handshake_steps": handshake_flows[qos_safe]
        }

    # =========================================================================
    # Feature 273: Sensor Data Dashboard & Z-Score Anomaly Detection
    # =========================================================================
    def analyze_sensor_telemetry(
        self,
        samples: List[float],
        metric_name: str = "Temperature",
        unit: str = "°C",
        upper_limit: float = 40.0,
        lower_limit: float = 10.0
    ) -> Dict[str, Any]:
        """
        Computes mean, standard deviation, and Z-scores for real-time telemetry stream.
        Identifies outliers (|Z| > 2.0 or threshold excursions).
        Z = (x - mean) / std_dev
        """
        if not samples:
            return {"error": "Sample list cannot be empty."}

        n = len(samples)
        mean_val = sum(samples) / n
        variance = sum((x - mean_val) ** 2 for x in samples) / (n - 1) if n > 1 else 0.0
        std_dev = math.sqrt(variance)

        anomalies = []
        z_scores = []
        for i, val in enumerate(samples):
            z = (val - mean_val) / std_dev if std_dev > 0 else 0.0
            z_scores.append(round(z, 2))
            is_z_anomaly = abs(z) > 2.0
            is_limit_anomaly = (val > upper_limit) or (val < lower_limit)
            if is_z_anomaly or is_limit_anomaly:
                anomalies.append({
                    "sample_index": i,
                    "value": val,
                    "z_score": round(z, 2),
                    "reason": "Z-score > 2.0 (Statistical Outlier)" if is_z_anomaly else "Threshold Boundary Violation"
                })

        return {
            "metric_name": metric_name,
            "unit": unit,
            "sample_count": n,
            "mean": round(mean_val, 2),
            "std_dev": round(std_dev, 3),
            "min_val": round(min(samples), 2),
            "max_val": round(max(samples), 2),
            "anomaly_count": len(anomalies),
            "anomaly_rate_percent": round((len(anomalies) / n) * 100.0, 1),
            "anomalies": anomalies,
            "z_scores": z_scores
        }

    # =========================================================================
    # Feature 274: IoT Device Registry Management
    # =========================================================================
    def register_device(
        self,
        node_id: str,
        name: str,
        platform: str,
        mac_address: str,
        ip_address: str,
        firmware_version: str = "v1.0.0",
        status: str = "ONLINE",
        battery_percent: int = 100
    ) -> int:
        """Adds or registers a new IoT hardware node in SQLite WAL."""
        with self._lock:
            conn = self._get_connection()
            try:
                now = datetime.now(timezone.utc).isoformat()
                cur = conn.execute("""
                    INSERT INTO iot_device_registry (
                        node_id, name, platform, mac_address, ip_address, firmware_version, status, battery_percent, created_at, last_seen
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(node_id) DO UPDATE SET
                        name=excluded.name,
                        platform=excluded.platform,
                        ip_address=excluded.ip_address,
                        status=excluded.status,
                        battery_percent=excluded.battery_percent,
                        last_seen=excluded.last_seen;
                """, (node_id, name, platform, mac_address, ip_address, firmware_version, status, battery_percent, now, now))
                conn.commit()
                return cur.lastrowid
            finally:
                conn.close()

    def list_devices(self) -> List[Dict[str, Any]]:
        """Retrieves all registered edge IoT devices."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.execute("SELECT * FROM iot_device_registry ORDER BY id ASC")
                return [dict(r) for r in cur.fetchall()]
            finally:
                conn.close()

    def get_device(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves single device details by node_id."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.execute("SELECT * FROM iot_device_registry WHERE node_id = ?", (node_id,))
                row = cur.fetchone()
                return dict(row) if row else None
            finally:
                conn.close()

    # =========================================================================
    # Feature 275: Virtual Sensor Calibration Tool
    # =========================================================================
    def calibrate_sensor_reading(
        self,
        raw_val: float,
        p1_raw: float,
        p1_ref: float,
        p2_raw: float,
        p2_ref: float,
        ambient_temp_c: float = 25.0,
        temp_coeff_per_deg_c: float = 0.002,
        ref_temp_c: float = 25.0
    ) -> Dict[str, Any]:
        """
        Applies 2-point linear gain/offset calibration with optional temperature drift compensation.
        y = m * x + c
        Temp compensation: y_comp = y * [1 - alpha * (T_ambient - T_ref)]
        """
        if p2_raw == p1_raw:
            raise ValueError("Calibration raw reference points p1_raw and p2_raw cannot be identical.")

        slope_m = (p2_ref - p1_ref) / (p2_raw - p1_raw)
        offset_c = p1_ref - (slope_m * p1_raw)

        calibrated_linear = (slope_m * raw_val) + offset_c

        # Temperature drift compensation
        temp_delta = ambient_temp_c - ref_temp_c
        temp_comp_factor = 1.0 - (temp_coeff_per_deg_c * temp_delta)
        calibrated_final = calibrated_linear * temp_comp_factor

        offset_error = raw_val - calibrated_final

        return {
            "raw_input": raw_val,
            "slope_m": round(slope_m, 5),
            "offset_c": round(offset_c, 5),
            "calibrated_linear": round(calibrated_linear, 3),
            "ambient_temp_c": ambient_temp_c,
            "temp_comp_factor": round(temp_comp_factor, 5),
            "calibrated_final": round(calibrated_final, 3),
            "offset_error": round(offset_error, 3)
        }

    # =========================================================================
    # Feature 276: MQTT Topic Structure Designer & Wildcard Matcher
    # =========================================================================
    def match_mqtt_topic(self, filter_pattern: str, topic: str) -> Dict[str, Any]:
        """
        Evaluates whether an MQTT topic matches a subscription pattern with '+' and '#' wildcards.
        - '+' matches exactly ONE level
        - '#' matches ZERO or MORE remaining levels (must be at the end)
        """
        filter_parts = filter_pattern.strip("/").split("/")
        topic_parts = topic.strip("/").split("/")

        matched = True
        i = 0
        while i < len(filter_parts):
            f = filter_parts[i]
            if f == "#":
                # '#' at end matches everything remaining
                matched = True
                break
            if i >= len(topic_parts):
                matched = False
                break
            if f != "+" and f != topic_parts[i]:
                matched = False
                break
            i += 1

        if matched and filter_parts[-1] != "#" and len(filter_parts) != len(topic_parts):
            matched = False

        return {
            "filter_pattern": filter_pattern,
            "actual_topic": topic,
            "is_matched": matched,
            "filter_levels": len(filter_parts),
            "topic_levels": len(topic_parts)
        }

    # =========================================================================
    # Feature 277: IoT Packet History Ledger
    # =========================================================================
    def record_packet(
        self,
        node_id: str,
        topic: str,
        packet_type: str,
        qos: int,
        payload: Dict[str, Any],
        rssi_dbm: float = -65.0,
        snr_db: float = 9.0
    ) -> int:
        """Stores an inbound or outbound IoT packet in the SQLite WAL ledger."""
        with self._lock:
            conn = self._get_connection()
            try:
                now = datetime.now(timezone.utc).isoformat()
                cur = conn.execute("""
                    INSERT INTO iot_telemetry_packets (
                        node_id, topic, packet_type, qos, payload, rssi_dbm, snr_db, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (node_id, topic, packet_type, qos, json.dumps(payload), rssi_dbm, snr_db, now))
                conn.commit()
                return cur.lastrowid
            finally:
                conn.close()

    def get_packet_history(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Retrieves recent telemetry packets."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.execute("""
                    SELECT id, node_id, topic, packet_type, qos, payload, rssi_dbm, snr_db, created_at
                    FROM iot_telemetry_packets
                    ORDER BY id DESC
                    LIMIT ?
                """, (limit,))
                rows = cur.fetchall()
                results = []
                for r in rows:
                    results.append({
                        "id": r["id"],
                        "node_id": r["node_id"],
                        "topic": r["topic"],
                        "packet_type": r["packet_type"],
                        "qos": r["qos"],
                        "payload": json.loads(r["payload"]),
                        "rssi_dbm": r["rssi_dbm"],
                        "snr_db": r["snr_db"],
                        "created_at": r["created_at"]
                    })
                return results
            finally:
                conn.close()

    # =========================================================================
    # Feature 278: Device Status Timeline Generator
    # =========================================================================
    def generate_device_timeline(self, node_id: str) -> List[Dict[str, Any]]:
        """Synthesizes chronological lifecycle state transitions for a node."""
        events = [
            {"time_offset_s": 0.0, "state": "POWER_ON", "event": "Cold boot via POR (Power-on Reset)", "status": "INFO"},
            {"time_offset_s": 0.45, "state": "WIFI_CONNECTING", "event": "Associating with AP SSID 'MIT_ECE_IoT_LAB'", "status": "PROGRESS"},
            {"time_offset_s": 1.82, "state": "WIFI_CONNECTED", "event": "DHCP IP Acquired: 192.168.1.101 (RSSI -62 dBm)", "status": "SUCCESS"},
            {"time_offset_s": 2.10, "state": "MQTT_CONNECTING", "event": "Initiating TLS MQTT handshake to broker:1883", "status": "PROGRESS"},
            {"time_offset_s": 2.38, "state": "MQTT_CONNECTED", "event": "CONNACK received (Return Code 0: Accepted)", "status": "SUCCESS"},
            {"time_offset_s": 2.50, "state": "TELEMETRY_PUB", "event": "Published BME280 telemetry (QoS 1, PacketID=1)", "status": "SUCCESS"},
            {"time_offset_s": 2.58, "state": "PUBACK_RECV", "event": "PUBACK acknowledged by broker in 80ms", "status": "SUCCESS"},
            {"time_offset_s": 3.00, "state": "DEEP_SLEEP_ENTER", "event": "Entering RTC Deep Sleep (Wake timer: 60s)", "status": "SLEEP"}
        ]
        return events

    # =========================================================================
    # Feature 279: Smart Home & Industrial Automation Rule Engine
    # =========================================================================
    def evaluate_automation_rule(
        self,
        rule_name: str,
        metric: str,
        operator: str,
        threshold: float,
        current_val: float,
        action_type: str = "RELAY_CONTROL",
        target_device: str = "NODE-MIT-SMART-04"
    ) -> Dict[str, Any]:
        """
        Evaluates conditional IF-THEN trigger:
        e.g. IF temperature > 32.0 THEN trigger RELAY_FAN = ON on NODE-MIT-SMART-04.
        """
        ops = {
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b
        }
        op_fn = ops.get(operator, ops[">"])
        triggered = bool(op_fn(current_val, threshold))

        action_payload = {}
        if triggered:
            action_payload = {
                "action": action_type,
                "target": target_device,
                "state": "ACTIVE",
                "triggered_by": f"{metric} ({current_val}) {operator} threshold ({threshold})"
            }

        return {
            "rule_name": rule_name,
            "metric": metric,
            "operator": operator,
            "threshold": threshold,
            "current_value": current_val,
            "is_triggered": triggered,
            "action_type": action_type,
            "target_device": target_device,
            "action_payload": action_payload
        }

    def save_automation_rule(
        self,
        student_id: str,
        rule_name: str,
        metric: str,
        operator: str,
        threshold: float,
        action_type: str,
        target_device: str,
        is_enabled: int = 1
    ) -> int:
        """Saves a custom automation rule to SQLite WAL."""
        with self._lock:
            conn = self._get_connection()
            try:
                now = datetime.now(timezone.utc).isoformat()
                cur = conn.execute("""
                    INSERT INTO automation_rules (
                        student_id, rule_name, metric, operator, threshold, action_type, target_device, is_enabled, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (student_id, rule_name, metric, operator, threshold, action_type, target_device, is_enabled, now))
                conn.commit()
                return cur.lastrowid
            finally:
                conn.close()

    def get_automation_rules(self, student_id: str) -> List[Dict[str, Any]]:
        """Retrieves rules for student."""
        with self._lock:
            conn = self._get_connection()
            try:
                cur = conn.execute("SELECT * FROM automation_rules WHERE student_id = ? ORDER BY id DESC", (student_id,))
                return [dict(r) for r in cur.fetchall()]
            finally:
                conn.close()

    # =========================================================================
    # Feature 280: IoT Network Topology & Link Budget Calculator
    # =========================================================================
    def calculate_rf_link_budget(
        self,
        distance_meters: float,
        freq_mhz: float = 2400.0,
        tx_power_dbm: float = 14.0,
        tx_antenna_gain_dbi: float = 2.0,
        rx_antenna_gain_dbi: float = 2.0,
        rx_sensitivity_dbm: float = -95.0
    ) -> Dict[str, Any]:
        """
        Calculates Free-Space Path Loss (FSPL) and RF Link Margin:
        FSPL (dB) = 20*log10(d) + 20*log10(f_MHz) - 27.55
        RSSI = Tx_Power + Tx_Gain + Rx_Gain - FSPL
        Link Margin = RSSI - Rx_Sensitivity
        """
        if distance_meters <= 0 or freq_mhz <= 0:
            raise ValueError("Distance and frequency must be strictly positive.")

        # Free space path loss standard formula with distance in meters and freq in MHz:
        # FSPL = 20*log10(d_m) + 20*log10(f_MHz) - 27.55
        fspl_db = 20.0 * math.log10(distance_meters) + 20.0 * math.log10(freq_mhz) - 27.55
        rssi_dbm = tx_power_dbm + tx_antenna_gain_dbi + rx_antenna_gain_dbi - fspl_db
        link_margin_db = rssi_dbm - rx_sensitivity_dbm

        link_quality = (
            "EXCELLENT" if link_margin_db >= 20.0
            else "GOOD" if link_margin_db >= 10.0
            else "MARGINAL" if link_margin_db >= 0.0
            else "UNREACHABLE"
        )

        return {
            "distance_meters": distance_meters,
            "freq_mhz": freq_mhz,
            "tx_power_dbm": tx_power_dbm,
            "fspl_db": round(fspl_db, 2),
            "rssi_dbm": round(rssi_dbm, 2),
            "rx_sensitivity_dbm": rx_sensitivity_dbm,
            "link_margin_db": round(link_margin_db, 2),
            "link_quality": link_quality,
            "is_link_viable": link_margin_db >= 0.0
        }
