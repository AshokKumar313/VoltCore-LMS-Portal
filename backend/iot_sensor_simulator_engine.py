"""
========================================================================================
VoltCore Apex Academia - IoT Sensor Telemetry Simulator Engine (Phase 32)
Anna University / MIT Campus Standards (Department of Electronics Engineering)
Target Facility: Lab 304 (Hardware Prototyping & Real-Time Embedded Systems Lab)
Regulation: Anna University ECE Regulation 2023
Platform Lead / System Architect: Ashok Kumar A (2023MITEC042)
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet
========================================================================================
"""

import os
import csv
import io
import json
import uuid
import random
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "voltcore_lms.db")
DEFAULT_STUDENT_ID = "2023MITEC042"
DEFAULT_NODE_ID = "ESP32_LAB304_DHT22_IR"


class IoTSensorSimulatorEngine:
    """
    Lightweight, thread-safe IoT Sensor Telemetry Simulator engine.
    Supports simulated ESP32/Arduino sensor streams (DHT22 temperature & humidity,
    IR proximity detection counters) logged directly to SQLite WAL mode with manual
    refresh triggers (zero background polling loops).
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Establishes an optimized SQLite connection in WAL mode."""
        conn = sqlite3.connect(self.db_path, timeout=10.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_db(self):
        """Initializes tables for simulated IoT sensor streams and session metrics."""
        with self._lock:
            conn = self._get_connection()
            try:
                # 1. Telemetry Readings Table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS iot_simulated_telemetry_readings (
                        reading_id TEXT PRIMARY KEY,
                        node_id TEXT NOT NULL,
                        student_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        temperature_c REAL NOT NULL,
                        humidity_pct REAL NOT NULL,
                        ir_proximity_count INTEGER NOT NULL,
                        rssi_dbm INTEGER NOT NULL,
                        bus_voltage_v REAL NOT NULL,
                        status TEXT NOT NULL,
                        checksum TEXT NOT NULL,
                        metadata_json TEXT NOT NULL
                    );
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_iot_sim_node ON iot_simulated_telemetry_readings(node_id);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_iot_sim_time ON iot_simulated_telemetry_readings(timestamp);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_iot_sim_student ON iot_simulated_telemetry_readings(student_id);")

                # 2. Simulator Aggregate Sessions Table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS iot_simulated_sessions (
                        session_id TEXT PRIMARY KEY,
                        node_id TEXT NOT NULL,
                        student_id TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        total_packets INTEGER NOT NULL,
                        avg_temperature REAL NOT NULL,
                        avg_humidity REAL NOT NULL,
                        total_ir_events INTEGER NOT NULL
                    );
                """)
                conn.commit()
            finally:
                conn.close()

    @staticmethod
    def _calculate_checksum(node_id: str, temp: float, hum: float, ir_count: int, ts: str) -> str:
        """Generates deterministic pseudo-CRC16 checksum for sensor packet integrity."""
        raw = f"{node_id}:{temp:.2f}:{hum:.2f}:{ir_count}:{ts}".encode("utf-8")
        crc = 0xFFFF
        for byte in raw:
            crc ^= (byte << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc = ((crc << 1) ^ 0x1021) & 0xFFFF
                else:
                    crc = (crc << 1) & 0xFFFF
        return f"0x{crc:04X}"

    def generate_simulated_reading(
        self,
        node_id: str = DEFAULT_NODE_ID,
        student_id: str = DEFAULT_STUDENT_ID,
        baseline_temp_c: float = 27.5,
        baseline_humidity_pct: float = 58.0,
        current_ir_count: Optional[int] = None,
        trigger_ir_event: bool = False
    ) -> Dict[str, Any]:
        """
        Generates a single realistic simulated sensor telemetry packet on demand.
        Zero background polling loops: invoked strictly upon manual user trigger.
        """
        # Determine latest cumulative IR count from database if not supplied
        if current_ir_count is None:
            latest = self.get_latest_reading(node_id)
            prior_count = latest["ir_proximity_count"] if latest else 12
        else:
            prior_count = current_ir_count

        ir_delta = 1 if trigger_ir_event or random.random() < 0.28 else 0
        new_ir_count = prior_count + ir_delta

        # Environmental thermal and psychrometric fluctuations
        temp_drift = round(baseline_temp_c + random.uniform(-0.8, 1.4), 2)
        humidity_drift = round(baseline_humidity_pct + random.uniform(-1.8, 2.2), 2)
        humidity_drift = max(10.0, min(99.0, humidity_drift))

        # Radio signal strength (RSSI) and battery voltage
        rssi = random.randint(-74, -56)
        bus_voltage = round(3.28 + random.uniform(-0.04, 0.04), 3)

        # Threshold safety evaluations
        status = "NORMAL"
        alerts = []
        if temp_drift >= 35.0:
            status = "HIGH_TEMP_ALERT"
            alerts.append(f"Temperature threshold exceeded: {temp_drift}°C >= 35.0°C")
        elif humidity_drift >= 75.0:
            status = "HIGH_HUMIDITY_ALERT"
            alerts.append(f"High Relative Humidity: {humidity_drift}% RH >= 75.0%")
        elif ir_delta > 0:
            status = "OBSTACLE_DETECTED"

        reading_id = f"TEL_{uuid.uuid4().hex[:10].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat()
        checksum = self._calculate_checksum(node_id, temp_drift, humidity_drift, new_ir_count, now_iso)

        metadata = {
            "sensor_model": "DHT22 (AM2302) + TCRT5000 IR",
            "microcontroller": "ESP32-WROOM-32 (FreeRTOS Core 1)",
            "sampling_mode": "Manual User Trigger (Zero Background Polling)",
            "alerts": alerts,
            "ir_delta": ir_delta
        }

        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT INTO iot_simulated_telemetry_readings
                    (reading_id, node_id, student_id, timestamp, temperature_c, humidity_pct,
                     ir_proximity_count, rssi_dbm, bus_voltage_v, status, checksum, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    reading_id, node_id, student_id, now_iso, temp_drift, humidity_drift,
                    new_ir_count, rssi, bus_voltage, status, checksum, json.dumps(metadata)
                ))
                conn.commit()
            finally:
                conn.close()

        return {
            "status": "SUCCESS",
            "reading_id": reading_id,
            "node_id": node_id,
            "student_id": student_id,
            "timestamp": now_iso,
            "temperature_c": temp_drift,
            "humidity_pct": humidity_drift,
            "ir_proximity_count": new_ir_count,
            "ir_delta": ir_delta,
            "rssi_dbm": rssi,
            "bus_voltage_v": bus_voltage,
            "telemetry_status": status,
            "checksum": checksum,
            "metadata": metadata
        }

    def generate_burst_readings(
        self,
        count: int = 5,
        node_id: str = DEFAULT_NODE_ID,
        student_id: str = DEFAULT_STUDENT_ID,
        baseline_temp_c: float = 27.5,
        baseline_humidity_pct: float = 58.0
    ) -> List[Dict[str, Any]]:
        """
        Generates a discrete burst of readings on manual trigger.
        Executes strictly synchronously in sub-10ms without background workers.
        """
        burst_readings = []
        cur_ir = None
        for i in range(max(1, min(count, 50))):
            reading = self.generate_simulated_reading(
                node_id=node_id,
                student_id=student_id,
                baseline_temp_c=baseline_temp_c,
                baseline_humidity_pct=baseline_humidity_pct,
                current_ir_count=cur_ir
            )
            cur_ir = reading["ir_proximity_count"]
            burst_readings.append(reading)
        return burst_readings

    def ingest_custom_reading(
        self,
        payload: Dict[str, Any],
        student_id: str = DEFAULT_STUDENT_ID
    ) -> Dict[str, Any]:
        """Ingests a verified custom sensor telemetry reading into the WAL database."""
        node_id = str(payload.get("node_id", DEFAULT_NODE_ID))
        temp = float(payload.get("temperature_c", 25.0))
        hum = float(payload.get("humidity_pct", 50.0))
        ir_count = int(payload.get("ir_proximity_count", 0))
        rssi = int(payload.get("rssi_dbm", -65))
        v_bus = float(payload.get("bus_voltage_v", 3.3))
        reading_status = str(payload.get("status", "NORMAL"))

        # Range sanity validation
        if not (-40.0 <= temp <= 125.0):
            return {"status": "ERROR", "message": f"Temperature out of sensor physical bounds: {temp}°C"}
        if not (0.0 <= hum <= 100.0):
            return {"status": "ERROR", "message": f"Humidity out of bounds: {hum}%"}

        reading_id = f"TEL_{uuid.uuid4().hex[:10].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat()
        checksum = self._calculate_checksum(node_id, temp, hum, ir_count, now_iso)
        metadata = payload.get("metadata", {"source": "custom_client_packet"})

        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute("""
                    INSERT INTO iot_simulated_telemetry_readings
                    (reading_id, node_id, student_id, timestamp, temperature_c, humidity_pct,
                     ir_proximity_count, rssi_dbm, bus_voltage_v, status, checksum, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    reading_id, node_id, student_id, now_iso, temp, hum,
                    ir_count, rssi, v_bus, reading_status, checksum, json.dumps(metadata)
                ))
                conn.commit()
            finally:
                conn.close()

        return {
            "status": "SUCCESS",
            "reading_id": reading_id,
            "node_id": node_id,
            "timestamp": now_iso,
            "temperature_c": temp,
            "humidity_pct": hum,
            "ir_proximity_count": ir_count,
            "checksum": checksum
        }

    def get_latest_reading(self, node_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieves the single most recent telemetry packet."""
        with self._lock:
            conn = self._get_connection()
            try:
                if node_id:
                    cur = conn.execute(
                        "SELECT * FROM iot_simulated_telemetry_readings WHERE node_id = ? ORDER BY timestamp DESC LIMIT 1;",
                        (node_id,)
                    )
                else:
                    cur = conn.execute(
                        "SELECT * FROM iot_simulated_telemetry_readings ORDER BY timestamp DESC LIMIT 1;"
                    )
                row = cur.fetchone()
                if not row:
                    return None
                return self._row_to_dict(row)
            finally:
                conn.close()

    def get_telemetry_readings(
        self,
        node_id: Optional[str] = None,
        limit: int = 30,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Retrieves paginated historical telemetry readings in descending order."""
        with self._lock:
            conn = self._get_connection()
            try:
                if node_id:
                    cur = conn.execute(
                        "SELECT * FROM iot_simulated_telemetry_readings WHERE node_id = ? ORDER BY timestamp DESC LIMIT ? OFFSET ?;",
                        (node_id, limit, offset)
                    )
                else:
                    cur = conn.execute(
                        "SELECT * FROM iot_simulated_telemetry_readings ORDER BY timestamp DESC LIMIT ? OFFSET ?;",
                        (limit, offset)
                    )
                rows = cur.fetchall()
                return [self._row_to_dict(r) for r in rows]
            finally:
                conn.close()

    def get_telemetry_statistics(self, node_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculates instantaneous summary aggregates for temperature, humidity, and IR proximity."""
        with self._lock:
            conn = self._get_connection()
            try:
                where_clause = "WHERE node_id = ?" if node_id else ""
                params = (node_id,) if node_id else ()

                cur = conn.execute(f"""
                    SELECT
                        COUNT(*) as total_packets,
                        ROUND(AVG(temperature_c), 2) as avg_temp,
                        ROUND(MIN(temperature_c), 2) as min_temp,
                        ROUND(MAX(temperature_c), 2) as max_temp,
                        ROUND(AVG(humidity_pct), 2) as avg_humidity,
                        ROUND(MIN(humidity_pct), 2) as min_humidity,
                        ROUND(MAX(humidity_pct), 2) as max_humidity,
                        COALESCE(MAX(ir_proximity_count), 0) as current_ir_count,
                        SUM(CASE WHEN status != 'NORMAL' THEN 1 ELSE 0 END) as alert_count
                    FROM iot_simulated_telemetry_readings
                    {where_clause};
                """, params)
                row = cur.fetchone()

                return {
                    "node_id": node_id or "ALL_NODES",
                    "total_packets": row["total_packets"] or 0,
                    "temperature": {
                        "avg": row["avg_temp"] or 0.0,
                        "min": row["min_temp"] or 0.0,
                        "max": row["max_temp"] or 0.0
                    },
                    "humidity": {
                        "avg": row["avg_humidity"] or 0.0,
                        "min": row["min_humidity"] or 0.0,
                        "max": row["max_humidity"] or 0.0
                    },
                    "current_ir_count": row["current_ir_count"] or 0,
                    "alert_count": row["alert_count"] or 0
                }
            finally:
                conn.close()

    def export_telemetry_csv(
        self,
        node_id: Optional[str] = None,
        limit: int = 500
    ) -> str:
        """
        Exports historical telemetry readings as a compliant RFC 4180 CSV string.
        Enables instant local downloads without third-party dependencies.
        """
        readings = self.get_telemetry_readings(node_id=node_id, limit=limit)
        output = io.StringIO()
        fieldnames = [
            "reading_id",
            "timestamp",
            "node_id",
            "student_id",
            "temperature_c",
            "humidity_pct",
            "ir_proximity_count",
            "rssi_dbm",
            "bus_voltage_v",
            "status",
            "checksum"
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for r in readings:
            writer.writerow({
                "reading_id": r["reading_id"],
                "timestamp": r["timestamp"],
                "node_id": r["node_id"],
                "student_id": r["student_id"],
                "temperature_c": r["temperature_c"],
                "humidity_pct": r["humidity_pct"],
                "ir_proximity_count": r["ir_proximity_count"],
                "rssi_dbm": r["rssi_dbm"],
                "bus_voltage_v": r["bus_voltage_v"],
                "status": r["status"],
                "checksum": r["checksum"]
            })

        return output.getvalue()

    def clear_simulated_readings(self, node_id: Optional[str] = None) -> Dict[str, Any]:
        """Purges simulated readings for automated test harnesses or session resets."""
        with self._lock:
            conn = self._get_connection()
            try:
                if node_id:
                    conn.execute("DELETE FROM iot_simulated_telemetry_readings WHERE node_id = ?;", (node_id,))
                else:
                    conn.execute("DELETE FROM iot_simulated_telemetry_readings;")
                conn.commit()
                return {"status": "SUCCESS", "message": "Telemetry readings cleared."}
            finally:
                conn.close()

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        """Serializes SQLite row into structured telemetry dictionary."""
        return {
            "reading_id": row["reading_id"],
            "node_id": row["node_id"],
            "student_id": row["student_id"],
            "timestamp": row["timestamp"],
            "temperature_c": row["temperature_c"],
            "humidity_pct": row["humidity_pct"],
            "ir_proximity_count": row["ir_proximity_count"],
            "rssi_dbm": row["rssi_dbm"],
            "bus_voltage_v": row["bus_voltage_v"],
            "status": row["status"],
            "checksum": row["checksum"],
            "metadata": json.loads(row["metadata_json"])
        }


# Singleton Simulator Engine Instance
iot_sensor_simulator_engine = IoTSensorSimulatorEngine()
