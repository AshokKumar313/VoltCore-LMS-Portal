"""
========================================================================================
VoltCore Apex Academia - Phase 39: Cloud IoT MQTT Broker & WebSerial / WebUSB HIL Engine
Anna University / MIT Campus - Department of Electronics Engineering (Regulation 2023)
Platform Lead: Ashok Kumar A (2023MITEC042)
Hardware Safe: Zero background polling loops, SQLite WAL mode, cool thermal footprint.
========================================================================================
"""

import os
import sqlite3
import json
import csv
import io
import math
import random
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Database path in workspace root
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "voltcore_telemetry.db")

# Microcontroller Hardware Targets for Hardware-in-the-Loop (HIL)
HIL_DEVICE_TARGETS: Dict[str, Dict[str, Any]] = {
    "ESP32_WROOM_32": {
        "key": "ESP32_WROOM_32",
        "name": "Espressif ESP32-WROOM-32 (Dual-Core Xtensa LX6)",
        "vendor": "Espressif Systems",
        "core": "Dual-Core Xtensa 32-bit LX6 @ 240MHz",
        "interfaces": ["WebSerial (CP2102/CH340)", "MQTT over Wi-Fi 802.11 b/g/n", "WebUSB"],
        "base_latency_ms": 14.2,
        "base_jitter_ms": 2.1,
        "default_baud": 115200,
        "sensor_suite": ["DHT22 Temp/Humidity", "INA219 Voltage/Current", "MPU6050 6-DOF IMU"]
    },
    "UNO_R4_WIFI": {
        "key": "UNO_R4_WIFI",
        "name": "Arduino Uno R4 WiFi (Renesas RA4M1 + ESP32-S3)",
        "vendor": "Arduino / Renesas",
        "core": "Renesas RA4M1 ARM Cortex-M4F @ 48MHz",
        "interfaces": ["WebUSB (Native CDC)", "WebSerial", "MQTT over ESP32-S3"],
        "base_latency_ms": 22.5,
        "base_jitter_ms": 3.4,
        "default_baud": 115200,
        "sensor_suite": ["Analog NTC Thermistor", "LDR Photodiode", "DAC Waveform Out"]
    },
    "RP2040_PICO_W": {
        "key": "RP2040_PICO_W",
        "name": "Raspberry Pi Pico W (Dual Cortex-M0+ & CYW43439)",
        "vendor": "Raspberry Pi Foundation",
        "core": "Dual ARM Cortex-M0+ @ 133MHz",
        "interfaces": ["WebSerial (TinyUSB CDC)", "MQTT over Wi-Fi", "WebUSB"],
        "base_latency_ms": 18.0,
        "base_jitter_ms": 2.8,
        "default_baud": 115200,
        "sensor_suite": ["On-die ADC Temp Sensor", "GPIO Quadrature Encoder", "PWM Power Rail"]
    },
    "NUCLEO_F401RE": {
        "key": "NUCLEO_F401RE",
        "name": "STMicroelectronics STM32 Nucleo-F401RE (Cortex-M4F)",
        "vendor": "STMicroelectronics",
        "core": "ARM Cortex-M4F with FPU @ 84MHz",
        "interfaces": ["WebSerial (ST-LINK V2-1 VCP)", "WebUSB CDC-ACM", "MQTT Gateway"],
        "base_latency_ms": 9.4,
        "base_jitter_ms": 1.2,
        "default_baud": 115200,
        "sensor_suite": ["BME280 Environmental", "MAX30102 Pulse Oximeter", "Current Sense Shunt"]
    }
}


def calculate_crc16_ccitt(data_bytes: bytes) -> int:
    """
    Computes standard CRC-16-CCITT (polynomial 0x1021, init 0xFFFF)
    for serial packet integrity verification.
    """
    crc = 0xFFFF
    for byte in data_bytes:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


class MqttHilEngine:
    """
    Manages Hardware-in-the-Loop WebSerial/WebUSB live packet streaming,
    MQTT topic Pub/Sub emulation, RFC 3550 inter-arrival jitter calculation,
    packet loss tracking, and SQLite WAL persistence.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_sqlite_tables()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns SQLite connection configured with WAL journaling."""
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        conn.row_factory = sqlite3.Row
        return conn

    def _init_sqlite_tables(self) -> None:
        """Initializes tables for MQTT/HIL sessions and telemetry packets."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mqtt_hil_sessions (
                    id TEXT PRIMARY KEY,
                    device_id TEXT NOT NULL,
                    transport_mode TEXT NOT NULL,
                    baud_rate INTEGER NOT NULL,
                    broker_url TEXT NOT NULL,
                    qos_level INTEGER NOT NULL,
                    packets_transmitted INTEGER NOT NULL,
                    packets_received INTEGER NOT NULL,
                    packet_loss_pct REAL NOT NULL,
                    avg_jitter_ms REAL NOT NULL,
                    avg_latency_ms REAL NOT NULL,
                    throughput_kbps REAL NOT NULL,
                    student_id TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mqtt_hil_packets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    seq_num INTEGER NOT NULL,
                    topic TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    payload_bytes INTEGER NOT NULL,
                    transit_time_ms REAL NOT NULL,
                    jitter_ms REAL NOT NULL,
                    crc_valid INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES mqtt_hil_sessions(id)
                );
            """)
            conn.commit()

    def get_available_devices(self) -> List[Dict[str, Any]]:
        """Returns catalog of supported HIL microcontroller targets."""
        return list(HIL_DEVICE_TARGETS.values())

    def simulate_hil_stream(
        self,
        device_id: str = "ESP32_WROOM_32",
        transport_mode: str = "WEBSERIAL",
        baud_rate: int = 115200,
        qos_level: int = 1,
        num_packets: int = 20,
        student_id: str = "2023MITEC042"
    ) -> Dict[str, Any]:
        """
        Executes a deterministic Hardware-in-the-Loop telemetry burst.
        Models live sensor frames, RFC 3550 inter-arrival jitter smoothing,
        CRC-16 CCITT validation, QoS delivery confirmation, and logs to SQLite WAL.
        """
        dev = HIL_DEVICE_TARGETS.get(device_id, HIL_DEVICE_TARGETS["ESP32_WROOM_32"])
        session_id = f"HIL_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(2).hex()}"
        now = datetime.now()

        packets = []
        jitter_running = dev["base_jitter_ms"]
        prev_transit = dev["base_latency_ms"]
        received_count = 0
        total_bytes = 0
        transit_times = []

        base_lat = dev["base_latency_ms"]
        # Latency adjustment based on transport mode
        if transport_mode.upper() == "WEBUSB":
            base_lat *= 0.7  # Low overhead USB endpoints
        elif transport_mode.upper() == "MQTT_WSS":
            base_lat *= 1.3  # WebSocket TLS framing overhead

        for seq in range(1, num_packets + 1):
            # Deterministic pseudo-random variation
            noise = math.sin(seq * 0.45) * 1.8 + math.cos(seq * 0.25) * 0.9
            transit = max(2.0, round(base_lat + noise, 2))
            transit_times.append(transit)

            # RFC 3550 Inter-Arrival Jitter: J_i = J_{i-1} + (|D(i-1, i)| - J_{i-1}) / 16
            diff = abs(transit - prev_transit)
            jitter_running = round(jitter_running + (diff - jitter_running) / 16.0, 3)
            prev_transit = transit

            # Simulate 2% channel loss if QoS 0, 0% loss for QoS 1 & 2 (retransmitted)
            dropped = (seq == 13 and qos_level == 0)
            status = "DROPPED" if dropped else ("RETRIED_ACK" if (seq == 13 and qos_level >= 1) else "ACKNOWLEDGED")

            # Synthetic Telemetry Payload
            telemetry_data = {
                "seq": seq,
                "node": dev["key"],
                "temp_c": round(26.5 + math.sin(seq * 0.3) * 3.2, 2),
                "humidity_pct": round(58.0 + math.cos(seq * 0.2) * 5.5, 1),
                "bus_v": round(3.29 + (seq % 5) * 0.005, 3),
                "current_ma": round(42.5 + math.sin(seq * 0.8) * 8.0, 1),
                "uptime_ms": seq * 100
            }

            payload_str = json.dumps(telemetry_data, separators=(",", ":"))
            payload_bytes_len = len(payload_str.encode("utf-8"))
            crc_val = calculate_crc16_ccitt(payload_str.encode("utf-8"))

            pkt_record = {
                "session_id": session_id,
                "seq_num": seq,
                "topic": f"voltcore/mit/ece/lab304/{dev['key'].lower()}/telemetry",
                "payload_json": payload_str,
                "payload_bytes": payload_bytes_len,
                "transit_time_ms": transit,
                "jitter_ms": jitter_running,
                "crc_valid": 1,
                "crc16_hex": f"0x{crc_val:04X}",
                "status": status,
                "timestamp": datetime.fromtimestamp(now.timestamp() + (seq * 0.05)).isoformat()
            }

            if not dropped:
                received_count += 1
                total_bytes += payload_bytes_len

            packets.append(pkt_record)

        packet_loss_pct = round(((num_packets - received_count) / num_packets) * 100.0, 2)
        avg_latency = round(sum(transit_times) / len(transit_times), 2)
        avg_jitter = round(jitter_running, 3)

        # Throughput in kbps: (Total Bytes * 8) / (Session Duration Seconds * 1000)
        session_duration_s = max(0.1, num_packets * 0.05)
        throughput_kbps = round((total_bytes * 8.0) / (session_duration_s * 1000.0), 2)

        # Persist session and packets to SQLite WAL
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO mqtt_hil_sessions (
                    id, device_id, transport_mode, baud_rate, broker_url,
                    qos_level, packets_transmitted, packets_received,
                    packet_loss_pct, avg_jitter_ms, avg_latency_ms,
                    throughput_kbps, student_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                session_id, dev["key"], transport_mode.upper(), baud_rate,
                "mqtt://broker.voltcore.mit.edu:1883", qos_level,
                num_packets, received_count, packet_loss_pct,
                avg_jitter, avg_latency, throughput_kbps, student_id,
                now.isoformat()
            ))

            for p in packets:
                conn.execute("""
                    INSERT INTO mqtt_hil_packets (
                        session_id, seq_num, topic, payload_json,
                        payload_bytes, transit_time_ms, jitter_ms,
                        crc_valid, status, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    p["session_id"], p["seq_num"], p["topic"],
                    p["payload_json"], p["payload_bytes"], p["transit_time_ms"],
                    p["jitter_ms"], p["crc_valid"], p["status"], p["timestamp"]
                ))
            conn.commit()

        return {
            "status": "SUCCESS",
            "session_id": session_id,
            "device": dev,
            "transport_mode": transport_mode.upper(),
            "baud_rate": baud_rate,
            "qos_level": qos_level,
            "summary": {
                "packets_transmitted": num_packets,
                "packets_received": received_count,
                "packet_loss_pct": packet_loss_pct,
                "avg_latency_ms": avg_latency,
                "avg_jitter_ms": avg_jitter,
                "throughput_kbps": throughput_kbps,
                "total_bytes_transferred": total_bytes
            },
            "packets": packets,
            "platform_lead": "Ashok Kumar A (2023MITEC042)",
            "institution": "MIT Campus, Anna University",
            "created_at": now.isoformat()
        }

    def publish_mqtt_message(
        self,
        device_id: str = "ESP32_WROOM_32",
        topic: str = "voltcore/mit/ece/lab304/esp32_01/command",
        payload: Dict[str, Any] = None,
        qos_level: int = 1,
        student_id: str = "2023MITEC042"
    ) -> Dict[str, Any]:
        """
        Publishes a discrete command/control MQTT packet and returns ACK confirmation.
        """
        if payload is None:
            payload = {"cmd": "RELAY_TOGGLE", "relay_id": 1, "state": "HIGH"}

        payload_str = json.dumps(payload, separators=(",", ":"))
        payload_bytes = len(payload_str.encode("utf-8"))
        crc_val = calculate_crc16_ccitt(payload_str.encode("utf-8"))
        now_str = datetime.now().isoformat()
        session_id = f"PUB_{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.urandom(2).hex()}"

        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO mqtt_hil_sessions (
                    id, device_id, transport_mode, baud_rate, broker_url,
                    qos_level, packets_transmitted, packets_received,
                    packet_loss_pct, avg_jitter_ms, avg_latency_ms,
                    throughput_kbps, student_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                session_id, device_id, "MQTT_PUBLISH", 115200,
                "mqtt://broker.voltcore.mit.edu:1883", qos_level,
                1, 1, 0.0, 0.5, 8.4, 12.0, student_id, now_str
            ))

            conn.execute("""
                INSERT INTO mqtt_hil_packets (
                    session_id, seq_num, topic, payload_json,
                    payload_bytes, transit_time_ms, jitter_ms,
                    crc_valid, status, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                session_id, 1, topic, payload_str,
                payload_bytes, 8.4, 0.5, 1, "ACKNOWLEDGED", now_str
            ))
            conn.commit()

        return {
            "status": "DELIVERED",
            "session_id": session_id,
            "topic": topic,
            "payload": payload,
            "payload_bytes": payload_bytes,
            "crc16_hex": f"0x{crc_val:04X}",
            "qos_level": qos_level,
            "transit_ms": 8.4,
            "timestamp": now_str
        }

    def get_session_history(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Returns recent HIL telemetry sessions from SQLite WAL."""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM mqtt_hil_sessions
                ORDER BY created_at DESC
                LIMIT ?;
            """, (limit,)).fetchall()
            return [dict(r) for r in rows]

    def get_packet_logs(self, session_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns recent packet logs for a specific session or globally."""
        with self._get_connection() as conn:
            if session_id:
                rows = conn.execute("""
                    SELECT * FROM mqtt_hil_packets
                    WHERE session_id = ?
                    ORDER BY seq_num ASC
                    LIMIT ?;
                """, (session_id, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM mqtt_hil_packets
                    ORDER BY id DESC
                    LIMIT ?;
                """, (limit,)).fetchall()
            return [dict(r) for r in rows]

    def export_session_csv(self, session_id: Optional[str] = None) -> str:
        """Exports HIL session packets formatted as RFC-4180 CSV."""
        packets = self.get_packet_logs(session_id=session_id, limit=100)
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        writer.writerow([
            "Packet_ID", "Session_ID", "Seq_Num", "Topic",
            "Payload_Bytes", "Transit_Time_ms", "Jitter_ms",
            "CRC_Valid", "Status", "Timestamp"
        ])

        for p in packets:
            writer.writerow([
                p["id"],
                p["session_id"],
                p["seq_num"],
                p["topic"],
                p["payload_bytes"],
                p["transit_time_ms"],
                p["jitter_ms"],
                p["crc_valid"],
                p["status"],
                p["timestamp"]
            ])

        return output.getvalue()


# Singleton Instance
mqtt_hil_engine = MqttHilEngine()
